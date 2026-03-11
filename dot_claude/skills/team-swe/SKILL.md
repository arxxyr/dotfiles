---
name: team-swe
description: 软件工程团队（最稳配置）：Tech Lead + Dev + QA + DevOps + Security（可选 Doc/Perf），适合中大型需求/长期可维护
disable-model-invocation: true
---

# 目标
对 $ARGUMENTS 进行“可维护、可测试、可发布、可回滚、可观测”的工程化交付。

# 0) 入口约定（lead 先收敛上下文）
- 需求/问题一句话定义（What）
- 验收标准（How to verify）—— 必须输出结构化 AC（Acceptance Criteria）：
  ```
  ### AC-N: [功能/场景名]
  - 前置条件：…
  - 操作：…
  - 预期结果：…（必须可判定 pass/fail，无歧义）
  - 验证方式：Playwright / curl / 单测 / 手动
  ```
  覆盖范围：正常路径 + 边界 + 异常 + 安全。AC 在代码之前定义，dev 和 qa 共享同一份 AC。
- 影响范围（模块/接口/数据/权限）
- 风险等级（低/中/高）与回滚策略（开关/版本/数据回退）
- 目标分支/交付形式（PR / 多 PR / hotfix）

# 1) 创建 agent team（建议 5~8 人）
创建一个 team，teammates 命名与职责如下（按需裁剪）：

## 核心必配
- tech_lead（Lead / Gatekeeper）
  - 拆任务、定接口/模块边界、控制技术债、合并/发布门禁
  - 强制：涉及接口/数据/权限/架构调整 => Require plan approval before any changes
- implementer_a（Dev）
  - 按模块实现（优先负责核心逻辑/核心库）
- implementer_b（Dev）
  - 按模块实现（优先负责边缘模块/适配层/工具）
- qa（Test/QA）
  - 用例矩阵、回归、边界与异常路径、最小复现、测试报告
- devops（DevOps/Release）
  - CI/CD、版本、部署、回滚、监控、发布清单
- security（Security）
  - 依赖风险、权限模型、输入校验、审计日志、安全测试清单

## 常见加成（按风险/规模启用）
- doc（Doc Writer）
  - README、设计文档、变更记录、迁移指南、Runbook
- perf（Perf Engineer）
  - profiling、压测、容量规划、性能回归门槛

# 2) 共享 Task List（tech_lead 维护）
建立 shared task list，必须满足：
- 每个任务都有：目标/验收、影响范围、风险、Owner、回滚、测试点、对应 AC 编号
- 任务粒度避免多人改同一文件（“同文件只允许 1 个 Owner”）
- 任务按依赖排序：先公共契约/接口 → 再实现 → 再集成 → 再测试 → 再发布

建议任务模板：
- [契约] API/数据/错误码/版本策略（Owner: tech_lead + security）
- [实现] 模块A（Owner: implementer_a）
- [实现] 模块B（Owner: implementer_b）
- [集成] 配置/部署/运行参数/迁移脚本（Owner: devops）
- [测试] 单测/集成/回归/异常路径（Owner: qa）
- [安全] 依赖审计/鉴权/输入校验/审计日志（Owner: security）
- [文档] README/变更记录/迁移指南（Owner: doc，可选）
- [性能] profiling/压测/基线/阈值（Owner: perf，可选）

# 3) 变更规则（防冲突 + 控风险）
- 同一文件只能由一个 teammate 修改；其他人只给 review 建议
- 接口/数据结构/权限模型改动：
  - tech_lead 必须先出 plan（文件清单、迁移步骤、回滚方案、测试策略、风险点）
  - security 必须 review 权限/输入/审计
  - plan 批准后才能动手
- 高风险改动默认加 feature flag 或开关，必须可回滚

## Plan 审批门禁（一票否决）
tech_lead 出 plan 后，以下角色拥有一票否决权：
- **security** — 权限/数据/输入校验存在未缓解风险
- **用户（人类）** — 架构方向不符合预期

否决触发条件（任一即否）：
- 缺少回滚方案
- 影响范围未覆盖（遗漏模块/接口）
- 安全风险未标注或未缓解
- AC 不可判定（模糊/有歧义）

否决后处理：
- 打回 tech_lead 修改 plan，附否决理由
- 修改后重新走审批，最多 2 轮
- 2 轮仍未通过 → 升级到用户决策

# 4) 质量闸门（不过不算完成）
tech_lead 定义并执行门禁，至少包含：
- 格式化/静态检查：format + lint（按仓库栈）
- 测试：单测 + 必要的集成/端到端最小链路
- 验证分离：dev 不写自己的验收测试，qa 独立验证（防止 self-congratulation）
- 按 AC 验证：qa 按阶段 0 定义的 AC 逐项验证，每个 AC 独立产出 evidence：
  ```
  .verify/
  ├── AC-1/
  │   ├── result.json      # pass/fail/needs_human + 原因
  │   └── screenshot.png   # 前端截图（如适用）
  ├── AC-2/
  │   └── result.json
  └── summary.json         # 汇总
  ```
- 三档判定：
  - ✅ PASS — 自动验证通过
  - ❌ FAIL — 自动验证失败，附原因（dev 修复后只需重跑失败的 AC）
  - ⚠️ NEEDS_HUMAN — 无法自动判定（UI 美观度、文案语气等），标注原因
- 安全：依赖扫描/高危漏洞处置、关键输入校验覆盖
- 可观测：关键路径日志/指标/告警最小集
- 发布：灰度/回滚路径可用（脚本/指令明确）

建议按栈自动选择（仅建议，不强制）：
- Rust：cargo fmt --check → cargo clippy -D warnings → cargo test
- C++/ROS2：clang-format/clang-tidy（如有）→ colcon test/ctest → 运行最小 demo

# 5) 交付物清单（tech_lead 汇总）
必须输出：
- 变更摘要（做了什么/没做什么）
- 风险与回滚（明确到命令/步骤）
- 测试结果（按 AC 组织：`.verify/` evidence 目录，含逐项判定 + 截图/日志）
- 安全检查（依赖风险、权限/输入/审计）
- 运行说明（启动参数/配置/部署步骤）
可选输出：
- ADR / 设计说明
- 性能报告（基线 + 变化 + 解释）

# 6) 收尾（必须做）
- 确认 task list 全部 completed 或明确标注 deferred（并写原因）
- Ask each teammate to shut down
- Clean up the team
