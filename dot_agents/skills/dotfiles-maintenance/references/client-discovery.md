# 客户端指令发现与历史记录

这里保存旧全局指令中的客户端差异与机器记录，供出现加载异常时定位。
它们不是当前产品保证；客户端更新后必须核对本机版本、实际配置和加载结果，必要时查询官方文档。

## 历史链接约定

| 应用后的内容 | 历史权威路径 | 历史链接入口 |
|---|---|---|
| Agent 指令 | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md`、`~/.agents/AGENTS.md` |
| 个人技能 | `~/.agents/skills/` | `~/.claude/skills/*`、`~/.codex/skills/*` |

实际链接由 chezmoi 源定义；检查现状后再使用这些路径，不根据表格创建重复入口。

## Claude Code 历史观察

- 旧记录在 Claude Code `2.1.247` 上观察到：仓库只有 `AGENTS.md` 时，Claude 未加载该文件。
- 当时采用项目内 `CLAUDE.md -> AGENTS.md` 链接兼容；“没有设置可以开启”是当时的判断，不能外推到新版本。
- 建链前检查是否已有真实 `CLAUDE.md`，避免覆盖独立内容；明确授权后按项目管理方式创建。
- 第三方仓库如只需本机兼容，可按授权用 `.git/info/exclude` 排除私有链接，避免混入上游提交。

## Codex 历史观察

- 旧约定以 `~/.codex/AGENTS.md` 作为用户级入口，不依靠 `~/.agents/AGENTS.md`。
- 旧记录显示，同级 `AGENTS.override.md` 会优先于 `AGENTS.md`；排障时检查是否存在覆盖文件，不能直接删除它。
- 旧配置使用 `project_doc_fallback_filenames = ["CLAUDE.md"]`，记录的语义为回退而非叠加：找到 `AGENTS.md` 时不再补读同级 `CLAUDE.md`。
- 当前版本的用户目录、查找顺序、回退行为以本机配置与官方说明复核。

## Kimi Code 历史观察

- 旧记录称裸 `~/CLAUDE.md`、`~/AGENTS.md` 不作为用户级入口。
- 当时观察到 `~/.kimi-code/AGENTS.md` 与 `~/.agents/AGENTS.md` 可分别加载，因此只在后者设置共享链接。
- 排查重复指令时先验证当前版本是否仍叠加加载，不因历史顺序覆盖已有专用配置。

## 机器遗留记录

- 旧记录提到 `repo/blog` 和 `repo/robot/dimos` 曾只有 `AGENTS.md`，尚未创建 Claude 兼容链接。
- 路径、仓库归属和未完成状态可能已变化；先确认当前机器是否存在对应项目，不把它当作待执行任务。
- 指令开头称呼异常可作为排查线索，但不足以单独证明文件未加载；结合链接、配置和当前客户端行为判断。
