# Azure CloudOps 教材 V1.0.1 逐讲审计

基线为 `8cdad7fba8db8f821aaf013bd20637441e6c22dc`。以 [核准课程](CURRICULUM.md) 核对 23 讲 Markdown、已发布 PDF、图、练习与关联实验；以原始验收与现场报告核对证据边界。出版基线为 23 册、183 页、95 个 SVG 图稿（92 张排入 PDF）和 0 张 Azure Portal 实拍图。原版正文与图例具有统一的视觉层级，部分章节在参考文献前强制分页，形成低密度尾页。

AWS 对照为 `b44160ea0f864ce7edf40cc0edb402cb53687a63`。阅读 A02-03 DNS/VPC 端点、A03-01 IAM/STS、A04-01 指标与告警、A04-02 日志与事件、A05-01 Systems Manager、A09-02 Terraform 状态与漂移、A10-02 企业治理。采用其中可迁移的教学做法：按配置对象示范字段，先预测结果再跑实验，用相邻两道门的反证缩小原因，最后用同一业务请求验收。Azure 的控制面、身份和证据独立按 Microsoft 文档与本仓库材料核对。

「确认缺陷」指可定位的错误、核准范围内的实质遗漏或证据状态偏差。「待补内容」指能提升现场可操作性的教学增补。空白云端验证按历史证据处理。

| 讲次 | 现有优势 | 确认缺陷 | 待补内容 | 计划修订 |
|---|---|---|---|---|
| AZ00-01 | ARM 202、资源提供程序、继承边界清楚 | 尾注仍将已记录的本地实验标为 B1 前待补 | 从审批范围走到实际资源配置 | 更新证据说明，用订阅、RG、策略分配和失败事件串成操作单 |
| AZ01-01 | 故障域、SLO 与串并联系统计算完整 | — | 区域配置如何影响端到端可用性 | 对照 zonal VM、ZRS、实测探针与预算决策 |
| AZ02-01 | 最长前缀、同前缀和回程分开推导 | 撤销 /24 后漏选仍有效的 /16 UDR | 把候选路由映射到资源字段 | 修正逐层回退结果，明确 UDR、subnet 关联和有效路由验收 |
| AZ02-02 | 五元组、两层 NSG 与现有 flow 解释清楚 | — | 建规则、挂 ASG 后怎么比对 | 用 NIC、NSG 规则字段和新连接验证最小修复 |
| AZ02-03 | CNAME、DNS zone group 和授权分层 | 只读示例直接使用无所有权证明的 Storage 名称 | 一份可顺序执行的端点配置卡 | 使用已批准变量，补账号到 Blob 的 DNS、TCP、TLS、授权四门 |
| AZ02-04 | 三类入口与探针差异、故障模型齐全 | — | 后端与探针配置的绑定键 | 用 Host/SNI、路径、端口和健康状态定位一次 502 |
| AZ03-01 | 主体、audience、scope、Actions/DataActions 区分好 | — | Portal 中按最小数据面范围分配 | 给出具体角色、assignment 字段、允许和拒绝探针 |
| AZ03-02 | FIC 与目标 token、Key Vault 两个平面分开 | — | 运行时挂载和 CI federation 实操字段 | 对照两个场景的身份选择、网络与数据角色 |
| AZ03-03 | Policy、Activity Log 与 Defender 分工清楚 | “尚未通过 L0” 与已完成的限定只读证据不符 | 策略分配字段和合规延迟 | 改为逐项授权边界，补分配、合规与 Activity Log 证据 |
| AZ04-01 | power、provisioning、guest、应用、I/O 分层 | 核准的 OS 补丁缺少工作流 | 周期评估、维护窗口、代理依赖与回退 | 补 Azure Update Manager 补丁环与失败诊断，复核 Flexible 文档矛盾 |
| AZ04-02 | swap、revision、app-wide 设置与故障模型 | — | 明确资源/SKU/参数及切流动作 | 补双平台发布卡，标清 Azure IR-11 止点与本地 HTTP 结果 |
| AZ04-03 | 镜像、调度、readiness 与 PDB 的连续诊断 | — | 从 kubectl 字段直接找到失败门 | 用 Deployment、Service、EndpointSlice、PDB 预判发布阻断 |
| AZ04-04 | Storage 与 SQL 的网络、身份和恢复机制区分好 | — | 账号冗余、授权、SQL 主体和数据验证 | 补一条 Blob + SQL PITR 操作卡及正负验证 |
| AZ05-01 | 聚合、时窗与告警状态解释齐全 | 40 台仅一台异常时健康率误写 99% | 将机制映射到一条真实指标及通知配置 | 重算 97.5%，保留独立 fixture，补 rule、action group、处理规则 |
| AZ05-02 | 先筛选再聚合，追踪父子 ID 和采样权重 | 采集图混用 Diagnostic Settings/DCR，遗漏 AMA 路径；“两条模板”应为七条 | 数据源、关联、私网端点、目标表与验证 | 修正图，补采集配置与断点排查，保留 KQL NOT_RUN |
| AZ05-03 | ARM 与 ARG 对照、排序/分页与新鲜度边界 | — | 缺页或缺权限如何证伪 | 用同一 ID、scope、续页键与直接 ARM 读取对齐 |
| AZ06-01 | 一致性、恢复目的地、RPO/RTO 和 ASR 验收 | 图 17-5 图注将 RTO 起点混为执行恢复的开始 | 从备份策略到隔离恢复的完整操作 | 图注改成业务中断；补 VM vault、恢复点、隔离恢复与留存 |
| AZ06-02 | 同时保留事件时间和到达时间、竞争假设、修复闭环 | 将 Azure 日志统称为需要诊断设置 | 学员如何复盘一次具体事件 | 区分 Activity Log 生成与导出；用既有时间线写调查单 |
| AZ07-01 | Core、Provider、ARM、state/import 图清楚 | — | 对计划进行可复验的变更审查 | 用真实 repo 模块依赖和一个错误计划辨析 |
| AZ07-02 | blob lease、漂移、版本恢复和受控 apply 扎实 | — | 将容器、key、身份和备份版本落实到运维单 | 加双 runner 操作次序、恢复与后置条件 |
| AZ07-03 | 模板、OIDC、计划哈希与失败关闭边界充分 | — | 从空项目到受保护 Apply 的分步配置 | 补 Project/Repos/Agent/Library/Environment/Checks 入口和验收 |
| AZ08-01 | BGP、路由和 DNS 三平面及 Virtual WAN 选择 | 端点案例未明确转发公用后缀、连接原始服务名 | 双向路由显式表、BGP 和 DNS 联合案例 | 用同一企业地址表推算返回和 DNS 修复，完善题解 |
| FIN-01 | gross/credit、预算和残留资源对账分开 | 习题把高峰用量与承诺利用率混写 | 预算通知与清理证据如何共同落地 | 明确用量与承诺额口径，加预算、费用和清理操作例 |

现有演练按「本地合成」「历史获批 Azure 证据」「未来需另行授权」「企业设计」表述。PDF 中的示例结果按其各自口径核查。外部工程服务的权限、SKU、费用和功能前提以章节引用的官方文档和实际授权边界为准。

## R0–R8 验收

| 阶段 | 结果 | 核查依据 |
|---|---|---|
| R0 学术与实践审查 | 通过 | 23 讲源稿与原版 PDF，七讲 AWS 样本，官方及仓库来源，逐讲差异见上表。 |
| R1 实质缺陷 | 通过 | VM 补丁缺口、指标算例、DCR 链路、KQL 台账和其他逐讲错误已修正。Flexible VMSS 官方文档冲突保留为配置前检查项。 |
| R2 配置实操 | 通过 | 每讲增加配置或操作步骤，标出资源归属、字段、作用域、验收和优先排障项。 |
| R3 优先扩展 | 通过 | Private Link、应用发布、Storage/SQL、隔离恢复、Azure DevOps 和混合网络均有完整示例。 |
| R4 视觉教学 | 通过 | 95 个 SVG 保留，92 张排入 PDF；采集图修订一张。Azure Portal 实拍 0 张。 |
| R5 推导与题解 | 通过 | 修正算术、路由优先级、RPO/RTO 和费用口径，增加证据对照、最小修复与回归验证。 |
| R6 学习步骤 | 通过 | 现有本地入口可复验，未来须获批的只读和 Azure 操作各设起点与清理范围，企业设计单独标注。 |
| R7 PDF | 通过 | 23 册全部重建并渲染至 88 DPI，逐页检查版面，另对 13 个实操密集页以 140 DPI 复查。无空白、溢出和占位标记；独立保留部分参考资料尾页和原样式封面。 |
| R8 交付 | 本地验收通过，GitHub 以提交的检查结果为准 | Python 534/534，Terraform 13/13（3 个根模块），Pester 6/6。两份 ZIP 及清单由现有出版工具生成和校验。最终发布状态取决于主分支该提交的 5 项 CI jobs。 |

### 23 讲复验结果

以下每册均通过源码对照、最终 PDF 构建及版面检查。图栏是正文排入图数／源图数。

| 讲次 | 基线页 → V1.0.1 页 | 图 | 修订结果 |
|---|---:|---:|---|
| [AZ00-01](chapters/AZ00-01/ACCEPTANCE.md) | 8 → 9 | 3 / 3 | 补齐管理组、订阅、RG、策略及 Provider 实操入口，更新已验证的本地实验尾注。 |
| [AZ01-01](chapters/AZ01-01/ACCEPTANCE.md) | 7 → 7 | 2 / 3 | 用 zonal VM、Storage ZRS 与端到端探针验收跨可用区设计，核对 SLO 算式。 |
| [AZ02-01](chapters/AZ02-01/ACCEPTANCE.md) | 8 → 8 | 3 / 3 | 更正 /24 移除后的 /16 选路，补 UDR 字段、子网关联和双向验收。 |
| [AZ02-02](chapters/AZ02-02/ACCEPTANCE.md) | 8 → 9 | 3 / 3 | 补 NIC 的 ASG 关联、优先级、五元组和新连接正反例。 |
| [AZ02-03](chapters/AZ02-03/ACCEPTANCE.md) | 11 → 12 | 3 / 3 | 补 StorageV2、PE、Blob、VNet link、DNS zone group 和公网限制，分四步验收。 |
| [AZ02-04](chapters/AZ02-04/ACCEPTANCE.md) | 9 → 9 | 3 / 3 | 补探针与后端设置、监听规则的绑定和同请求复验。 |
| [AZ03-01](chapters/AZ03-01/ACCEPTANCE.md) | 9 → 10 | 3 / 3 | 用容器级 Blob Data Reader 做正反例，并标清 token、主体、scope 的检查顺序。 |
| [AZ03-02](chapters/AZ03-02/ACCEPTANCE.md) | 9 → 9 | 3 / 3 | 补 UAMI 挂载、FIC 三字段、Key Vault 授权模式及交换与数据读取的分层。 |
| [AZ03-03](chapters/AZ03-03/ACCEPTANCE.md) | 8 → 9 | 3 / 3 | 修正历史 L0 状态，补策略分配、DoNotEnforce、合规刷新与 Activity Log。 |
| [AZ04-01](chapters/AZ04-01/ACCEPTANCE.md) | 6 → 8 | 3 / 3 | 补 Update Manager 补丁环、任务与代理故障排查。Flexible VMSS 升级策略的官方冲突仍已注明。 |
| [AZ04-02](chapters/AZ04-02/ACCEPTANCE.md) | 7 → 8 | 4 / 4 | 补两条发布路径、计划/槽、revision/探针/切流。Azure IR-11 保持部分完成，本机回滚证据独立。 |
| [AZ04-03](chapters/AZ04-03/ACCEPTANCE.md) | 9 → 10 | 5 / 5 | 补 Kubernetes 和 Azure 配置定位、ACR 身份、EndpointSlice 与 PDB 验证。 |
| [AZ04-04](chapters/AZ04-04/ACCEPTANCE.md) | 8 → 9 | 5 / 5 | 补 Storage 冗余、授权、SAS 与 SQL 的私有连接、对象授权及 PITR 验收。 |
| [AZ05-01](chapters/AZ05-01/ACCEPTANCE.md) | 6 → 7 | 5 / 5 | 修正 97.5% 和等权平均算例，补实用 Blob 指标规则和通知诊断。 |
| [AZ05-02](chapters/AZ05-02/ACCEPTANCE.md) | 7 → 8 | 5 / 5 | 更新采集图与 AMA/DCR/DCRA/DCE 配置，保留七条 KQL 模板 NOT_RUN。 |
| [AZ05-03](chapters/AZ05-03/ACCEPTANCE.md) | 7 → 7 | 5 / 5 | 补显式范围、稳定分页、ARG 缺项和同 ID 的 ARM 对照。 |
| [AZ06-01](chapters/AZ06-01/ACCEPTANCE.md) | 7 → 8 | 5 / 5 | 更正 RTO 图注，补策略/point、隔离恢复、完整性及 retained 资源。 |
| [AZ06-02](chapters/AZ06-02/ACCEPTANCE.md) | 7 → 8 | 5 / 5 | 补基于三条关联证据的事故练习，区分 Activity Log 生成和导出。 |
| [AZ07-01](chapters/AZ07-01/ACCEPTANCE.md) | 9 → 9 | 4 / 5 | 用现有模块和 Provider 从依赖图导出可复核 Plan 审阅，完善练习分页。 |
| [AZ07-02](chapters/AZ07-02/ACCEPTANCE.md) | 9 → 9 | 6 / 6 | 补后端状态键、唯一写入者、版本恢复与两进程本地锁复验指引。 |
| [AZ07-03](chapters/AZ07-03/ACCEPTANCE.md) | 8 → 9 | 4 / 5 | 补 Azure DevOps 服务侧项目授权、WIF、Plan artifact 与 Apply 边界。 |
| [AZ08-01](chapters/AZ08-01/ACCEPTANCE.md) | 7 → 9 | 5 / 5 | 补双向路由表、BGP 传播、原始 SQL 名称解析与 vWAN 关联、传播题解。 |
| [FIN-01](chapters/FIN-01/ACCEPTANCE.md) | 9 → 9 | 5 / 5 | 补预算与磁盘对账操作，区别承诺利用率和超出承诺的用量。 |
| **合计** | **183 → 200** | **92 / 95** | 23 册，真实截图为 0，修订 SVG 一张。 |

### 交付与证据边界

- [PDF ZIP](dist/Azure-CloudOps-PDF.zip) · [Sources ZIP](dist/Azure-CloudOps-Sources.zip) · [大小、条目清单及 SHA-256](dist/publication-manifest.json)。仓库工作树与发布 ZIP 由原工具比对，清单含每个条目的摘要。
- [主分支 GitHub Actions](https://github.com/miku-wwl/azure-cloudops/actions/workflows/ci.yml?query=branch%3Amain)。CI 校验工程与发布文件。图文质量依据本次逐页复核。
- 本轮新增的 Azure 操作均为文档演练，无 Azure 会话、API、变更、KQL 或新增费用。历史的七条 KQL 模板保持 `NOT_RUN`，IR-11 的云端应用发布与回退维持未验证，账单历史状态为 `BILLING_PENDING`。
- 未来服务配置仍需核查区域/SKU、账号权限和报价。Flexible 升级策略需查具体 API 和编排模式。未做独立学员实操或纸样验证。原版少量仅供源稿使用的图保留在可编辑资产中。
