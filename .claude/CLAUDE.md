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

### 6.1 基本规范
- **分支**：`master` 保护；特性分支 `feat/*`、修复 `fix/*`。
- **提交规范**：Conventional Commits（`feat/fix/refactor/docs/test/build/chore/style/perf/build/ci/revert`），**不使用 scope 括号**。
- **评审**：小步提交；PR 必需通过构建与静态检查；描述明确动机与影响面。
- **标签**：`vX.Y.Z`；遵循语义化版本。
- **署名**：生成commit的时候不要加最后的
    ``` 🤖 Generated with [Claude Code](https://claude.ai/code)

    Co-Authored-By: Claude <noreply@anthropic.com>

    ```

### 6.2 Commit Message 详细格式

**简单修改**（单行即可）：
```
<type>: 简短描述
```

**复杂修改**（多段式）：
```
<type>: 简短标题（一行概括）

问题描述：
- 原有逻辑/问题现象
- 实际需求/预期行为

修复内容/修改内容：
- 具体修改点1
- 具体修改点2
- 其他修改说明

业务逻辑：
- 从业务角度解释修改的合理性
- 说明修改后的预期行为

影响文件：
- 文件路径（行号范围）
```

**关键要素说明**：
1. **标题行**：`<type>: 简短描述`（**不带 scope 括号**）
   - **type**: feat/fix/refactor/docs/test/chore 等
   - **简短描述**: 一句话说明做了什么
   - **错误示例**：`feat(module): 描述` ❌
   - **正确示例**：`feat: 描述` ✅

2. **问题描述**：说明"为什么"要修改
   - 原有逻辑是什么
   - 存在什么问题或不符合需求

3. **修复内容/修改内容**：说明"做了什么"
   - 列出关键修改点
   - 使用对比格式清晰展示变化

4. **业务逻辑**（可选）：从业务角度解释
   - 修改后的行为
   - 业务合理性

5. **影响文件**（可选）：技术细节
   - 文件路径
   - 可选的行号范围

**示例**：
```
fix: 调整多层级位姿生成的排序顺序

问题描述：
- 原排序逻辑：拾取从低到高入队（出队从高到低），放置从高到低入队（出队从低到高）
- 实际需求：需要直接控制生成顺序，而非通过队列特性间接实现

修复内容：
- object_id="0"(拾取)：改为从高到低排序（降序：4,3,2,1）
- object_id="6"(放置)：改为从低到高排序（升序：1,2,3,4）
- 简化注释，移除"入队后出队"的间接描述

业务逻辑：
- 拾取工件时，先处理高层位姿再处理低层位姿
- 放置工件时，先处理低层位姿再处理高层位姿

影响文件：
- muliti_pose_generator_action.cpp（line 190-199）
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
- `8438221` fix: 修复 HeadControlAction 的 heap-use-after-free 竞态条件

### 10.2 异步回调生命周期管理缺陷（局部变量过早销毁）

**问题场景**：ROS2 Action 客户端异步回调 + 局部生命周期标记

**症状**：Action Server 有时收不到 goal，间歇性失败（10%-80%概率），命令行发送总是正常。

**典型错误模式**：
```cpp
// ❌ 错误：生命周期标记是局部变量
BT::NodeStatus onStart() {
    // 创建局部生命周期标记
    auto self = std::make_shared<int>(1);  // ← 局部变量！
    weak_self_ = self;

    send_goal_options.goal_response_callback =
        [this, weak_self = weak_self_, self](...) {  // ← 捕获局部变量
            auto shared_self = weak_self.lock();
            if (!shared_self) {
                // ← 检测到"对象已销毁"，直接返回
                return;  // goal_handle_ 永远不会被设置！
            }
            goal_handle_ = goal_handle;
        };

    async_send_goal(goal, send_goal_options);
    return BT::NodeStatus::RUNNING;
    // ← 函数返回后，局部变量 self 立即被销毁！
}
```

**时序分析（为什么间歇性失败）**：

成功场景（罕见）：
```
T0: onStart() 被调用
T1: 创建 self (引用计数=1)
T2: async_send_goal() 发送请求
T3: Server 立即接受 goal
T4: goal_response_callback 被调度
T5: 回调执行，weak_self.lock() 成功（self 还存活）✓
T6: goal_handle_ 被正确设置
T7: onStart() 返回，self 被销毁
```

失败场景（常见）：
```
T0: onStart() 被调用
T1: 创建 self (引用计数=1)
T2: async_send_goal() 发送请求
T3: onStart() 返回 RUNNING
T4: self 被销毁（离开作用域）← 关键！
T5: Server 接受 goal（有网络/调度延迟）
T6: goal_response_callback 被调度
T7: 回调执行，weak_self.lock() 返回 nullptr ✗
T8: 回调直接返回，goal_handle_ 永远不会被设置
T9: Server 认为已接受，但 Client 侧没有 handle
```

**失败概率影响因素**：
- 网络延迟：DDS 通信延迟增加失败率
- Executor 调度：MultiThreadedExecutor 的不确定性
- 系统负载：CPU 忙时，回调调度延迟
- CallbackGroup 竞争：MutuallyExclusive 类型导致阻塞

估算失败率：
- 低负载 + 本地通信：10-20%
- 高负载 + 网络通信：60-80%
- 极端情况：接近100%

**正确写法**：
```cpp
// ✅ 正确：生命周期标记作为成员变量
class NavAction {
private:
    std::shared_ptr<void> self_holder_;  // ← 成员变量
    std::weak_ptr<void> weak_self_;
};

BT::NodeStatus onStart() {
    // 创建成员变量的生命周期标记
    self_holder_ = std::make_shared<int>(1);  // ← 成员变量
    weak_self_ = self_holder_;

    send_goal_options.goal_response_callback =
        [this, weak_self = weak_self_](...) {  // ← 只捕获 weak_ptr
            auto shared_self = weak_self.lock();
            if (!shared_self) {
                return;  // 对象已销毁（节点被停止）
            }
            goal_handle_ = goal_handle;  // ← 正常设置
        };

    async_send_goal(goal, send_goal_options);
    return BT::NodeStatus::RUNNING;
    // ← self_holder_ 作为成员变量，会持续存活到 onRunning/onHalted 清理
}

BT::NodeStatus onRunning() {
    if (action_completed_) {
        // 清理生命周期标记
        weak_self_.reset();
        self_holder_.reset();  // ← 释放
        return success ? SUCCESS : FAILURE;
    }
    return RUNNING;
}

void onHalted() {
    // 清理生命周期标记
    weak_self_.reset();
    self_holder_.reset();  // ← 释放
}
```

**关键原则**：
1. **绝不在异步回调中捕获局部变量作为生命周期标记**
2. **生命周期标记必须是成员变量（self_holder_），确保在整个 Action 执行期间存活**
3. **回调中只捕获 weak_ptr，不捕获 shared_ptr**
4. **在 onRunning（完成时）和 onHalted（停止时）中释放 self_holder_**
5. **使用 RAII 模式管理生命周期，避免手动管理**

**为什么命令行总是正常**：
- 独立进程，有独立的 Executor
- 生命周期绑定到整个命令执行
- 独享 CallbackGroup，无资源竞争
- 通常会同步等待结果

**检测工具**：
- AddressSanitizer（`-fsanitize=address`）：检测 UAF
- ThreadSanitizer（`-fsanitize=thread`）：检测数据竞争
- 日志验证：在回调中添加 `RCLCPP_WARN` 记录 `weak_self.lock()` 结果

**适用场景**：
- ROS2 Action 客户端（NavAction, WaistAction, DoubleArmAction, HeadControlAction）
- ROS2 Service 异步回调
- 任何异步回调 + 短生命周期对象的组合

**相关修复**：
- fix: 修复 nav_action/waist_action/double_arm_action/head_control_action 的异步回调生命周期缺陷
- 影响文件：
  - nav_action.h/cpp
  - waist_action.h/cpp
  - double_arm_action.h/cpp
  - head_control_action.h/cpp

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
