---
name: cpp-engineering
description: C++20 项目的代码、CMake、并发和性能工程约定；适用于实现、评审或调整 C++ 构建，保留已有工具链和公共接口。
---

# C++ 工程

将个人 C++ 偏好应用到当前改动；已有项目约定和明确兼容性要求优先。
只加载任务涉及的参考，不把新项目模板套用到维护中的工程。

## 范围与判断

- 先检查语言标准、编译器、目标平台、构建预设和已有依赖。
- 新项目默认 C++20、Linux/Windows、CMake；升级语言标准或更换核心库须属于任务范围。
- 修改命名或头文件结构时维持公开 API、安装路径和 ABI 约定。
- 只有缺失状态用 `optional`；需要区分失败原因时使用类型化结果。
- C++20 使用已有结果类型或 `variant`；仅已采用 C++23 的项目使用 `std::expected`。

## 实现偏好

- 函数、变量、文件使用 `snake_case`，类型使用 `UpperCamelCase`。
- 公共头使用 `#pragma once`，减少包含和实现暴露，定义尽量放 `.cc/.cpp`。
- 使用 `const/constexpr`、`span`、`string_view`、`[[nodiscard]]`、`enum class` 表达约束。
- 用 RAII 和智能指针管理资源，禁止裸 `new/delete`；共享所有权确有需要时才用 `shared_ptr`。
- 用独立类型区分容易混淆的 ID 和参数；接口清楚表达借用与所有权转移。
- 禁止 `goto`；按场景使用条件分支、状态机或分发表。
- 新 JSON 功能偏好 `nlohmann::json` 与 `to_json/from_json`，日志偏好 `spdlog` 的 `key=value` 字段。
- 并发偏好 `std::jthread` 与 `stop_token`；任务图需要时使用 Taskflow，不为简单修改引入依赖。

## 按需参考

- 新建工程、改 CMake、依赖、预设或 CI：读取 [构建与验证](references/build.md)。
- 优化结构体、分配、并发或延迟：读取 [性能与类型边界](references/performance.md)。
- ROS 2 / C++ 异步机器人任务可用 `ros2-cpp`，Rust 互操作可用 `rust-ffi`；普通 C++ 修改不加载它们。
- 产物和发布任务可用 `release-engineering`，不从代码修改推定发布授权。

## 验证与交付

- 使用项目已有的 `clang-format`、`clang-tidy` 与构建命令，检查修改涉及的目标。
- 新项目默认 GoogleTest；测试保持确定性，单元测试不依赖网络和脆弱时序。
- 关键模块追踪覆盖率，集成测试使用最小数据与 golden files。
- 内存或并发改动按风险运行相关 Sanitizer；性能结论附可复现测量。
- 报告行为变化、平台验证和实际限制，不把未运行的平台检查写成通过。
