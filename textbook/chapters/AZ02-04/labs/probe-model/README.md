# Load-balancer health-probe local model

Run the synthetic fixture from this directory:

~~~powershell
python -m unittest -v
python probe_model.py
~~~

The fixture compares a TCP listener check, an exact-200 Load Balancer HTTP probe, the Application Gateway default accepted range (200–399), a dedicated `/ready` path, an HTTPS certificate-validity assertion, and a Front Door last-N sample threshold. The route result is only the eligible priority candidate set. It never assigns a real request to an origin.

The model uses fictional `pay-east` and `pay-west` backends. Status codes, sample windows, probe outcomes and priorities are synthetic inputs; a green output is verified only for this Python fixture. The model does not start a server, issue HTTP/TCP requests, implement TLS/X.509, construct certificates/SNI, reproduce a Front Door edge mesh, choose a latency origin, apply weights/session affinity, apply WAF policy, execute an Application Gateway routing rule, or call Azure APIs. It does not emulate Azure Load Balancer flow hashing, connection state, or Azure control/data planes. The fixture boolean `backend_tls_valid` is an asserted outcome for certificate-chain, subject/hostname and validity checks; it is not a certificate parser. Azure Load Balancer HTTPS-probe certificate behavior is intentionally not modeled.

For Front Door, the fixture abstracts a single recent sample sequence. Real probes run from edge locations and health/routing behavior depends on the configured profile, origin group and current platform observations. The all-unhealthy line reports only the documented fallback candidate set; it does not fabricate which origin received a request.
