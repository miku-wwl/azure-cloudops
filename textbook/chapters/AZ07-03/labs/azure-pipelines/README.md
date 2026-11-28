# Azure DevOps 离线练习：Plan、Review 与 Apply

## 学习目标

沿着仓库、Pipeline、Service Connection、agent、Environment 与 Azure 身份的边界，判断一个 Terraform Plan 如何被审阅、授权并安全地交给 Apply。

## 本地练习

`azure-pipelines.yml` 只运行离线检查，不配置 Azure task 或 Apply。`enterprise-pipeline.yml` 默认关闭云端交付，展示 `Plan → PlanReview → Apply` 的配置关系。先阅读对应章节，再查看 YAML 中的触发条件、编译期参数、artifact 来源、Environment 名称和连接引用。

需要 Python 3.10+ 与 PyYAML。运行：

```powershell
python -m pip install -r textbook/chapters/AZ07-03/labs/azure-pipelines/requirements.txt
python -m unittest discover -s textbook/chapters/AZ07-03/labs/azure-pipelines/tests -p "test_*.py" -v
```

预期：本地配置样例可被解析，示例合同对合成 Plan 与错误输入作出相应判断。普通 YAML 解析和本地模型不能证明 Azure Pipelines 服务端接受 YAML，也不能证明审批、WIF 或 Azure 权限已生效。

## 企业环境的配置清单

云端演练需要资源 owner 在 Azure DevOps 中设置服务端资源；YAML 不能替代这些配置：

1. 在 Azure Repos 目标分支配置 Build Validation 并保护 Pipeline 模板。生产 Required template 应由独立受保护的仓库提供；同仓库 include 不是防篡改边界。
2. 为 Plan 与 Apply 建立不同的 Azure Resource Manager Workload Identity Federation Service Connection，逐一核对 issuer、subject、audience、pipeline permission 和最小 Azure/Blob 权限。不要授权所有 Pipeline。
3. 创建独立 Review 与 Apply Environment，配置审批人、禁止自批、Branch control、Required template、超时与 Exclusive lock。`lockBehavior: sequential` 只选择排队行为，不会创建服务端 lock check。
4. 对 Variable Group 与 Secure Files 单独配置授权。仅将非敏感目标信息放入普通变量；backend、target 配置和受保护信任资料应留在仓库之外。
5. 使用隔离的 Plan、Review、Apply agent pool，并固定一致的 Terraform 与 Provider 工具链。Plan artifact 和日志可能含敏感值，应限制读取权限和保留时间。
6. 若部署设计依赖签名审批，需要独立受保护的签发/验证服务、真实审批人核验和持久防重放存储。单凭离线合同或 YAML 不构成信任根。

## 边界与清理

Azure DevOps 服务端模板、Service Connection、Environment、Variable Group 和 agent pool 尚未配置。练习只运行本地代码，不创建 Azure 资源，也不生成云端费用；本地 Python 缓存可按需删除。
