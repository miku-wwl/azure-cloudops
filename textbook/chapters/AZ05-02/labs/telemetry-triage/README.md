# Log Analytics 与 Application Insights 离线练习

该 Python 模型读取合成的 workspace `AppRequests`、`AppDependencies` 和 `AppExceptions` 行，演示限定时间、按 `ItemCount` 加权采样、按 `OperationId` 分组以及用 `ParentId` 与 item ID 检查父子调用关系。

从仓库根目录运行：

```powershell
python -m unittest discover -s textbook/chapters/AZ05-02/labs/telemetry-triage -p "test_*.py" -v
python textbook/chapters/AZ05-02/labs/telemetry-triage/telemetry_model.py
```

七条 KQL 模板位于 `queries/`。每条都注明表、列和时间字段假设；运行前应对照目标 workspace 的实际 schema、权限和敏感数据要求。七条模板尚未在 workspace 执行。不要把资源标识、目标地址或事件行复制到公开日志。

本地模型不会解析或执行 KQL，也不模拟 Azure 的采样、导出和摄取行为。fixture 时间、事件标识和记录均为合成数据；缺少一条合成记录不能证明真实遥测不存在。
