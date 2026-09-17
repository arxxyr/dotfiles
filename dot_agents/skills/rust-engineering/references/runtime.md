# Rust 运行时与性能

## Tokio 性能取舍

提炼自 [Principles for fast Tokio applications](https://dial9-rs.github.io/blog/principles-for-fast-tokio-applications/)（2026-09-13 发布，2026-09-15 更新），具体 API 边界按下文官方文档核对。

- 从端到端 p99、吞吐等实际目标倒查；长 poll 是线索，不等于需要修复的瓶颈。
- 延迟优先时限制单次处理量、改善公平性；吞吐优先时批量摊薄调度和线程切换成本，同时约束批量等待与内存。
- 检查共享协调点：同一 runtime 的 blocking pool、全局任务队列，以及应用的指标锁、日志和 channel；增加 worker 不一定改善竞争。
- 约束下游并发与入口积压，不能用无界派生任务代替容量规划。
- worker 被唤醒后迟迟得不到 CPU 时，检查其他进程和后台线程；确认操作系统调度竞争后再评估核心隔离。
- 较长 poll 在有空闲 worker 时可能可接受，但不能据此允许不可控阻塞。多 runtime、绑核和短时自旋是特殊优化，需回测尾延迟、吞吐与 CPU 成本；不固化原文的次数、微秒值或性能倍数。

## 异步边界

### 让出与任务粒度

- `.await` 不保证交还执行权；持续返回 `Ready` 的缓存读取或消息循环仍可能占住 worker。按测量设置单轮工作预算，再考虑协作式让出；不要给每个微小工作单元都派生独立任务。参见 [Tokio 协作调度](https://docs.rs/tokio/latest/tokio/task/coop/index.html)。
- `yield_now().await` 不保证下一次先运行其他任务，组合器也可能使让出无法传到 runtime；不能依赖具体调度顺序保证正确性。参见 [yield_now 的限制](https://docs.rs/tokio/latest/tokio/task/fn.yield_now.html#non-guarantees)。
- `join!` / `select!` 的分支在同一任务中运行；一支阻塞会阻止其他分支推进，空闲 worker 不能单独窃取这些分支。需要独立调度时再拆任务，并明确取消与完成回收。参见 [join!](https://docs.rs/tokio/latest/tokio/macro.join.html#runtime-characteristics) 与 [select!](https://docs.rs/tokio/latest/tokio/macro.select.html#runtime-characteristics)。

### 阻塞操作与背压

- Tokio worker 不直接执行阻塞文件操作。`tokio::fs` 的常规实现借助 blocking pool，不代表没有线程切换成本；密集小操作先评估缓冲，或将相关同步操作合并到一次有界 `spawn_blocking`，同时保留内存上限和取消响应。参见 [文件 I/O 调优](https://docs.rs/tokio/latest/tokio/fs/index.html#tuning-your-file-io)。
- CPU 密集任务不能仅改成 `async`；按规模选择受限计算池。`spawn_blocking` 的线程上限不等于业务并发或排队上限，持续运行的阻塞循环宜放专用线程。参见 [spawn_blocking](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html)。
- 工程约束：使用信号量时，在提交阻塞工作前获取许可，并让闭包持有到工作真正结束；入口还需有界队列或受限生产者，避免大量任务只为等待许可而驻留。参见 [Semaphore 的派生前限流示例](https://docs.rs/tokio/latest/tokio/sync/struct.Semaphore.html#limit-the-number-of-outgoing-requests-being-sent-at-the-same-time)。
- 已开始的 `spawn_blocking` 闭包不能靠 `abort` 或 runtime 关闭超时停止；调用方超时后工作可能继续，必须设计协作退出、资源释放和重复执行语义。参见 [取消与关闭限制](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html)。

### 锁与共享状态

- 短小、低竞争、不跨 `.await` 的纯数据临界区可用同步 Mutex；不持同步锁跨等待。需要跨 `.await` 保护共享 I/O 资源时评估异步 Mutex，检查锁顺序、取消及持锁 future 的生命周期；不用固定毫秒门槛选型。参见 [Mutex 选型](https://docs.rs/tokio/latest/tokio/sync/struct.Mutex.html#which-kind-of-mutex-should-you-use)。
- 锁内只更新或提取必要数据，flush、I/O 和重计算移到锁外；快照复制也要计入持锁成本，并确认允许陈旧读取。竞争明显时考虑单任务拥有状态与消息传递，同时测量 channel 的背压及串行瓶颈。参见 [Tokio 共享状态](https://tokio.rs/tokio/tutorial/shared-state) 与 [消息传递](https://tokio.rs/tokio/tutorial/channels)。
- `RwLock` 不一概禁用，也不因读多就默认更快；测量读写比例、竞争和持锁时间。Tokio `RwLock` 偏向写者，排队写者可阻挡后来的读者。参见 [RwLock 公平策略](https://docs.rs/tokio/latest/tokio/sync/struct.RwLock.html)。

### 调度证据

- 区分 poll 执行时长、任务就绪到实际 poll 的调度等待，以及操作系统让 worker 等待 CPU 的时间；结合队列深度、锁等待和火焰图解释端到端指标，不把单项直方图当作根因。参见 [RuntimeMetrics](https://docs.rs/tokio/latest/tokio/runtime/struct.RuntimeMetrics.html)。
- 采集 schedule latency histogram 前核对锁定的 Tokio 版本、`schedule-latency` feature、`tokio_unstable` 和目标平台条件，并在 Builder 显式启用；测量自身有成本，不为普通修改默认开启实验能力。参见 [直方图配置](https://docs.rs/tokio/latest/tokio/runtime/struct.Builder.html#method.enable_metrics_schedule_latency_histogram)；此处于 2026-09-17 按 Tokio 1.53.1 核对，后续版本重新确认。

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
