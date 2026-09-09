# Cargo 构建

## 工具链能力与版本记录

本参考从个人旧配置迁移。旧配置记录的版本门槛为：Cargo 自动 GC 为 1.88+、
`--timings` 的 SVG 渲染为 1.95+、`build.warnings` 为 1.97+。
应用这些版本相关功能前，读取项目的 `cargo --version`、工具链固定值及对应版本官方文档，
并用实际行为验证；不据此自动升级 MSRV，也不把旧版本忽略未知配置当作验证成功。

## 缓存分工

| 场景 | 默认选择 |
|------|----------|
| 本地开发 | 保留 Cargo 增量编译，不同时配 sccache |
| CI | 需要 sccache 时设 `CARGO_INCREMENTAL=0`，使用项目既定安装与缓存机制 |

- sccache 不缓存增量编译单元；不要同时开启以期待叠加收益。
- `rustc-wrapper = "sccache"` 限定在需要它的环境，避免破坏未安装工具的本机构建。
- 不保证特定耗时倍数；比较冷/热缓存、命中率与实际 CI 时间。
- 保留 Cargo 全局 registry/git 缓存，使用工具链支持的自动 GC；禁止整目录清空 `~/.cargo/registry`。
- 项目 `target/` 优先用 cargo-sweep 的旧工具链或时间策略，先解析用户授权的具体项目路径。
- `cargo sweep --installed` 适合工具链更新后的旧产物，`--time 30` 可用于长期未使用产物；按已安装版本帮助确认参数。
- 不一刀切 `cargo clean` 活跃项目，不把整个家目录作为清理目标。

## 警告与 CI

确认支持 `build.warnings` 后，优先用 Cargo 层配置，避免把全局 `-D warnings` 写进 RUSTFLAGS：

```toml
[build]
warnings = "deny"
```

- `warn/allow/deny` 是全局诊断处理偏好；分 lint 渐进策略继续使用 `[lints]`。
- `CARGO_BUILD_WARNINGS=deny` 用于 CI 的 test/build，`cargo build --keep-going` 可汇总失败诊断。
- 本机临时恢复提示可用 `CARGO_BUILD_WARNINGS=warn`；确认环境变量优先级与当前 Cargo 行为。
- 不通过修改 `RUSTFLAGS` 来区分日常本机与 CI 的警告等级，避免不同指纹反复使缓存失效。
- Clippy 的 `-- -D warnings` 保持不变，按 fmt → clippy → test → build 严格串行验证。
- Cargo 警告处理与链接器/codegen 诊断不同；不能承诺拦截所有非 lint 警告。
- registry/git 依赖通常由 Cargo 的 `--cap-lints allow` 静音；workspace 和 path 依赖（含作为 path 的 vendor）仍在本地 lint 范围。
- 工具链不支持时保留有效的已有 CI 策略，明确兼容边界，不提交一个实际无效的“零警告”开关。

## 构建耗时

新增依赖、开启 feature、替换底层库或改 workspace/build.rs 时运行一次：

```sh
cargo build --workspace --all-targets --timings
cargo tree -d
```

- 查看 `target/cargo-timings/cargo-timing.html` 及历史报告；以实际工具链产物确认渲染格式。
- 相关 PR 附 timing 报告；CI 主分支定期留存 `target/cargo-timings/*.html` 作为趋势基线。
- 先找阻塞最多后续 unit 的关键路径，再检查重复版本、build.rs、外部 C/C++ 编译、bindgen 与系统探测。
- active 表示执行中，waiting 表示等待调度槽位，inactive 表示依赖未就绪；结合报告版本实际标签解释。
- build.rs 优化关注生成结果复用、默认 feature 收敛和外部工具版本固定。
- crate 拆分以减少高频改动的重编译为准，不以 crate 数量作为优化目标。
- Cargo timings 不能替代 rustc 内部阶段分析或运行时火焰图。
