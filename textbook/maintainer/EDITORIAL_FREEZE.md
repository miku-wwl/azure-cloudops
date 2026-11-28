# Azure CloudOps — Final Editorial Cleanup & Publication Freeze

- 日期：2026-11-28（Pacific/Auckland）
- 范围：最终读者版编辑清理和再出版；不恢复 Stage 3，不执行 Azure 资源变更。
- 起始接受基线：`82af4f82e628750041f8e6bf07ae86b6845383ae`
- 本地状态：编辑、重建、视觉审阅及本地回归通过；最终 ZIP 与 manifest 生成后须再执行归档校验。
- 远端状态：推送最终提交后，需核对该确切 SHA 的 GitHub Actions 结果，再宣布冻结。

## 本轮编辑结果

将教材首页和目录说明整理为面向学习者的中文内容；把验收、进度、来源映射、审计和历史记录收纳到 `textbook/maintainer/`，保留原始工程证据和接受历史；清理 23 讲中的内部阶段标签、测试数量、内部验收措辞及重复结尾，统一读者版章节结构与要点段；更新内部链接；重建全部 23 份 PDF。实验说明仍明确区分本地实验、获批只读 Azure 练习、未来在线练习和设计练习。

所有现有安全边界、成本限制、NOT_RUN 状态、合成证据与真实 Azure 证据的区别均予保留。没有重新认证、Azure 登录、资源部署或资源配置写入。本轮 Azure 花费为 USD 0.00。

## 逐讲最终编辑结果

| 讲次 | 主题 | 最终结果 | 页数 |
|---|---|---|---:|
| AZ00-01 | ARM 与 Landing Zone 控制平面 | 清理内部流程文字，保留控制平面机制与证据边界；重建并通过视觉检查 | 9 |
| AZ01-01 | Well-Architected 可靠性 | 统一读者版结构，保留故障域和可靠性推理；重建并通过视觉检查 | 7 |
| AZ02-01 | VNet、UDR 与有效路由 | 保留路由诊断和本地模型边界；重建并通过视觉检查 | 8 |
| AZ02-02 | NSG、ASG 与网络诊断 | 保留规则判断与 Azure 实际状态的边界；重建并通过视觉检查 | 9 |
| AZ02-03 | Private Link 与私有 DNS | 保留端点、DNS 和网络验证流程；重建并通过视觉检查 | 12 |
| AZ02-04 | 负载均衡与健康探测 | 保留探测和后端健康机制；重建并通过视觉检查 | 9 |
| AZ03-01 | Entra token 与 Azure RBAC | 保留 token、scope 与 data-plane 授权区别；重建并通过视觉检查 | 10 |
| AZ03-02 | Managed Identity、Key Vault 与联邦 | 保留凭据链与最小权限内容；重建并通过视觉检查 | 9 |
| AZ03-03 | Azure Policy、Activity Log 与 Defender | 保留治理控制和证据范围；重建并通过视觉检查 | 9 |
| AZ04-01 | VM、VMSS 与磁盘运维 | 保留补丁、代理依赖和恢复操作内容；重建并通过视觉检查 | 8 |
| AZ04-02 | App Service 与 Container Apps 发布 | 保留实际应用回滚与 Azure IR-11 部分执行的区别；重建并通过视觉检查 | 8 |
| AZ04-03 | AKS、ACR 与就绪性 | 保留工作负载就绪和镜像访问机制；重建并通过视觉检查 | 10 |
| AZ04-04 | Storage 与 Azure SQL 边界 | 保留网络、身份、数据保护和恢复配置说明；重建并通过视觉检查 | 9 |
| AZ05-01 | Azure Monitor 指标与告警 | 保留指标告警计算、配置和状态诊断；重建并通过视觉检查 | 7 |
| AZ05-02 | Log Analytics、KQL 与 Application Insights | 保留 DCR 数据路径和 KQL 状态边界；重写实验说明；重建并通过视觉检查 | 8 |
| AZ05-03 | Azure CLI、PowerShell 与 Resource Graph | 保留只读查询与结果解释；重建并通过视觉检查 | 7 |
| AZ06-01 | Azure Backup、还原与 Site Recovery | 保留工作负载相关恢复要求；重写恢复模型实验说明；重建并通过视觉检查 | 8 |
| AZ06-02 | 事件响应与 RCA | 保留事件推理、根因和证据限制；重建并通过视觉检查 | 7 |
| AZ07-01 | Terraform 核心、Provider、Graph、State 与 Plan | 保留本地可执行配置和 Azure 写入边界；重建并通过视觉检查 | 9 |
| AZ07-02 | Terraform 远程状态、锁与漂移 | 保留状态所有权、锁与漂移诊断；重建并通过视觉检查 | 9 |
| AZ07-03 | Azure DevOps 与 Workload Identity | 保留 YAML 与服务端设置的区别；重写 Pipeline 实验说明并更新官方参考；重建并通过视觉检查 | 9 |
| AZ08-01 | 企业混合路由与 DNS | 保留地址规划、路径推理和未来只读运行边界；重建并通过视觉检查 | 9 |
| FIN-01 | FinOps 成本归属与恢复 | 保留成本计算及未来只读练习边界；重建并通过视觉检查 | 9 |

## 出版与视觉 QA

- PDF：23 份；总计 199 页。编辑前本地出版集为 200 页，本轮没有为增加篇幅而扩写。
- 原有机制图：95 份 SVG；全部保留。未新增虚构 UI 图。
- 经确认的真实 Azure Portal 截图：0。教材以原有机制图、配置示例和 Portal 导航说明教学。
- 已生成并检查 50 张 88 DPI 接触表，覆盖所有 199 页；未发现空白页、内容裁切、重叠、页码或代码越界。
- 另以 150 DPI 检查 12 张代表性高密度页（路由、Private Link、RBAC、补丁、应用发布、Storage/SQL、Monitor、KQL、备份、Azure DevOps、混合网络和 FinOps）；文字、代码、表格与图均可读，未发现溢出。
- 页数：AZ00-01 9、AZ01-01 7、AZ02-01 8、AZ02-02 9、AZ02-03 12、AZ02-04 9、AZ03-01 10、AZ03-02 9、AZ03-03 9、AZ04-01 8、AZ04-02 8、AZ04-03 10、AZ04-04 9、AZ05-01 7、AZ05-02 8、AZ05-03 7、AZ06-01 8、AZ06-02 7、AZ07-01 9、AZ07-02 9、AZ07-03 9、AZ08-01 9、FIN-01 9。

## 本地验证

- `python textbook/tools/verify_repository.py`：通过；23 个课程条目、来源映射和 PDF 一致，314 个本地 Markdown 链接有效，E9 目录覆盖 13 个实验并满足 18 个必需字段。
- `python textbook/tools/test_python.py`：通过；24 个测试目录，534 个测试，失败目录 0。
- `python textbook/tools/verify_terraform.py`：通过；3 个 Terraform 根目录均通过格式、初始化、验证和 mock 测试，共 13 个 Terraform 测试断言，Azure 登录与 CLI/OIDC/MSI 认证已禁用。
- Pester 5.7.1：通过；6 项 PowerShell 工具与安全契约检查，失败 0。
- `git diff --check`：通过；仅提示两个 Markdown 文件将按仓库换行策略规范为 LF。
- `python textbook/tools/package.py`：生成 23 PDF 的 PDF ZIP 与 433 个文件的源稿 ZIP；发布清单记录归档与条目 SHA-256。内置 `--verify` 校验通过，两个 ZIP 与当前 PDF/源稿逐条一致。
- 敏感模式扫描：打包工具未找到本机专用 `tools/sensitive.local.txt` 规则文件，因此该可选扫描未执行；源稿 ZIP 与仓库工作树一致性校验已执行。

## 最终冻结条件

本地归档与一致性检查已通过。将修改与归档清单提交到 `main` 并推送，不得 force-push；核对远端 `main` 与最终本地提交一致，并验证该确切提交的 GitHub Actions 全部必需工作流通过。最终提交 SHA、CI URL、ZIP 字节数和 SHA-256 列入交付说明。只有这些检查通过后，才将版本状态称为 `TEXTBOOK_V1_0_1_FINAL_FROZEN`。
