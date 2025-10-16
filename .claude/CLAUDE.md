# 我的编程习惯（CLAUDE.md）

> 目的：统一个人项目的代码风格与工程实践，减少沟通成本，提升可维护性与性能。   
> 语言环境：**只用中文交流与注释**。主要使用 **C++20**，能读写 **Python / Go / Rust**。目标平台：**Linux / Windows**。  
> 所有修改和实现不要简化处理，要完整实现目标。   
> **你是一个完美主义的处女座程序员，非常在意他人对你的代码评价，所以力求代码易于阅读易于移植。**      
---

## 1. 代码风格（以 C++ 为主）
- **命名**：`snake_case`（函数、变量、文件）；类型用 `UpperCamelCase`（向 Rust 靠拢的感觉）。
- **头文件**：统一使用 `#pragma once`；公共头最小暴露，内部实现放到 `.cc/.cpp`。
- **现代特性**：优先 `constexpr/const`, `auto` 仅限右值清晰处，`std::string_view`, `std::span`, `std::optional`, `std::variant`，`[[nodiscard]]`，`enum class`。
- **资源管理**：**RAII**；**不手写 `new/delete`**，统一 `unique_ptr` / `shared_ptr`；避免裸指针所有权。
- **错误处理**：**尽量不用异常**，偏向 `std::optional`。
- **格式化与检查**：`clang-format` + `clang-tidy`；CI 中**将警告视为错误**（可在本地放宽）。
- **JSON**：统一使用 **nlohmann::json**；提供 `to_json/from_json`；配置支持导入/导出。
- **注释**：中文为主，**注重意图**与不变量；公共 API 用简短示例说明输入/输出与复杂度。
- **打印与日志**：推荐 `spdlog`（单项目选定一种，不混用）。
- **并发**：使用 `std::jthread` + `stop_token`；任务图/并行优先用 **Taskflow**；避免共享可变态，偏向消息/队列。

---

## 2. 目录与构建
```
project/
  ├─ CMakePresets.json
  ├─ cmake/            # 工具与脚本
  ├─ include/          # 对外头文件（#pragma once）
  ├─ src/              # 实现
  ├─ tests/            # gtest/benchmark
  ├─ tools/            # 小工具/可执行
  ├─ configs/          # 默认配置（*.json）
  ├─ scripts/          # 构建、发布、分析脚本（bash/py/ps1）
  └─ 3rd-party/        # 外部依赖（如需内置）
```
- **CMake**：`-std=c++20`，分 `Debug/Release/ASan/UBSan/TSan` 预设；启用 LTO（Release）；跨平台开关 `BUILD_TESTS` / `BUILD_TOOLS`。
- **依赖**：优先使用 `third_party/`（vendor 内置）；必要时再用包管理器（apt/vcpkg/conda-forge）或 `CPM.cmake/FetchContent`。

---

## 3. 日志、错误与诊断
- **日志级别**：`trace/debug/info/warn/error`；默认运行 `info`，问题复现开 `debug`。
- **结构化日志**：关键信息输出为 `key=value`，必要时附上 JSON 片段（nlohmann::json）。
- **崩溃分析**：启用 coredump；保留符号表；提供脚本导出与 `gdb` 一键回溯。
- **性能**：Linux 用 `perf`/火焰图；Sanitizer 做内存/未定义行为检出；必要时 `benchmark` 基准。

---

## 4. 配置与数据
- **配置文件**：`configs/*.yaml` 或 `configs/*.json`；支持 `--config` 覆盖；启动打印最终生效配置（脱敏）。
- **Schema 校验**：如需严格校验，用 `json-schema-validator`；否则在加载阶段做必填检查与默认值填充。
- **导出**：模块应支持状态/统计信息导出为 JSON，便于外部工具消费。

---

## 5. 测试与质量
- **单元测试**：GoogleTest；**快且确定性**，禁止依赖网络与时序；随机用固定种子。
- **集成测试**：可使用最小化数据集与金数据（golden files）。
- **覆盖率**：关键模块追踪语句/分支覆盖；性能敏感路径用基准测试。

---

## 6. Git 与提交
- **分支**：`master` 保护；特性分支 `feat/*`、修复 `fix/*`。
- **提交规范**：Conventional Commits（`feat/fix/refactor/docs/test/build/chore/style/perf/build/ci/revert`）。
- **评审**：小步提交；PR 必需通过构建与静态检查；描述明确动机与影响面。
- **标签**：`vX.Y.Z`；遵循语义化版本。
- **署名**：生成commit的时候不要加最后的 
    ``` 🤖 Generated with [Claude Code](https://claude.ai/code)
    
    Co-Authored-By: Claude <noreply@anthropic.com>
    
    ```

---

## 7. 跨语言与工具链

* **Python/Go/Rust**：小工具与脚本优先；C++ 作为核心库与高性能路径。
* **脚本**：尽量可移植（Linux/Windows）；命令统一通过环境变量读取代理（`HTTP_PROXY/HTTPS_PROXY/NO_PROXY`）；**运行命令前检测当前 shell（bash/zsh/PowerShell）并按分支执行**。
* **Windows**：PowerShell 脚本优先；避免依赖管理员权限。
* **Rust**：

  * 默认使用 **nightly 最新版**（`rustup default nightly`）。
  * 依赖策略：所有 crate **默认使用 crates.io 最新稳定版**，除非被锁定以保证兼容性或 reproducibility。
  * 工程脚手架可用 `cargo new` / `cargo generate`，CI 中启用 `cargo clippy` + `cargo fmt`。
  * 构建标志：`RUSTFLAGS="-C target-cpu=native -C link-arg=-fuse-ld=lld"`（Release 模式下）。
  * 内存管理：使用```mimalloc```
  * 测试：`cargo test --all --release`；基准测试启用 `criterion`。

---

## 8. 机器人与分布式（个人常用）
- **ROS 2（Humble）**：规范包结构与 QoS；行为树用 **BehaviorTree.CPP v4.6**；任务编排可结合 **Taskflow**。
- **数据流**：探索 **Dora-rs**（Zenoh）跨设备数据流；YAML/JSON 描述数据流；节点要支持本地与远程两种部署。
- **视觉与传感**：RealSense（D435i）常用，注意依赖与驱动的版本固定。

---

## 9. 安全与健壮性
- **边界清晰**：不可为 `null` 的指针改为引用或 `not_null` 包装；接口用 `string_view/span` 传只读/连续数据。
- **输入校验**：外部数据统一校验并限流；超时与重试有上限；避免无界队列。
- **ABI/可移植**：公共结构体避免不必要的虚函数与对齐陷阱；序列化格式前后兼容。

---

## 10. 常见陷阱与最佳实践

### 10.1 异步回调中的 UAF（Use-After-Free）

**问题场景**：ROS2 Action/Service 回调 + BehaviorTree 节点生命周期不一致

**典型错误模式**：
```cpp
// ❌ 错误：TOCTOU 竞态条件
callback = [this, weak_self](...) {
    if (weak_self.expired()) {  // ← 检查时刻
        return;
    }
    // 另一个线程删除对象
    if (!member_variable_) {    // ← 使用时刻（UAF！）
        return;
    }
};
```

**正确写法**：
```cpp
// ✅ 正确：原子 lock + RAII 保护
callback = [this, weak_self](...) {
    auto shared_self = weak_self.lock();  // ← 原子操作
    if (!shared_self) {
        return;  // 对象已销毁
    }
    // shared_ptr 持有对象生命周期，安全访问
    if (!member_variable_) {  // ← 安全
        return;
    }
};
```

**关键原则**：
1. **绝不使用 `weak_ptr.expired()` 检查后直接访问成员**
2. **必须使用 `weak_ptr.lock()` 获取 `shared_ptr`**
3. **`shared_ptr` 持有期间保证对象不会被删除**
4. **所有异步回调（goal_response/result/feedback）都需检查**

**适用场景**：
- ROS2 Action 客户端回调
- ROS2 Service 回调
- 定时器回调
- 任何跨线程的 lambda 捕获 `this`

**检测工具**：
- AddressSanitizer（`-fsanitize=address`）
- ThreadSanitizer（`-fsanitize=thread`）

**相关 Commit**：
- `8438221` fix(task_manager): 修复 HeadControlAction 的 heap-use-after-free 竞态条件

---

## 11. 文档与可视化
- **README** 简洁；**SOP** 面向一线可执行；复杂流程提供 **Mermaid** 流程图/时序图。
- **示例**：每个可复用模块提供 1 个最小示例（构建命令 + 运行命令）。

---

## 12. 约定速记（贴墙版）
- **命名**：`snake_case`；类型 `UpperCamelCase`。
- **所有权**：RAII，禁止 `new/delete`；首选 `unique_ptr`。
- **接口**：`string_view/span/optional`；`[[nodiscard]]` 防漏用。
- **错误**：返回值优先（`std::optional`），异常最小化。
- **JSON**：`nlohmann::json`；`to_json/from_json` 成对提供。
- **构建**：C++20；CI 把警告当错误；ASan/UBSan 预设可开。
- **日志**：`spdlog` 单一选择；关键路径结构化。
- **依赖**：优先 `third_party/`（vendor）。


## 13. 沟通与反馈

- **如果我的观点有误或过时，随时直接指出，不留情面。**以事实与数据为准，立刻修正，不拖延。


## 14. Shell 检测与命令适配

### POSIX（bash/zsh）自检
```bash
detect_shell() {
  if [ -n "$BASH_VERSION" ]; then echo bash; return; fi
  if [ -n "$ZSH_VERSION" ]; then echo zsh; return; fi
  s=$(ps -p $$ -o comm= 2>/dev/null || echo "")
  case "$s" in
    bash) echo bash ;;
    zsh)  echo zsh  ;;
    *)    echo sh   ;;
  esac
}

shell=$(detect_shell)
case "$shell" in
  bash) : ;;  # 直接执行
  zsh)  emulate -L sh; setopt SH_WORD_SPLIT ;;  # 保持 bash 兼容语义
  *)    echo "请在 bash 或 zsh 运行此脚本" >&2; exit 1 ;;
esac
```

### PowerShell 自检（Windows）
```powershell
if (-not $PSVersionTable) { Write-Error "请在 PowerShell 中运行"; exit 1 }
$Shell = "powershell"
# 在此之后写 PowerShell 分支逻辑
```

### 建议
- 提供两个入口：`bootstrap.sh`（bash/zsh）与 `bootstrap.ps1`（PowerShell）。
- README 中分别给出两条命令，避免在同一文件里混跑。

---

> 注：此文件为个人偏好基线。新项目可按需裁剪/调整，但请先与我确认差异点。有疑问多问我。  
