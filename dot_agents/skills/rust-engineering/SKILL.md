---
name: rust-engineering
description: Rust 项目的实现、Cargo 构建、Tokio 和性能约定；适用于修改 Rust 代码或构建配置，版本相关功能先核实实际工具链能力。
---

# Rust 工程

保持现有项目的工具链、分配器和发布协议；新项目偏好 nightly 与 mimalloc。
只读取任务涉及的参考，不把构建实验或性能优化作为普通修改的必经步骤。

## 范围与实现

- 先读 workspace、`rust-toolchain.toml`、MSRV、Cargo 配置和 CI；项目约定优先。
- 新项目考虑 `mimalloc = { version = "0.1", default-features = false }` 与全局分配器声明。
- 现有项目不因个人偏好改 nightly 或分配器，先验证目标平台和互操作要求。
- 多分支判断优先 `match`；枚举、行为分发和类型区分使用 `match`。
- 接口明确拥有与借用；不要为了减少分配引入失效引用或不必要的全量驻留。
- 异步 worker 不执行阻塞 I/O，使用异步 API 或适当的 `spawn_blocking`。
- 不持同步锁跨 `await`；锁保护的数据先在局部作用域内处理。
- 优化先定位热点，保留业务排序、序列化与并发语义。

## 提交与 CI

- 在 Rust 项目中，每次提交前依次执行以下命令，全部零警告后才能提交：

```sh
cargo fmt --all &&
    cargo clippy --all --all-targets -- -D warnings
```

- CI 顺序为 fmt → clippy → test → build，前一步失败即停止；沿用项目对应的目标与 feature 矩阵。
- `test/build` 的 Cargo 警告拦截仅在实际工具链支持后配置，详见构建参考。
- 本规则不要求在非 Rust 仓库执行 Cargo；普通诊断和测试不需要工单初始化。

## 按需参考

- 调整缓存、CI、警告配置、依赖或分析构建耗时：读取 [Cargo 构建](references/build.md)。
- 调整异步、序列化、集合、分配或并行热点：读取 [运行时与性能](references/runtime.md)。
- 检查复杂 trait、GAT、关联类型的下一代求解器差异：读取 [求解器 canary](references/next-solver.md)。
- Rust/C/C++ 边界可用 `rust-ffi`，Bevy ECS 可用 `bevy-ecs`；仅在涉及对应领域时加载。
- 版本产物与发布任务可用 `release-engineering`；技术实现不隐含发布授权。

## 交付证据

- 说明行为变化、执行的检查和未完成验证；性能结论给出基线与可复现条件。
- Cargo 和 nightly 选项可能变化，先核实版本、帮助或对应官方文档，不能把配置被接受等同功能已生效。
- 不用更新工具链、删缓存或修改测试预期掩盖未经定位的问题。
