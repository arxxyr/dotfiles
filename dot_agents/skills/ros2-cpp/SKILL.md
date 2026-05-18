---
name: ros2-cpp
description: ROS 2 / C++ 机器人项目规范与并发陷阱。当项目涉及 ROS 2（Humble）、行为树、Dora-rs 数据流、RealSense 视觉、或 C++ 异步回调时使用。包含 Action Server goal_handle 终止原则、weak_ptr UAF 防护、jthread/stop_token 用法。
---

# ROS 2 / C++ 机器人开发规范

## 1. C++/ROS2 并发陷阱

### 1.1 异步回调 UAF（Use-After-Free）
```cpp
// ❌ expired() 检查后直接访问 — TOCTOU 竞态
if (weak_self.expired()) return;
member_var_;  // UAF!

// ✅ lock() 获取 shared_ptr 保护生命周期
auto self = weak_self.lock();
if (!self) return;
member_var_;  // 安全
```

### 1.2 异步回调局部变量过早销毁
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

### 1.3 Action Server goal_handle 终止原则
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

## 2. 机器人与分布式

- **ROS 2（Humble）**：规范包结构与 QoS；行为树用 **BehaviorTree.CPP v4.6**
- **数据流**：探索 **Dora-rs**（Zenoh）；YAML/JSON 描述数据流
- **视觉**：RealSense D435i；注意驱动版本固定
