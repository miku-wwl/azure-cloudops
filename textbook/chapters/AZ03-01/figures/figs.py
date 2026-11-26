"""Original mechanism figures for AZ03-01."""

from figlib import Fig, NAVY, TEAL, ORANGE, RED, GREEN, MUTED


# Figure 7-1: one token is issued for one resource API audience.
f = Fig(760, 366)
f.text(380, 23, "先让接收 API 信任这张 token：audience 是资源边界", size=12.2, weight=700, color=NAVY, anchor="middle")
f.box(22, 82, 142, 76, "Client", ["asks Entra for", "API-A access token"], "gray", title_size=9.8, size=8.4)
f.box(210, 82, 160, 76, "Microsoft Entra ID", ["signs token for", "requested resource"], "navy", title_size=9.5, size=8.2)
f.box(431, 51, 146, 91, "API-A", ["check signature + issuer", "tenant + audience", "time + API policy"], "green", title_size=9.5, size=8.0)
f.box(617, 51, 122, 91, "Accept", ["then evaluate", "authorization"], "teal", title_size=9.5, size=8.2)
f.arrow((164, 120), (210, 120), color=NAVY, label="token request", dy=-9, label_size=7.8)
f.arrow((370, 120), (431, 104), color=GREEN, label="aud = API-A", dy=-9, label_size=7.8)
f.arrow((577, 96), (617, 96), color=GREEN)
f.box(431, 202, 146, 81, "API-B", ["audience mismatch", "reject before RBAC"], "red", title_size=9.4, size=8.0)
f.arrow((370, 137), (431, 235), color=RED, label="same token", dx=2, dy=0, label_size=7.8)
f.box(617, 202, 122, 81, "Reject", ["wrong recipient", "does not mean", "identity is invalid"], "orange", title_size=9.5, size=7.7)
f.arrow((577, 242), (617, 242), color=RED)
f.text(380, 319, "Model boundary: a fixture boolean stands in for prior signature trust; this lab does not parse or cryptographically validate a JWT.", size=8.2, color=MUTED, anchor="middle")
f.text(380, 341, "A token for Azure Resource Manager is not automatically a token for Azure Storage data endpoints.", size=8.6, color=RED, anchor="middle")
f.save("token-audience-boundary.svg")


# Figure 7-2: token subject is resolved to a tenant-local principal; role assignments evaluate separately.
f = Fig(760, 370)
f.text(380, 23, "token 通过接收边界后，RBAC 才计算主体、操作与作用域", size=12, weight=700, color=NAVY, anchor="middle")
f.box(20, 92, 177, 102, "Accepted token context", ["tid = tenant boundary", "oid = tenant-local object", "aud = this API", "scp / roles ≠ Azure RBAC"], "navy", title_size=9.4, size=8.0, lh=15)
f.box(255, 64, 200, 112, "Role assignments", ["principalId + roleDefinitionId", "assignment scope", "direct + inherited parents", "resolve in the token tenant"], "teal", title_size=9.5, size=8.0, lh=15)
f.arrow((197, 135), (255, 120), color=NAVY, label="principal + request", dy=-9, label_size=7.7)
f.box(513, 48, 221, 105, "Control plane", ["Actions − NotActions", "manage ARM resources", "ARM authorizes control calls"], "orange", title_size=9.6, size=8.1, lh=15)
f.box(513, 201, 221, 105, "Data plane", ["DataActions − NotDataActions", "operate on object data", "service-specific evaluation"], "green", title_size=9.3, size=8.0, lh=15)
f.arrow((455, 115), (513, 100), color=ORANGE, label="management action", dy=-9, label_size=7.5)
f.arrow((455, 144), (513, 250), color=GREEN, label="data operation", dy=7, label_size=7.5)
f.text(380, 336, "NotActions and NotDataActions subtract within one role definition; a separate role assignment can still grant the operation.", size=8.2, color=RED, anchor="middle")
f.save("rbac-decision-planes.svg")


# Figure 7-3: scope permissions inherit downward, but not sideways.
f = Fig(760, 408)
f.text(380, 23, "role assignment 向下继承到子 scope；不会横向穿过兄弟资源", size=12, weight=700, color=NAVY, anchor="middle")
f.box(277, 48, 206, 48, "Subscription", ["parent scope"], "navy", title_size=9.6, size=7.9)
f.box(277, 117, 206, 48, "Resource group", ["assignment may inherit"], "teal", title_size=9.4, size=7.9)
f.box(277, 186, 206, 48, "Storage account", ["common parent"], "navy", title_size=9.4, size=7.9)
f.arrow((380, 96), (380, 117), color=GREEN, label="inherits", dx=40, dy=0, label_size=7.4)
f.arrow((380, 165), (380, 186), color=GREEN, label="inherits", dx=40, dy=0, label_size=7.4)
f.box(70, 270, 238, 62, "Container: payments", ["child scope", "DataAction: blob read"], "green", title_size=9.2, size=7.9)
f.box(452, 270, 238, 62, "Container: audit", ["sibling scope", "not inherited from payments"], "orange", title_size=9.2, size=7.9)
f.arrow((333, 234), (220, 270), color=GREEN, label="child", dx=-7, dy=-5, label_size=7.2)
f.arrow((427, 234), (540, 270), color=GREEN, label="child", dx=7, dy=-5, label_size=7.2)
f.box(70, 350, 620, 38, "Operation plane must also match", ["Actions govern control-plane operations · DataActions govern data-plane operations"], "gray", title_size=9.0, size=8.0)
f.text(380, 402, "A role's assignableScopes limits where a custom role can be assigned; it is separate from an assignment's scope.", size=7.8, color=MUTED, anchor="middle")
f.save("scope-inheritance-and-actions.svg")
