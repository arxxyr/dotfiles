# 分诊标签映射参考

只有项目使用分诊工作流时才需要本表。先读取系统中的真实标签，再将状态映射到实际名称；以下同名值仅为无既有约定时的候选。

| 状态角色 | 项目标签候选 | 含义 |
|---|---|---|
| `needs-triage` | `needs-triage` | 等待维护者评估 |
| `needs-info` | `needs-info` | 等待补充信息 |
| `ready-for-agent` | `ready-for-agent` | 目标与验收完整，可由 agent 实现 |
| `ready-for-human` | `ready-for-human` | 需要人工实施或决策 |
| `wontfix` | `wontfix` | 决定不处理 |

已有等价标签直接映射，不重复创建。配置映射不等于已创建远程标签；缺失标签的创建、工单标签修改以及通知分别按任务授权执行。本地工单可将这些值映射到 `Status:` 字段。
