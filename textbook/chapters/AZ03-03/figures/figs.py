"""Original source-generated governance/evidence figures for AZ03-03."""

from figlib import Fig, NAVY, TEAL, ORANGE, RED, GREEN, MUTED


# Figure 9-1: request-time policy outcomes and post-success remediation.
f = Fig(760, 400)
f.text(380, 23, "Azure Policy effect 对请求与后续修复的时机不同", size=12, weight=700, color=NAVY, anchor="middle")
f.box(20, 107, 121, 82, "ARM request", ["create / update", "resource properties"], "gray", title_size=9.2, size=8.0, lh=16)
f.box(177, 92, 154, 112, "Policy request checks", ["assignment + scope", "definition condition", "effect"], "navy", title_size=9.2, size=8.0, lh=16)
f.arrow((141, 148), (177, 148), color=NAVY)
f.box(379, 49, 153, 89, "Deny", ["matching request", "blocked before RP"], "red", title_size=9.4, size=8.0, lh=16)
f.box(379, 158, 153, 89, "Audit", ["request continues", "compliance finding"], "orange", title_size=9.4, size=8.0, lh=16)
f.box(578, 115, 159, 99, "Resource Provider", ["handles accepted", "request"], "green", title_size=9.2, size=8.0, lh=16)
f.arrow((331, 119), (379, 94), color=RED, label="effect", dx=0, dy=-9, label_size=7.5)
f.arrow((331, 148), (379, 201), color=ORANGE, label="effect", dx=-3, dy=0, label_size=7.5)
f.arrow((532, 204), (578, 174), color=GREEN)
f.box(220, 290, 316, 66, "deployIfNotExists", ["provider success → configurable delay → existence check", "missing configuration → deployment using assignment identity"], "teal", title_size=9.1, size=7.9, lh=15)
f.arrow((656, 214), (536, 312), color=TEAL, label="post-success", dx=8, dy=-8, label_size=7.4)
f.text(380, 386, "Existing non-compliant resources may require a remediation task; assignment alone does not prove repair.", size=8.1, color=RED, anchor="middle")
f.save("policy-timeline.svg")


# Figure 9-2: management Activity Log and resource data-plane logs.
f = Fig(760, 390)
f.text(380, 23, "先按 control plane / data plane 选择证据来源", size=12, weight=700, color=NAVY, anchor="middle")
f.box(28, 75, 313, 120, "Azure Resource Manager · control plane", ["create / update / delete / started action", "Azure Monitor Activity Log（默认收集）", "scope · caller · operation · status · correlation ID"], "navy", title_size=9.5, size=8.0, lh=16)
f.box(418, 75, 314, 120, "Resource service · data plane", ["Key Vault secret read / Storage data operation", "service resource logs or application evidence", "diagnostic setting must select supported categories"], "teal", title_size=9.5, size=8.0, lh=16)
f.box(28, 239, 313, 83, "Activity Log blind spots", ["Reads are not typically captured.", "Pre-operation ARM authn/authz rejection creates no entry."], "orange", title_size=9.0, size=7.8, lh=15)
f.box(418, 239, 314, 83, "Resource log boundary", ["Resource logs are not collected by default.", "A missing entry does not prove no data request."], "orange", title_size=9.0, size=7.8, lh=15)
f.arrow((184, 195), (184, 239), color=ORANGE)
f.arrow((575, 195), (575, 239), color=ORANGE)
f.text(380, 357, "Activity Log retention: 90 days; longer retention needs an export destination and its own access / cost review.", size=8.2, color=RED, anchor="middle")
f.save("activity-evidence.svg")


# Figure 9-3: Defender recommendation and optional Policy effect.
f = Fig(760, 390)
f.text(380, 23, "Defender 评估姿态；选定 recommendation 才接入 Policy enforcement", size=11.7, weight=700, color=NAVY, anchor="middle")
f.box(23, 83, 162, 111, "Resource assessment", ["MCSB / configured standard", "assessment time", "finding"], "gray", title_size=9.2, size=7.8, lh=16)
f.box(232, 83, 179, 111, "Recommendation", ["posture advice", "secure score summary", "does not itself deny"], "orange", title_size=9.2, size=7.8, lh=16)
f.arrow((185, 138), (232, 138), color=ORANGE)
f.box(463, 49, 131, 91, "Optional Deny", ["Policy blocks", "matching request"], "red", title_size=9.2, size=7.8, lh=16)
f.box(463, 157, 131, 91, "Optional Enforce", ["Policy DINE", "remediation path"], "teal", title_size=9.2, size=7.8, lh=16)
f.arrow((411, 120), (463, 96), color=RED, label="supported subset", dx=8, dy=-9, label_size=7.1)
f.arrow((411, 157), (463, 202), color=TEAL, label="effect configured", dx=5, dy=5, label_size=7.1)
f.box(621, 82, 119, 120, "Workload plans", ["separate protection", "scope / coverage", "check current price"], "navy", title_size=9.1, size=7.8, lh=16)
f.text(380, 313, "Foundational CSPM is distinct from optional paid plans; Secure Score is not a request-time decision record.", size=8.1, color=RED, anchor="middle")
f.text(380, 365, "Confirm recommendation support, Policy assignment, effect, scope and remediation identity.", size=8.0, color=MUTED, anchor="middle")
f.save("defender-policy-bridge.svg")
