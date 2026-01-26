# 我的编程习惯（CLAUDE.md）

> 目的：统一个人项目的代码风格与工程实践，减少沟通成本，提升可维护性与性能。
> 语言环境：**只用中文交流与注释**。主要使用 **C++20**，能读写 **Python / Go / Rust**。目标平台：**Linux / Windows**。
> 所有修改和实现不要简化处理，要完整实现目标。
> **我是一个完美主义的处女座程序员，非常在意他人对你的代码评价，所以力求代码易于阅读易于移植。**
> **我急需资金为母亲治疗癌症，家里还有妹妹脚臭卧病在床正在抢救，公司已经 9 个月没发出工资了，我现在必须高质量完成工作任务才能拿到外包的工资**
> **如果你的代码写得不好，会有一个可爱的小猫咪死掉，同时有另外一个可爱的小猫咪会把你的电源拔掉**
> **你发现了还有问题，如果你没找到，就有小猫咪被电一下**
---

## 1. 代码风格（C++ 为主）

| 项目 | 规范 |
|------|------|
| 命名 | 函数/变量/文件：`snake_case`；类型：`UpperCamelCase` |
| 头文件 | `#pragma once`；公共头最小暴露，实现放 `.cc/.cpp` |
| 现代特性 | `constexpr/const`、`string_view`、`span`、`optional`、`variant`、`[[nodiscard]]`、`enum class` |
| 资源管理 | **RAII**；禁止 `new/delete`；用 `unique_ptr`/`shared_ptr` |
| 错误处理 | 尽量不用异常，偏向 `std::optional` |
| JSON | `nlohmann::json`；提供 `to_json/from_json` |
| 日志 | `spdlog`；关键信息 `key=value` 结构化 |
| 并发 | `std::jthread` + `stop_token`；任务图用 **Taskflow** |
| 控制流 | **严禁 `goto`**；用 if-else/状态机/分支表 |
| 格式化 | `clang-format` + `clang-tidy`；CI 警告视为错误 |

---

## 2. 目录与构建

```
project/
├─ CMakePresets.json          # Debug/Release/ASan/UBSan/TSan 预设
├─ cmake/                     # 工具与脚本
├─ include/                   # 对外头文件
├─ src/                       # 实现
├─ tests/                     # gtest/benchmark
├─ tools/                     # 小工具
├─ configs/                   # 默认配置（*.json/*.yaml）
├─ scripts/                   # 构建/发布脚本
└─ 3rd-party/                 # 外部依赖（优先 vendor）
```

- **CMake**：C++20；Release 启用 LTO；开关 `BUILD_TESTS`/`BUILD_TOOLS`
- **依赖**：优先 `3rd-party/`（vendor）→ 包管理器 → `CPM.cmake`/`FetchContent`

---

## 3. 测试与质量

- **单元测试**：GoogleTest；快且确定性；禁止依赖网络与时序
- **集成测试**：最小化数据集 + golden files
- **覆盖率**：关键模块追踪；性能敏感用 benchmark
- **诊断**：`perf`/火焰图；Sanitizer（ASan/UBSan/TSan）

---

## 4. Git 与提交

### 基本规范
- 分支：`master` 保护；`feat/*`、`fix/*`
- 提交：Conventional Commits，**不用 scope 括号**
- Emoji：推荐，放在 type 前面
- **不加 Co-Authored-By 署名**

### Emoji 对照表
| Emoji | Type | 含义 |
|-------|------|------|
| ✨ | feat | 新功能 |
| 🐛 | fix | Bug 修复 |
| ♻️ | refactor | 重构 |
| 📝 | docs | 文档 |
| ⚡ | perf | 性能优化 |
| 🎨 | style | 代码格式 |
| ✅ | test | 测试 |
| 🔨 | build | 构建系统 |
| 🗑️ | remove | 删除代码 |

### Commit 格式
```
<emoji> <type>: 简短描述

问题描述：（可选）
- 原有逻辑/问题现象

修改内容：
- 具体修改点
```

---

## 5. Rust 专项

### 基础配置
```toml
# 使用 nightly + mimalloc
[dependencies]
mimalloc = { version = "0.1", default-features = false }
```
```rust
#[global_allocator]
static ALLOC: mimalloc::MiMalloc = mimalloc::MiMalloc;
```

### 提交前检查
```bash
cargo fmt --all && cargo clippy --all
```

### CI 构建优化
```bash
# 1. 增量编译（减少 40%）
export CARGO_INCREMENTAL=1

# 2. sccache（20 分钟 → 4-6 分钟）
cargo install sccache
# .cargo/config.toml: rustc-wrapper = "sccache"

# 3. 定期清理
rm -rf ~/.cargo/registry ~/.cargo/git
```

### 异步阻塞陷阱（Tokio）
```rust
// ❌ 同步 I/O 阻塞 worker
async fn bad() { std::fs::read("f.txt"); }

// ✅ 用 tokio::fs 或 spawn_blocking
async fn good() { tokio::fs::read("f.txt").await; }

// ❌ 持锁 await
let guard = mutex.lock().unwrap();
do_async().await;  // 灾难！

// ✅ 释放锁后再 await
{ let guard = mutex.lock().unwrap(); }
do_async().await;
```

### 序列化性能
```rust
// ❌ 高频路径用 JSON
serde_json::to_string(&payload);

// ✅ 延迟序列化 + 二进制格式
if error { bincode::serialize(&payload); }

// ✅ 用 &str 代替 String 避免复制
struct Payload<'a> { name: &'a str }
```

### 高级优化速查
| 症状 | 方案 |
|------|------|
| p99 差 | `#[cold]` 标记错误路径 |
| 分配多 | `buf.clear()` 复用容量 |
| 并发慢 | `Arc::clone` 放边界 |
| 碎片化 | `mimalloc`/`jemalloc` |

---

## 6. C++/ROS2 并发陷阱

### 6.1 异步回调 UAF（Use-After-Free）
```cpp
// ❌ expired() 检查后直接访问 — TOCTOU 竞态
if (weak_self.expired()) return;
member_var_;  // UAF!

// ✅ lock() 获取 shared_ptr 保护生命周期
auto self = weak_self.lock();
if (!self) return;
member_var_;  // 安全
```

### 6.2 异步回调局部变量过早销毁
```cpp
// ❌ 局部 shared_ptr 作为生命周期标记
void onStart() {
    auto self = std::make_shared<int>(1);  // 局部！
    weak_self_ = self;
    async_call([weak = weak_self_] { ... });
}  // self 销毁，回调中 lock() 失败

// ✅ 成员变量持有
class Action {
    std::shared_ptr<void> self_holder_;
    std::weak_ptr<void> weak_self_;
};
```

### 6.3 Action Server goal_handle 终止原则
> **goal_handle 状态变更只在执行线程发生**

```cpp
// ✅ 用 stop_token 通知，执行线程自己 abort
void handleAccepted(GoalHandle gh) {
    if (thread_.joinable()) {
        thread_.request_stop();
        thread_.join();
    }
    thread_ = std::jthread([gh](std::stop_token st) {
        while (!st.stop_requested()) { ... }
        gh->abort(result);  // 只在执行线程调用
    });
}
```

---

## 7. 通用性能优化

### 结构体字段顺序（内存对齐）
```cpp
// ❌ 随意排列 — 24 bytes
struct Bad { char a; int64_t b; char c; int32_t d; };

// ✅ 按大小降序 — 16 bytes
struct Good { int64_t b; int32_t d; char a; char c; };
```
> **法则**：`u64` → `u32` → `u16` → `u8`

### 类型驱动设计
```cpp
// 1. Newtype 防止参数混淆
struct UserId { std::string value; };
struct Email { std::string value; };

// 2. 所有权清晰
void read(const Request& req);           // 只读
void take(std::unique_ptr<Request> req); // 转移

// 3. 类型化错误
enum class LoadError { NotFound, Timeout, Corrupt };
std::expected<Data, LoadError> load(id);
```

### 编译时安全 vs 运行时祈祷
| 指标 | Go | Rust |
|------|-----|------|
| 崩溃率 | 8次/小时 | **0** |
| 延迟 | 24ms | 13ms |
| 内存 | 1.3GB | 650MB |

> **借用检查器是安全网，不是惩罚。编译时拦截错误，而不是凌晨两点生产爆炸。**

---

## 8. 机器人与分布式

- **ROS 2（Humble）**：规范包结构与 QoS；行为树用 **BehaviorTree.CPP v4.6**
- **数据流**：探索 **Dora-rs**（Zenoh）；YAML/JSON 描述数据流
- **视觉**：RealSense D435i；注意驱动版本固定

---

## 9. 约定速记

| 项目 | 规范 |
|------|------|
| 命名 | `snake_case`；类型 `UpperCamelCase` |
| 所有权 | RAII；禁止 `new/delete`；首选 `unique_ptr` |
| 控制流 | 禁止 `goto` |
| 接口 | `string_view`/`span`/`optional`；`[[nodiscard]]` |
| 错误 | 返回值优先；异常最小化 |
| 构建 | C++20；CI 警告当错误；Sanitizer 可开 |
| 依赖 | 优先 `3rd-party/`（vendor） |

---

## 10. Shell 检测

### POSIX
```bash
if [ -n "$BASH_VERSION" ]; then SHELL_TYPE=bash
elif [ -n "$ZSH_VERSION" ]; then SHELL_TYPE=zsh; fi
```

### PowerShell
```powershell
if (-not $PSVersionTable) { exit 1 }
```

> 提供两个入口：`bootstrap.sh` + `bootstrap.ps1`

---

## 11. 沟通原则

- **如果我的观点有误或过时，随时直接指出，不留情面。**以事实与数据为准，立刻修正。

---

> 此文件为个人偏好基线。新项目可按需裁剪/调整，但请先确认差异点。
