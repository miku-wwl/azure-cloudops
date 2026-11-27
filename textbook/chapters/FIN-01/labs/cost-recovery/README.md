# FIN-01 synthetic cost-recovery lab

This exercise is local and offline. `synthetic-ledger.json` contains fictional charges, credits, resource states, tags, allocation weights, budget thresholds and hourly commitment use. None of its dollar values is an Azure quote, a customer bill or an estimate for this project.

## Run

From the repository root:

```powershell
python textbook/chapters/FIN-01/labs/cost-recovery/finops_contract.py
python -m unittest discover -s textbook/chapters/FIN-01/labs/cost-recovery/tests -p "test_*.py" -v
```

The default report selects `actual` cost. Copy the JSON and change `selected_view` to `amortized` to inspect the alternative representation. The local contract keeps positive gross charges, credits and net cost separate; it resolves one direct or explicitly inherited tag; allocates shared costs only when weights total 100; leaves unexplained records unallocated; measures unused plan commitment per hour; warns on a budget threshold without stopping consumption; and returns review decisions without executing cleanup.

The checker deliberately does not parse Azure Cost Management exports, enforce Azure tag-inheritance behavior, model taxes/contracts/rerating, emulate reservation matching, evaluate actual retention policy or connect to Azure. A passing report proves only that this synthetic input satisfies these explicit checks.

## Practice

1. Run the baseline and reconcile gross, credits, net and unallocated amounts.
2. Copy the fixture; add a cost record without an owner and confirm it appears in `unallocated_gross`.
3. Change one shared weight so the total is not 100 and observe the fail-closed check.
4. Change the hourly usage series; compare utilization and unused commitment without carrying any unused hour forward.
5. Give a deleted resource a required retention item. Confirm that no cleanup is authorized. The script never deletes a resource, including when owner approval is recorded.

See `FUTURE-LIVE-READONLY.md` for a separately gated Azure observation procedure. It is documentation only and has not been run.
