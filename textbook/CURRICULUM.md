# Azure CloudOps 技术教材目录

本课程面向有云平台、网络、身份、Terraform、Kubernetes 或软件运维经验，并希望承担高级 Azure 平台、DevOps、SRE 与云架构工作的工程师。正文使用中文解释，并保留常用英文技术术语。课程围绕系统机制、配置和运维推理展开，不是认证考试复习提纲。

| 讲次 | 教材 | 核心问题 |
|---:|---|---|
| 01 | AZ00-01 — Azure Landing Zone、ARM 与控制平面 | Azure 订阅如何成为受治理的企业环境？ |
| 02 | AZ01-01 — Well-Architected Framework 与可靠性 | 为什么跨可用区部署仍不能自动保证可靠性？ |
| 03 | AZ02-01 — VNet、UDR 与有效路由 | 哪条路由胜出，非对称路径可能在哪里出现？ |
| 04 | AZ02-02 — NSG、ASG 与网络诊断 | 哪条有状态规则允许或拒绝流量，如何证明？ |
| 05 | AZ02-03 — Private DNS、Private Link 与 Private Endpoint | 域名如何解析到私有端点，哪些边界仍可能拒绝连接？ |
| 06 | AZ02-04 — Load Balancer、Application Gateway 与 Front Door | 健康探测或请求转发在哪一层失败？ |
| 07 | AZ03-01 — Microsoft Entra ID、Token 与 Azure RBAC | 哪个身份、受众、操作与作用范围决定请求结果？ |
| 08 | AZ03-02 — Managed Identity、Key Vault 与联合身份 | 工作负载如何在不保存凭据的情况下取得并使用身份？ |
| 09 | AZ03-03 — Azure Policy、Activity Log 与 Defender for Cloud | 哪种控制会阻止、记录、评估或修复配置？ |
| 10 | AZ04-01 — VM、VMSS、Managed Disk 与运维 | 哪个 VM 生命周期或依赖状态解释了当前症状？ |
| 11 | AZ04-02 — App Service、Container Apps 与发布 | Slot、Revision、探针和回退如何影响在线发布？ |
| 12 | AZ04-03 — Azure Kubernetes Service 与 Azure Container Registry | 哪个身份、网络或调度边界阻止工作负载就绪？ |
| 13 | AZ04-04 — Azure Storage 与 Azure SQL | 哪些网络、身份和数据保护边界决定访问或恢复？ |
| 14 | AZ05-01 — Azure Monitor、指标与告警 | 维度、聚合和评估窗口如何形成告警状态？ |
| 15 | AZ05-02 — Log Analytics、KQL 与 Application Insights | 遥测架构和关联信息如何揭示分布式故障？ |
| 16 | AZ05-03 — Azure CLI、PowerShell 与 Resource Graph | 如何安全、完整、重复地盘点资源？ |
| 17 | AZ06-01 — Azure Backup、还原与 Site Recovery | 恢复点、完整性验证、RPO 与 RTO 如何影响实际恢复？ |
| 18 | AZ06-02 — 事故响应、根因分析与综合银行案例 | 如何用证据、竞争假设和有限修复形成可信根因结论？ |
| 19 | AZ07-01 — Terraform、AzureRM、AzAPI 与模块 | 哪一层负责每项操作，Terraform 如何构建依赖图？ |
| 20 | AZ07-02 — Azure 远端 State、锁与漂移 | Blob 租约保护什么，如何发现并恢复状态漂移？ |
| 21 | AZ07-03 — Azure DevOps、Pipeline 与 Workload Identity Federation | 精确的 Plan 如何经过可信审批边界？ |
| 22 | AZ08-01 — Hub-Spoke、VPN、ExpressRoute 与企业 DNS | 哪些路由、BGP 与 DNS 边界连接混合网络？ |
| 23 | FIN-01 — Azure FinOps 与资源成本回收 | 如何核对毛额、抵扣、保留资源和拆除结果？ |

每讲依次引入工程场景、学习目标、技术原理、机制图、演算示例、Azure 配置与运维方法、实践实验、故障诊断与恢复、带解答的练习及参考资料。章节会区分文档机制、本地实验和云端观察。
