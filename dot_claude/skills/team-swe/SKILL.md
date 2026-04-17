---
name: team-swe
description: 软件工程团队（最稳配置）：Tech Lead + Dev + QA + DevOps + Security（可选 Doc/Perf），适合中大型需求/长期可维护；内置 RIPER 状态机、Spec 落盘、Archive 资产沉淀、轻量模式与线上故障 SOP
disable-model-invocation: true
---

# 目标
对 $ARGUMENTS 进行"可维护、可测试、可发布、可回滚、可观测"的工程化交付。

# 三条铁律（先读）
- **No Spec, No Code** — 未经 Plan Approved，不得改代码
- **Spec is Truth** — Spec 和代码冲突时，错的一定是代码
- **Reverse Sync** — 发现偏差/Bug，先修 Spec，再修代码

# RIPER 状态机总览（完整模式）
完整流程按阶段推进，**每阶段只产出一种东西**，阶段之间有门禁。走轻量模式见文末 §轻量模式。

| 阶段 | 目的 | 主要产出 | Owner | 自由度 |
|------|------|---------|-------|--------|
| -1 Pre-Research | 建索引 | CodeMap / Context Bundle / ProjectMap | tech_lead | 放开 |
| 0 Intake | 需求锁定 | Spec 骨架 + AC | tech_lead + 用户 | 放开 |
| 1 Research | 事实锁定 | 带代码出处的调研报告 | implementer + security | 放开 |
| 2 Innovate | 方案对比 | 2-3 个方案 Pros/Cons | tech_lead | 放开 |
| 3 Plan | 原子拆解 | 文件/函数级清单 | tech_lead | 放开（审批严） |
| 4 Execute | 按图施工 | 代码 + Execute Log | implementer_a/b | **收紧**（禁自由发挥） |
| 5 Review | 三角验收 | .verify/ evidence | qa + security | **收紧** |
| 6 Archive | 资产沉淀 | _human.md + _llm.md | tech_lead | 中 |

> 自由度原则：需要创造力时放开（Research / Innovate），需要执行力时收紧（Execute / Review）。不要反过来。

# 工程目录（Spec 落盘约定）
```
mydocs/
├── codemap/              # 长期资产：单项目代码索引，跨需求复用
├── context/              # 一次性语料：PRD/设计图/讨论记录，用完即归档
├── specs/                # 核心资产：每个需求一份 Spec，是代码的"源码"
│   ├── <name>.md         # 活跃 Spec（含 Research / Innovate / Plan / Execute / Review 段）
│   ├── <name>_human.md   # Archive 产出：精炼方案汇报，给人读
│   └── <name>_llm.md     # Archive 产出：压缩上下文切片，给下次 AI 恢复现场
└── projectmap.md         # 多项目一级导航（跨项目场景才需要）
```

---

# Step -1) Pre-Research（不熟模块必做）
**触发条件**（任一成立即必须做）：
- 接手的老项目，>1 个月没碰
- 跨项目联动（多仓/多服务/前后端）
- tech_lead 或任一 implementer 对相关代码路径不熟

**操作**：
- tech_lead 让 agent 扫描相关模块，产出 `mydocs/codemap/<module>.md`，覆盖：
  - 入口点（Controller / Filter / 定时任务 / CLI）
  - 核心调用链路（必须带 `文件:行号`）
  - 外部依赖（DB / RPC / MQ / 外部 API）
  - 风险点 + 不确定项
- 需求来源分散时额外产出 `mydocs/context/<name>_bundle.md`：提炼 PRD + 设计图 + 讨论记录，标注冲突与不确定项。
- 跨项目场景产出 `mydocs/projectmap.md`，回答四个问题：
  - 本次任务涉及哪些项目
  - 项目间如何调用/依赖/传数据
  - 每个项目应先看哪条链路、哪几个模块
  - 哪些项目必须改，哪些只是背景

**原则**：CodeMap 聚焦本次任务链路，不是全项目总图；复杂工程用"节点化拆解"，禁止一口吃下整个系统。

**可跳过**：单点小改（改配置、修文案）可直接进 Step 0。

---

# Step 0) Intake（tech_lead 收敛上下文）
产出 `mydocs/specs/<需求名>.md` 首版：
- 需求一句话定义（What）
- **结构化 AC（Acceptance Criteria）**，AC 在代码之前定义，dev 和 qa 共享同一份：
  ```
  ### AC-N: [功能/场景名]
  - 前置条件：…
  - 操作：…
  - 预期结果：…（必须可判定 pass/fail，无歧义）
  - 验证方式：Playwright / curl / 单测 / 手动
  ```
  覆盖范围：正常路径 + 边界 + 异常 + 安全。
- 影响范围（模块/接口/数据/权限）
- 风险等级（低/中/高）+ 回滚策略（开关/版本/数据回退）
- 目标分支/交付形式（PR / 多 PR / hotfix）
- 不确定项用 `[待确认]` 标注，Research 阶段补齐

---

# Step 1) 创建 agent team（建议 5~8 人）

## 核心必配
- **tech_lead**（Lead / Gatekeeper）
  - 拆任务、定接口/模块边界、控制技术债、合并/发布门禁
  - 强制：涉及接口/数据/权限/架构调整 => Require plan approval before any changes
- **implementer_a**（Dev）— 按模块实现（优先核心逻辑/核心库）
- **implementer_b**（Dev）— 按模块实现（优先边缘模块/适配层/工具）
- **qa**（Test/QA）— 用例矩阵、回归、边界与异常路径、最小复现、测试报告
- **devops**（DevOps/Release）— CI/CD、版本、部署、回滚、监控、发布清单
- **security**（Security）— 依赖风险、权限模型、输入校验、审计日志、安全测试清单

## 常见加成（按风险/规模启用）
- **doc**（Doc Writer）— README、设计文档、变更记录、迁移指南、Runbook
- **perf**（Perf Engineer）— profiling、压测、容量规划、性能回归门槛

## 共享 Task List（tech_lead 维护）
每个任务必须有：目标/验收、影响范围、风险、Owner、回滚、测试点、对应 AC 编号。
- **同一文件只允许 1 个 Owner**，避免多人改同文件
- 按依赖排序：先公共契约/接口 → 再实现 → 再集成 → 再测试 → 再发布

任务模板：
- [契约] API/数据/错误码/版本策略（Owner: tech_lead + security）
- [实现] 模块 A（Owner: implementer_a）
- [实现] 模块 B（Owner: implementer_b）
- [集成] 配置/部署/运行参数/迁移脚本（Owner: devops）
- [测试] 单测/集成/回归/异常路径（Owner: qa）
- [安全] 依赖审计/鉴权/输入校验/审计日志（Owner: security）
- [文档] README/变更记录/迁移指南（Owner: doc，可选）
- [性能] profiling/压测/基线/阈值（Owner: perf，可选）

---

# Step 2) Research（事实锁定）
**做什么**：agent 查清代码现状，锁定事实，消除信息差。**绝不允许 agent 瞎猜。**

**核心原则**：
- 每个结论必须带**代码出处**（`文件:行号` 或 `函数名`）
- 不接受"我认为"、"通常来说"——只接受"我在 `XXX.java:L42` 看到了 YYY"
- agent 必须主动提问；没有任何疑问 = 在敷衍，强制追问"你有什么不确定的点？"
- 反向复述：让 agent 用自己的话复述需求，检查理解一致性
- 所有发现**回写 Spec § Research Findings**，禁止散落在对话里

**完成标准**：入口/链路/依赖/风险全部锁定；每个结论有代码出处；`[待确认]` 已全部回答或显式标记。

---

# Step 3) Innovate（方案对比）
**做什么**：tech_lead 逼 agent 给 **2-3 个方案**，对比 Pros/Cons，**人类拍板选哪个**。

**核心原则**：
- **禁止只给一个方案**——一个方案 = 没有选择 = 局部最优陷阱
- 每个方案必须说清：改哪些文件、影响范围、风险点、工作量估算
- 人类做决策，agent 做分析；人类没拍板前不得进入 Plan
- 选定方案后必须回写 Spec § Innovate Decision（选了什么、为什么）

**可跳过**：单点修改（如改配置），在 Spec 中标注 `Innovate: Skipped, Reason: 单点修改，无需多方案对比`。

---

# Step 4) Plan（原子级规划 + 审批门禁）
**这是整个流程的决胜点。Plan 看不懂 = 不准动手。**

**核心原则**：
- 每一步必须精确到：改哪个文件、改哪个函数、怎么改
- 必须包含**函数签名**（新增的函数/类）
- 必须有明确的执行顺序（依赖关系）
- 高风险改动**默认加 feature flag 或开关**，必须可回滚
- 接口/数据结构/权限模型改动：tech_lead 必须先出 plan（文件清单、迁移步骤、回滚方案、测试策略、风险点）

## Plan 审批门禁（一票否决）
tech_lead 出 plan 后，以下角色拥有一票否决权：
- **security** — 权限/数据/输入校验存在未缓解风险
- **用户（人类）** — 架构方向不符合预期

否决触发条件（任一即否）：
- 缺少回滚方案
- 影响范围未覆盖（遗漏模块/接口）
- 安全风险未标注或未缓解
- AC 不可判定（模糊/有歧义）
- Plan 步骤粒度不到文件/函数级

否决后处理：
- 打回 tech_lead 修改 plan，附否决理由
- 修改后重新走审批，最多 2 轮
- 2 轮仍未通过 → 升级到用户决策

## 审批检查清单（用户拍板前核对）
- 每一步我都看得懂吗？
- 文件路径和函数签名是否正确？
- 执行顺序是否合理？
- 有没有遗漏的文件或步骤？
- 风险点是否已标注？

**审批通过必须明确回复 `Plan Approved`**，之后才能进入 Execute。**Plan 完整回写 Spec § Plan**。

---

# Step 5) Execute（按图施工）
**做什么**：implementer 严格按 Plan 逐步执行，生成代码。tech_lead / qa 监督。

**核心原则**：
- **关闭 YOLO / 全自动模式**，绝对禁止"先斩后奏"
- implementer 只能按 Plan 执行，**不允许自由发挥**
- 每完成一步，在 Spec § Execute Log 打勾记录
- 如果 implementer 觉得"Plan 可以优化"——**拒绝**。要么按 Plan 执行，要么**回到 Plan 阶段重新审批**
- 编译错误/类型不匹配可自修；**逻辑变更必须报告**，等 tech_lead 裁决
- 同一文件只能由任务 Owner 修改；其他人只给 review 建议

---

# Step 6) Review（三角验收 + Reverse Sync）
**做什么**：对照 Spec 验收代码，确保"文档说的 = 代码做的"。

## 三角定位
Spec（预期）vs 代码（实现）vs Execute Log（过程），三方交叉验证。

## Reverse Sync（强铁律）
- 发现偏差：**先修 Spec，再修代码**
- **严禁"改代码让它通过 AC"**——这是伪造交付
- Plan-Execution Diff 必须留底：任何偏离 Plan 原轨道的变动都要说明原因
- Review 结果回写 Spec § Review Verdict；不通过回 Plan 阶段重算

## 质量闸门（不过不算完成）
tech_lead 定义并执行，至少包含：
- **格式化/静态检查**：format + lint（按仓库栈）
- **测试**：单测 + 必要的集成/端到端最小链路
- **验证分离**：dev 不写自己的验收测试，qa 独立验证（防止 self-congratulation）
- **按 AC 验证**：qa 按 Step 0 定义的 AC 逐项验证，每个 AC 独立产出 evidence：
  ```
  .verify/
  ├── AC-1/
  │   ├── result.json      # pass/fail/needs_human + 原因
  │   └── screenshot.png   # 前端截图（如适用）
  ├── AC-2/
  │   └── result.json
  └── summary.json         # 汇总
  ```
- **三档判定**：
  - ✅ PASS — 自动验证通过
  - ❌ FAIL — 自动验证失败，附原因（dev 修复后只需重跑失败的 AC）
  - ⚠️ NEEDS_HUMAN — 无法自动判定（UI 美观度、文案语气等），标注原因
- **安全**：依赖扫描/高危漏洞处置、关键输入校验覆盖
- **可观测**：关键路径日志/指标/告警最小集
- **发布**：灰度/回滚路径可用（脚本/指令明确）

按栈自动选择（仅建议）：
- Rust：`cargo fmt --check` → `cargo clippy -D warnings` → `cargo test`
- C++/ROS2：`clang-format`/`clang-tidy`（如有）→ `colcon test`/`ctest` → 运行最小 demo

---

# Step 7) 交付物清单（tech_lead 汇总）
必须输出：
- 变更摘要（做了什么/没做什么）
- 风险与回滚（明确到命令/步骤）
- 测试结果（按 AC 组织：`.verify/` evidence 目录，含逐项判定 + 截图/日志）
- 安全检查（依赖风险、权限/输入/审计）
- 运行说明（启动参数/配置/部署步骤）

可选输出：
- ADR / 设计说明
- 性能报告（基线 + 变化 + 解释）

---

# Step 8) Archive（资产沉淀，必须做）
> **遗忘 = 资产断供。** RIPER 闭环后，必须把本次 Spec 精简合并为团队长期复用资产。

tech_lead 执行归档，产出：
- `mydocs/specs/<需求名>_human.md` — **Human 视角版**：精炼方案与汇报，可供人阅读、维护与同侪 Review
- `mydocs/specs/<需求名>_llm.md` — **LLM 视角版**：萃取项目背景、数据结构、关键决策，高度浓缩为机器输入切片，**留给下次接手项目或修复 Bug 的 AI 直接恢复上下文的钥匙**
- 更新对应 `mydocs/codemap/<module>.md`（如本次改动涉及链路/依赖变更）
- 对应 `mydocs/context/` 内的一次性语料标记归档或清理

归档完成前不得进入 Step 9 收尾。

---

# Step 9) 收尾
- 确认 task list 全部 completed 或明确标注 deferred（并写原因）
- 确认 Archive 已产出
- Ask each teammate to shut down
- Clean up the team

---

# 轻量模式（team-swe-light，单点小改快车道）
**触发条件**（必须**全部**满足，任一不满足立即降级到完整模式）：
- 改动范围：单文件或单一函数
- 无接口 / 数据结构 / 权限模型变更
- 无跨项目影响
- 风险等级：低
- 无新增外部依赖

**配置**：
- Team 规模：2 agent（`implementer` + `qa`），tech_lead 由用户兼任或异步批准
- **micro-spec**：一句话目标 + 一条 AC + 一条回滚
- 省略 Step -1 Pre-Research（除非连文件都找不到）
- 省略 Step 3 Innovate（Spec 标注 `Innovate: Skipped`）
- Step 4 Plan 简化为 3-5 行清单（仍需用户 `Plan Approved`）
- Step 5 `.verify/` 只需覆盖 1 个 AC
- Step 8 Archive：micro-spec 直接归档为 `_llm.md`，可省略 `_human.md`

**升级触发点**（中途发现任一即必须停下来切回完整模式）：
- 改动扩散到第 2 个文件
- 发现需要改接口/数据/权限
- 发现跨项目影响
- security 标红

---

# 线上故障排查 SOP（DEBUG）
**触发**：线上 Bug / P0-P2 故障 / 紧急 hotfix

**操作**：
1. **三件套喂给 agent**：
   - 出事节点**日志**（关键 error/warn 行，带时间戳）
   - 报错的**直接结果**（调用栈 / 响应体 / 监控截图）
   - 最原始实现该功能的 **Spec**（`mydocs/specs/<name>.md` 或 `_llm.md`）
2. **三角定位**：agent 对比"设计预期（Spec）vs 现实表现（日志/监控）vs 实际实现（代码）"，输出定界结论与根因假设
3. **Reverse Sync 强约束**：定界后**先落 Spec 修改方案**（新增 § Fix Plan），经 tech_lead + security 审批，**再对代码打补丁**
4. **修复后必须更新**对应 `mydocs/codemap/<module>.md`（如链路/依赖有变）与 Spec § Review Verdict
5. 若本次是既有 Spec 未覆盖的盲区，Archive 阶段把教训写进 `_llm.md` 的"易错点"段，防下次踩同坑

**禁止**：不对照 Spec 就盲目抓 Bug；修完代码不回写 Spec。
