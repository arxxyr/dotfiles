# GitHub 工单配置参考

只在项目选用 GitHub Issues 时读取。以现有约定填写真实的 `OWNER/REPO`，不要将示例占位符原样写入项目配置。

- 优先复用已连接的 GitHub 工具；使用 `gh` 时明确目标仓库，避免当前目录或默认远程选错项目。
- 读取工单可用 `gh issue view NUMBER --repo OWNER/REPO --comments`。
- 列表查询可用 `gh issue list --repo OWNER/REPO --state open --json number,title,labels`，按任务收窄筛选范围。
- 用户已授权发布时才创建或更新工单；先检查重复项，保留已有正文和人工修改。
- 使用结构化工具参数传递多行正文；若使用 `gh`，用文件编辑工具生成正文文件，再传 `--body-file`，避免命令替换和转义破坏内容。
- 标签、评论、关闭工单和 PR 操作分别服从任务授权，不由“已配置 GitHub”自动授权。

项目说明应记录：目标仓库、首选工具、PRD 与实施工单的关系、采用的标签，以及已发布结果应回填的 URL。只有需要分诊时引用 `triage-labels.md`。
