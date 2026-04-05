---
name: rust-ffi
description: Rust 与 C/C++ 互操作规范。当项目需要渐进式从 C 迁移到 Rust、或 Rust 需要调用现有 C 库时使用。包含 FFI 三明治架构、跨边界类型规范、内存管理铁律、双路对比迁移四步法、以及可观测 FFI（tracing/metrics/报警）。
---

# Rust FFI 三明治（渐进式 C → Rust 迁移）

> **核心思路**：不搞大爆炸式重写。用 Rust 安全层包住现有 C 代码，一个函数一个函数地迁移，生产环境照常跑。

**三层架构：**
```
Rust 应用层（安全，无裸指针）
        ↓
FFI 垫片层（unsafe 但极薄，只做类型转换）
        ↓
C 库层（久经考验，正在赚钱）
```

## 1. 调用方向：每个子系统只选一个

| 方向 | 场景 | 说明 |
|------|------|------|
| Rust 调 C | C 库算法成熟，只想加安全壳 | 用 `bindgen` 生成 Rust 绑定 |
| C 调 Rust | 用 Rust 写新模块，C 程序需要调用 | 用 `cbindgen` 生成 C 头文件 |

> **禁止双向互调**。一个子系统选定方向后不要混用。

## 2. 跨边界类型规范

| 允许通过 | 禁止通过 |
|----------|----------|
| `*const T`、`*mut T` | `String`、`Vec`、`Option`（C 不认识布局） |
| 固定宽度整数：`i32`、`u64`、`usize` | `panic`（不能穿越 FFI 边界） |
| `#[repr(C)]` 结构体 | Rust 的 `drop` 语义 |
| `(指针, 长度)` 缓冲区组合 | 闭包（用函数指针 + `void*` 上下文替代） |
| 整数错误码（0 成功，负数失败） | `Result`、`enum`（非 `#[repr(C)]`） |

## 3. 安全写法模式：出参 + 状态码

```rust
use std::os::raw::c_int;

#[repr(C)]
pub struct FfiResult {
    pub code: c_int,  // 0 = 成功, <0 = 错误
}

#[no_mangle]
pub extern "C" fn rs_sum_u32(
    input: *const u32,
    len: usize,
    out: *mut u64,
) -> FfiResult {
    // 1. 检查输入：空指针直接拒绝
    if input.is_null() || out.is_null() {
        return FfiResult { code: -1 };
    }

    // 2. unsafe 块尽量小，像手术刀一样精准
    // Safety: 调用方保证 input 指向 len 个 u32，out 是有效的
    let slice = unsafe { std::slice::from_raw_parts(input, len) };
    let sum: u64 = slice.iter().map(|&x| x as u64).sum();
    unsafe { *out = sum; }

    // 3. 返回状态码，不用异常不用 panic
    FfiResult { code: 0 }
}
```

**四条铁律：**
1. **检查输入**：空指针、非法长度，入口就拦
2. **返回状态码**：`0` 成功，负数错误，`extern "C"` 两边都懂
3. **通过出参写结果**：不在 FFI 层分配内存
4. **`unsafe` 块最小化**：只包裹真正需要的语句

## 4. 内存管理：谁分配谁释放

```rust
// ❌ Rust 分配、C 释放 — 分配器不同，必炸
let ptr = Box::into_raw(Box::new(data));
// C 端: free(ptr);  // 灾难！

// ✅ Rust 分配 → 必须提供配套的 Rust 释放函数
#[no_mangle]
pub extern "C" fn rs_create_buffer(size: usize) -> *mut u8 {
    let mut buf = Vec::with_capacity(size);
    let ptr = buf.as_mut_ptr();
    std::mem::forget(buf);
    ptr
}

#[no_mangle]
pub extern "C" fn rs_free_buffer(ptr: *mut u8, size: usize) {
    if !ptr.is_null() {
        unsafe { let _ = Vec::from_raw_parts(ptr, 0, size); }
    }
}
```

| 规则 | 说明 |
|------|------|
| Rust 分配 → Rust 释放 | 提供 `rs_free_*` 配套函数 |
| C 分配 → C 释放 | 不要在 Rust 侧 `drop` |
| 禁止跨 FFI 传线程共享缓冲区 | 两边运行时对线程理解不同 |
| 回调用 C 风格 | 函数指针 + `void*` 上下文，不用闭包 |

## 5. 构建配置

**Rust 调 C：**
```toml
# Cargo.toml
[lib]
crate-type = ["cdylib"]  # 动态库，或 ["staticlib"] 静态库
```
```rust
// build.rs
fn main() {
    println!("cargo:rustc-link-lib=你的C库名");
}
```

**C 调 Rust：** 用 `cbindgen` 从 Rust 代码自动生成 `.h` 头文件，C/C++ 项目正常链接。

## 6. FFI 测试：双通道对比

```bash
# 同一批输入（边界值、大输入、奇葩 locale），两边跑，比输出
./c_test_harness < test_corpus.bin > c_output.txt
./rust_test_harness < test_corpus.bin > rust_output.txt
diff c_output.txt rust_output.txt
```

- 浮点数比较约定精度容差：`assert!((a - b).abs() < 1e-9)`
- `cargo-fuzz` 加入夜间 CI，随机输入轰炸两边接口

## 7. FFI 性能要点

| 原则 | 做法 |
|------|------|
| 批量处理 | 传 `(指针, 长度)` 一次处理上千条，别一条一条调 |
| 热循环单语言 | 算法在 C 或 Rust 内部完成，别跨边界循环 |
| 不在 FFI 层分配 | 引擎层分配好再传过去 |
| 性能目标 | 热路径 p95 延迟 ±3% 以内 |

> 瓶颈在**跨边界调用次数**，不在语言本身。用 `perf`/VTune 分析时重点看调用次数。

## 8. 渐进式迁移四步法

| 步骤 | 操作 | 要点 |
|------|------|------|
| 1. 包一层 | 选最危险的 C 接口，Rust 加安全入口 + 输入校验 | 灰度 10% 流量 |
| 2. 双跑对比 | C 原路径与 FFI 路径同时跑，比对输出 | 跑满一周，有差异就修 |
| 3. 搬逻辑 | 三明治内部用 Rust 重写一段 C 逻辑 | 保留 C 回退路径 |
| 4. 重复 | 下一个危险接口，重复 1-3 | 按**接口面积**迁移，不是代码行数 |

**度量指标：**
| 指标 | 目标 |
|------|------|
| 崩溃率 | FFI 边界引起的段错误/panic 归零 |
| 热路径 p95 | 前后对比 ±3% |
| bug 类别 | 跟踪"消灭了哪类 bug"（输入校验类、生命周期类） |
| 迁移节奏 | 每 sprint 包一个接口，每两个 sprint 搬一块逻辑 |

## 9. 安全增益速查

即使底层仍是 C，Rust 壳层也能拦截：

| 风险 | Rust 层防御 |
|------|------------|
| 缓冲区溢出 | 入口校验 `(指针, 长度)` 配对，拒绝离谱长度 |
| 栈溢出 / 死循环 | API 层限制递归深度和迭代上限 |
| 非法字符串 | 先当 `&[u8]` 处理，显式验证 UTF-8 后再传给 C |
| 空指针解引用 | 所有 `null` 和非法枚举值在入口拦截 |

## 10. 可观测 FFI：日志 + 指标 + 报警

> 三明治解决"怎么安全地迁移"，可观测层解决"迁移过程中出了事怎么知道"。

**升级后的架构：**
```
Rust 应用层（安全）
        ↓
  ┌─ 观测层（tracing span + metrics + guard）
  │     ↓
  │  FFI 垫片层（unsafe，极薄）
  │     ↓
  │  C 库层
  └─ 观测层（记录耗时、校验输出、对比结果）
```

> 观测层**不碰 `unsafe`、不改 FFI 签名**，装上拆下不影响三明治本体。

### 观测包装器

```rust
use tracing::{info_span, warn};
use std::time::Instant;

/// 给任意 FFI 函数加探针，调用方无感知
#[inline]
fn observed_ffi_call<F, R>(func_name: &'static str, f: F) -> R
where
    F: FnOnce() -> R,
{
    let _span = info_span!("ffi_call", func = func_name).entered();
    let start = Instant::now();
    let result = f();
    let elapsed = start.elapsed();

    tracing::debug!(func = func_name, elapsed_us = elapsed.as_micros() as u64, "ffi 调用完成");
    if elapsed.as_millis() > 50 {
        warn!(func = func_name, elapsed_ms = elapsed.as_millis() as u64, "ffi 慢调用");
    }
    result
}

// 使用：一行包住原始 FFI 函数体
#[no_mangle]
pub extern "C" fn rs_sum_u32(input: *const u32, len: usize, out: *mut u64) -> FfiResult {
    observed_ffi_call("rs_sum_u32", || {
        // 原始逻辑不动...
    })
}
```

### 四类核心指标（`metrics` crate，Prometheus 兼容）

| 指标 | 类型 | 用途 |
|------|------|------|
| `ffi_calls_total{func, status}` | Counter | 每个函数调用次数、成功/失败比 |
| `ffi_duration_us{func}` | Histogram | 调用耗时分布，看 p50/p95/p99 |
| `ffi_rejected_total{func, reason}` | Counter | 入口校验拦截数（空指针、非法长度） |
| `ffi_alloc_bytes_total{func}` | Counter | 跨边界内存分配量，`alloc - free` 差值 = 泄漏 |

```rust
use metrics::{counter, histogram};

fn record_ffi_success(func: &'static str, elapsed_us: u64) {
    counter!("ffi_calls_total", "func" => func, "status" => "ok").increment(1);
    histogram!("ffi_duration_us", "func" => func).record(elapsed_us as f64);
}

fn record_ffi_error(func: &'static str, code: i32) {
    counter!("ffi_calls_total", "func" => func, "status" => "error").increment(1);
    counter!("ffi_errors_total", "func" => func, "code" => code.to_string()).increment(1);
}

fn record_ffi_rejected(func: &'static str, reason: &'static str) {
    counter!("ffi_rejected_total", "func" => func, "reason" => reason).increment(1);
}
```

### 双路对比（迁移期专用）

同一输入跑 C 和 Rust 两条路，自动对比输出。生产用 C 结果，Rust 仅用于验证：

```rust
/// feature 开关控制，稳定后关闭，零运行时开销
#[cfg(feature = "dual_run")]
fn dual_path_compare<T: PartialEq + std::fmt::Debug>(
    func: &'static str,
    c_result: &T,
    rust_result: &T,
) {
    if c_result != rust_result {
        tracing::error!(func, c = ?c_result, rust = ?rust_result, "双路对比不一致");
        counter!("ffi_divergence_total", "func" => func).increment(1);
    }
}
```

### 采样策略：高频调用别全记

```rust
use std::sync::atomic::{AtomicU64, Ordering};

static CALL_SEQ: AtomicU64 = AtomicU64::new(0);

fn should_log_detail(sampling_rate: u64) -> bool {
    CALL_SEQ.fetch_add(1, Ordering::Relaxed) % sampling_rate == 0
}
```

| 层级 | 采样率 | 说明 |
|------|--------|------|
| Metrics（Counter/Histogram） | **100%** | 全量，原子操作开销极低 |
| 日志（正常调用） | **1/1000** | 采样，只记代表性的 |
| 日志（错误/慢调用） | **100%** | 全量，每次出事都要有据可查 |
| 双路对比 | **100%** → **1/100** | 初期全量，确认一致后降采样 |

### 报警规则

| 条件 | 级别 | 动作 |
|------|------|------|
| `ffi_divergence_total` > 0 | **P1** | 双路结果不一致，立即回滚到 C 路径 |
| `ffi_errors_total` 5 分钟增长 > 历史 3 倍 | **P2** | FFI 层错误激增，检查最近部署 |
| `ffi_duration_us` p95 偏移 > ±10% | **P3** | 性能回退，排查调用次数变化 |
| `alloc_bytes - free_bytes` 持续增长 | **P2** | 内存泄漏，检查 `free_*` 是否被调用 |
| `ffi_rejected_total` 突增 | **P3** | 上游传非法输入，协调调用方修复 |

### 迁移时间线（结合可观测性）

| 阶段 | 动作 | 观测重点 |
|------|------|---------|
| 第 1 周 | 部署观测层，只记录不改逻辑 | 建立基线：正常调用量、耗时分布、错误率 |
| 第 2-3 周 | 包第一个危险接口，打开 `dual_run` | `ffi_divergence_total` 是否为 0 |
| 第 4 周 | 双路一致后，切 10% 流量到 Rust 路径 | p95 延迟和错误率是否稳定 |
| 第 5 周 | 全量切换，关闭 C 路径和 `dual_run` | 保留观测层持续监控 |
| 循环 | 下一个接口，重复以上 | 每轮迭代都有数据兜底 |

> 每一步的决策依据是**指标**，不是"我觉得没问题"。
