# 下一代 trait solver canary

仅在用户要求体检，或复杂 trait 代码确需验证兼容性时使用。
先检查 nightly 版本和 `-Znext-solver=globally` 是否仍可用，不凭历史年度计划判断当前稳定状态。

## 范围与隔离

- 保持默认构建与主 CI 不变；新增 canary 使用 `continue-on-error: true`，不阻塞主链路。
- 保留项目已有 RUSTFLAGS，并追加求解器实验开关，避免丢掉 target/feature 的必要配置。
- 在独立 `CARGO_TARGET_DIR` 运行实验；不要为了干净对照清空活跃 `target/`。
- 比较使用相同工具链、代码、feature 和依赖；先确保基线本来就能构建。
- 当求解器已成为当前工具链默认值或选项已移除时，按官方能力调整体检方式，不机械追加旧命令。

## 体检命令

以下展示核心命令；执行时先选定实际工具链、追加已有编译参数，并指定独立产物目录：

```sh
RUSTFLAGS="${RUSTFLAGS:+$RUSTFLAGS }-Znext-solver=globally" cargo +nightly check --workspace --all-targets
RUSTFLAGS="${RUSTFLAGS:+$RUSTFLAGS }-Znext-solver=globally" cargo +nightly test --workspace --all-targets --no-run
```

有项目级 `build.rustflags` 或编码参数时，应保留其实际编译效果；环境 RUSTFLAGS 可能覆盖配置文件。
CI 使用已有 checkout 与 nightly 安装步骤，固定项目要求的依赖；不为 canary 无关升级 Actions。

## 关注信号

- GAT、关联类型、RPIT/RPITIT、深层 blanket impl、递归约束与高阶生命周期组合。
- 同一程序在基线与实验中接受/拒绝差异，以及诊断是否集中在同类 trait 模式。
- 少数文件的 IDE 悬停、补全和诊断是否可复现变慢。
- 用独立干净产物目录比较构建时间，不能把冷/热缓存差异当成回归。

遇到差异先收窄到单 crate，再缩成可独立执行的最小复现；报告两边版本、命令和错误。
不要用更改默认工具链或直接关闭 nightly 掩盖尚未定位的问题。
