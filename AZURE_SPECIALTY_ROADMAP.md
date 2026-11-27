# Azure CloudOps & Enterprise Infrastructure — V3 工程实施与学习路线图

> **版本：** V3.1 implementation contract / 2026-11-26；承接 V3.0，增加已批准的三阶段交付顺序与 USD 1.00 累计 Azure 费用边界。
> **V1 结项（2026-11-28）：** Stage 1 B0–B9、Stage 2 E0–E10 与 Stage 3 L0 已通过。LAB-IR-11 创建 F1 计划后卡在 Linux 字段核验，计划和资源组已清理。应用发布、故障和回退未获云端实证。当前验收见 [最终报告](textbook/FINAL_ACCEPTANCE_REPORT.md)。
> **原始 V3 基线：** miku-wwl/azure-cloudops main，提交 853ba6cbaa4ee67e448550fbe192c6c89b24fd2f；该提交已与 origin/main 同步。
> **目标：** Azure Cloud / Senior Infrastructure / Platform / SRE / DevOps Engineer，尤其适合金融等重视安全、治理、变更与恢复的企业环境。  
> **学习原则：** 不重复 AZ-104、AZ-305、Terraform 认证备考；以技术机制、工程实施、独立排障和可复验结果为主。

## 0. V3 的设计决策

V2 的 M0–M9 全部保留其核心学习目标，但不再以十个孤立知识主题组织工程。V3 改用统一的企业云基础设施场景、阶段化交付和分层证据标准。
### 0.1 本次批准的三阶段执行合同

本执行合同来自 2026-11-26 批准的 Azure CloudOps master prompt；它更新交付顺序和实时 Azure 费用上限，保留本路线图后续定义的架构、实验、incident、Terraform、交付和安全验收条件。

1. **Stage 1 — Technical Textbook Engineering & Publication：** 按 B0–B9 顺序完成 23 讲、离线实验、机制图、逐页 PDF 检查、出版包和离线 CI。每讲先达到本讲验收，再进入下一讲。每讲目录与学习问题以 textbook/CURRICULUM.md 为准。
2. **Stage 2 — Enterprise Engineering & Lab Readiness：** 按 E0–E10 审核并加强本地底座、Terraform、受控交付、Azure Pipelines、运营自动化、12 个 incident 合同、8 个必选本地闭环、清理及独立重放。此阶段禁止 Azure 资源创建或修改；保留实际 V3 的 P0–P8 要求并映射到这些工程包。
3. **Stage 3 — USD 1 Budget-Constrained Live Azure Validation：** 先做 L0 授权只读预检，再评估小型 live 机制。整个项目的累计新增 Azure 支出上限为 USD 1.00，保守计划线为 USD 0.70，USD 0.30 留作意外和清理余量。必须把 gross charges 与 credits、discounts、实际账单分开；不能可靠估价、缺少精确 scope/许可或未获此次部署批次授权即停止部署。

本次切换时目标仓库 main 和 origin/main 均为批准基线 853ba6c。工作仅在 main 持续前进，不创建分支或 PR。AWS 参考仓库在 b44160ea0f864ce7edf40cc0edb402cb53687a63 上只读分析，不修改。

#### 0.1.1 实施历史（截至 2026-11-27 的 E7 检查点）

- Stage 1 B0–B9 完成：23/23 讲、PDF、源稿与逐讲 acceptance 均已交付；历史 B9 验收详见 `textbook/RELEASE_ACCEPTANCE.md`。该较窄 B9 不代表 master prompt 的 hosted CI、secret scan 或 PDF/UA 验收已通过。
- Stage 2 E0 完成：审计发现并修正 FIN-01 成本分摊分币错误、AZ02-01 路由模型接受无效 next-hop contract，以及 AZ07-02 本地 Terraform State verifier 对 checkout 状态和失败清理的安全问题。修复、测试和证据见 `textbook/E0_INDEPENDENT_AUDIT.md` 及对应 chapter acceptance addenda。
- E0 回归：Windows 与 WSL 各通过 407 个 Python 测试、22 个目录；Windows Terraform 1.15.5 递归 fmt 通过，两 Terraform roots backend-free init/validate 与 5 个 mock contract tests 通过。三个修订 PDF 共 24 页已逐页复看。
- E1 已完成：三个不同用途的架构视图和六个 ADR 已写入 `textbook/architecture/`，本地检查确认 3 个 Mermaid 图、6 个 ADR、内部链接无缺失。
- E2 已完成：Windows/WSL 工具清单、可复用本地生命周期命令和公共 Python 测试入口已在工作树；两端各通过 418 tests/23 directories，合成 smoke 的 teardown 后残留检查通过。Docker Linux Engine 缺失，因此未生成 kind/k3d 运行证据。
- E3 已完成：`textbook/terraform/azure-enterprise-reference/` 锁定 AzureRM 5.15.0 与 AzAPI 2.14.0，覆盖网络、VM、AKS/ACR、身份、Key Vault、Storage、监控、Recovery Services 与 audit-only Policy；所有资源旗标默认关闭，存在准确范围/成本/运行时前置条件，并关闭自动 Provider 注册。Windows Terraform 1.15.5 通过 chapter/terraform 递归 fmt、3 roots 的 backend-free init/validate 和 13 个 plan-only 测试运行；Azure root 8 个 mock-provider 场景全过。Windows 和 WSL Python suites 各 429 tests/23 directories；静态合同检查强制所有 Terraform test 为 plan-only，并实测环境凭据移除。AZ07-01 的 9 页新版在 88/140 DPI 逐页检查。Stage 2 禁止创建或修改 Azure 资源；Stage 3 L0 尚未开始。详见 `textbook/E3_TERRAFORM_ENGINEERING.md`。
- E4 已完成：精确 Plan 签名包验证器绑定 Git SHA、环境和订阅/RG、Provider lock、Plan hash、操作、审批身份/时间、run/approval ID 与一次性 nonce；隔离 sealed Plan，破坏性操作独立授权，并在本地拒绝重放、并发及不安全 Azure 凭据回退。外部 trust store 和 trust digest 需受保护平台注入；未实现 signer、Azure DevOps 服务端 Environment checks 或分布式锁。AzureRM OIDC backend 仅通过 `init -backend=false`/validate，远端 init 未运行。AZ07-02 的 9 页/6 图教材完成复排；本地 Terraform 锁竞争、state-only import、drift、HCL rollback、State 恢复和 destroy 通过。Windows/WSL 各通过 458 tests/23 directories；无 Azure API、远端状态、资源操作或账单查询。详见 `textbook/E4_STATE_CONTROLLED_DELIVERY.md`。
- E5 已完成离线门槛：AZ07-03 的企业模板将 Plan、PlanReview、Apply 分开，并默认在编译期排除云阶段；`plan_bundle.py` 将精确 Plan 字节绑定到 source、scope、backend、provider lock 和 run，输出不含敏感值。29 个 E5 本地测试通过；Windows/WSL 各通过 471 tests/23 directories；Terraform 1.15.5 递归 fmt、3 roots backend-free init/validate 与 13 个 plan-only/mock runs 通过。8 页 PDF 完成 88 DPI 逐页检查，更新页 6–8 另以 140 DPI 检查。Broker、signer、受保护外部模板、实际 WIF、Environment checks 与分布式 replay lock 是未配置前置条件；无 Azure DevOps/Azure 访问。详见 `textbook/E5_AZURE_DEVOPS_DELIVERY.md`。
- E6 已完成离线门槛：新增显式订阅范围的 Azure Resource Graph 分页库存脚本、13 类只读诊断目录、DNS/TCP/TLS 与 HTTP HEAD 本地探针、隐藏输入 JWT claim 检查器，以及 5 个 AzureActivity/Heartbeat/AppRequests/AppDependencies/AppExceptions KQL 模板。定向测试 36 项通过；Windows 与 WSL 各通过 507 tests/23 directories。测试使用合成 CLI 响应、合成 token 和 loopback；KQL 仅做表结构源审阅，未编译或执行；无 Azure/ADO/Kubernetes/外部主机/账单查询。DNS 的 OS `getaddrinfo` 无法取消，只能限制调用者等待且后台线程可能继续到解析完成；详见 `textbook/E6_DIAGNOSTICS_AUTOMATION.md`。
- E7 已完成十二个 incident 合同及课程映射，覆盖 healthy baseline、scope、故障机制、类别、假设、区分探针、根因证据、最小修复、同探针复验、负面断言、清理、权限、成本和实际状态。契约校验 3 项通过；Windows/WSL 各通过 510 tests/24 directories。8 个 mandatory local 与 4 个 design-only 已明确标注；没有事故实际执行，E4 Terraform evidence 不计作 E8 IR-08 闭环。详见 `textbook/E7_INCIDENT_CONTRACTS.md` 与 `textbook/incidents/`。
- 当前阶段为 E8；之后依次 E9–E10。Stage 3 尚未执行 Azure 登录、订阅查询、账单查询或资源操作。
- Docker Desktop Linux Engine 在之前的 host 检查中不可用；开始 E2 时重新检查。Azure CLI 命令存在不代表登录、scope 或授权可用。
- 实际累计 Azure 支出：`NOT_VERIFIED`。USD 1.00 总上限、USD 0.70 计划线和 USD 0.30 清理/未知费用余量继续适用；不得声明 actual spend 为 USD 0.00。

#### 0.1.2 V1 最终验收（2026-11-28）

- `TEXTBOOK_V1_RELEASE_READY` 与 `LIVE_LAB_READY` 达成。23 讲出版，E8 八个本地故障、同探针恢复和清理闭环均通过。E10 两轮历史证据校验通过。
- `READ_ONLY_AZURE_VERIFIED` 达成。明确订阅范围的 Resource Graph REST 清点返回三项 Network Watcher，见 [L0 记录](textbook/L0_READ_ONLY_PREFLIGHT.md)。
- LAB-IR-11 获批并创建专用组和 F1 计划。CLI 结果缺少顶层 `reserved` 字段，阻止创建 Web App。约 126 秒确认清理，独立看门狗复核通过。最终运行手册使用 ARM `properties.reserved` 核验，修改已完成离线检查。[现场证据](textbook/incidents/evidence/IR-11_azure-2026-11-28.md)。
- `LIVE_VALIDATED_SUBSET` 与 `PORTFOLIO_READY_LIVE` 保持未达成。按 USD 1.00 约束完成本轮结项。其余 incident 状态见 [实验索引](textbook/LIVE_LAB_INDEX.md)。费用查询前后均返回空结果，实际账单 `BILLING_PENDING`。

#### 0.1.3 旧 P0–P8 与 E0–E10 的关系

原 P0–P8 合同作为 Stage 2 的需求来源保留；原 L0–L3 是 Stage 3 的 live gate。B0–B9 是增加的出版和教材 gate，不替代架构、安全或实验验收。课程改为 23 个独立 lecture PDFs，索引见 textbook/CURRICULUM.md。阶段状态必须由实际证据更新，不得因为推进路线图而自动标 PASS.

| V2 模块 | V3 承接阶段 | 变化 |
|---|---|---|
| M0 Landing Zone | P0、P3 | 增加职责、信任、治理与实验映射 |
| M1/M2 Networking & Troubleshooting | P2、P7、L1 | 从单一事故升级为可复验网络故障组 |
| M3 Identity & Governance | P3、L2 | 区分控制面、数据面、身份、网络和策略拒绝 |
| M4 Terraform Delivery | P1、P5、L1/L3 | 加入状态、审批、漂移与 Azure Pipelines |
| M5 Monitor/KQL | P6、L2 | 合成数据、官方 Demo、自有云日志三类分开 |
| M6 Incident/RCA | P7、L1–L3 | 12 个场景规格、8 个必选本地闭环、授权 live 子集 |
| M7 PowerShell/CLI | P6 | 默认只读，含分页/错误/权限处理 |
| M8 Backup/Restore | P7、L3 | 恢复数据校验、实测时间、残留审计 |
| M9 Hybrid Design | P0、P8 | 混合网络、跨区域 DR、PIM 等以设计为主 |

新增 Compute/Storage/App Service/ACR/AKS/Azure SQL 的企业运维知识、Azure DevOps 交付、本地低成本实训及技术教材体系。保留原有低成本、真实证据、无授权不部署等红线。项目不是 Azure 平台产品，不重新实现 KPCP，不开发复杂银行业务系统。

### 0.2 本地工程与条件性 Azure 验证

1. **本地工程主线（必做）**：本地版不依赖 Azure 订阅、付费 SaaS 或云端 CI 容量。原 P0–P8 要求在 Stage 2 中按本路线图和 E0–E10 映射执行；Stage 1 先完成技术教材及离线出版验收。
2. **真实 Azure 验证（有条件）**：Stage 3 只选择学习价值高、短期可清理且经过费用与授权审核的实验。未授权或缺少服务资格时，完成所有安全离线工作并将 live 场景标为 BLOCKED、PERMISSION_DEFERRED、BUDGET_DEFERRED 或 LIVE_NOT_RUN；不降低验收标准。
3. **费用和权限**：项目累计新增 Azure 支出不得超过 USD 1.00；计划估算不超过 USD 0.70，并保留 USD 0.30。Azure Budget 不是硬支出上限。任何实际部署均需验证当前价格、资源清单、时间窗口、累计费用、清理路径和该批次授权。不能可靠估价则不部署。
4. 不预设已有 Azure credits、管理组权限、Azure DevOps 组织、Microsoft-hosted parallel jobs、固定区域或特定订阅类型。Stage 2 不创建或修改 Azure 资源。Stage 3 的 L0 只读预检不得自动登录、自动注册 provider 或静默切换订阅。

本 master prompt 改变阶段次序、出版范围和费用上限；本路线图原有拓扑、fidelity、P0–P8、incident、stage 3 资格及安全要求继续有效。
## 1. 统一企业场景与范围

### 1.1 Fictional Banking Cloud Infrastructure Lab

假设一家金融机构运营内部交易查询/账单文档服务，要求开发与生产隔离、应用通过私网访问数据、身份权限最小化、变更可审核、故障可恢复。业务仅采用合成数据与最小探针或已有轻量镜像，不处理真实交易、PII、客户数据，不做行业合规认证声明。

企业参考架构需覆盖：

- Management Group、Platform / Landing Zone subscriptions、dev/prod 边界、资源组及资源所有权；个人订阅仅映射最小 lab，不假装拥有完整管理组权限。
- Hub-spoke、IP 地址规划、路由、Private DNS、Internet ingress/egress、私有 PaaS 访问；比较 Virtual WAN、Azure Firewall、Private Resolver、VPN/ExpressRoute，但不默认部署。
- Entra ID、工作负载身份、RBAC、Azure Policy、Key Vault、监控归属、成本中心和职责分离。
- 交付路径：版本控制 → 审查 → 静态检查 → 计划 → 批准 → 部署 → 健康检查 → 回退或恢复 → 审计。
- 工作负载路径：客户端 → 应用 → 数据/秘密服务；遥测覆盖网络、应用、控制面、数据面；失败时用同一探针复验。

### 1.2 三种环境拓扑

| 环境 | 拓扑 | 边界 |
|---|---|---|
| Reference | 双工作负载环境、共享 hub、管理/连接/安全服务 | 仅设计，无真实 prod；架构选择用 ADR |
| Local | 单机隔离容器网络、DNS 服务、最小 HTTP 应用/探针、Azurite、合成日志；按需本地 K8s | 机制类比与真实本地 API；不能声称复制 Azure 控制面 |
| Live | 授权专用 RG、VNet/subnet、最小探针、Storage/Private Endpoint/DNS 等按实验启用 | 一次一个小场景；非生产、短生命周期；昂贵服务按需设计而非默认部署 |

本地命名、实验 ID、数据模型和诊断契约尽量一致。Azure 资源与本地模拟组件采用显式不同 provider/adapter、目录和标签，禁止通过改名把本地测试包装成真实 Azure。

## 2. 技术选型与服务优先级

| 领域 | 核心（必学/必交付相应设计或本地机制） | 扩展（条件触发） |
|---|---|---|
| Azure architecture | CAF/ALZ、Hub-Spoke、Management Groups、RBAC、Policy、成本与命名 | Virtual WAN、跨租户、多订阅真实部署 |
| Network | VNet、Subnet、NSG、UDR、Peering、Private Link、Private DNS、Network Watcher | Application Gateway/WAF、Load Balancer、Firewall、Private Resolver、VPN/ExpressRoute |
| Identity | Entra ID、Managed Identity、RBAC 管理面/数据面、Key Vault、Policy audit/deny | PIM、Defender for Cloud、企业策略分发 |
| Compute | VM/VMSS、App Service 的部署和健康/扩缩容机制；本地 HTTP workload | 真实 VM/VMSS、App Service slot、区域可用性实测 |
| Container | OCI registry、K8s image pull、ACR/AKS identity 与网络设计 | 真实 ACR/AKS、节点升级、Autoscaler |
| Data | Storage Account/Blob、Azurite、本地数据恢复；Azure SQL 访问与恢复设计 | Azure SQL 实际部署/PITR、生产级跨区域复制 |
| IaC | Terraform AzureRM；模块/状态/锁/漂移；AzAPI/Bicep 选型对比 | 特定 AzureRM 未覆盖场景才引入 AzAPI；不重复维护完整 Bicep 栈 |
| Delivery | GitHub Actions、Azure Pipelines YAML、WIF、Service Connections、Environments、Approvals & Checks | 真实 Azure DevOps 运行与云端受控部署（L3） |
| Observability | Azure Monitor、Activity Log、Log Analytics、KQL、Application Insights、告警链路 | DCR、复杂跨工作区查询、真实采集配置 |
| Ops | Azure CLI / Az PowerShell、Resource Graph、Pester、JSON/CSV | 企业级报表、复杂自动化平台 |

具体工具版本、镜像 digest、provider 版本及平台能力以 P0 实测和 P1 锁定为准，不在规划里臆造版本。优先 WSL2/Linux + Podman；如果 compose provider、本地 K8s 或网络机制不兼容，先记录最小复现和替代方案，不能未经同意切换为必须付费工具。Kubernetes 只在容器运维练习中按需启动，不与 KPCP 重复建设控制面。

### 2.1 Fidelity matrix（必须在 P0 建立，P8 审核）

| Azure 机制 | 本地可验证能力 | 不能由本地结果证明 |
|---|---|---|
| Storage Account | Azurite 支持范围内的 Blob/Queue/Table API、应用错误与恢复 | Azure RBAC、网络 ACL、Private Endpoint、geo-redundancy、实际备份服务 |
| Private DNS / Private Link | DNS 查询、错误记录、缓存/回退、私网目标连通性 | Azure VNet link、平台 DNS 和 Private Endpoint 控制面 |
| NSG / UDR / Peering | 容器/命名空间流量、路由、隔离和拒绝机制 | Azure NSG 优先级/状态、有效路由、peering transit 等具体实现 |
| Entra ID / MI / Key Vault | 测试 token/授权 fixture、明确 allow/deny 与应用错误处理 | Entra 签发、Managed Identity token endpoint、角色传播及 Key Vault 实际授权 |
| Azure Policy | 本地配置规则或策略 fixture 的正反例 | ARM 实际 deny/audit/modify、remediation、scope/inheritance |
| AzureRM / Terraform | fmt/validate、mock provider 单测（若版本支持）、本地 provider 状态/锁/漂移 | 实际 Azure plan/apply、ARM API 接受、Azure Storage backend 锁行为 |
| AKS/ACR | 本地 Kubernetes 与本地 registry、ImagePullBackOff 排障 | AKS managed identity、ACR role mode、网络权限和托管升级 |
| Monitor/KQL | 合成信号、日志关联、可执行本地告警链路；官方 Demo KQL 如可访问 | 自有 Azure Monitor 采集、Azure 告警实际触发、真实 KQL 执行结果（除非对应引擎执行） |
| Backup/DR | 恢复副本、checksum、计时和数据一致性 | Azure Backup/PITR/跨区域故障转移实际行为 |
| Azure Pipelines | YAML 静态检查、阶段脚本执行、审批协议测试 | Azure DevOps 服务端 YAML 编译、Environment checks/WIF 和实际任务执行 |

禁止构建一个庞大、未经证实的通用 Azure 仿真器；本地替代实现只服务于明确的实验目标。若引入第三方模拟器，先单独记录版本、API 覆盖、缺口、许可证、维护状态及契约测试，不作为未经验证的核心依赖。

## 3. 阶段化实施合同（P0–P8）

所有阶段按依赖推进；允许对明确独立的任务并行开发，但每次交付必须有一个可核验阶段结论。后续实施代理先读当前 main、实际文件与上次证据，再选择最小任务，不得凭文档推断已完成。以下目录/入口均为目标，当前尚未实现。

### P0 — Architecture, Scope & Engineering Contracts

**目标：** 确立统一实验场景、企业参考架构、实现边界与可验收合同。

- 绘制 reference/local/live 三种拓扑，标记信任边界、正常流量、身份与遥测路径；建立 CIDR、资源命名、标签及环境所有权约定。
- 至少 5 条 ADR：订阅/管理组边界；Hub-Spoke vs Virtual WAN；私有 DNS/访问；身份/策略职责；Terraform state/交付边界。Hybrid connectivity 与跨区域 DR 可另加 ADR。
- 建立服务覆盖/Fidelity matrix、风险与威胁模型、实验数据声明、成本清单模板、阶段/incident/evidence ID 和验证状态规范。
- 探测实际宿主机、WSL、Podman、可选 K8s、Terraform、Azure CLI、PowerShell、可用网络能力；区分安装存在、版本可用、实际运行成功。不得自动登录或部署 Azure。
- 记录授权/订阅/region 条件为 unknown 或已核实值；建立待办清单和版本锁定策略。

**产物：** `architecture/`、实验/证据合同、状态追踪记录。  
**Gate P0：** 三种架构均有明确边界；ADR 说明备选方案、代价与验证；必选场景有验收标准；云端无授权默认禁用。仅设计部分标 `DESIGNED`，没有运行不写 `PASS`。

### P1 — Local Substrate, IaC Baseline & CI

**目标：** 构建一个可重复启动/停止的最小本地环境和可信的离线交付入口。

- 用固定版本的容器实现 HTTP probe、测试应用、DNS、Azurite 和合成数据生成；按需启用遥测或本地 K8s profile，避免全部常驻。默认 bind loopback；内部网络仅允许所需访问。
- 构建 Terraform 最小 Azure root/module（VNet/subnet/NSG 及明确 provider 版本），以 `fmt -check`、`init -backend=false`、`validate` 和适用的静态扫描/fixture tests 验证；网络安装 provider 需区分首次获取依赖与后续离线重跑。不能把 mock plan 当 live plan。
- 提供本地启动、健康检查、测试、重置、清理入口，例如 `scripts/lab` 子命令（具体实现由 P1 决定），全部有帮助、非零失败码、超时和目标限制。重复启动不得破坏状态，重复清理应安全。
- GitHub Actions 默认仅静态/本地测试，无真实云凭证、最小 `permissions`、不信任 fork 输入，依赖和 action 版本固定；日志保留不含秘密。

**Gate P1：** 在目标平台执行 clean setup → baseline → tests → teardown，记录版本/命令/退出码；第二次 clean replay 成功；CI 实际运行结果与当前提交关联，若 hosted CI 无额度可保留本地结果但 CI 验收明确 `BLOCKED`，不能伪造绿灯。

### P2 — Networking & Private Connectivity

- 按 DNS → route → security filtering → TCP/TLS → service authorization → application response 形成可解释的诊断树；不是所有故障都强制沿固定顺序，按症状调整假设。
- 设计 Azure VNet peering、NSG、UDR、Private Endpoint/DNS Zone/Link、有效路由/规则、Network Watcher IP Flow Verify/Next Hop/Connection Troubleshoot 的使用边界。
- 实施 IR-01、IR-02；IR-03/04 提供合同和可选本地增强。用可复现 DNS、流量、路由证据区分错误类别。
- 对 live DNS 场景预定义 FQDN、预期 private IP、探针所在 VNet、public network access 配置及 DNS 缓存刷新，避免断开 zone link 后公共访问仍然成功而误报故障。

**Gate P2：** IR-01、02 完成本地 baseline/fault/diagnose/recover/cleanup；验证相同探针；能够排除至少一个有意义的替代假设；Azure-specific 检查若未执行仍 `NOT_RUN`。

### P3 — Identity, Security & Governance

- 建立身份/角色/scope 矩阵与控制面/数据面访问图；分别设计 Azure RBAC、Entra ID、Managed Identity、Key Vault、Policy audit/deny/modify 的职责。
- IR-05 身份/权限 fixture 实现 allow/deny 和恢复；IR-06/09 提供具体 Azure 诊断合同及可选本地机制。配置测试覆盖秘密不入库、最小权限、禁止非批准范围和公共访问策略。
- 对 PIM、Defender for Cloud、Azure Policy remediation 和管理组部署记录权限、许可、费用前提，不默认启用收费功能或跨订阅阻断策略。

**Gate P3：** 至少一个可执行本地身份正反例，拒绝原因可区分，修复不使用全局特权；策略 fixture 具备允许/拒绝样例；明确本地证据不能证明 Azure Enforcement。

### P4 — Compute, Data & Container Operations

- 解释 VM/VMSS、App Service、AKS 的生命周期、健康检查、扩缩容、更新与故障边界；对 Application Gateway/LB 的入口与探针作设计对照，不同时部署所有选项。
- 最小 HTTP 应用采用健康检查与两个可识别版本，配合 Azurite 支持范围内的数据读写和合成 fixture。记录 Azure Storage/SQL/Key Vault 的网络、权限与数据恢复区别。
- 按需启动本地 Kubernetes 和 registry，实施 IR-07 镜像拉取故障；观察真实 kubelet/pod events，而不是只手写日志。记录 Azure ACR/AKS 的身份/role mode/私网差异，禁止把本地 registry 结果称为 ACR 验证。
- 准备 IR-11 版本回退机制。不要建设完整业务微服务系统或第二套 K8s 控制面。

**Gate P4：** HTTP probe、实际本地数据写读、版本标识和健康检查通过；IR-07 有真实本地 K8s 故障/恢复。如果目标机器不支持本地 K8s，该必选场景 `BLOCKED`，须经所有者决定替代方案，不擅自删掉门槛。

### P5 — Terraform State & Controlled Delivery / Azure DevOps

- Terraform 模块边界、版本固定、环境目录、输入/输出、状态隔离。设计 Azure Storage backend、权限、锁、版本恢复与 bootstrap 单独生命周期；本地 provider 的可执行锁/漂移/状态场景与 AzureRM 云操作分离。
- 实施 IR-08：观察真实本地状态锁竞争或等价的真实后端互斥机制，以及配置漂移检测和纠正；不能用 sleep 或自造日志冒充 Terraform 锁验证。`force-unlock` 仅在确认无活跃持有者的专用状态环境使用；不在共享状态练习。
- 交付 GitHub Actions 和 Azure Pipelines 两条职责清晰的路径：GitHub Actions 是仓库 CI；Azure Pipelines 是企业交付专项。覆盖 Azure Repos/GitHub 接入、YAML stages/jobs/templates、Service Connections、Variable Groups、Environments、Approvals & Checks、Workload Identity Federation、agent 能力与权限。
- 对 live 交付采用精确 plan 审批：绑定 Git SHA、目标 scope、provider lock file、plan hash、审批人/时间和有效期；apply 仅消费已批准且未改变的 plan，过期、漂移、目标不一致或重新生成 plan 必须重新审批。原始 plan/state 只保留在授权受限位置，不提交 Git；审批外部检查配置与 YAML 分开取证。
- PR 不提供 live 写权限；禁止自动 apply/destroy；Terraform plan 与 apply 角色按真实 provider 操作需求设计，不声称任意纯 Reader 都能完成计划。定义并测试 fail-closed 的审批条件和环境串线防护。回滚依赖具体资源语义：配置还原/重新计划、应用版本切换或数据恢复，不能声称 Terraform 有通用 undo。

**Gate P5：** 静态 Terraform 通过、实际本地 state/lock/drift 证据、Azure Pipelines YAML 与离线阶段脚本验证、错误目标/篡改 plan/未批准/过期/并发等负面测试。真实 Azure DevOps 服务端执行、WIF 和审批未运行则 `NOT_RUN`；其 live gate 在 L3。

### P6 — Observability, KQL & Operations Automation

- 建立本地结构化日志/指标与 request/correlation ID，定义成功率、错误率、延迟、可用性、告警窗口/阈值及去重。至少一条实际本地信号 → 告警 → 恢复闭环（IR-10），包含错配/无数据处理。
- Azure Monitor/Log Analytics/Activity Log/Resource Logs/Application Insights/DCR/Action Groups/Alert Processing Rules 建立数据流与权限成本图。
- 至少 5 条 KQL：控制面变更、错误趋势、失败请求关联、延迟分位数、身份/网络故障定位。逐条列明真实表或 schema 前提、字段、时间窗、预期结果、误报/空结果解释。官方 Demo 如可访问则记录实际执行及数据来源；否则保留查询和 fixture/语义审查，KQL 执行标 `NOT_RUN`，绝不拿本地 SQL/Python 输出冒充 KQL。
- 默认只读 PowerShell/Azure CLI inventory：限定 scope、分页、JSON/CSV、错误/重试/超时、权限不足、空集合、退出码与脱敏。参考 Resource Graph / Azure Resource Inventory；Pester 或等效测试使用 fixture，真实云查询放 L2。

**Gate P6：** 本地告警触发、诊断与恢复均有机器可验证证据；5 条 KQL 具有来源与独立执行状态；只读 inventory 测试通过，云端查询未执行不影响本地 release，但不得声称实际云盘点完成。

### P7 — Incident Response, Recovery & Independent Replay

- 整理全部 12 个 incident 合同和诊断/runbook；8 个 mandatory local 场景全部闭环。其余场景保留设计/条件实验状态。
- IR-11：已知健康版本 → 故障版本 → health/signal 失败 → 回退至已知版本 → 同一探针恢复。验证响应内容/版本与数据，不能只看进程 running。
- IR-12：确定数据集及 checksum → 生成备份/副本 → 对隔离对象进行可逆损坏或删除 → 恢复到新路径 → 验证 checksum、对象数、读取行为和耗时。该结果只证明本地恢复，不证明 Azure Backup/SQL PITR。
- 做一次独立 clean replay：由另一执行者或隔离的新会话按文档执行，不依赖原作者未记录步骤；验证故障诊断与复验，记录差异、失败及修复。至少一个网络场景、一个身份/交付场景及恢复场景必须被独立重放。

**Gate P7：** 8/8 本地必选场景通过；关键数据完整性断言通过；独立重放有真实记录；所有实验后环境回到基线/清理完成。若只是同一代理重新跑，不称为独立人工复核。

### P8 — Technical Handbook, Final Acceptance & Local Release

- 形成机制导向、图文并茂的技术教材（第 8 节），与最终源码版本、实测结果和能力映射一致。
- 完整 clean replay、CI 状态核验、证据追踪、依赖/秘密扫描、残留审计；明确所有设计/本地/demo/live-only 的范围和实际结果。
- 生成单一 release acceptance summary 和阶段/场景结果矩阵；检查 README 不再使用过时的计划状态，且所有完成声明有证据来源。

**Gate P8：** P0–P7 的强制 gate 均满足，手册审核通过，必选场景实际执行，没有未披露的 fail/blocked。若任何必选项缺失，保持 `PARTIAL`，不得封为 `LOCAL_RELEASE_READY`。live 状态单列，不要求为了本地版花钱。

## 4. Incident Catalogue — 可复验故障场景

下面是 V3 的目标场景清单，并非已发生的事故。Mandatory local = 必须执行真实本地机制的 8 项；Design/optional = 至少完成可执行的设计合同，增加实际测试需记录对应结果。每项均有独立 ID、前置条件、受控注入、断言、复验及清理。注入工具只对本实验对象开放，不对任意目标执行。

| ID | 场景 | 本地要求 | 注入及预期诊断证据 | 恢复与验收 | Live Azure 映射 |
|---|---|---|---|---|---|
| IR-01 | Private DNS resolution | Mandatory | 改变隔离 DNS 记录/解析路径；从 probe 观测错误 IP/NXDOMAIN，区分 DNS 和 TCP | 恢复记录，处理缓存；同一 FQDN/IP/应用探针通过 | L1：Private DNS zone/link 与 Private Endpoint |
| IR-02 | Network filtering / NSG | Mandatory | 在隔离网络拒绝特定流量；DNS 正常但 TCP 失败，有规则/连接证据 | 恢复最小规则；允许路径通过，不相关拒绝路径仍拒绝 | L1：NSG/Network Watcher |
| IR-03 | UDR / route failure | Design/optional | 隔离 namespace 或路由 fixture 观察错误下一跳；明确与 NSG 的差异 | 恢复路径、验证有效路由/连通性 | 可选：Azure UDR/Next Hop |
| IR-04 | Peering connectivity | Design/optional | 双网络拓扑与断链/转发限制；不得把本地桥接叫作 peering | 恢复受控连通性和隔离断言 | 可选：VNet peering/effective routes |
| IR-05 | Identity permission denied | Mandatory | 移除测试身份所需数据权限；记录拒绝原因，区分认证失败和权限拒绝 | 只补必要权限；授权操作成功且越权仍拒绝 | L2：Managed Identity + Storage 或 Key Vault data-plane RBAC |
| IR-06 | Key Vault access failure | Design/optional | 通过 fixture 区分网络不可达、token audience、数据权限或 secret 状态 | 恢复具体错误条件；不授予 Owner，不泄露秘密 | 可选：真实 Key Vault |
| IR-07 | Image pull failure | Mandatory | 本地 K8s 使用不存在的镜像/tag 或受控 registry auth 错误；实际 Pod events | 修复引用/授权，Pod Ready 并通过应用探针 | 可选：AKS/ACR 角色、网络、镜像拉取 |
| IR-08 | Terraform state lock / drift | Mandatory | 实际锁竞争与带外改动；保留锁拒绝、plan diff 和目标范围证据 | 等待锁释放，重新审查计划、纠正漂移；最终一致 | L3：Azure Storage state 与真实计划/交付 |
| IR-09 | Azure Policy denial | Design/optional | 本地策略 fixture 验证合规/违规配置；对 scope 和 effect 建立预期 | 修改违规配置；合规通过、违规仍拒绝 | 可选：授权 RG 的 Azure Policy deny/audit |
| IR-10 | Monitoring / alert failure | Mandatory | 注入可观测的错误或规则错配；保留信号、规则评价、触发和通知证据 | 修复后同一故障触发告警；恢复时信号和状态正确 | L2：Azure Monitor alert/action group |
| IR-11 | Deployment regression | Mandatory | 两个可识别版本，坏版本实际健康/功能检查失败 | 回退已知版本；响应、版本、健康和必要数据断言通过 | L3 可选应用部署/回退；不替代 IaC 审批 |
| IR-12 | Data loss / restore | Mandatory | 合成数据备份后，对专用对象删除或破坏；证明数据确实失效 | 恢复到隔离目标，校验 checksum/数量/读取，记录时间 | L3：真实 Azure Storage 数据恢复；Azure Backup/PITR 单独标注 |

本地 mandatory 共 8 项：IR-01、02、05、07、08、10、11、12。其余 4 项不得以无执行的文档领取本地 `PASS`。Live 场景仅在真实 Azure 服务上执行后才能获得 `LIVE_VERIFIED`。

### 4.1 每个故障的验收协议

```text
preflight → known-good baseline → controlled injection
          → observed failure → hypothesis and discrimination
          → bounded repair/rollback → same-probe verification
          → RCA → teardown/residual audit
```

- baseline 必须先通过；否则不得继续注入。故障检测必须断言预期错误类别（而不是仅接受任意非零退出码）。注入后的应用探针与 baseline 相同或明确等价。
- 记录预期影响、实际影响、时间线、关键证据、至少一个合理替代假设及排除方法、根因、最小修复、预防措施。不得将预设故障答案或静态文档当作独立诊断。
- 为检测时间、诊断时间、恢复时间定义起止事件、计时源及单位。仅报告实际测量值；单次实验不等于生产 MTTR、SLA 或可用性。
- 使用 run ID 关联实验对象、日志和输出。即使测试失败也要执行限定范围的 cleanup，并保留失败原因。注入/恢复脚本不得接受未经校验的生产域名、订阅或外部目标。
- 独立重放优先只提供症状与正常目标，不暴露注入细节；保留实际诊断步骤。自动化回归与独立排障是不同证据。

## 5. 条件性真实 Azure 验证 — L1–L3

Live 阶段只允许在 P0 完成范围合同、相关本地阶段具备可验证探针后启动；可按模块完成后逐次执行，但本地发布不要求它们。以下是最小 live qualification 套件，不是授权书，也不是对 Azure 当前价格或订阅可用性的保证。

### L0 — 每次 live 实验都必须通过的前置检查

- 由所有者确认准确订阅、tenant、RG、region、允许 SKU/资源清单、时间窗口、费用上限及实际权限。检查 region/quota、价格、资源 provider、必要 RBAC、Azure DevOps entitlement，失败则 `BLOCKED`。不得使用记忆中的旧预算替代本次授权。
- 使用专用 lab scope、合成数据、唯一 run ID 和 owner/expiry 标签，锁定实际 target。先清点共享或既有资源，禁止修改不属于本实验的对象。只在批准范围内创建必要的角色/资源；不对管理组或 tenant 实施默认变更。
- 估算全部依赖和生命周期成本：VM、disk、IP、private endpoint、Storage 交易、DNS、log ingestion、backup retention、pipeline capacity、数据传输等；设置人工时间限制、监控和停止条件。无额度或无法可靠估算则不执行。Azure Budget 不提供硬支出保证。
- 优先短期凭证；本地交互登录由所有者操作。执行代理不索要或输出密码/token，不自行创建超范围凭据。保存原始 plan/state/log 至授权存储并脱敏后发布摘要。
- 删除路径、资源清单和 owner 已确认。清理后检查原始 scope、bootstrap backend、保留备份、磁盘、日志和相关外部资源；Azure 成本数据可能滞后，明确后续复查。禁止为了清理而删除共享 backend、保留策略之外的数据或未知资源。

### L1 — Terraform Deploy & Network Troubleshooting

- 在批准的最小 lab 中用 AzureRM 实际 plan/apply，部署 VNet/subnet/NSG、Storage、必要 Private Endpoint/DNS Zone/Link 及最小探针资源；按预算分批启用，不强行部署高价组件。
- 验证正确 FQDN 解析到实际 private IP、应用连通、预设公共路径限制；执行 IR-01、02 至少其中一个完整真实云闭环（另一个记录实际状态）。用 Azure CLI/Network Watcher 的可用工具、effective rules/routes、DNS/连接探针确定失败环节。
- 记录 approved plan、apply、验证、restore、destroy、残留清单及成本复查。若 backend 为后续实验复用，必须是预先批准的显式保留项，不可宣称全部零残留。

**Gate L1：** Azure API 实际部署、至少一个真实 network incident recovered、同一探针复测通过、受控销毁与残留处理证据均存在。

### L2 — Identity, Monitoring & Read-only Operations

- 在受控 scope 使用 Managed Identity 或授权工作负载身份访问 Storage/Key Vault。执行 IR-05：通过最小数据面角色实现真实 allow/deny/recover，排除网络、token audience 与权限传播延迟；不以提权到 Owner 规避故障。
- 创建最小实际监控信号、适用的 alert rule 和受控 action group 或可观测通知路径；执行 IR-10，记录实际触发、通知/处理及恢复。不以手工发消息代替 Azure 告警。
- 在自有 Azure 数据上执行至少 3 条适用 KQL（P6 总查询包至少 5 条，其余可用官方 Demo 或标注 NOT_RUN）；记录表、时间范围、查询结果和解释。若服务/schema 不可用则如实阻塞，不生成虚假日志。
- 在授权 scope 执行 P6 只读 inventory，输出脱敏结果，与资源清单核对。真实 Azure Policy audit/deny 是额外目标，仅在独立授权 RG 与必要权限下执行。

**Gate L2：** 一个真实身份事件完整恢复、一次实际 Azure 告警触发及恢复、至少 3 条自有云 KQL 实际执行、真实只读盘点和清理证据均存在。

### L3 — Azure Pipelines, State & Data Restoration

- 在所有者授权 Azure DevOps organization/project、repository、agent、WIF service connection 和 Environment 的前提下，实际运行 pipeline；以 Azure Pipelines 的服务端运行记录及外部 approvals/checks 取证，而非只提供 YAML。
- 验证 Terraform plan → authorized approval → exact plan apply；使用专用 Azure Storage state，观察真实锁/状态隔离或受控漂移；验证未经批准的 apply 被阻止。无需为了验证而建立昂贵环境，复用已批准的最小资源。禁止 agent 自行绕过审批。
- 对合成 Blob 等数据执行真实 Azure 数据恢复（例如已启用并适用的 versioning/soft delete 或受控副本恢复）。必须预先验证选定保护机制、保留期限和恢复目标，记录删除/损坏前后、恢复校验及实测耗时。除非实际使用 Azure Backup，不称为 Azure Backup 恢复。Azure SQL PITR、跨区域恢复只在单独授权时实测。
- 完成 pipeline、身份、storage backend、恢复副本等所有资源与保留项核对，确认无未批准残留或持续支出。

**Gate L3：** 真实 Azure DevOps pipeline、精确计划审批/未批准拒绝、真实 Azure state 验证、真实数据恢复、完整性检查、计时及清理记录均存在。若 Azure DevOps hosted capacity 或身份权限不可得，保留本地 YAML 验收并标 live gate `BLOCKED`。

## 6. 工程规范与证据模型

### 6.1 版本、目录与复现

实现以 README 的目标目录为准。`architecture/` 存设计；`infrastructure/` 存真实 Azure IaC 与明确区分的本地实现；`labs/` 组织可重用环境和探针；`incidents/` 存实验合同与 RCA；`pipelines/azure-devops/` 存 Azure Pipelines；`scripts/`、`tests/` 存可执行验证；`evidence/` 存脱敏摘要；`manual/` 存教材。

- 固定 Terraform/provider、镜像、关键 CLI/工具与 action 版本，记录实际环境差异。不要提交 provider cache、镜像、`node_modules`、运行时临时文件或原始敏感日志。保留适用 root module 的 `.terraform.lock.hcl`。
- 公共 CI 可以下载明确依赖，但不能依赖未授权 Azure credentials。云端 workflow 必须显式受控触发、限制 branch/environment/scope。实施后用实际运行 URL、commit SHA 和 job conclusion 验证。
- 不堆一次性 evidence 脚本。复用小而清晰的实验入口与断言；机器可读结果辅助审核，教材解释机制。所有失败、跳过、无权限状态均保留。

### 6.2 状态规范

| 状态 | 含义 |
|---|---|
| `PLANNED` | 已列计划但尚未完成设计/实施 |
| `DESIGNED` | 设计和评审已完成，无运行证明 |
| `STATIC_CHECK_PASS` | 明确列出的静态检查实际成功 |
| `LOCAL_VERIFIED` | 对应本地机制实际运行且断言通过 |
| `DEMO_VERIFIED` | 在标注的外部 demo 数据/服务上实际执行成功 |
| `DEPLOYED` | 实际目标资源已创建；不自动证明功能或安全 |
| `LIVE_VERIFIED` | 对应 Azure 服务行为实际验证且断言通过 |
| `RECOVERED` | 已观测故障并用同一探针证明恢复；必须标注模式 |
| `CLEANED_UP` | 目标资源/进程与批准保留项经过核对 |
| `NOT_RUN` | 未执行，包括无授权或可选未安排 |
| `BLOCKED` | 已知前置条件/环境/权限/成本阻塞 |
| `FAIL` | 已执行且未满足预期 |
| `PARTIAL` | 聚合阶段有部分结果但强制 gate 尚未满足 |

同一个实验可能拥有多个独立检查状态，例如 STATIC 已通过、LOCAL 已恢复、LIVE NOT_RUN。不能用最高单一状态覆盖未执行检查。阶段 `PASS` 只代表该阶段明确要求的全部检查满足；不等价于 Azure 全部服务 live pass。

### 6.3 最小证据记录

每个 run 必须记录以下字段（P0 定义实际 schema，P1 实现验证；此处不是已实现文件）：

```yaml
run_id: <unique-id>
scenario_id: <P-stage-or-IR-id>
mode: <DESIGN|STATIC|LOCAL|DEMO|LIVE>
source_commit: <tested-commit-sha>
started_at_utc: <timestamp>
ended_at_utc: <timestamp>
environment: <redacted-scope-and-tool-versions>
preconditions: <authorization-and-baseline-result>
checks:
  - id: <check-id>
    expectation: <testable-condition>
    observed: <actual-result-or-not-run>
    status: <status>
    evidence_ref: <redacted-relative-path-or-authorized-run-reference>
cleanup: <inventory-result-and-approved-retained-resources>
limitations: <fidelity-gaps-and-blockers>
```

记录实际执行命令、退出码、探针输出、变更摘要、工具版本、RCA 与必要图示。对于可公开文件可记录 SHA-256 和 artifact manifest，不能将 hash 当作内容真实性或独立复核证明。禁止提交敏感原始 plan/state/token/secret/tenant ID；机器生成的敏感计划仅授权受限存放。记录 source commit 时使用被测试的源码 SHA，后续证据 commit 单列，避免循环自引用。

### 6.4 安全、成本和测试有效性

| 风险 | 强制控制 |
|---|---|
| 非授权部署/费用 | 默认禁用 live；明确授权、预算、scope、停止条件、销毁和复查 |
| 环境串线 | 独立环境/state/凭据；显式 target allowlist；拒绝未知目标 |
| 计划被替换 | 精确 plan hash + commit/scope/lockfile + 审批绑定；变化则重新审批 |
| 凭据泄露 | WIF/短期凭证、最小权限、脱敏扫描、受控 artifact、PR 无 live 写权限 |
| 测试假阳性 | baseline 成功、指定错误断言、同探针复测、真实退出码、负面对照 |
| 数据损失 | 合成数据、专用对象、恢复目标、校验和、清理保护 |
| 成本残留 | 专用资源清单、实际 destroy/删除、已批准保留项、延迟账单复查 |

## 7. 最终验收与封版定义

### 7.1 Local release — 必须满足全部条件

- [ ] P0 三层架构、至少 5 ADR、职责矩阵、威胁与成本模型、Fidelity matrix 完成。
- [ ] P1 本地环境可 clean setup/replay/teardown；真实 CLI/容器/依赖版本已记录。
- [ ] Terraform 最小 Azure 配置静态验证及适当测试通过；本地 state/lock/drift 真实运行。
- [ ] IR-01、02、05、07、08、10、11、12 共 8/8 mandatory local 完整闭环，其他四项有设计合同及真实状态。
- [ ] 身份允许/拒绝、策略 fixture、审批篡改/过期/错误 scope/并发等负例通过。
- [ ] Azure Pipelines YAML 与本地阶段脚本已验证；实际 Azure DevOps 未运行明确标注。
- [ ] 5 条 KQL 具有明确表/schema 和独立验证状态；本地 telemetry/alert 闭环与只读 inventory 测试通过。
- [ ] 数据恢复实际成功，checksum/对象数/读取断言与耗时完整。
- [ ] 至少三个规定类别独立 replay，保留观察结果；当前源码 CI 必选检查实际通过。
- [ ] 教材发布、图/源码/实测状态一致；证据脱敏、最终残留审计、README 更新。

全部满足才标 `LOCAL_RELEASE_READY`；否则 `PARTIAL`。官方 Demo 不可访问或 live 未授权不是本地 gate 的失败，只要相应状态如实披露。若 CI 或本地 Kubernetes 必选项被环境阻塞则仍 PARTIAL；所有者可以显式审议变更合同，不能执行者私自豁免。

### 7.2 Live portfolio qualification

- [ ] `LOCAL_RELEASE_READY` 已成立。
- [ ] L1、L2、L3 三个 gate 全部真实通过，且各次 L0 授权、成本与清理记录完整。
- [ ] 自有 Azure 与 Azure DevOps 实测记录可追溯；未验证服务仍逐项标记，不以 qualification 泛化到全部 Azure 能力。

全部满足才标 `PORTFOLIO_READY_LIVE`。只完成部分 live 实验可报告 `LIVE_VALIDATED_SUBSET` 并列出实际通过 ID；既不否定本地封版，也不声称完整 live qualification。项目没有 `PRODUCTION_READY` 状态。

### 7.3 里程碑与资源控制

P0–P1 优先建立最小可运行骨架；P2–P6 按阶段增加真实练习；P7 做集成、重放与纠错；P8 生成最终教材与验收。阶段粒度以可验证增量为单位，不规定虚假的工时或页数。若需要缩减范围，优先保留网络、Terraform、身份、告警、恢复闭环；改变必选 gate 必须先由所有者明确批准并形成变更记录。

## 8. 技术教材（Technical Handbook）

目标是形成可以独立学习和复习的工程教材，而非代码之外的大量证据文件。以模块化 PDF 为主，保留对应可编辑源文件；可以后期合订，不能只保留 PDF 无源。参考此前专项教材的机制导向，但不强行复制其页数、数量或排版。

| 教材模块 | 核心内容 | 来源阶段 |
|---|---|---|
| H01 Enterprise Azure Architecture | Landing Zone、责任边界、信任/成本、Hybrid/DR ADR | P0 |
| H02 Engineering Lab & Terraform Foundations | 本地环境、AzureRM、模块与验证层级 | P1 |
| H03 Azure Networking & Diagnostics | DNS、route、NSG、peering、Private Link、Network Watcher | P2 |
| H04 Identity, Security & Governance | Entra ID、RBAC、MI、Key Vault、Policy、安全机制 | P3 |
| H05 Compute, Containers & Data | VM/VMSS、App Service、AKS/ACR、Storage/SQL | P4 |
| H06 Terraform Delivery & Azure DevOps | state、drift、精确计划审批、WIF、Pipelines | P5 |
| H07 Monitoring, KQL & Operations | 日志、指标、告警、查询与 PowerShell/CLI | P6 |
| H08 Incident Response & Disaster Recovery | RCA、rollback、restore、checksum、RPO/RTO、复验 | P7 |
| H09 Integrated Case & Interview Guide | 综合拓扑、故障诊断树、边界、岗位映射 | P8 |

每册建议按以下结构组织：学习目标与前置条件 → 技术原理/内部机制 → 架构图和数据/控制面时序 → 配置/关键代码摘录（实际路径和版本）→ 可复验实验步骤 → 故障分析和修复 → 实际结果与限制 → 技术权衡和面试问题 → 官方参考。Live 增补材料单列，不修改历史本地证据的性质。

教材质量门槛：图优先解释机制而非装饰；架构示意图明确标注 proposed/reference/local/live；真实截图必须来自对应真实环境并脱敏；示例代码标明是否已经实现；所有源码摘录与最终版本一致；没有真实 Azure 截图就不伪造；PDF 应实际渲染检查分页、可读性、代码截断、链接、字体和图例。不得大段复制官方教程或把证据日志当教材正文。

## 9. 岗位能力映射与叙述

| 目标岗位 | 应能解释及演示 | 不得夸大 |
|---|---|---|
| Senior Cloud / Infrastructure | Landing Zone、私网访问、Terraform、identity、治理、恢复 | 参考设计不是企业级实际部署 |
| Platform Engineer | 模块边界、环境隔离、交付权限与准入、K8s/registry 运维 | 本地 K8s 不是 AKS 生产运维 |
| SRE / CloudOps | 信号、KQL、独立诊断、错误预算概念、回滚与恢复 | 实验 MTTR 不是线上 SLA；不等于真实 On-call |
| DevOps Engineer | Azure Pipelines、WIF、state、审批、CI、drift | YAML 静态验证不是 Azure DevOps 执行 |
| Azure Architect | ADR、network/identity/data 的成本可靠性取舍 | 不声称拥有未经授权的企业架构落地经历 |

最终简历只选已通过场景、真实工具和实际测量结果。例：完成后可陈述“Built a reproducible local lab to diagnose DNS and network-filtering failures; verified recovery using identical probes.” 只有 L1 实测后才可改写为真实 Azure Private DNS / NSG 故障恢复经历；所有表述仍是独立 lab 而非生产银行经验。

## 10. 官方资料与事实核验入口

实施时优先核查官方文档和 provider schema，记录访问日期及与锁定版本的对应关系；以下是参考入口，不代表全部服务已可用，也不构成课程复刻。

- [Azure Landing Zones / CAF](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/)
- [ALZ Terraform guidance](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/deploy-landing-zones-with-terraform)
- [AZ-700 networking labs](https://microsoftlearning.github.io/AZ-700-Designing-and-Implementing-Microsoft-Azure-Networking-Solutions/)
- [AZ-104 labs](https://microsoftlearning.github.io/AZ-104-MicrosoftAzureAdministrator/)
- [AZ-305 case studies](https://microsoftlearning.github.io/AZ-305-DesigningMicrosoftAzureInfrastructureSolutions/)
- [Private Endpoint DNS configuration](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns)
- [Private Endpoint connectivity troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/azure/private-link/troubleshoot-private-endpoint-connectivity-problems)
- [Network Watcher connection troubleshoot](https://learn.microsoft.com/en-us/azure/network-watcher/connection-troubleshoot-overview)
- [Azurite and its limitations](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite)
- [Azure RBAC overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)
- [Azure Policy overview](https://learn.microsoft.com/en-us/azure/governance/policy/overview)
- [Terraform AzureRM backend](https://developer.hashicorp.com/terraform/language/backend/azurerm)
- [AzureRM provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Pipelines workload identity federation](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/configure-workload-identity?view=azure-devops)
- [Azure Pipelines approvals and checks](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops)
- [Azure Monitor / Log Analytics tutorial](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-tutorial)
- [Azure Resource Inventory](https://github.com/microsoft/ARI)
- [Azure pricing calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

## 11. 执行与授权边界

原始 2026-11-26 文档更新的交接约束仅适用于当时，不限制后续获批工程。本轮 owner 已通过 master prompt 与“开始执行”授权连续推进 Stage 1–3，并授权对 main 提交/推送已验证增量。Stage 2 继续禁止 Azure 资源创建或修改；Stage 3 先执行授权范围内的 L0 只读预检。任何 live 资源变更仍必须拥有对应实验的明确授权、精确资源/scope allowlist 和可复核成本估算；USD 1.00 是全项目累计上限，可靠成本无法估计则不部署。
