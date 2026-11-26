"""Original credential-flow figures for AZ03-02."""

from figlib import Fig, NAVY, TEAL, ORANGE, RED, GREEN, MUTED


# Figure 8-1: identity lifecycle and token selection.
f = Fig(760, 390)
f.text(380, 23, "managed identity 把凭证生命周期交给平台；工作负载仍要选对身份", size=12, weight=700, color=NAVY, anchor="middle")
f.box(28, 72, 305, 109, "System-assigned identity", ["在 Azure resource 上启用", "生命周期与宿主绑定", "宿主删除时身份一并删除", "仅该宿主可使用"], "navy", title_size=9.6, size=8.0, lh=15)
f.box(427, 72, 305, 109, "User-assigned identity", ["作为独立 Azure resource 创建", "生命周期独立于 compute", "可关联多个宿主", "适合预授权与可替换工作负载"], "teal", title_size=9.6, size=8.0, lh=15)
f.box(224, 228, 312, 83, "Azure Identity SDK / managed identity endpoint", ["选择附加在此宿主上的 identity", "按目标资源请求 access token"], "green", title_size=9.5, size=8.0, lh=16)
f.arrow((180, 181), (300, 228), color=NAVY, label="宿主提供", dx=-9, dy=-6, label_size=7.7)
f.arrow((580, 181), (460, 228), color=TEAL, label="显式选择", dx=9, dy=-6, label_size=7.7)
f.box(244, 329, 272, 43, "Credential boundary", ["宿主上的代码都能请求该宿主可用的 identity token"], "orange", title_size=8.8, size=7.5)
f.arrow((380, 311), (380, 329), color=ORANGE)
f.text(380, 386, "多份 user-assigned identity 并存时，请显式指定目标 identity；不要把“默认选中”当作稳定合同。", size=8.1, color=RED, anchor="middle")
f.save("managed-identity-lifecycle.svg")


# Figure 8-2: external OIDC assertion and Entra resource token are different tokens.
f = Fig(760, 395)
f.text(380, 23, "Federation 接收外部 assertion，再签发面向目标 API 的 Entra access token", size=11.8, weight=700, color=NAVY, anchor="middle")
f.box(22, 81, 173, 104, "External IdP", ["GitHub / Kubernetes", "iss · sub · aud", "short-lived OIDC assertion"], "gray", title_size=9.5, size=8.0, lh=16)
f.box(251, 64, 245, 138, "Federated credential", ["issuer + subject + audience", "逐项精确、区分大小写匹配", "incoming aud: token exchange", "不保存 client secret"], "orange", title_size=9.3, size=7.8, lh=16)
f.box(554, 81, 183, 104, "Microsoft Entra ID", ["federated identity", "exchange assertion", "issue API token"], "navy", title_size=9.5, size=8.0, lh=16)
f.arrow((195, 132), (251, 132), color=ORANGE)
f.arrow((496, 132), (554, 132), color=GREEN, label="trusted assertion", dy=-10, label_size=7.3)
f.box(285, 260, 188, 81, "Key Vault endpoint", ["final aud = https://vault.azure.net", "then network + data authorization"], "green", title_size=9.4, size=7.9, lh=16)
f.arrow((646, 185), (473, 284), color=GREEN, label="Entra-issued access token", dx=5, dy=-7, label_size=7.3)
f.text(380, 370, "外部 assertion 的 audience 说明 Entra 可接受什么输入；Entra access token 的 audience 说明哪个 API 可接收它。", size=8.1, color=RED, anchor="middle")
f.save("federated-token-exchange.svg")


# Figure 8-3: Key Vault has independent network, authentication, and authorization gates.
f = Fig(760, 390)
f.text(380, 23, "Key Vault secret read 要同时通过网络、身份认证与数据面授权", size=12, weight=700, color=NAVY, anchor="middle")
f.box(22, 99, 162, 119, "1 · Network", ["DNS / route", "firewall / private endpoint", "caller path allowed?"], "orange", title_size=9.5, size=8.0, lh=16)
f.box(217, 99, 162, 119, "2 · Authentication", ["Entra access token", "aud = https://vault.azure.net", "tenant + principal"], "navy", title_size=9.3, size=8.0, lh=16)
f.box(412, 99, 162, 119, "3 · Data authorization", ["Azure RBAC mode:", "Key Vault Secrets User", "or legacy access policy"], "teal", title_size=9.0, size=7.8, lh=16)
f.box(607, 99, 131, 119, "4 · Operation", ["secrets/get", "secret value", "returned"], "green", title_size=9.3, size=8.0, lh=16)
f.arrow((184, 158), (217, 158), color=ORANGE)
f.arrow((379, 158), (412, 158), color=NAVY)
f.arrow((574, 158), (607, 158), color=GREEN)
f.box(106, 274, 548, 69, "Planes are separate", ["Key Vault Contributor manages the vault control plane; it grants no secret data read by itself.", "Firewall failure is a network result, not proof that the RBAC role is missing."], "gray", title_size=9.0, size=7.8, lh=15)
f.text(380, 374, "Valid identity, correct audience and a data role still cannot bypass a blocked network path.", size=8.1, color=RED, anchor="middle")
f.save("key-vault-gates.svg")
