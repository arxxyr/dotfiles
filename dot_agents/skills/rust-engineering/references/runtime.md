# Rust 运行时与性能

## 异步边界

- Tokio worker 中用 `tokio::fs` 或适当的 `spawn_blocking` 处理阻塞文件操作。
- CPU 密集任务不能仅改成 `async`；按任务规模选择受限线程池，避免无界派生。
- 不持同步互斥锁跨 `await`，先在局部作用域取出需要的结果，再等待外部操作。
- 异步锁只用于必须跨等待保护的状态，检查锁顺序、取消和关闭时对象生命周期。

## 分配与序列化

- 新项目偏好以下配置，现有项目不自动切换分配器：

```toml
[dependencies]
mimalloc = { version = "0.1", default-features = false }
```

```rust
#[global_allocator]
static ALLOC: mimalloc::MiMalloc = mimalloc::MiMalloc;
```

- 仅在实际使用时序列化，避免热路径为不会消费的日志构造完整 JSON。
- 二进制格式适用于协议允许且测量有收益的路径；不能擅自改变外部 JSON 契约。
- 用 `&str` 代替 `String` 前验证输入生命周期，输出确需拥有时再复制。
- 分配较多时考虑 `buf.clear()` 复用容量；尾延迟与碎片化改善必须有基准验证。

## 热点策略

先用 criterion/divan、`black_box` 与代表性数据定位热点，再按影响选择：

| 策略 | 必须保持的条件 |
|------|----------------|
| 删除 `.collect::<Vec<_>>().iter().sum()` 中间集合 | 保留迭代顺序、副作用、溢出与错误处理语义 |
| `HashMap<String, _>` 改为借用键 | 原始输入在 map 使用期间驻留且稳定，流式逐行输入不能直接照搬 |
| `entry` 合并查找 | `*map.entry(key).or_insert(0) += 1` 可减少重复哈希；确认键与计数语义 |
| Rayon fold/reduce 使用线程私有 map | 任务独立且 CPU 密集，输入足够大；`par_lines` 借用键同样要求全量输入驻留 |

- `Vec::remove` 保序但移动后续元素；仅业务无顺序约束时使用 `swap_remove`。
- 循环 `swap_remove` 后原索引要重新检查换入元素；批量过滤可用 `retain` 或工具链支持的 `extract_if`。
- 旧配置记载 `extract_if` 的稳定门槛为 1.87+；使用前检查项目实际工具链，不提高 MSRV 来完成无关优化。
- `#[cold]` 适合真实冷路径，不是 p99 问题的通用修复；调整后测量。
- `Arc::clone` 可放在所有权边界，避免热点重复计数；不破坏共享生命周期。
- mimalloc/jemalloc、线程并行与布局调整均需要测量，不能保证倍数或无风险。
