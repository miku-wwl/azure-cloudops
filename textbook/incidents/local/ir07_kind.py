#!/usr/bin/env python3
"""Verify real kubelet image-pull failure/recovery in a disposable kind cluster."""
from __future__ import annotations

import argparse
import http.client
import json
import shutil
import socket
import subprocess
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def invoke(args: list[str], timeout: int = 30, input_bytes: bytes | None = None) -> dict[str, Any]:
    result = subprocess.run(args, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
    return {"command": args, "returncode": result.returncode, "output": result.stdout.decode("utf-8", "replace").strip()}


def record(evidence: dict[str, Any], key: str, args: list[str], timeout: int = 30, accepted: set[int] = {0}, input_bytes: bytes | None = None) -> dict[str, Any]:
    result = invoke(args, timeout, input_bytes)
    evidence.setdefault("commands", {})[key] = result
    if result["returncode"] not in accepted:
        raise RuntimeError(f"{key} exited {result['returncode']}: {result['output'][:1600]}")
    return result


def open_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def write_pod(path: Path, name: str, image: str, pull_policy: str, release: str) -> None:
    path.write_text(
        "apiVersion: v1\nkind: Pod\nmetadata:\n  name: " + name + "\n  namespace: " + NAMESPACE +
        "\nspec:\n  restartPolicy: Never\n  containers:\n  - name: app\n    image: " + image +
        "\n    imagePullPolicy: " + pull_policy +
        "\n    command: [\"/health_server\", \"--listen\", \"0.0.0.0:8080\", \"--release\", \"" + release + "\"]\n"
        "    ports:\n    - containerPort: 8080\n",
        encoding="utf-8",
    )


NAMESPACE = ""


def json_command(evidence: dict[str, Any], key: str, args: list[str], timeout: int = 30) -> Any:
    result = record(evidence, key, args, timeout)
    try:
        data = json.loads(result["output"])
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{key} did not return valid JSON") from exc
    evidence.setdefault("observations", {})[key] = data
    return data


def port_forward_probe(evidence: dict[str, Any], kubectl: list[str], pod: str, port: int) -> dict[str, Any]:
    host_port = open_port()
    log_path = evidence["_temporary_root"] / f"port-forward-{pod}.log"
    with log_path.open("wb") as stream:
        process = subprocess.Popen(kubectl + ["port-forward", "--address", "127.0.0.1", f"pod/{pod}", f"{host_port}:8080"],
                                   stdout=stream, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 25
            last_error = "port-forward has not accepted a connection"
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(f"port-forward exited {process.returncode}: {log_path.read_text(encoding='utf-8', errors='replace')}")
                try:
                    connection = http.client.HTTPConnection("127.0.0.1", host_port, timeout=2)
                    connection.request("GET", "/health")
                    response = connection.getresponse()
                    body = response.read(256).decode("utf-8", "replace")
                    result = {"status": response.status, "body": body, "release": response.getheader("X-Release"),
                              "url_path": "/health", "method": "GET"}
                    connection.close()
                    if response.status == 200:
                        evidence.setdefault("http_probes", {})[pod] = result
                        return result
                    last_error = f"HTTP {response.status}: {body}"
                except OSError as exc:
                    last_error = str(exc)
                time.sleep(0.2)
            raise RuntimeError(f"functional HTTP probe timed out: {last_error}")
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            evidence.setdefault("port_forward_cleanup", {})[pod] = {"process_exit": process.returncode,
                                                                  "log": log_path.read_text(encoding="utf-8", errors="replace")}


def run(node_image: str, health_binary: Path, registry_binary: Path, repo: Path, evidence_path: Path) -> dict[str, Any]:
    global NAMESPACE
    suffix = uuid.uuid4().hex[:8]
    cluster = f"azure-cloudops-ir07-{suffix}"
    namespace = f"ir07-{suffix}"
    NAMESPACE = namespace
    good_pod, bad_pod, repaired_pod = "good-" + suffix, "bad-" + suffix, "recovered-" + suffix
    image_tag = f"azure-cloudops/ir07-health:e8-{suffix}"
    missing_tag = f"missing-{suffix}"
    registry_image = f"localhost:5000/azure-cloudops/ir07-health:{missing_tag}"
    clusters_before = invoke(["kind", "get", "clusters"])
    evidence: dict[str, Any] = {
        "incident_id": "IR-07", "status": "FAILED", "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": {"cluster": cluster, "namespace": namespace, "registry_endpoint": "127.0.0.1:5000 inside the unique kind control-plane node",
                  "baseline_image": image_tag, "fault_image": registry_image, "network_policy": "manifest request is remapped to node loopback; no public registry is contacted"},
        "mechanism": "A real kubelet/containerd pull request reaches a run-owned local Distribution API fixture, which returns an actual 404 MANIFEST_UNKNOWN for the unique missing manifest. Recovery uses a separately built local image preloaded into this disposable cluster.",
        "commands": {}, "_temporary_root": None,
    }
    created_attempt = False
    namespace_created = False
    image_created = False
    temp_context: tempfile.TemporaryDirectory[str] | None = None
    try:
        work = repo / "work"
        work.mkdir(exist_ok=True)
        temp_context = tempfile.TemporaryDirectory(prefix="ir07-", dir=work)
        temp_root = Path(temp_context.name)
        evidence["_temporary_root"] = temp_root
        kubeconfig = temp_root / "kubeconfig"
        context = temp_root / "image"
        context.mkdir()
        shutil.copy2(health_binary, context / "health_server")
        (context / "Dockerfile").write_text("FROM scratch\nCOPY health_server /health_server\nENTRYPOINT [\"/health_server\"]\n", encoding="ascii")
        image_created = True
        record(evidence, "build_static_app_image", ["docker", "build", "--pull=false", "--network=none", "--tag", image_tag, str(context)], 120)
        config = temp_root / "kind-config.yaml"
        config.write_text(
            "kind: Cluster\napiVersion: kind.x-k8s.io/v1alpha4\n"
            "containerdConfigPatches:\n- |-\n    [plugins.\"io.containerd.grpc.v1.cri\".registry]\n      config_path = \"/etc/containerd/certs.d\"\n",
            encoding="utf-8",
        )
        created_attempt = True
        record(evidence, "create_unique_kind_cluster", ["kind", "create", "cluster", "--name", cluster, "--image", node_image,
                                                           "--config", str(config), "--kubeconfig", str(kubeconfig), "--wait", "120s"], 180)
        kubectl = ["kubectl", "--kubeconfig", str(kubeconfig)]
        nodes = record(evidence, "list_unique_cluster_nodes", ["kind", "get", "nodes", "--name", cluster])
        node_names = [line.strip() for line in nodes["output"].splitlines() if line.strip()]
        if len(node_names) != 1:
            raise RuntimeError(f"expected exactly one control-plane node, got: {node_names}")
        node = node_names[0]
        record(evidence, "load_synthetic_app_image", ["kind", "load", "docker-image", image_tag, "--name", cluster], 90)
        record(evidence, "write_local_registry_binary", ["docker", "exec", "-i", node, "sh", "-c", "cat > /root/ir07-registry && chmod 0755 /root/ir07-registry"],
               input_bytes=registry_binary.read_bytes())
        record(evidence, "verify_local_registry_binary", ["docker", "exec", node, "test", "-x", "/root/ir07-registry"])
        record(evidence, "start_loopback_registry_fixture", ["docker", "exec", "--detach", node, "/root/ir07-registry", "--listen", "127.0.0.1:5000",
                                                               "--log", "/root/ir07-registry.jsonl"])
        record(evidence, "configure_localhost_registry_remap", ["docker", "exec", node, "sh", "-c",
                "mkdir -p /etc/containerd/certs.d/localhost:5000 && printf '%s\\n' '[host.\"http://127.0.0.1:5000\"]' '  capabilities = [\"pull\", \"resolve\"]' > /etc/containerd/certs.d/localhost:5000/hosts.toml"])
        registry_probe = invoke(["docker", "exec", node, "curl", "--silent", "--show-error", "--fail", "--max-time", "2", "http://127.0.0.1:5000/v2/"])
        evidence["commands"]["registry_loopback_baseline"] = registry_probe
        if registry_probe["returncode"] != 0:
            raise RuntimeError("the local image registry fixture did not answer on node loopback")

        record(evidence, "create_namespace", kubectl + ["create", "namespace", namespace])
        namespace_created = True
        record(evidence, "apply_baseline_pod", kubectl + ["apply", "-f", str(write_manifest(temp_root, good_pod, image_tag, "Never", "e8-ir07-good"))])
        record(evidence, "wait_baseline_ready", kubectl + ["wait", "--namespace", namespace, "--for=condition=Ready", f"pod/{good_pod}", "--timeout=90s"], 100)
        baseline = port_forward_probe(evidence, kubectl + ["--namespace", namespace], good_pod, 8080)
        baseline_json = json_command(evidence, "baseline_pod_status", kubectl + ["get", "pod", "--namespace", namespace, good_pod, "-o", "json"])

        record(evidence, "apply_missing_manifest_pod", kubectl + ["apply", "-f", str(write_manifest(temp_root, bad_pod, registry_image, "Always", "unused"))])
        fault_json: Any = None
        fault_events: Any = None
        deadline = time.monotonic() + 100
        while time.monotonic() < deadline:
            fault_json = json.loads(record(evidence, "poll_fault_pod_status", kubectl + ["get", "pod", "--namespace", namespace, bad_pod, "-o", "json"]).get("output", "{}"))
            fault_events = json.loads(record(evidence, "poll_fault_pod_events", kubectl + ["get", "events", "--namespace", namespace, "--field-selector",
                    f"involvedObject.name={bad_pod}", "-o", "json"]).get("output", "{}"))
            statuses = fault_json.get("status", {}).get("containerStatuses", [])
            waiting = statuses[0].get("state", {}).get("waiting", {}) if statuses else {}
            event_list = fault_events.get("items", [])
            messages = [event.get("message", "") for event in event_list]
            if waiting.get("reason") in {"ErrImagePull", "ImagePullBackOff"} and any(
                "manifest unknown" in message.casefold() or "not found" in message.casefold() for message in messages
            ):
                break
            time.sleep(0.5)
        statuses = fault_json.get("status", {}).get("containerStatuses", []) if fault_json else []
        waiting = statuses[0].get("state", {}).get("waiting", {}) if statuses else {}
        event_list = fault_events.get("items", []) if fault_events else []
        messages = [event.get("message", "") for event in event_list]
        if waiting.get("reason") not in {"ErrImagePull", "ImagePullBackOff"} or not any(
            "manifest unknown" in message.casefold() or "not found" in message.casefold() for message in messages
        ):
            raise RuntimeError("no real kubelet image-pull failure plus local manifest-unknown event was observed")
        evidence.setdefault("observations", {})["fault_pod_status"] = fault_json
        evidence["observations"]["fault_warning_events"] = fault_events
        describe = record(evidence, "describe_fault_pod", kubectl + ["describe", "pod", "--namespace", namespace, bad_pod])
        evidence["observations"]["fault_pod_describe"] = describe["output"]
        registry_logs = record(evidence, "capture_registry_request_log", ["docker", "exec", node, "cat", "/root/ir07-registry.jsonl"], accepted={0})
        evidence["observations"]["registry_http_log"] = registry_logs["output"]
        if "/manifests/" not in registry_logs["output"] or "404" not in registry_logs["output"]:
            raise RuntimeError("local registry did not record an actual manifest 404 request")

        record(evidence, "apply_repaired_pod", kubectl + ["apply", "-f", str(write_manifest(temp_root, repaired_pod, image_tag, "Never", "e8-ir07-recovered"))])
        record(evidence, "wait_repaired_ready", kubectl + ["wait", "--namespace", namespace, "--for=condition=Ready", f"pod/{repaired_pod}", "--timeout=90s"], 100)
        recovery = port_forward_probe(evidence, kubectl + ["--namespace", namespace], repaired_pod, 8080)
        repaired_json = json_command(evidence, "repaired_pod_status", kubectl + ["get", "pod", "--namespace", namespace, repaired_pod, "-o", "json"])
        bad_after = json_command(evidence, "bad_image_negative_control_after_recovery", kubectl + ["get", "pod", "--namespace", namespace, bad_pod, "-o", "json"])
        bad_after_waiting = bad_after.get("status", {}).get("containerStatuses", [{}])[0].get("state", {}).get("waiting", {})
        evidence["checks"] = {
            "preexisting_shared_cluster_not_selected": cluster not in clusters_before.get("output", "").splitlines(),
            "baseline_pod_ready_and_http_probe_passed": baseline_json.get("status", {}).get("phase") == "Running" and baseline["status"] == 200 and baseline["body"].strip() == "healthy",
            "kubelet_observed_real_manifest_pull_failure": waiting.get("reason") in {"ErrImagePull", "ImagePullBackOff"} and any("manifest unknown" in message.casefold() or "not found" in message.casefold() for message in messages),
            "registry_recorded_local_404": "/manifests/" in registry_logs["output"] and "404" in registry_logs["output"],
            "recovery_same_http_probe_passed": repaired_json.get("status", {}).get("phase") == "Running" and recovery["status"] == 200 and recovery["body"].strip() == "healthy" and recovery["release"] == "e8-ir07-recovered",
            "missing_manifest_remains_rejected": bad_after_waiting.get("reason") in {"ErrImagePull", "ImagePullBackOff"},
        }
        evidence["ok"] = all(evidence["checks"].values())
        evidence["status"] = "LOCAL_VERIFIED" if evidence["ok"] else "FAILED"
    finally:
        # Remove only this run's namespace and cluster, then only its unique app image.
        if created_attempt:
            if namespace_created:
                cleanup_ns = invoke(["kubectl", "--kubeconfig", str(evidence.get("_temporary_root") / "kubeconfig"), "delete", "namespace", namespace, "--wait=true", "--timeout=60s"], 70)
                evidence.setdefault("cleanup", {})["delete_namespace"] = cleanup_ns
            else:
                evidence.setdefault("cleanup", {})["delete_namespace"] = {"returncode": 0, "output": "namespace was not created"}
            cleanup_cluster = invoke(["kind", "delete", "cluster", "--name", cluster], 90)
            evidence["cleanup"]["delete_unique_cluster"] = cleanup_cluster
            cluster_list = invoke(["kind", "get", "clusters"])
            evidence["cleanup"]["cluster_absent"] = cluster not in cluster_list.get("output", "").splitlines()
            evidence["cleanup"]["shared_cluster_still_present"] = "argo-canary-local" in cluster_list.get("output", "").splitlines()
        if image_created:
            image_cleanup = invoke(["docker", "image", "rm", "--force", image_tag], 30)
            evidence.setdefault("cleanup", {})["remove_unique_app_image"] = image_cleanup
            evidence["cleanup"]["app_image_absent"] = image_tag not in invoke(["docker", "image", "ls", "--format", "{{.Repository}}:{{.Tag}}"])["output"].splitlines()
        if temp_context is not None:
            temp_context.cleanup()
            evidence.setdefault("cleanup", {})["temporary_kubeconfig_and_build_context_removed"] = not temp_root.exists()
        if evidence.get("cleanup") and (not evidence["cleanup"].get("cluster_absent", True) or not evidence["cleanup"].get("shared_cluster_still_present", True)
                                         or not evidence["cleanup"].get("app_image_absent", True) or not evidence["cleanup"].get("temporary_kubeconfig_and_build_context_removed", True)):
            evidence["status"] = "FAILED_CLEANUP"
        evidence.pop("_temporary_root", None)
        evidence["completed_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return evidence


def write_manifest(root: Path, name: str, image: str, policy: str, release: str) -> Path:
    path = root / f"{name}.yaml"
    path.write_text(
        f"apiVersion: v1\nkind: Pod\nmetadata:\n  name: {name}\n  namespace: {NAMESPACE}\n"
        f"spec:\n  restartPolicy: Never\n  containers:\n  - name: app\n    image: {image}\n    imagePullPolicy: {policy}\n"
        f"    command: [\"/health_server\", \"--listen\", \"0.0.0.0:8080\", \"--release\", \"{release}\"]\n"
        "    ports:\n    - containerPort: 8080\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node-image", required=True, help="cached immutable kind node image")
    parser.add_argument("--health-binary", type=Path, required=True)
    parser.add_argument("--registry-binary", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, default=Path(__file__).resolve().parents[1] / "evidence" / "IR-07_local-kind.json")
    args = parser.parse_args()
    result = run(args.node_image, args.health_binary, args.registry_binary, args.repo.resolve(), args.evidence)
    if result.get("ok") and result.get("cleanup", {}).get("cluster_absent") and result.get("cleanup", {}).get("app_image_absent"):
        print("IR-07 LOCAL_VERIFIED: kubelet observed the local manifest 404, the repaired Pod passed the HTTP probe, and run-owned resources were removed.")
        return 0
    print(f"IR-07 {result.get('status', 'FAILED')}: inspect {args.evidence}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
