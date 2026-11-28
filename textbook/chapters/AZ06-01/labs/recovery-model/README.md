# Azure Backup 与 Site Recovery 离线实验

该 Python 实验使用合成恢复场景，根据明确的时间戳计算 RPO 与 RTO，并检查恢复点、记录数、数据摘要、应用探针、测试故障转移隔离与清理条件。

从仓库根目录运行：

```powershell
python -m unittest discover -s textbook/chapters/AZ06-01/labs/recovery-model -p "test_*.py" -v
python textbook/chapters/AZ06-01/labs/recovery-model/recovery_model.py
```

先预测每种情况是否满足恢复目标，再查看模型输出并解释差异。示例时间、哈希、记录数和探针均为合成值。实验不创建 VM 或数据库，也不会执行 Azure Backup 或 Site Recovery 作业；真实恢复仍需使用获批的隔离环境、工作负载专属 runbook、完整性校验和清理流程。
