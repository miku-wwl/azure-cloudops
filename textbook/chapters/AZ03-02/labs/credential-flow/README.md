# AZ03-02 offline credential-flow lab

Run from this directory:

~~~powershell
cd textbook/chapters/AZ03-02/labs/credential-flow
python -m unittest -v
python credential_flow_model.py
~~~

The fixtures contain fictional identity IDs and token claims. The model checks managed-identity selection, exact federated issuer/subject/audience matching, the final Key Vault token audience, a separate network gate, and a symbolic data authorization mode. It prints only decisions and reasons; it never contains or returns a secret value.

This is not an Azure, Entra, IMDS, OIDC, JWT, firewall, or Key Vault emulator. It does not create or validate signatures, request credentials, exchange tokens, resolve DNS, send network traffic, read a real role assignment, model propagation or token caching, or evaluate every Key Vault role and operation. The two authorization modes are a deliberately small teaching subset. A passing fixture proves only the local branch behavior.
