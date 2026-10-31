# Azure Cloud Operations & Incident Response — 专项训练路线图（2026）

> **定位：** `azure-cloudops` 仓库的实操与工程证据路线图；不建设第三个大型云平台。  
> **适用方向：** Azure Cloud Engineer / Azure Platform Engineer / SRE / CloudOps  
> **已有基础：** AZ-104、AZ-305；Kubernetes、Terraform、云原生工程及 KPCP 项目。  
> **训练目标：** 补齐 KPCP 尚未深入覆盖的 Azure Networking、Identity、PowerShell、Azure Monitor/KQL、故障排查和备份恢复实践。  
> **整理日期：** 2026-10-31  
> **当前状态：** Planned / 本仓库内各实操尚未执行；打勾前必须保存可复现证据。

## 1. 训练原则

- **不重复建设 KPCP。** 不再做新的 Terraform 管理平台、Kubernetes 控制器或云资源 Dashboard。
- **重点练 Azure 专有的运维能力。** 从应用部署转向网络连通性、权限、诊断、变更、恢复与治理。
- **使用“设计 → 实施 → 故障 → 恢复 → 证据”闭环。** 每个实验都要形成能复现、能解释的技术材料。
- **按岗位区分重点。** Azure Platform 偏架构、IaC、治理；Azure CloudOps 偏诊断、变更、PowerShell、KQL 和值班交接。
- **不把模拟经验包装成生产经验。** 实验能证明实操能力，但不能代替企业环境的真实 On-call 或生产运维经历。

## 2. 四类微软官方学习资源

| 资源 | 训练定位 | 优先内容 | 官方入口 |
|---|---|---|---|
| **AZ-305** | 架构设计与技术权衡 | Network、Identity、Governance、Monitoring、业务连续性设计 | [AZ-305 Case Studies](https://microsoftlearning.github.io/AZ-305-DesigningMicrosoftAzureInfrastructureSolutions/) |
| **AZ-104** | 部署、管理和运维 | Lab 02a/02b、Lab 10、Lab 11 | [AZ-104 Labs](https://microsoftlearning.github.io/AZ-104-MicrosoftAzureAdministrator/) |
| **AZ-700** | 深入 Azure 网络 | VNet Peering、DNS、NSG、Routing、Private Endpoint | [AZ-700 Exercises](https://microsoftlearning.github.io/AZ-700-Designing-and-Implementing-Microsoft-Azure-Networking-Solutions/) |
| **Applied Skills** | 在微软实验考核环境验证实操 | Azure Networking、Azure Monitor | [Networking Assessment](https://learn.microsoft.com/en-us/credentials/applied-skills/configure-secure-workloads-use-azure-virtual-networking/) · [Azure Monitor Assessment](https://learn.microsoft.com/en-us/credentials/applied-skills/deploy-and-configure-azure-monitor/) |

**重要区别：** AZ-305 主要是设计案例，不是 AZ-104/AZ-700 式的逐步操作实验。建议把它放在实验**之前**做方案设计，再用 AZ-104/AZ-700 进行验证。两项 Applied Skills 为交互式实验评估；参加前核对当时的资格、服务和费用规则。

## 3. 八个专项训练模块

### M1 — Azure Networking（最高优先级）

**内容：** VNet、Subnet、VNet Peering、NSG、UDR、Private Endpoint、Private DNS。

- 先做 AZ-305 的 **Network Infrastructure Design** 案例，写出网络拓扑、信任边界、DNS 解析路径与技术选型理由。
- 再选做 AZ-700 的 VNet、DNS、Peering 和 Private Endpoint 实验。
- 故障实验：将测试环境中的 Private DNS Zone Link 或 NSG 规则配置错误，验证现象并恢复。
- **验收：** 正常路径连通；错误路径可解释；提供网络图、DNS 查询、路由/NSG 验证记录和 RCA。

资源：[AZ-700 目录](https://microsoftlearning.github.io/AZ-700-Designing-and-Implementing-Microsoft-Azure-Networking-Solutions/) · [Azure Networking Applied Skills](https://learn.microsoft.com/en-us/credentials/applied-skills/configure-secure-workloads-use-azure-virtual-networking/)

**成本：** VNet 与部分规则本身费用有限，但 Private Endpoint、测试 VM、公共 IP、Firewall 等可能收费；不必运行完整 Azure Firewall/ExpressRoute 环境。

### M2 — Azure Network Troubleshooting

**内容：** Network Watcher、IP Flow Verify、Next Hop、Connection Troubleshoot、Effective Security Rules / Routes。

- 针对连接失败，按 **DNS → 路由 → NSG/防火墙 → 服务权限 → 应用响应** 的顺序排障。
- 对测试环境的错误 NSG/路由开展至少一次独立诊断；不能直接查看预设答案。
- **验收：** 能指出是哪条规则或哪个路由/DNS 环节导致故障，并保存修复前后证据。

资源：[微软网络监控与诊断指南](https://learn.microsoft.com/en-us/azure/networking/design-guide/monitor) · [Connection Troubleshoot](https://learn.microsoft.com/en-us/azure/network-watcher/connection-troubleshoot-manage)

### M3 — Entra ID / RBAC / Managed Identity / Governance

**内容：** Entra ID、RBAC、Managed Identity、Key Vault、Azure Policy；PIM 作为可选扩展。

- 使用 AZ-305 的 **Authentication & Authorization** 和 **Governance** 案例写出权限设计。
- 完成 AZ-104 Lab 02a（RBAC）和 Lab 02b（Azure Policy）。
- 设计一个“身份缺少 Key Vault 权限”的故障，用最小权限修复，不通过直接授予 Owner 解决。
- **验收：** 授权访问成功、越权访问失败；能说明 Scope、Role Assignment 和 Managed Identity 的边界。

资源：[AZ-104 Labs](https://microsoftlearning.github.io/AZ-104-MicrosoftAzureAdministrator/) · [AZ-305 Case Studies](https://microsoftlearning.github.io/AZ-305-DesigningMicrosoftAzureInfrastructureSolutions/)

**注意：** PIM 等特性可能需要特定 Microsoft Entra 许可；无法使用时可以先完成设计与文档，不伪称真实验证。

### M4 — Azure Monitor + KQL（可以免费先练）

**内容：** Log Analytics、KQL、Azure Monitor、Application Insights 基础。

- 先在微软 **Log Analytics Demo** 环境练习 KQL，无须使用自己的 Azure 订阅。
- 能写出 `where`、`summarize`、`bin()`、`join`、时间窗口等基础查询，并解释查询含义。
- 选一个 AZ-305 **Logging & Monitoring** 案例，设计指标、日志、告警、负责人和升级路径。
- **验收：** 保存 5 条可运行查询及样例结果，能回答“什么时候开始异常、影响哪些资源、如何定位”。

资源：[Log Analytics 官方交互教程（包含 Demo 入口）](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-tutorial)

### M5 — Monitoring、Alerts & Incident Response

**内容：** Log Analytics Workspace、Azure Monitor Agent、Data Collection Rule、Activity Log Alert、Action Group、Alert Processing Rule、KQL、RCA。

- 完成 AZ-104 **Lab 11 — Implement Monitoring**。
- 在隔离的测试环境中触发预期的管理操作或模拟服务故障，验证数据采集与告警链路。
- 参考 Azure Monitor Baseline Alerts（AMBA），调整阈值与告警噪声。
- **验收：** 记录检测时间、告警条件、诊断查询、恢复步骤和误报/漏报风险。

资源：[AZ-104 Lab 11](https://microsoftlearning.github.io/AZ-104-MicrosoftAzureAdministrator/Instructions/Labs/LAB_11-Implement_Monitoring.html) · [Azure Monitor Baseline Alerts](https://github.com/Azure/azure-monitor-baseline-alerts) · [Monitor Applied Skills](https://learn.microsoft.com/en-us/credentials/applied-skills/deploy-and-configure-azure-monitor/)

### M6 — PowerShell + Azure CLI + Resource Inventory

**内容：** `Az` PowerShell Module、Azure CLI、资源清点、标签治理、只读安全巡检、自动化脚本测试。

- 学习微软的开源 **Azure Resource Inventory (ARI)**，先运行限定范围的只读资产清点。
- 自己编写一个脚本：列出指定 Resource Group 的资源、标签缺失项、资源类型和关键信息，导出 CSV/JSON。
- 为脚本设计幂等性、错误处理和 Pester 测试；**默认只读**。
- **验收：** 一条命令生成报告；权限不足时可清楚报错；不修改生产资源。

资源：[Microsoft ARI](https://github.com/microsoft/ARI) · [ARI How-to](https://github.com/microsoft/ARI/blob/main/HowTo.md)

### M7 — Azure Backup / Restore / Disaster Recovery

**内容：** Recovery Services Vault、Backup Policy、恢复点、VM Backup、恢复验证、RPO/RTO；Site Recovery 作为可选。

- 完成 AZ-104 **Lab 10 — Implement Data Protection** 中 Backup 相关部分。
- 明确列出要恢复的测试文件或工作负载，确保不仅“备份成功”，而且**确实完成了恢复验证**。
- 使用 AZ-305 的业务连续性设计知识，记录 RPO、RTO、成本和恢复约束。
- **验收：** 有恢复操作、数据校验、耗时测量和清理证据。

资源：[AZ-104 Lab 10](https://microsoftlearning.github.io/AZ-104-MicrosoftAzureAdministrator/Instructions/Labs/LAB_10-Implement_Data_Protection.html)

**成本警告：** 备份存储、受保护实例及 Site Recovery 可能收费；先只做小范围 Backup/Restore，跨区域复制不作为必选。

### M8 — Microsoft Applied Skills（可选的最终验收）

这两项是**基于交互式实验环境的实操评估**，并非以记忆选择题为主。

1. [Configure secure access to your workloads using Azure networking](https://learn.microsoft.com/en-us/credentials/applied-skills/configure-secure-workloads-use-azure-virtual-networking/) — VNet、Routing、DNS、NSG 和 Azure Firewall。
2. [Deploy and configure Azure Monitor](https://learn.microsoft.com/en-us/credentials/applied-skills/deploy-and-configure-azure-monitor/) — Log Analytics、应用与 VM 监控、网络监控、告警和响应。

**策略：** 先完成实际练习和文档，再决定是否参加官方评估；你已经有 AZ-104 和 AZ-305，不需要把新增证书数量作为核心目标。

## 4. 三周执行计划

> 建议分阶段执行，必要时拉长。需要 Azure 付费资源的操作安排在可控制的短时实验窗口。

| 周次 | 训练重点 | 本周任务 | 可交付证据 |
|---|---|---|---|
| **Week 1** | Networking + Identity + AZ-305 Design | 完成网络/身份设计案例；AZ-700 Private DNS、Peering、Private Endpoint；RBAC/Policy 实验 | 架构图、权限矩阵、一次 DNS/NSG 事故 RCA |
| **Week 2** | Monitor + PowerShell | 在免费 Demo 中练 KQL；完成 AZ-104 Lab 11；运行 ARI 并编写只读审计脚本 | 5 条 KQL、监控与告警截图、自动化脚本及测试 |
| **Week 3** | Recovery + Evaluation | 完成 Backup/Restore；撰写两份 Incident RCA；选择性参加 Applied Skills 实操评估 | 恢复验证、RPO/RTO 记录、最终技能矩阵与文档 |

### 自查清单

- [ ] AZ-305 网络架构案例：设计决策和权衡
- [ ] AZ-700：VNet/Peering/Private Endpoint/Private DNS
- [ ] Azure Network Watcher：完成一例连接诊断
- [ ] AZ-104 Lab 02a/02b：RBAC 与 Azure Policy
- [ ] Log Analytics Demo：完成 5 条 KQL 查询
- [ ] AZ-104 Lab 11：完成监控、告警与触发
- [ ] ARI + PowerShell：完成只读资源审计脚本
- [ ] AZ-104 Lab 10：完成一次真实恢复验证
- [ ] 整理至少 2 份 RCA，并检查 Applied Skills 是否适合参加

## 5. 标准故障演练模板

**推荐案例：Private Endpoint 连通性失败**

1. **正常基线：** 在隔离测试环境中部署 VNet、最小测试客户端、Storage Account 与 Private Endpoint，确认 DNS 和连接正常。
2. **故障注入：** 故意断开测试 Private DNS Zone Link，或者施加一条可逆的拒绝规则。
3. **观察影响：** 记录报错、解析结果、目标 IP、连接测试输出及影响范围。
4. **系统排查：** 使用 `nslookup` / Azure CLI / Network Watcher 检查 DNS、路由、NSG 与端点配置。
5. **恢复验证：** 修复配置，重新测量 DNS 解析与连接状态。
6. **复盘：** 写出根因、影响、恢复时间、预防措施、监控改进和成本。

**每项实验统一保存：** 设计与假设、命令及环境版本、脱敏的 `evidence/`、`incident-rca.md`、清理核验记录。可以从 `docs/templates/` 复制模板。截图和日志必须移除 Tenant ID、订阅 ID、用户身份、密钥和其他敏感信息。

## 6. Azure 成本和安全边界

| 实验 | 费用预期 |
|---|---|
| Microsoft Learn 文档和官方 GitHub 教材 | 免费阅读 |
| Log Analytics 官方 Demo | 不需要 Azure 订阅 |
| VNet、NSG、RBAC、部分 Policy | 本身可能无需额外计费，关联资源可能收费 |
| Private Endpoint、VM、公共 IP、存储 | 可能持续计费 |
| Log Analytics 日志摄取和监控 | 依配置和用量计费 |
| Azure Backup、Site Recovery、Firewall | 可能较贵，选择性执行 |

**执行守则：**

- 每项实操使用单独 Resource Group 和明确的测试标签。
- 先查看相关服务在目标 Region 的实际定价，再部署。
- 配置 Budget Alert，但不要把它当作自动断费开关。
- 优先使用最小规格，实验结束立刻清理，并检查是否存在残留磁盘、公共 IP、备份、日志或跨区域资源。
- 不在个人真实账户、真实工作环境或未知权限边界下进行故障注入。

## 7. 求职岗位映射

| 目标岗位 | 主要训练模块 | 与 KPCP 的关系 |
|---|---|---|
| Azure Cloud Engineer / CloudOps | M1、M2、M3、M4、M5、M6、M7 | 补足 Azure 运维和故障恢复 |
| Azure Platform Engineer | AZ-305、M1、M3、M6 | 补足 Azure 原生网络、身份和治理，KPCP 提供平台工程主证据 |
| SRE / DevOps | M2、M4、M5、M6、M7 | 补足 KQL、Incident Response、可观测性与恢复 |
| Azure Solutions Architect | AZ-305 案例 + M1、M3、M4、M7 | 将架构设计与实际验证结合 |

## 8. 最终验收标准

只有完成以下成果，才算真正完成专项训练：

1. **一份架构设计说明**：至少包含网络/身份/监控/恢复设计的关键权衡。
2. **两个真实故障排查案例**：包含可复现步骤、诊断过程、修复与 RCA。
3. **一个 PowerShell 自动化工具**：默认只读，有错误处理与可重复测试。
4. **一组 KQL 查询与监控证据**：说明查询目的、信号来源与告警语义。
5. **一次实际恢复验证**：备份之外还要证明恢复成功，并记录 RPO/RTO 假设和实测恢复耗时。
6. **成本与清理记录**：证明没有长期遗留不必要的付费资源。

## 9. 职业作品集定位

- **固定主项目：KPCP** — Go、Kubernetes、Terraform、平台控制与基础设施自动化。
- **`azure-cloudops`** — 网络、身份、PowerShell、KQL、故障诊断和恢复的专项证据仓；在 Azure 强相关 JD 中，完成后可作为简历的第二项目。
- **LedgerCore** — Java Full Stack 项目；申请 Java / Backend / Full Stack 时更适合作为简历第二项目。

**最终策略：AZ-305 负责“为什么这样设计”，AZ-104/AZ-700 负责“怎么部署与管理”，Azure Monitor/Network Watcher 负责“出现问题如何诊断”，故障演练和 RCA 负责“如何恢复并防止再次发生”。**

## 10. 官方链接汇总

- [AZ-104 Labs](https://microsoftlearning.github.io/AZ-104-MicrosoftAzureAdministrator/)
- [AZ-305 Case Studies](https://microsoftlearning.github.io/AZ-305-DesigningMicrosoftAzureInfrastructureSolutions/)
- [AZ-305 GitHub Repository](https://github.com/MicrosoftLearning/AZ-305-DesigningMicrosoftAzureInfrastructureSolutions)
- [AZ-700 Exercises](https://microsoftlearning.github.io/AZ-700-Designing-and-Implementing-Microsoft-Azure-Networking-Solutions/)
- [AZ-700 GitHub Repository](https://github.com/MicrosoftLearning/AZ-700-Designing-and-Implementing-Microsoft-Azure-Networking-Solutions)
- [AZ-104 Lab 10 — Data Protection](https://microsoftlearning.github.io/AZ-104-MicrosoftAzureAdministrator/Instructions/Labs/LAB_10-Implement_Data_Protection.html)
- [AZ-104 Lab 11 — Monitoring](https://microsoftlearning.github.io/AZ-104-MicrosoftAzureAdministrator/Instructions/Labs/LAB_11-Implement_Monitoring.html)
- [Log Analytics Tutorial / Demo](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-tutorial)
- [Azure Network Watcher](https://learn.microsoft.com/en-us/azure/networking/design-guide/monitor)
- [Azure Monitor Baseline Alerts](https://github.com/Azure/azure-monitor-baseline-alerts)
- [Microsoft Azure Resource Inventory](https://github.com/microsoft/ARI)
- [Applied Skills — Azure Networking](https://learn.microsoft.com/en-us/credentials/applied-skills/configure-secure-workloads-use-azure-virtual-networking/)
- [Applied Skills — Azure Monitor](https://learn.microsoft.com/en-us/credentials/applied-skills/deploy-and-configure-azure-monitor/)


## 11. 仓库实施 Gate（必须证据驱动）

| Gate | 准入条件 | 状态 |
|---|---|---|
| G0 — Repo Ready | README、Roadmap、模板、保密规则已保存 | Planned |
| G1 — Free First | 免费 KQL Demo 里五个查询已独立运行并保存结果 | Planned |
| G2 — Azure Connectivity | 真实隔离环境连通性和 DNS/NSG 事故诊断完成 | Planned |
| G3 — Identity & Security | RBAC/Managed Identity 的允许与拒绝路径均通过 | Planned |
| G4 — Operations | PowerShell 审计脚本和监控告警链路验证完成 | Planned |
| G5 — Recovery | 从备份成功恢复并检验测试数据 | Planned |
| G6 — Portfolio Ready | 至少两份 RCA、可复现记录和成本清理报告 | Planned |

**状态原则：** 不把阅读材料、静态配置、计划中的实验等同于真实 Azure 实操通过；没有实时证据就保持 Planned / Not Verified。

**AZ-305 范围说明：** 微软 AZ-305 当前官方目录为网络、认证授权、监控、治理等提供正式案例；Business Continuity 在该目录中标注为 *No formal case study*。业务连续性部分可按 AZ-305 设计原则自拟案例，随后通过 AZ-104 Lab 10 验证。
