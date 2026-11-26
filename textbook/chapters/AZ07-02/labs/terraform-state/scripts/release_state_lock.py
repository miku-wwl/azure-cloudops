"""Release the local lock-holder only after observing the competing CLI result."""

import hashlib
import os
from multiprocessing.connection import Client
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHKEY = b"az07-02-local-lock-gate"
if os.name == "nt":
    token = hashlib.sha256(str(ROOT).encode()).hexdigest()[:20]
    ADDRESS = rf"\\.\pipe\az07-02-{token}"
    FAMILY = "AF_PIPE"
else:
    ADDRESS = str(ROOT / "work" / "az07-02-lock-gate.sock")
    FAMILY = "AF_UNIX"

with Client(ADDRESS, family=FAMILY, authkey=AUTHKEY) as connection:
    connection.send("release")
print("Sent release to the waiting local Terraform operation.")