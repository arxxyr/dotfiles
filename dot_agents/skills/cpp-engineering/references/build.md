# C++ 构建与验证

## 新项目默认结构

以下是新建工程的起点；已有项目保持原目录与公开包含路径。

```text
project/
├── CMakePresets.json    # Debug/Release/ASan/UBSan/TSan 预设
├── cmake/              # 工具与构建辅助
├── include/            # 对外头文件
├── src/                # 实现
├── tests/              # GoogleTest 与基准
├── tools/              # 小工具
├── configs/            # 默认 JSON/YAML 配置
├── scripts/            # 构建与发布入口
└── 3rd-party/          # 纳管依赖
```

- 默认 C++20，明确是否允许编译器扩展；跨平台检查使用实际支持的标准库能力。
- 提供 `BUILD_TESTS` / `BUILD_TOOLS` 开关，关闭后不额外下载其专用依赖。
- Release 优先启用 LTO，先验证编译器、链接器及第三方库兼容性。
- 依赖优先已有 `3rd-party/` vendor，再选择包管理器或 CPM.cmake/FetchContent。
- 新依赖固定可复现版本；不要为了满足个人默认库替换工程中正常使用的等价依赖。
- 提供独立的 Debug、Release 和适用 Sanitizer 预设；ASan/UBSan 与 TSan 按工具链支持分别运行。
- 使用 `clang-format` 和 `clang-tidy`，CI 将本项目警告视为错误；不要无差别重排无关文件。

## 验证选择

- 单元测试用 GoogleTest；避免真实网络、外部服务和 `sleep` 驱动的竞态断言。
- 集成测试准备最小数据集和稳定的 golden files；明确跨平台路径与换行差异。
- 修复可复现行为或更改关键逻辑时补足有价值的回归覆盖，不编写只复述实现的测试。
- 关键模块跟踪覆盖率；性能敏感目标提供 benchmark，记录构建类型和平台。
- 内存问题优先 ASan/UBSan，数据竞争优先 TSan；不能运行的检查如实说明。
- 配置了 Windows 与 Linux 的项目应验证两平台；只有当前平台可用时检查另一平台的路径与编译分支，并说明验证范围。

## 脚本入口

跨平台初始化提供 `bootstrap.sh` 与 `bootstrap.ps1`；部署入口和产物约定读取 `release-engineering`。
遵循项目已有 Shell：需要 Bash/Zsh 特性时显式声明解释器，POSIX 脚本不使用专属语法。
确需检测时使用专用变量，不覆盖 `HOME`、`home` 或 `CODEX_HOME`：

```sh
if [ -n "${BASH_VERSION:-}" ]; then
    bootstrap_shell=bash
elif [ -n "${ZSH_VERSION:-}" ]; then
    bootstrap_shell=zsh
else
    bootstrap_shell=posix
fi
```

PowerShell 入口检查 `$PSVersionTable`，根据实际最低版本使用可用语法；外部命令失败通过退出码传递。
