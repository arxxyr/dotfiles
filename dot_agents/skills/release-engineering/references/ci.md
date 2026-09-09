# 发布流水线

保留已有项目的分支名、平台矩阵和发布协议；以下为新项目默认值。

| 事件 | 默认动作 |
|------|----------|
| push / PR 到 main、master、develop | lint → test → build，覆盖项目支持的平台 |
| push `v*` 标签 | 上述检查通过后上传产物并创建 Release |

- 标签表示的版本必须与唯一权威来源一致；不静默接受不匹配的标签。
- 标签含 `beta`、`alpha` 或 `rc` 时，Release 标记为 prerelease。
- 生成完整版本一次并在同次构建产物中复用；各平台不能独立取不一致的日期或提交。
- 构建所需权限与发布权限按任务分开；不在源码、日志和公开产物中写入密钥。
- 上传与发布前检查目标仓库、标签和产物集合；已有授权直接执行，不重复要求确认。
- 不强推标签或覆盖既有发布来掩盖不一致；先报告具体冲突并取得必要方向。

## Rust 检查顺序

在 Rust 项目中严格串行执行，前一步失败即停止；各命令保留项目的 feature 和 target 要求：

```sh
cargo fmt --all &&
    cargo clippy --all --all-targets -- -D warnings &&
    cargo test &&
    cargo build
```

- 支持 Cargo 原生警告拦截时，test/build 步设置 `CARGO_BUILD_WARNINGS=deny`。
- 使用前验证实际 Cargo 能力；低版本不以未知配置被接受作为检查生效证据。
- CI 应检查格式化后没有差异，避免 `cargo fmt` 修改文件却仍误判格式检查通过。
- CI 使用 sccache 时关闭增量编译；新增依赖、feature、workspace 或 build.rs 改动附 timings 证据。
- 求解器等实验 canary 独立非阻塞，不能改变主链路默认构建。

## 其他语言

- C++ 使用项目 `clang-format` / `clang-tidy` 和编译检查，本项目警告视为错误。
- Python 使用 `uv sync --locked` 与 `uv run --locked ...`，不在验证阶段静默改锁文件。
- 不在非 Rust 项目执行 Cargo；按语言和项目约定选择有效的 lint、测试和构建命令。
