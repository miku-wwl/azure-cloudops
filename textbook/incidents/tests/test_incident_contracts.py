from __future__ import annotations

import re
import unittest
from pathlib import Path


CONTRACTS = Path(__file__).resolve().parents[1] / "CONTRACTS.md"
REQUIRED_IDS = {f"IR-{number:02d}" for number in range(1, 13)}
MANDATORY = {"IR-01", "IR-02", "IR-05", "IR-07", "IR-08", "IR-10", "IR-11", "IR-12"}
REQUIRED_FIELDS = (
    "Lecture mapping",
    "Execution class / verification status",
    "Healthy baseline",
    "Target scope",
    "Fault mechanism",
    "Expected failure category",
    "Diagnostic hypotheses",
    "Discriminating probes",
    "Root-cause evidence",
    "Minimal repair",
    "Same-probe recovery",
    "Negative assertions",
    "Cleanup",
    "Required permissions",
    "Cost assumptions",
)


class IncidentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = CONTRACTS.read_text(encoding="utf-8")
        headings = list(re.finditer(r"^## (IR-\d{2}) — .+$", cls.source, re.MULTILINE))
        cls.sections = {
            match.group(1): cls.source[match.start():headings[index + 1].start() if index + 1 < len(headings) else len(cls.source)]
            for index, match in enumerate(headings)
        }

    def test_exactly_twelve_incident_contracts_are_present(self) -> None:
        self.assertEqual(set(self.sections), REQUIRED_IDS)

    def test_every_contract_has_all_required_evidence_fields_and_unrun_status(self) -> None:
        for incident_id, source in self.sections.items():
            with self.subTest(incident=incident_id):
                for field in REQUIRED_FIELDS:
                    self.assertIn(f"**{field}:**", source)
                self.assertIn("Live Azure status: `NOT_RUN`", source)
                self.assertRegex(source, r"(?m)^- \*\*Lecture mapping:\*\* AZ[0-9]{2}-[0-9]{2}")

    def test_only_eight_roadmap_scenarios_are_marked_mandatory_for_local_execution(self) -> None:
        marked = {
            incident_id
            for incident_id, source in self.sections.items()
            if "`MANDATORY_LOCAL_E8`" in source
        }
        self.assertEqual(marked, MANDATORY)
        for incident_id in REQUIRED_IDS - MANDATORY:
            self.assertIn("`DESIGN_ONLY`", self.sections[incident_id])


if __name__ == "__main__":
    unittest.main()
