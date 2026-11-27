"""Keep one real Terraform apply open until the competing CLI check finishes."""

import hashlib
import os
from multiprocessing.connection import Listener
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHKEY = b"az07-02-local-lock-gate"
SOCKET_PATH: Path | None = None
if os.name == "nt":
    token = hashlib.sha256(str(ROOT).encode()).hexdigest()[:20]
    ADDRESS = rf"\\.\pipe\az07-02-{token}"
    FAMILY = "AF_PIPE"
else:
    work = ROOT / "work"
    work.mkdir(exist_ok=True)
    ADDRESS = str(work / "az07-02-lock-gate.sock")
    SOCKET_PATH = Path(ADDRESS)
    if SOCKET_PATH.exists():
        raise RuntimeError(
            f"lock gate path already exists; inspect the previous run before removing it: {SOCKET_PATH}"
        )
    FAMILY = "AF_UNIX"

try:
    with Listener(ADDRESS, family=FAMILY, authkey=AUTHKEY) as listener:
        print(
            "LOCK_GATE_OPEN: terraform apply is active and holds the local backend lock. "
            "Run a competing state-changing Terraform apply, then run scripts/release_state_lock.py.",
            flush=True,
        )
        with listener.accept() as connection:
            message = connection.recv()
            if message != "release":
                raise RuntimeError(f"unexpected gate message: {message!r}")
        print("LOCK_GATE_RELEASED", flush=True)
finally:
    if SOCKET_PATH is not None:
        SOCKET_PATH.unlink(missing_ok=True)
