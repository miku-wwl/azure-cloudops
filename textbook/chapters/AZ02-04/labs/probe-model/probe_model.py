"""Synthetic comparison of Azure load-balancer probe decisions.

This is a small teaching model, not an Azure emulator. It makes no network or
Azure API calls and does not assign real traffic to a backend.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys


class ModelInputError(ValueError):
    """Raised when the local fixture uses an unsupported or invalid value."""


@dataclass(frozen=True)
class Backend:
    name: str
    priority: int
    tcp_open: bool
    responses: dict[str, int | None]
    afd_samples: tuple[int | None, ...]
    backend_tls_valid: bool = True
    enabled: bool = True

    def status(self, path: str) -> int | None:
        return self.responses.get(path)


@dataclass(frozen=True)
class RouteDecision:
    candidates: tuple[str, ...]
    all_unhealthy_fallback: bool


def _status(value: object, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or not 100 <= value <= 599:
        raise ModelInputError(f"{label} must be an HTTP status 100..599 or null")
    return value


def backend_from_dict(raw: dict) -> Backend:
    try:
        name = raw["name"]
        priority = raw["priority"]
        tcp_open = raw["tcp_open"]
        responses_raw = raw["responses"]
        samples_raw = raw["afd_samples"]
        tls_valid = raw.get("backend_tls_valid", True)
        enabled = raw.get("enabled", True)
    except (KeyError, TypeError) as exc:
        raise ModelInputError(f"backend is missing a required field: {exc}") from exc
    if not isinstance(name, str) or not name.strip():
        raise ModelInputError("backend name must be a non-empty string")
    if isinstance(priority, bool) or not isinstance(priority, int) or priority < 1:
        raise ModelInputError("priority must be a positive integer")
    if not isinstance(tcp_open, bool) or not isinstance(tls_valid, bool) or not isinstance(enabled, bool):
        raise ModelInputError("tcp_open, backend_tls_valid and enabled must be booleans")
    if not isinstance(responses_raw, dict) or not isinstance(samples_raw, list):
        raise ModelInputError("responses must be an object and afd_samples must be a list")
    responses = {path: _status(code, f"response {path}") for path, code in responses_raw.items()}
    samples = tuple(_status(code, "AFD sample") for code in samples_raw)
    return Backend(name, priority, tcp_open, responses, samples, tls_valid, enabled)


def lb_healthy(backend: Backend, protocol: str, path: str = "/") -> bool:
    """Model TCP reachability or exact-200 HTTP probe eligibility only."""
    protocol = protocol.upper()
    if protocol == "TCP":
        return backend.tcp_open
    if protocol == "HTTP":
        return backend.tcp_open and backend.status(path) == 200
    if protocol == "HTTPS":
        raise ModelInputError("Azure Load Balancer HTTPS probe certificate behavior is outside this model")
    raise ModelInputError("Load Balancer probe protocol must be TCP or HTTP in this model")


def appgw_healthy(
    backend: Backend,
    *,
    path: str = "/",
    protocol: str = "HTTP",
    accepted_range: tuple[int, int] = (200, 399),
) -> bool:
    """Model one App Gateway HTTP(S) probe status range and a TLS-validity assertion."""
    protocol = protocol.upper()
    if protocol not in {"HTTP", "HTTPS"}:
        raise ModelInputError("Application Gateway probe protocol must be HTTP or HTTPS")
    low, high = accepted_range
    if not (100 <= low <= high <= 599):
        raise ModelInputError("accepted_range must be a valid inclusive HTTP status range")
    if not backend.tcp_open:
        return False
    status = backend.status(path)
    if status is None or not low <= status <= high:
        return False
    if protocol == "HTTPS":
        return backend.backend_tls_valid
    return True


def front_door_healthy(
    samples: tuple[int | None, ...], *, sample_size: int, successful_required: int
) -> bool:
    """Use one synthetic last-n sample window; HTTP/HTTPS probes require exact 200."""
    if sample_size < 1 or not 1 <= successful_required <= sample_size:
        raise ModelInputError("require 1 <= successful_required <= sample_size")
    recent = samples[-sample_size:]
    return len(recent) == sample_size and sum(code == 200 for code in recent) >= successful_required


def select_priority_candidates(
    backends: list[Backend], health: dict[str, bool]
) -> RouteDecision:
    """Return a candidate set; do not simulate Front Door request assignment."""
    if len({backend.name for backend in backends}) != len(backends):
        raise ModelInputError("backend names must be unique")
    enabled = [backend for backend in backends if backend.enabled]
    if not enabled:
        raise ModelInputError("at least one origin must be enabled")
    healthy = [backend for backend in enabled if health.get(backend.name, False)]
    if not healthy:
        return RouteDecision(tuple(backend.name for backend in enabled), True)
    best_priority = min(backend.priority for backend in healthy)
    return RouteDecision(
        tuple(backend.name for backend in healthy if backend.priority == best_priority), False
    )


def load_document(path: Path) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or not isinstance(document.get("scenarios"), list):
        raise ModelInputError("fixture must contain a scenarios array")
    return document


def evaluate_scenario(scenario: dict, *, sample_size: int, successful_required: int) -> tuple[list[tuple], RouteDecision]:
    backends = [backend_from_dict(raw) for raw in scenario["backends"]]
    if len({backend.name for backend in backends}) != len(backends):
        raise ModelInputError("backend names must be unique")
    results = []
    afd_health: dict[str, bool] = {}
    for backend in backends:
        values = (
            lb_healthy(backend, "TCP"),
            lb_healthy(backend, "HTTP"),
            appgw_healthy(backend),
            appgw_healthy(backend, path="/ready"),
            appgw_healthy(backend, path="/ready", protocol="HTTPS"),
            front_door_healthy(
                backend.afd_samples,
                sample_size=sample_size,
                successful_required=successful_required,
            ),
        )
        results.append((backend.name, *values))
        afd_health[backend.name] = values[-1]
    return results, select_priority_candidates(backends, afd_health)


def render(path: Path) -> list[str]:
    document = load_document(path)
    sample = document["front_door_window"]
    sample_size = sample["sample_size"]
    successful_required = sample["successful_required"]
    lines = ["Synthetic only: no Azure API, DNS query, probe, network connection or traffic assignment."]
    for scenario in document["scenarios"]:
        results, decision = evaluate_scenario(
            scenario, sample_size=sample_size, successful_required=successful_required
        )
        lines.append(f"{scenario['name']}:")
        for name, lb_tcp, lb_http, appgw_default, appgw_ready, appgw_https, afd in results:
            state = lambda healthy: "healthy" if healthy else "unhealthy"
            lines.append(
                f"  {name}: LB/TCP={state(lb_tcp)} LB/HTTP(/)={state(lb_http)} "
                f"AppGW/default(/)={state(appgw_default)} AppGW(/ready)={state(appgw_ready)} "
                f"AppGW/HTTPS(/ready)={state(appgw_https)} FrontDoor={state(afd)}"
            )
        suffix = " (all-unhealthy documented fallback; candidate set only)" if decision.all_unhealthy_fallback else ""
        lines.append(f"  Front Door priority candidates: {', '.join(decision.candidates)}{suffix}")
    return lines


def main() -> int:
    default = Path(__file__).with_name("scenarios") / "probe-cases.json"
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    try:
        print("\n".join(render(path)))
    except (OSError, KeyError, TypeError, json.JSONDecodeError, ModelInputError) as exc:
        print(f"fixture error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
