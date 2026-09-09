# 个人技能精简验收

审计日期：2026-09-09。首轮提交：`16ebbc2`；本记录随独立复审修正一并提交。
三位未参与实现的子 agent 分别审计迁移恢复、技能行为和规则保留；主代理复核证据并执行最终检查。

## 范围与证据

| 要求 | 已检查的证据 |
|---|---|
| 移除重复个人技能，不改系统或插件技能 | `.chezmoidata.toml` 退役名单、`.chezmoiremove` 的精确目标、旧链接源移除；隔离迁移保留系统及未知技能哨兵 |
| 合并设计评审入口 | `design-review` 与领域参考；存在 CONTEXT/ADR 时加载相关文档，纯建议只读 |
| 合并 PRD 与拆工单入口 | `planning` 两种参考模式；草稿不发布，明确创建请求不重复审批，不顺带修改父工单 |
| 普通诊断、测试不被工单初始化打断 | `setup-matt-pocock-skills`、`triage` 的触发边界及独立场景演练 |
| 团队技能仅明确调用 | `team-swe` 正文、Claude 专用字段和 Codex `allow_implicit_invocation: false` |
| 全局精简后保留工程约束 | 对照 `0fce8bd`：504 → 87 行；中文/爸爸、完整实现、C++20、Git、Rust 提交检查、PATCH、uv、chezmoi 与密钥约束均保留；详细规则按需参考 |
| 保留南亚翻译技能 | 原 13 文件核对：只改入口大小写并补末尾换行，原正文和其余 12 个资源不变 |
| 保留并恢复 archify | 纳管 199 文件及固定上游 revision；CLI、五类渲染器、schema、模板、校验器、许可证均存在；doctor 与五类示例渲染成功 |
| 跨客户端与跨机器恢复 | 真实源向空 Linux 目标恢复，逐字节检查 253 个技能文件、54 个技能链接、2 个全局链接、全局正文及锁文件；目标集合无额外文件，再次 diff 为空 |
| 锁文件不覆盖后续个人安装 | 移除本次纳管/退役登记，保留其他技能、未知顶层字段与偏好；空输入、非法输入、无修改透传及幂等性均测试 |
| 模型偏好保持不变 | 源数据与本机配置均为 `gpt-6-astra` / `ultra` / `service_tier = "default"` |

## 独立审计发现与修正

1. `triage` 主入口虽已限制授权，旧参考仍要求自动评论、关闭工单及删除历史。
   两份参考已同步为条件式操作，保留已确认需求与历史。复审覆盖：简报草稿、仅记录拒绝理由、明确要求记录＋评论＋关闭；未发现剩余冲突。
2. README 原定向恢复命令在空目标缺少父目录时失败。
   已加 `--parent-dirs` 并补齐两个共享 `AGENTS.md` 链接目标。新回归使用真实源，覆盖了旧占位技能测试未覆盖的完整恢复。
3. 新回归首次比较器遗漏 `literal_` 源属性；已改为批量 `chezmoi target-path` 映射。
   保持南亚技能 `literal_run_linguagacha.py` 源文件名不变，目标仍为 `run_linguagacha.py`，没有将它误当迁移脚本执行。

## 重跑命令

从源仓库运行：

```sh
uv run --no-project tests/test_agent_skills.py
uv run tests/validate_skills.py
uvx ruff check --no-cache --target-version py311 tests
uvx ruff format --no-cache --target-version py311 --check tests
git diff --check
```

最终结果：8 项测试、18 个技能入口校验、Ruff 和差异检查通过。
技能校验对 `team-swe` 的 Claude 专用布尔字段单独检查，再复用系统验证器；不将原版验证器拒绝该字段误报为原版直接通过。
Codex 显式调用元数据已对照 [OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills) 核实。

## 验证边界

- 实际恢复与运行检查在 Linux 执行；macOS/Windows 仅验证清理模板分支，未执行真实平台部署。
- 工单场景为只读前向演练，没有创建、评论、关闭真实工单，也没有启动自动实施。
- archify 验证覆盖包资源和五类渲染，不等于浏览器视觉验收；完整上游开发测试需要上游仓库的额外脚本。
- 已核实本地定向应用无漂移。提交推送到独立分支 `feat/simplify-agent-skills`，没有合并受保护的 `master`。
