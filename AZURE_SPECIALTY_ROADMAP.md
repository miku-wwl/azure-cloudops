# Azure CloudOps & Enterprise Infrastructure — 学习与实战路线图（2026 V2）

> **仓库：** [`miku-wwl/azure-cloudops`](https://github.com/miku-wwl/azure-cloudops)  
> **方向：** Azure Cloud Engineer / Senior Cloud & Infrastructure Engineer / Platform Engineer / SRE  
> **原则：** 基于现有 AZ-104、AZ-305、Terraform、Kubernetes 知识，重在企业级设计与真实运维证据，而非重复备考。  
> **状态：** 当前是学习规划；**没有完成、执行或验证的实验，不得标记为 PASS**。  
> **更新：** 2026-11-05

## 1. 升级目标与边界

原路线图的 Azure Networking、Identity、PowerShell、Monitor/KQL、Incident Response、Backup/Restore 全部保留。对照高级 Cloud / Infrastructure Engineer 岗位，新增两个重要能力：

1. **Enterprise Landing Zone & Cloud Governance**：管理组、订阅分区、网络拓扑、身份、Policy、监控与成本治理，以及架构决策记录（ADR）。
2. **Terraform / Infrastructure Delivery Engineering**：模块设计、State 隔离、计划审查、CI/CD、最小权限部署与变更回滚。

**本项目仍是专项实战学习仓，不扩张为第三个大型平台项目。** 不做自研控制台、Terraform 控制平面、复杂多租户系统；KPCP 已覆盖对应的平台产品工程能力。

成功标准不是“看完课程”或“积累文件数量”，而是能够解释架构权衡、亲自部署、独立定位故障、执行恢复，并拿出可复验的脱敏证据。

## 2. 核心技能优先级

| 优先级 | 技能 | 应掌握的高级问题 | 最低可交付结果 |
|---|---|---|---|
| **P0** | Azure Landing Zone / 架构 | 如何拆分管理组和订阅？共享平台和应用团队的边界在哪？Policy 如何落地？ | 设计图 + 2 条 ADR + 权限/订阅矩阵 |
| **P0** | Azure Networking | Private Endpoint 为什么解析错误？NSG、UDR、路由、DNS 如何逐层排查？ | 一次真实网络故障诊断 + 恢复证据 |
| **P0** | Terraform Engineering | 模块如何复用？State 如何隔离、保护与恢复？Plan 谁来审核？ | 最小 IaC 实验 + 静态验证 + Plan 证据 |
| **P1** | Identity / Security / Governance | RBAC 与 Azure Policy 的限制有什么不同？如何证明最小权限？ | allow/deny 测试与权限设计 |
| **P1** | Azure Monitor / KQL | 哪些日志和指标能够识别用户影响？如何降低告警噪声？ | 5 条有数据来源说明的 KQL + 告警验证 |
| **P1** | Incident Response / Recovery | 如何建立正常基线、找到根因、回滚和验证恢复？ | 2 份 RCA + 一次真实恢复验证 |
| **P2** | PowerShell / Azure CLI | 如何安全盘点资源、处理 API 失败、确保默认只读？ | 小型只读审计脚本与测试 |
| **P2** | Hybrid / DR Design | VPN/ExpressRoute、DNS 转发、跨区域恢复的技术与成本取舍？ | 设计 ADR；不要求付费部署 |

先做 P0/P1 的真实闭环，P2 以设计和小规模练习补充。

## 3. 学习模块（保持 Azure 专项，不重复 KPCP）

### M0 — Enterprise Landing Zone & Architecture（新增，P0）

**核心：** Cloud Adoption Framework / Azure Landing Zones；Management Groups、Subscriptions、Resource Groups、Azure Policy、RBAC、命名与标签规范、Hub-Spoke 或 Virtual WAN 的选择、平台/工作负载责任边界。

- 设计“一个组织、两个工作负载环境（dev/prod）”的**参考方案**：管理组/订阅层级、连接、权限、日志与审计、成本归属。
- 写出至少两条 ADR：例如 Hub-Spoke vs Virtual WAN；分订阅 vs 单订阅；集中式 vs 分布式日志。
- 对每项设计区分“个人订阅可验证”和“仅企业级设计讨论”。管理组、管理订阅与跨订阅部署可能受权限限制。
- **不要**为了作品集强行部署完整企业 Landing Zone、大型 Azure Firewall 或 Virtual WAN。

**验收：** 可讲清楚架构图、信任边界、治理控制点与技术选型，至少 2 条明确的决策权衡。

### M1 — Azure Networking & Private Connectivity（P0）

**核心：** VNet/Subnet、Peering、NSG、UDR、Private Endpoint、Private DNS Zone/Link、DNS 查询链路。

- 先写设计：访问路径、名称解析预期、路由和防火墙/NSG 生效位置。
- 在**个人授权非生产**范围内搭建一个最小实验；记录正常连通性。
- 注入可逆错误（如断开 Private DNS Zone Link、错误 NSG 规则），观察故障并恢复。
- **验收：** 修复前后 `nslookup` 或等效查询、连接测试、配置差异与 RCA；具体资源按预算选择。

### M2 — Network Troubleshooting（P0）

**核心：** Network Watcher、IP Flow Verify、Next Hop、Connection Troubleshoot、Effective Routes / Security Rules。

- 按 **DNS → 路由 → NSG/防火墙 → 身份/服务访问 → 应用响应** 排查，明确每一步的证据。
- 不直接看预设故障答案，先作假设、用工具验证，再归因。
- **验收：** 能指出具体失败环节；恢复后对同一探针复测，并记录不是根因的备选假设。

### M3 — Entra ID, RBAC, Managed Identity & Governance（P1）

**核心：** Entra ID、Azure RBAC、Managed Identity、Key Vault、Azure Policy、作用域和继承；PIM 仅作可选设计。

- 比较 Azure RBAC 和 Azure Policy：前者管理谁能执行什么管理操作，后者约束资源配置与合规状态；不要混淆数据平面权限。
- 设计并验证一个 Key Vault 或 Storage 的 allow/deny 权限场景：用最小权限修复，不直接授予 Owner。
- 审视 Policy 的 `audit`、`deny`、`modify` 等效果及落地限制；不要对现有共享资源施加阻断策略。
- **验收：** 允许与拒绝路径都经过实际测试，附作用域、角色、身份和策略配置的脱敏证据。

### M4 — Terraform Engineering & Controlled Delivery（新增，P0）

**核心：** AzureRM / AzAPI 适用场景、Terraform Modules、Provider/Module 版本固定、Remote State、State Locking、CI 验证、Plan 审批、OIDC Federation。

- 只构建一个**最小、可销毁**的 Azure 基础设施练习（例如 VNet + Subnet + NSG）；不建设自己的 IaC 平台。
- 用变量、输出、模块接口和环境目录解释复用边界；不要为了“模块化”制造过度抽象。
- 明确 State 的存储、加密、权限、锁定与环境隔离。不要提交 `*.tfstate`、敏感 `tfvars`、计划文件或身份凭证。
- PR 运行 `terraform fmt -check`、`terraform validate`、必要的静态扫描；**计划输出应在明确的身份与凭证边界下生成和审查**，不可把 `validate` 当成真实 Plan/Apply。
- 设计（并在具备权限时验证）Plan → 审核 → Apply 的权限分离，以及漂移检测、回滚与销毁。
- **验收：** 小型配置能静态验证；若实际部署，则保存真实 Plan/Apply/Destroy 与清理证据，注明工具版本和目标 Azure Scope。

### M5 — Azure Monitor, Log Analytics & KQL（P1）

**核心：** Log Analytics、Azure Monitor、Activity Logs、Resource Logs、Metrics、Data Collection Rules、KQL、Action Groups、Alert Processing Rules。

- 无订阅时先练官方 Log Analytics Demo；注明样本数据不是个人 Azure 环境。
- 编写至少 5 条查询，包括筛选、分组/时间窗、资源关联、异常定位等；**在查询旁写清数据表和诊断用途**。
- 选一个自己的小规模事件验证告警链路：信号来源 → 条件 → 触发 → 处理 → 恢复。
- **验收：** 查询可重跑、来源明确；如果告警尚未真实触发，就标记为 `NOT RUN`。

### M6 — Incident Response & RCA（P1）

**核心：** Baseline、故障注入、假设检验、检测时间、诊断、回滚/修复、影响评估和事后复盘。

- 至少两个不同类别的实验：**网络/DNS** + **身份/RBAC 或监控**。
- 每个案例写下发现方式、影响范围、排障时间线、根因证据、修复与预防措施。
- 明确实验与真实生产 On-call 是不同经历，不对外声称具有未发生的企业生产事故经验。
- **验收：** 两个可复现、完整的故障处理闭环；有修复前后证据。

### M7 — PowerShell / Azure CLI Operations Automation（P2）

**核心：** Az PowerShell / Azure CLI、资源盘点、标签与配置审计、错误处理、Pester。

- 先学习 Microsoft Azure Resource Inventory (ARI) 的设计，再写一个限定范围的**只读**资源盘点脚本。
- 输出 JSON/CSV，记录依赖与版本；权限不足时失败应清晰且安全。
- **验收：** 至少一组离线测试及一次授权环境实际运行记录；默认不修改资源。

### M8 — Backup, Restore & Disaster Recovery（P1）

**核心：** Backup Policy、恢复点、恢复测试、数据完整性、RPO/RTO、保留成本。

- 选择最小成本对象做一次**真实恢复**，记录备份时点与恢复目标。
- 在恢复后检查文件校验和或等效数据完整性，而不是仅凭“备份任务成功”。
- 区分设计 RTO/RPO 目标与实验实际恢复时长、数据损失窗口。
- **验收：** 恢复步骤、测试结果、实际耗时、残留资源与费用检查。

### M9 — Optional Validation / Hybrid Design（P2）

- Microsoft Applied Skills 的 Azure Networking / Azure Monitor 评估可作为额外验证，**不作为毕业门槛**。
- Hybrid Networking（VPN/ExpressRoute、DNS 转发）、跨区域 DR、Virtual WAN、Azure Firewall：优先做 ADR 和故障分析，不要求为简历耗费高额云费用。
- 根据应聘 JD 调整权重，避免为了扩展覆盖面降低完成质量。

## 4. 四个 Sprint（建议节奏，可按实际权限与成本调整）

| Sprint | 主线 | 实际学习任务 | Gate |
|---|---|---|---|
| **S1 — Architecture** | M0 + M1 设计 + M3 | Landing Zone 架构图、2 条 ADR、网络/DNS 路径、RBAC/Policy 模型 | 能解释边界与技术取舍；文档不冒充部署 |
| **S2 — IaC & Networking** | M4 + M1 + M2 | 最小 Terraform Lab、CI 静态验证、网络故障注入与排障 | 网络故障真实恢复；IaC 状态按实际证据标记 |
| **S3 — Operations** | M3 + M5 + M6 + M7 | allow/deny 权限实验、KQL、告警链路、只读巡检、第二份 RCA | 有可重现探针、查询和恢复证据 |
| **S4 — Recovery & Portfolio** | M8 + 总结 | 真实 Backup/Restore、成本复核、脱敏、求职岗位映射 | 全部必选验收项通过后才标记 Portfolio Ready |

**最小可执行版本：** 如果时间或 Azure 预算有限，优先完成 **M0 设计 + M1/M2 网络事故 + M4 小型 IaC + M5 KQL + M6 RCA**，其余模块逐项补齐。没有授权云环境就先做设计和离线验证；不要伪造 live evidence。

## 5. 每次实验的证据与质量门槛

记录以下信息即可，不强制新建模板文件夹：

1. **Scope：** 目标、实验 Subscription/RG（公开时脱敏）、Region、所有者、预计费用与停止条件。
2. **Architecture：** 正常路径、权限边界、预期结果、失败假设和设计决策。
3. **Commands & versions：** CLI/PowerShell/Terraform 版本、关键操作与配置；敏感参数脱敏。
4. **Baseline：** 故障注入前的工作状态以及可以复测的诊断探针。
5. **Experiment：** 实际变更、错误现象、检测方式、排查假设与时间线。
6. **Recovery：** 修复、相同探针复测、数据/服务有效性检查与 RCA。
7. **Cleanup：** Destroy/删除后的资源清点、备份/日志保留、费用和遗留项。
8. **Evidence status：** 只用 `PLANNED`、`DESIGNED`、`STATIC_CHECK_PASS`、`DEPLOYED`、`LIVE_VERIFIED`、`RECOVERED`、`CLEANED_UP`、`BLOCKED`、`NOT_RUN` 中**确实满足**的状态；一个状态不能代表其他状态。

### 示例：Private Endpoint 解析故障

正常 DNS/连接通过 → 在隔离测试范围内断开 Private DNS Zone Link → 记录失败的解析与连接结果 → 使用 Network Watcher / DNS/路由/NSG 证据逐层诊断 → 恢复 Zone Link → 复测相同探针 → 写 RCA、成本与清理记录。

**禁止**对生产、雇主、共享或未知所有权资源注入故障。

## 6. 成本、权限和安全红线

- **默认 free-first：** 文档、ADR、离线设计与公开 Demo KQL 优先；只有明确收益时才启用 Azure 付费资源。
- 每次部署前确认地区定价、资源依赖、预计运行时间和自动/人工清理方案；预算告警不等于硬限额。
- Private Endpoint、VM、Managed Disk、Public IP、Log Analytics 摄取与保留、Backup、Firewall 等均可能收费，部分保留资源在删除 RG 后仍需额外处理。
- 明确 CI 身份和权限：避免在 PR 上暴露可直接 Apply 的凭据；优先短期令牌和受控审批。
- State / Plan / 日志中可能包含敏感数据；不要上传密钥、`tfstate`、凭证或未脱敏截图。
- PIM、管理组、某些 Enterprise 服务或跨订阅权限需要额外授权和许可；没有权限就做设计，不声称已部署。

## 7. 求职叙述方式（按岗位，不夸大）

| 岗位 | 最值得展示 | 不能混淆的点 |
|---|---|---|
| Senior Cloud & Infrastructure Engineer | Landing Zone 设计、Terraform 交付、Governance、Network 与运维事件 | 设计案例不等于真实企业大规模落地 |
| Azure Cloud / Platform Engineer | IaC 模块、Policy/RBAC、连接性、安全边界、CI 变更控制 | `terraform validate` 不等于 Apply |
| SRE / CloudOps | Monitor/KQL、Network Watcher、事件 RCA、备份恢复 | 模拟 incident 不等于生产 On-call |
| Cloud Architect | ADR、拓扑、权限与成本/可靠性取舍 | 参考架构不等于生产实施 |

可以在简历中写经过验证的具体结果，例如“在隔离 Azure Lab 中复现并定位 Private DNS 配置故障，恢复后验证网络路径”；**不要**写“负责大型企业 Azure Landing Zone 生产建设”之类未经发生的经历。

## 8. 完成定义（Definition of Done）

- [ ] **Architecture：** 一份 Landing Zone 设计图，2 条 ADR，明确权限、网络、治理与成本权衡。
- [ ] **Networking：** 一次完整 DNS/NSG/路由故障的真实诊断和恢复。
- [ ] **Terraform：** 可重现的最小基础设施配置；真实执行了哪些 `fmt` / `validate` / `plan` / `apply` / `destroy`，逐项注明并保留证据。
- [ ] **Identity：** 最小权限 allow/deny 路径有验证结果。
- [ ] **Monitoring：** 5 条有出处的 KQL；至少一次真实告警链路验证。
- [ ] **Incident：** 至少 2 份可复验 RCA，覆盖两个不同故障类别。
- [ ] **Automation：** 一份默认只读、含错误处理与测试的资源审计脚本。
- [ ] **Recovery：** 实际恢复数据成功，记录恢复时长和验证方式。
- [ ] **Security & Cost：** 证据脱敏、部署授权、费用复核、销毁与残留清点完成。

**Gate 规则：** 全部必选项目有证据后才能标记 `PORTFOLIO_READY`。不足时继续保持 `PLANNED` 或 `PARTIAL`，明确阻塞原因。这个仓库当前仍为 **PLANNED / NOT LIVE VERIFIED**。

## 9. 查资料时优先使用的官方入口

只保留官方入口，不在本仓库复制教程或额外创建学习材料：

- [Azure Landing Zones / Cloud Adoption Framework](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/)
- [Azure Landing Zones Terraform deployment guidance](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/deploy-landing-zones-with-terraform)
- [Microsoft Learn — AZ-700 labs](https://microsoftlearning.github.io/AZ-700-Designing-and-Implementing-Microsoft-Azure-Networking-Solutions/)
- [Microsoft Learn — AZ-104 labs](https://microsoftlearning.github.io/AZ-104-MicrosoftAzureAdministrator/)
- [Microsoft Learn — AZ-305 case studies](https://microsoftlearning.github.io/AZ-305-DesigningMicrosoftAzureInfrastructureSolutions/)
- [Azure Monitor / Log Analytics](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-tutorial)
- [Azure Resource Inventory (ARI)](https://github.com/microsoft/ARI)

**下一步：** 完成 S1 的设计决策与网络路径，再启动最小、可回收的 S2 实验。先把一条故障闭环做扎实，再扩展覆盖面。
