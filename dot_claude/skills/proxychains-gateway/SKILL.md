---
name: proxychains-gateway
description: 通过 proxychains4 让 OpenClaw 网关透明走 SOCKS5 代理，解决 Node.js 不支持 SOCKS5 的问题。含 launchd 配置、启动脚本、localnet 排除、踩坑记录和运维手册。
---

# OpenClaw 网关代理配置（proxychains4）

## 概述

OpenClaw 网关是 Node.js 进程，需要访问 Anthropic/DeepSeek 等境外 API，但 Node.js 原生不支持 SOCKS5 代理，OpenClaw 也没有代理配置项。方案：用 proxychains4 在系统层拦截所有 TCP 连接，透明转发到本机 SOCKS5 代理（Clash 等）。

## 架构

```
launchd (ai.openclaw.gateway)
  -> /bin/bash start-gateway.sh
     -> nc -z 探测 SOCKS5 端口（最多 90s）
        -> 就绪: proxychains4 node openclaw gateway
        -> 超时: node openclaw gateway（无代理直连）

proxychains4 流量分流:
  localnet 127.0.0.0/8   -> 直连（Qdrant/Cognee/n8n/bridge）
  localnet 10.0.0.0/8    -> 直连（Ollama）
  其他                    -> SOCKS5 127.0.0.1:10808（Anthropic/Telegram/DeepSeek）
```

## 涉及文件

| 文件 | 用途 |
|------|------|
| `~/.openclaw/scripts/start-gateway.sh` | 延迟启动脚本（等代理 -> proxychains4 启动） |
| `~/.proxychains/proxychains.conf` | proxychains4 配置（链模式/localnet/代理列表） |
| `~/Library/LaunchAgents/ai.openclaw.gateway.plist` | launchd 服务定义 |
| `~/.openclaw/logs/gateway.log` | 网关标准输出 |
| `~/.openclaw/logs/gateway.err.log` | 网关标准错误（含 proxychains 链路日志） |

## 配置详解

### proxychains.conf

```
strict_chain                          # 代理链严格模式，代理不可达则失败（不会默默直连）
proxy_dns                             # DNS 也走代理（防 DNS 污染）
remote_dns_subnet 224
tcp_read_time_out 15000
tcp_connect_time_out 8000

localnet 127.0.0.0/255.0.0.0         # 排除 localhost（Qdrant/Cognee/n8n/bridge）
localnet 10.0.0.0/255.0.0.0          # 排除局域网（Ollama）

[ProxyList]
socks5 127.0.0.1 10808               # Clash SOCKS5 端口
```

**localnet 规则至关重要**：不加则 proxychains 会把连 localhost:6333（Qdrant）、10.0.1.81:11434（Ollama）的请求也发给远端代理，导致内网服务无响应。

### start-gateway.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

PROXY_HOST="127.0.0.1"
PROXY_PORT="10808"
MAX_WAIT=90
CHECK_INTERVAL=5

# 1. 等代理就绪（开机时 Clash 可能还没启动）
elapsed=0
while (( elapsed < MAX_WAIT )); do
    if /usr/bin/nc -z -w2 "$PROXY_HOST" "$PROXY_PORT" 2>/dev/null; then
        exec /opt/homebrew/bin/proxychains4 \
            /opt/homebrew/opt/node@24/bin/node \
            /opt/homebrew/lib/node_modules/openclaw/dist/index.js \
            gateway --port 18789
    fi
    sleep "$CHECK_INTERVAL"
    (( elapsed += CHECK_INTERVAL ))
done

# 2. 超时则无代理直连（国内服务照常，Anthropic 不通）
exec /opt/homebrew/opt/node@24/bin/node \
    /opt/homebrew/lib/node_modules/openclaw/dist/index.js \
    gateway --port 18789
```

### launchd plist 关键配置

```xml
<!-- 改为通过 bash 脚本启动，而非直接启动 node -->
<key>ProgramArguments</key>
<array>
  <string>/bin/bash</string>
  <string>/Users/loosqk/.openclaw/scripts/start-gateway.sh</string>
</array>

<!-- 快速重试（默认 10s，设为 1s） -->
<key>ThrottleInterval</key>
<integer>1</integer>

<!-- 手动补全环境变量（launchd 环境极其精简） -->
<key>EnvironmentVariables</key>
<dict>
  <key>HOME</key><string>/Users/loosqk</string>
  <key>PATH</key><string>/opt/homebrew/opt/node@24/bin:...</string>
  <key>NODE_EXTRA_CA_CERTS</key><string>/etc/ssl/cert.pem</string>
  <key>DEEPSEEK_API_KEY</key><string>sk-xxx</string>
  <!-- 其他必要的环境变量 -->
</dict>
```

## 踩坑记录

### 1. proxychains 代理了本地/局域网流量（最严重）

**现象**：`openclaw mem0 search` 挂住不返回，看起来像 Qdrant 慢。

**原因**：proxychains 默认代理所有 TCP，连 localhost:6333（Qdrant）和 10.0.1.x（Ollama）的请求被发给远端代理服务器，远端不认识内网地址。

**修复**：在 proxychains.conf 加 localnet 规则排除 127.0.0.0/8 和 10.0.0.0/8。

**教训**：proxychains 是全量代理，必须显式排除不该代理的流量。加新内网服务时要检查 localnet 是否覆盖。

### 2. strict_chain vs dynamic_chain

用 `strict_chain`。只有一个代理的场景，代理挂了应该直接失败，而不是默默直连（直连会被墙拦住返回 HTML 错误页，OpenClaw 解析不了更混乱）。

### 3. proxy_dns 必须开

不开则 DNS 走本地，`api.anthropic.com` 可能被 DNS 污染解析到错误 IP。

### 4. launchd 环境变量缺失

launchd 启动的进程没有用户 shell 的环境变量。PATH 只有 `/usr/bin:/bin:/usr/sbin:/sbin`，找不到 homebrew 的 node、proxychains4。必须在 plist 中显式补全。

### 5. nc 版本差异

macOS 自带 `/usr/bin/nc` 和 homebrew ncat 行为不同。脚本显式用 `/usr/bin/nc -z -w2` 确保跨版本一致。

### 6. OpenClaw 更新可能覆盖 plist

`openclaw gateway install` 会重新生成 plist，覆盖自定义的 ProgramArguments 和 EnvironmentVariables。**更新后必须检查 plist 是否还指向自定义启动脚本。**

## 运维手册

### 日常操作

```bash
# 重启网关
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway

# 查看服务状态
launchctl list | grep openclaw

# 查看网关日志
tail -f ~/.openclaw/logs/gateway.log

# 查看 proxychains 链路日志（正常应全部显示 OK）
tail -f ~/.openclaw/logs/gateway.err.log
# 正常输出：[proxychains] Strict chain ... 127.0.0.1:10808 ... api.telegram.org:443 ... OK

# 测试代理端口是否可达
nc -z -w2 127.0.0.1 10808 && echo "代理OK" || echo "代理不通"
```

### 排查流程

1. **服务不响应** -> 先看 `launchctl list | grep openclaw`，确认 PID 存在
2. **API 调用失败** -> 看 `gateway.err.log`，找 proxychains 输出
   - 全部 `OK` = 代理正常，问题在 API 层（token/配额）
   - 有 `DENIED` = 代理不通，检查 Clash 是否运行
   - 无 proxychains 输出 = 网关以无代理模式启动（启动时代理没就绪）
3. **内网服务不通** -> 检查 proxychains.conf 的 localnet 是否覆盖目标网段
4. **启动后秒退** -> 看 `gateway.log` 开头，是否有配置错误；检查 plist 中的路径是否存在

### 新增内网服务时

如果新增了不在 127.0.0.0/8 和 10.0.0.0/8 网段的内网服务（如 192.168.x.x），需要：

1. 编辑 `~/.proxychains/proxychains.conf`，加一行 `localnet 192.168.0.0/255.255.0.0`
2. 重启网关：`launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway`

### 代理工具切换端口时

1. 编辑 `~/.proxychains/proxychains.conf`，修改 `[ProxyList]` 中的端口
2. 编辑 `~/.openclaw/scripts/start-gateway.sh`，修改 `PROXY_PORT`
3. 重启网关

### OpenClaw 升级后

1. 检查 `~/Library/LaunchAgents/ai.openclaw.gateway.plist`
2. 确认 ProgramArguments 仍指向 `/bin/bash` + `start-gateway.sh`
3. 确认 EnvironmentVariables 中的路径和密钥未丢失
4. 如果 node 版本变了（如 node@24 -> node@26），更新 plist PATH 和启动脚本中的绝对路径

## 设计决策

| 决策 | 理由 |
|------|------|
| proxychains4 而非 HTTP_PROXY 环境变量 | Node.js 原生不支持 SOCKS5；HTTP_PROXY 只对部分 HTTP 库生效，WebSocket/gRPC 不走 |
| 延迟启动而非依赖排序 | launchd 没有可靠的服务依赖机制，轮询是最稳的 |
| 超时后无代理启动 | 保证国内服务（Ollama/盯盘）可用，Anthropic 不通可以后续重启补救 |
| 绝对路径 | launchd 环境极简，PATH 不可靠，所有可执行文件用绝对路径 |
| plist 中补 DEEPSEEK_API_KEY | mem0 插件在网关进程内运行，需要访问 DeepSeek API 做记忆提取 |
