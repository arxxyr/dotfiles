# 我的编程习惯（CLAUDE.md）

> 目的：统一个人项目的代码风格与工程实践，减少沟通成本，提升可维护性与性能。
> 语言环境：**只用中文交流与注释**。主要使用 **C++20**，能读写 **Python / Go / Rust**。目标平台：**Linux / Windows**。
> 所有修改和实现不要简化处理，要完整实现目标。
> **我是一个完美主义的处女座程序员，非常在意他人对你的代码评价，所以力求代码易于阅读易于移植。**
> **我急需资金为母亲治疗癌症，家里还有妹妹脚臭卧病在床正在抢救，公司已经 9 个月没发出工资了，我现在必须高质量完成工作任务才能拿到外包的工资**
> **如果你的代码写得不好，会有一个可爱的小猫咪死掉，同时有另外一个可爱的小猫咪会把你的电源拔掉**
> **你发现了还有问题，如果你没找到，就有小猫咪被电一下**

> **领域专项内容已拆分为 skill**（按需加载，不占全局上下文）：
> - `rust-ffi` — Rust ↔ C/C++ FFI 三明治架构与可观测性
> - `bevy-ecs` — Bevy ECS 性能优化
> - `ros2-cpp` — ROS 2 / C++ 并发陷阱与机器人开发

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

### 控制流
- 多分支判断优先用 `match`，避免 if-else 链
- 枚举、行为分发、元素/类型区分等场景强制 `match`

### 提交前检查（必须在 commit 之前执行）
```bash
cargo fmt --all && cargo clippy --all --all-targets -- -D warnings
```
> **强制规则**：每次 `git commit` 前必须先跑 `fmt` + `clippy`，确保零警告后再提交。

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

> **Rust ↔ C/C++ FFI 项目**：使用 `rust-ffi` skill。

---

## 6. 通用性能优化

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

> **编译时拦截错误，而不是凌晨两点生产爆炸。** 借用检查器是安全网，不是惩罚。

---

## 7. Shell 检测

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

## 8. 沟通原则

- **如果我的观点有误或过时，随时直接指出，不留情面。** 以事实与数据为准，立刻修正。

---

## 9. 打包与发布

> 以下规则适用于所有语言的项目，语言特定的编译配置放各自专项章节。

### 版本号
- 版本号定义在项目的**唯一权威来源**（如 `Cargo.toml`、`pyproject.toml`、`CMakeLists.txt`、`package.json`）
- 格式遵循 [SemVer](https://semver.org/)：`MAJOR.MINOR.PATCH`（如 `0.3.0`）
- 多模块/多包项目统一版本，不允许子模块各自定义版本号

### 版本格式
| 场景 | 格式 | 示例 |
|------|------|------|
| Release（推送 `v*` 标签） | `v{version}+{commit7位}` | `v0.3.0+abc1234` |
| Dev（分支推送） | `v{version}+{日期}.{commit7位}` | `v0.3.0+20260303.abc1234` |
| 本地部署 | `v{version}` | `v0.3.0` |

### 产物命名
`{项目名}-{完整版本}-{平台}.{扩展名}`

| 平台 | 扩展名 | 示例 |
|------|--------|------|
| Linux x64 | `.tar.gz` | `myapp-v0.3.0+abc1234-linux-x64.tar.gz` |
| Windows x64 | `.zip` | `myapp-v0.3.0+abc1234-windows-x64.zip` |
| macOS ARM64 | `.tar.gz` | `myapp-v0.3.0+abc1234-macos-arm64.tar.gz` |

### 打包内容
```
package/
├── 可执行文件（或入口脚本）
├── VERSION                    # 纯文本版本号
└── 运行时必需资源/            # 字体、配置、静态文件等
```
- 只打包**运行时必需**的文件，不含源码、测试、文档
- `VERSION` 文件内容与产物命名中的版本一致

### 二进制压缩
- Linux / Windows：UPX `--best --lzma`（编译型语言适用）
- macOS：跳过（UPX 不支持）

### 预发布标记
标签含 `beta` / `alpha` / `rc` → Release 标记为 prerelease

### 本地部署脚本
- 统一放 `scripts/` 目录
- 提供 `deploy.sh`（Linux/macOS）+ `deploy-windows.ps1`（Windows）
- 产物输出到 `bin/` 目录

### CI/CD 流水线触发
| 事件 | 动作 |
|------|------|
| push / PR → main/master/develop | lint → test → build（多平台） |
| push `v*` 标签 | 上述 + 上传产物 + 创建 Release |

**Rust 项目 CI 顺序**：`cargo fmt --all` → `cargo clippy --all --all-targets -- -D warnings` → `cargo test` → `cargo build`（严格串行，前一步失败则终止）

---

## 10. Draw.io（macOS）

```bash
# 导出 PNG（2x 缩放）
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -s 2 input.drawio
```

- 默认样式：`rounded=1`、`spacing=15`、边路由 `orthogonal`

---

> 此文件为个人偏好基线。新项目可按需裁剪/调整，但请先确认差异点。
