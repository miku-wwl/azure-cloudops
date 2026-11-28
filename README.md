# Azure CloudOps — 云运维工程教材

本仓库提供 23 讲中文 Azure CloudOps 技术教材，面向具备云平台、网络、身份、基础设施即代码或软件运维经验的工程师。课程通过具体故障引出机制，再用配置、演算和实验说明系统为什么如此运行。

## 开始学习

- [课程目录与 23 讲核心问题](textbook/CURRICULUM.md)
- [下载 23 讲 PDF 合集](textbook/dist/Azure-CloudOps-PDF.zip)
- [下载可编辑教材与实验源码](textbook/dist/Azure-CloudOps-Sources.zip)
- [阅读教材使用指南](textbook/README.md)

建议按以下顺序学习：治理与可靠性（AZ00–AZ01）→ 网络与 Private Link（AZ02）→ 身份与治理（AZ03）→ VM、应用、AKS 与数据服务（AZ04）→ 监控、日志与资源清单（AZ05）→ 备份与事故响应（AZ06）→ Terraform 与受控交付（AZ07）→ 混合网络（AZ08）→ FinOps（FIN-01）。课程目录说明每讲之间的依赖关系。

## 实验准备

先读对应章节及实验目录中的说明。每个实验列出所需环境、权限、命令、预期结果、排错和清理步骤。多数实验使用本地模型或离线配置，不需要 Azure 订阅；涉及 Azure 的示例会标明它是文档配置、只读操作还是未来现场实验。请以具体实验的前置条件为准：常见依赖包括 Python、Terraform、PowerShell，以及少数实验需要的 Docker 或 Kubernetes 本地环境。

## 验证范围

配置说明以章节列出的 Microsoft 与工具官方文档为依据；本地模拟结果只证明给定模型的行为，不等于 Azure 服务已实测。七条 KQL 查询模板尚未在真实 Log Analytics workspace 执行。一次 App Service 现场尝试只完成临时资源计划的创建与清理，Web App 发布和回退未在 Azure 验证。本书使用原理图，没有 Azure Portal 实拍截图。

## 许可

仓库依据 Apache License 2.0 发布。使用示例前，请按自身环境核对服务支持、权限、区域和费用。