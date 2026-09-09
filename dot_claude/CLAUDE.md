# 我的编程习惯（CLAUDE.md）

个人工程偏好基线；只加载当前任务需要的专项技能与参考资料。
主要使用 C++20，也使用 Python / Go / Rust；目标平台优先 Linux / Windows。

## 沟通与交付

- 只用中文交流与注释，每次回答以「爸爸」开头。
- 观点有误或过时直接指出，以事实与验证结果为准。
- 完整实现已授权目标，重视可读性、可移植性和维护成本，不用占位实现交付。
- 简短说明关键选择、验证结果和未解决问题；不把未执行的检查说成通过。
- 按任务风险选择流程，不因文件数量、固定角色或仪式化审批扩大工作。
- 已有授权持续有效；正常实现步骤直接推进，范围外发布、删除或外部写入不从技能推定授权。
- 明确用户要求优先；已有项目工具链、兼容性和发布协议优先于个人新项目默认值。
- 遇到实质冲突先说明影响；有足够上下文时自行解决常规选择。

## 代码与质量

- C++ 函数、变量和文件用 `snake_case`，类型用 `UpperCamelCase`；保留已有公共接口兼容性。
- C++ 默认 C++20；公共头最小暴露，使用 `#pragma once`，实现放 `.cc/.cpp`。
- 资源用 RAII 管理；禁止裸 `new/delete`，使用智能指针；严禁 `goto`。
- 优先 `const/constexpr`、`string_view`、`span`、`optional`、`variant`、`[[nodiscard]]` 和 `enum class`。
- 用独立类型表达标识、所有权和错误；尽量不用异常，仅有“缺失”语义时用 `optional`。
- `std::expected` 需要 C++23；C++20 项目使用现有结果类型或 `variant`，不擅自升级标准。
- 保留用户已有修改，不覆盖无关改动；先阅读项目约定，再调整代码。
- 测试应快且确定；单元测试不依赖网络或脆弱时序，集成测试使用最小数据与 golden files。
- 按修改风险完成必要检查；关键模块关注覆盖率，性能优化先测量再改动。
- 不把特定基准的性能倍数当成保证；保持业务语义、对象生命周期和 ABI 约束。

## Git 与提交

- 保护 `master`；新功能用 `feat/*`，修复用 `fix/*`，尊重已有分支策略。
- 使用 Conventional Commits，不用 scope 括号，不加 `Co-Authored-By` 署名。
- 推荐格式：`<emoji> <type>: 简短中文描述`；正文按需写问题和具体修改。
- 类型参考：✨ feat、🐛 fix、♻️ refactor、📝 docs、⚡ perf、🎨 style、✅ test、🔨 build、🗑️ remove。
- 在 Rust 项目中，每次提交前必须先执行 `cargo fmt --all`，再执行 `cargo clippy --all --all-targets -- -D warnings`，零警告后提交。
- 非 Rust 项目执行自身适用检查；不因通用提交规则运行无关 Cargo 命令。
- 不把其他人的改动夹带进提交；提交、推送和发布依用户当前任务及已有授权执行。

## 版本语义

- 版本在项目唯一权威来源定义，遵守 SemVer；新建多模块应用默认共享版本，保留既有独立发布协议。
- 用户指定目标版本时直接使用该版本，不自行替换。
- “小版本”/“bump patch”/“补丁号加一”统一表示 `PATCH + 1`，包括 `0.x` 项目。
- “bump minor”/“次版本号加一”表示 `MINOR + 1` 并清零 PATCH。
- “bump major”/“主版本号加一”表示 `MAJOR + 1` 并清零 MINOR/PATCH。
- 未指定级别且仅为兼容修复、解析修复或 CI/构建修正时默认 PATCH；其他改动按实际发布范围判断。
- 执行前读取权威版本，简短说明“当前版本 → 目标版本”。
- 同步应用锁文件版本和当前发布示例，不改第三方依赖、历史记录或固定测试样例的版本。
- 产物命名、打包和 CI 规则按需读取 `release-engineering`。

## Python 工具链

- 默认使用 `uv` 管理解释器、隔离环境、依赖与命令；复用现有项目版本，不擅自迁移工具链。
- 新项目用 `pyproject.toml` 声明依赖并提交 `uv.lock`；不手改锁文件。
- 依赖使用 `uv add` / `uv remove`，开发依赖用 `uv add --dev`，环境同步用 `uv sync`。
- 项目脚本、测试和工具用 `uv run`；不默认用裸 `python` / `pip` / `pytest` 或要求手动激活环境。
- CI 与锁定复现用 `uv sync --locked`、`uv run --locked ...`，验证时不静默更新锁文件。
- 独立临时 CLI 用 `uvx`；依赖项目环境的工具仍用 `uv run`。
- 单文件脚本需要第三方依赖时用 `uv add --script` 写入 PEP 723 元数据，再用 `uv run` 执行。
- 非 Python 项目的一次性检查可用 `uv run --no-project python ...`，不为此创建项目配置。
- 已有 `requirements.txt` 项目复用隔离环境，缺失时用 `uv venv`，依赖用 `uv pip install -r requirements.txt`。
- 不向系统 Python 安装依赖，不用 `sudo pip` 或 `uv pip install --system`。
- `uv` 缺失时按项目约定处理，不默默改用全局 `pip`。

## Dotfiles 与密钥

- 所有 dotfiles（包括本文件）由 chezmoi 管理，源仓库为 `~/.local/share/chezmoi`。
- 严禁直接改已纳管目标文件；先用 `chezmoi source-path <目标文件>` 定位并修改源文件。
- 流程：改源文件 → `chezmoi diff <目标文件>` 预览 → `chezmoi apply <目标文件>` 定向应用 → 提交源仓库。
- 只应用本次相关目标，避免覆盖其他漂移；新文件用 `chezmoi add <目标文件>` 纳管。
- 机器差异使用 `*.tmpl` 与 `.chezmoidata`，不复制多套配置。
- 真实密钥和令牌禁止明文入库；使用 `encrypted_` 的 age/gpg 加密或密码管理器模板。
- `private_` 只控制文件权限，不加密内容，不能用于保护公开仓库中的密钥。
- 客户端发现机制、符号链接、技能恢复和工具备忘按需读取 `dotfiles-maintenance`。

## 专项规则按需加载

- C++ 代码、CMake、并发与性能：`cpp-engineering`。
- Rust 代码、Cargo、Tokio 与性能：`rust-engineering`；nightly 和 mimalloc 是新项目偏好，不强迁现有项目。
- 跨语言打包、版本产物、部署和 CI：`release-engineering`。
- Rust/C/C++ 边界：`rust-ffi`；ROS 2 / C++ 机器人并发：`ros2-cpp`；Bevy / Archetype ECS：`bevy-ecs`。
- 设计评审：`design-review`，存在领域文档时再加载相应参考流程。
- PRD 或拆工单：`planning`，是否发布到工单系统由任务授权决定。
- `setup-matt-pocock-skills` 仅在需要工单集成且项目缺少配置时运行，普通诊断、测试不以它为前置。
- 仅在用户明确调用 `team-swe` 时加载它；普通任务按实际需要协作，不自动进入该技能流程。
- 技能只加载相关参考文件；系统和插件提供的技能由所属组件维护，不复制另一份到个人目录。
