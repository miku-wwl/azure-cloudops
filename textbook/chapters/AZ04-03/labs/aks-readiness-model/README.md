# AKS workload readiness model

This deterministic Python exercise evaluates synthetic JSON cases. It models a narrow subset of scheduling constraints, autoscaler eligibility, ACR registry-mode authorization, workload identity trust matching, probe/Service eligibility, DNS forwarding, PDB eviction and Kubernetes version skew.

Run from the repository root:

```powershell
python -m unittest discover -s textbook/chapters/AZ04-03/labs/aks-readiness-model -p "test_*.py" -v
python textbook/chapters/AZ04-03/labs/aks-readiness-model/aks_readiness_model.py
```

The fixture values and CLI output are generated locally. The model does not run Kubernetes, Docker, Azure CLI, AKS, Azure CNI, CoreDNS, ACR, Entra ID, OIDC federation or network requests. It is a teaching model for decision boundaries, not an AKS emulator and not proof that an Azure role assignment, scheduler, probe or upgrade will behave as predicted in a live cluster.

The local Docker daemon was unavailable during this lecture, so no disposable `kind` cluster was created. A local kubeconfig context inventory was read-only; no context was selected or changed and no cluster API request was made. This lab has no Azure prerequisites, does not read credentials and creates no cloud resources.
