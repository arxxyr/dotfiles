# dotfiles

简体中文 | [English](README.en.md)

使用 [chezmoi](https://www.chezmoi.io/) 管理，跨平台（Linux / macOS / Windows）。

```bash
sh -c "$(curl -fsLS get.chezmoi.io/lb)"
```

## 快速开始

### 新机器（一条命令）

```bash
chezmoi init --apply git@github.com:arxxyr/dotfiles.git
```

### 日常使用

```bash
chezmoi add ~/.zshrc              # 配置有改动？自动提交并推送
chezmoi add ~/.config/xxx/conf    # 纳管新配置
chezmoi diff                      # 查看待应用的变更
```

## 自动化安装（run_once）

`chezmoi init --apply` 会触发按操作系统区分的 `run_once_*` 脚本，自动安装完整工具链。
所有联网安装均走代理（WSL：经 `cc-proxy-host` 运行时探测网关；其余平台：`127.0.0.1:10808`），
失败自动退回直连。每一步幂等——已安装的组件直接跳过。

| 组件 | Ubuntu/Debian (apt) | Arch (pacman) | macOS (brew) | Windows |
|---|---|---|---|---|
| 基础 CLI（zsh/fzf/ripgrep/btop/jq/zoxide/git/…） | apt | pacman | brew | —（终端活在 WSL 干） |
| SSH 打洞工具 | `netcat-openbsd`（`nc -X`） | `openbsd-netcat` | `connect`（mac 专属保留） | — |
| Rust nightly | rustup 官方脚本，`--no-modify-path` | 同左 | 同左 | `rustup-init.exe` |
| uv | 官方脚本，`UV_NO_MODIFY_PATH=1` | pacman | 官方脚本 | 官方 `install.ps1` |
| eza | `cargo install` → GitHub release 兜底 | pacman | brew | — |
| yazi | 官方 apt 源（nightly）→ 二进制兜底 | pacman | brew | — |
| Node.js LTS | 官方 nvm 脚本，`PROFILE=/dev/null` | 同左 | brew `node` | winget `OpenJS.NodeJS.LTS` |
| Codex CLI | `npm install -g @openai/codex` | 同左 | 同左 | 同左 |
| Claude Code | 官方安装器（静态二进制 → 必须 env 代理） | 同左 | 同左 | 官方 `install.ps1` |
| Neovim nightly | unstable PPA + vim/vi/editor alternatives | AUR `neovim-nightly-bin`（需 yay/paru） | `brew --HEAD` | 不安装 |
| Oh My Zsh + 插件 | git clone | 同左 | 同左 | — |
| WezTerm（GUI 终端；WSL 跳过） | 官方 fury 源（nightly）+ x-terminal-emulator | pacman | —（未纳管） | — |
| AUR helper（yay-bin） | — | AUR makepkg | — | — |
| Git / PowerShell 7 / Windows Terminal / PowerToys | — | — | — | winget 带 `--proxy` |

### 安装的软件清单（各包管理器的确切包名）

| 平台 | 包名 |
|---|---|
| Ubuntu/Debian（apt） | `zoxide zsh fzf ripgrep btop jq git wget curl unzip build-essential netcat-openbsd proxychains4 software-properties-common` |
| Arch（pacman） | `zoxide zsh eza fzf yazi uv ripgrep btop jq git wget curl unzip base-devel openbsd-netcat proxychains-ng` |
| macOS（brew） | `zoxide bash-completion xmake connect proxychains-ng eza fzf yazi ripgrep btop jq wget node` |
| Windows（winget） | `Git.Git` `OpenJS.NodeJS.LTS` `Microsoft.PowerShell` `Microsoft.WindowsTerminal` `Microsoft.PowerToys` |

包管理器之外（全平台一致，见上方矩阵的安装渠道）：

- **rust nightly**（rustup）、**uv**、**Node.js LTS**（nvm，mac 为 brew）、**Codex CLI**（npm）、**Claude Code**（官方安装器）
- **eza**（Ubuntu 走 cargo/二进制）、**yazi**（Ubuntu 走官方 apt 源）、**Neovim nightly**（PPA / AUR / brew --HEAD）
- **Oh My Zsh** + 插件：`zsh-syntax-highlighting` `zsh-autosuggestions` `zsh-completions`

脚本内置的约定：

- 安装器一律不许碰纳管 rc 文件——PATH/env 引导统一放在
  `~/.config/shell/profile.sh`（rustup `--no-modify-path`、`UV_NO_MODIFY_PATH=1`、
  nvm `PROFILE=/dev/null`）。
- Windows 的 winget 代理受管理员设置 `ProxyCommandLineOptions` 管控；脚本先查状态，
  缺失时触发一次性 UAC 提权启用。
- Windows 刻意不装 nvim 与 fzf/rg/eza/zoxide/yazi 等 CLI 族。
- apt 安装先按包是否存在分区，单个包名缺失不会拖垮整笔事务；失败组件汇总后统一报错。
- apt 全局强制 IPv4（`/etc/apt/apt.conf.d/99force-ipv4`），规避 IPv6 路由不稳时 update 挂起。

## 可选：完整开发工具链（嵌入式 / OpenWrt 编译）

> 原"手动引导"各项已全部并入 run_once 自动化：apt 强制 IPv4、WezTerm（fury 源 +
> 默认终端 alternatives，WSL 跳过）、AUR helper（yay-bin）由 setup 脚本安装；
> pip 国内镜像由纳管配置直接提供（POSIX：`~/.config/pip/pip.conf`；
> Windows：`%APPDATA%\pip\pip.ini`），无需 `pip config set`。

不属于纳管范围——仅编译机需要：

```bash
sudo apt install -y ack antlr3 asciidoc autoconf automake autopoint binutils bison build-essential bzip2 \
  ccache clang clang-tidy clangd cmake cpio device-tree-compiler ecj fastjar flex \
  gawk gettext gnutls-dev gperf haveged help2man intltool libelf-dev libglib2.0-dev \
  libgmp3-dev libltdl-dev libmpc-dev libmpfr-dev libncurses-dev libpython3-dev \
  libreadline-dev libssl-dev libtool libyaml-dev libz-dev lld llvm lrzsz mkisofs msmtp nano \
  neofetch net-tools ninja-build p7zip p7zip-full patch pkgconf python3 \
  python3-dev python3-docutils python3-pip python3-ply python3-pyelftools qemu-utils \
  re2c rsync scons squashfs-tools subversion swig texinfo uglifyjs upx-ucl vim \
  xmlto xsel xxd zlib1g-dev zstd
```

## 纳管清单

| 配置 | 路径 | 说明 |
|---|---|---|
| zsh | `~/.zshrc`、`~/.p10k.zsh` | Zsh + Powerlevel10k（含 nvm 加载器） |
| bash | `~/.bashrc` | Bash 配置（含 nvm 加载器 + 补全） |
| shell | `~/.config/shell/profile.sh` | 共享 PATH/env 引导（cargo、nvm、uv、自定义脚本、kimi-code） |
| claude | `~/.claude/` | Claude Code 配置（模板化：WSL 渲染裁掉写死的代理） |
| codex | `~/.codex/AGENTS.md`、`~/.codex/config.toml`、`~/.codex/skills/` | Codex 指令（符号链接到 Claude 的 CLAUDE.md）；config.toml 用 `modify_` 脚本只钉住 model/effort/status_line，`[projects]` 取并集，nux 计数器等透传 |
| kimi | `~/.kimi-code/config.toml`、`~/.kimi-code/tui.toml` | Kimi Code CLI（config.toml 用 `modify_` 脚本只钉住强制项、其余透传给 CLI；tui.toml 全量纳管。凭据目录不纳管） |
| agents | `~/.agents/skills/` | 共享 agent skills（claude / codex 共用） |
| cargo | `~/.cargo/config.toml` | Rust cargo 配置（模板化：WSL 渲染无 proxy 行） |
| kitty | `~/.config/kitty/` | Kitty 终端 |
| alacritty | `~/.config/alacritty/` | Alacritty 终端 |
| wezterm | `~/.config/wezterm/` | WezTerm 终端 |
| starship | `~/.config/starship.toml` | Starship 提示符 |
| lazygit | `~/.config/lazygit/` | Lazygit TUI |
| neofetch | `~/.config/neofetch/` | Neofetch + 自定义 ASCII art |
| pip | `~/.config/pip/pip.conf`（POSIX）、`%APPDATA%\pip\pip.ini`（Windows） | pip USTC 镜像，双平台同配 |

## 自定义脚本

全部位于 `~/.custom_scripts/`，跨平台（Linux / macOS / Windows）。

代理宿主机是单一事实来源：`cc-proxy-host` 输出正确地址（WSL NAT → 运行时探测默认网关；
其余环境 → `127.0.0.1`），其他脚本都基于它构建。环境变量层保持 `http://`
（wget/pip/Node 兼容）；proxychains 与 SSH 打洞层走 socks5。

**proxychains 自动配置**（mac / Linux / WSL）：登录 shell 会执行
`export PROXYCHAINS_CONF_FILE="$(cc-pc --refresh)"`（见 profile.sh），该变量优先于
`/etc/proxychains4.conf`——裸敲 `proxychains4 <cmd>` 即走动态配置，WSL 重启后开新终端
自动跟上新网关。`sudo` 会剥离环境变量，root 场景用 `cc-install` / `cc-pc`（内部显式
`-f`）。macOS 注意：SIP 使 proxychains 无法注入系统自带二进制（`/usr/bin/*`），对
brew 安装的程序有效。

| 命令 | 说明 |
|---|---|
| `cc-proxy-host` | 输出代理宿主机（WSL NAT → 网关，否则 127.0.0.1） |
| `cc-claude [kill]` | 带代理启动 Claude Code / 杀掉全部 Claude 进程 |
| `cc-codex [kill]` | 带代理启动 Codex CLI |
| `cc-kimi [kill]` | 启动 Kimi Code CLI（K3 + max 思考 + auto 权限，直连不走代理） |
| `cc-codex-app` | macOS：给 Codex 桌面 App 注入代理环境（launchctl） |
| `source cc-proxy [off]` | 当前 shell 设置/清除代理 env + git 代理 |
| `cc-pc <cmd>` | 经动态生成配置的 proxychains 执行命令 |
| `cc-install <包>…` | 走代理的 apt / brew 安装 |
| `cc-update` | 系统更新（apt / brew / winget） |
| `cc-synctime [时区偏移]` | 同步时间并设置时区（NTP 是 UDP，不涉及代理） |

```bash
cc-claude                    # 带代理启动 Claude（宿主机自动探测）
cc-kimi                      # 启动 Kimi（K3 / max 思考 / auto 权限）
cc-kimi -c                   # 以 - 开头的参数透传给 kimi：续上次会话
source cc-proxy              # 当前 shell 启用代理 env
source cc-proxy off          # 关闭代理
cc-pc git clone <url>        # 单次命令走 proxychains
cc-install btop              # 走代理的 apt/brew 安装
cc-update                    # apt / brew / winget 升级
cc-synctime                  # UTC+8（默认）；cc-synctime -5 → 纽约
```

## 速查

```bash
# SSH 权限
chmod 0700 ~/.ssh
chmod 0644 ~/.ssh/authorized_keys
chmod 0644 ~/.ssh/id_ed25519.pub
chmod 0600 ~/.ssh/id_ed25519

# Git 代理
git config --global http.proxy http://127.0.0.1:1080
git config --global https.proxy http://127.0.0.1:1080
# 取消
git config --global --unset http.proxy
git config --global --unset https.proxy

# Git 凭据存储
git config --global credential.helper store

# 卸载 CUDA
sudo apt --purge remove "*cuda*" "*cublas*" "*cufft*" "*cufile*" "*curand*" \
  "*cusolver*" "*cusparse*" "*gds-tools*" "*npp*" "*nvjpeg*" "nsight*" "*nvvm*"

# 卸载 NVIDIA 驱动
sudo apt --purge remove "*nvidia*" "libxnvctrl*"
sudo apt autoremove -y
sudo apt install linux-headers-$(uname -r)
```

## 仓库结构

```
dotfiles/
├── dot_*                            # dotfiles（chezmoi 命名规则）
├── private_dot_config/              # ~/.config/ 内容
├── dot_custom_scripts/              # 跨平台脚本（.tmpl）
├── dot_agents/skills/               # 共享 agent skills（claude/codex 符号链接至此）
├── dot_local/bin/create_env         # ~/.local/bin/env 占位（uv PATH 引导）
├── .chezmoiignore.tmpl              # 按操作系统过滤文件
├── run_once_darwin_setup.sh.tmpl    # 首次运行安装（macOS）
├── run_once_linux_setup.sh.tmpl     # 首次运行安装（Linux）
└── run_once_windows_setup.ps1.tmpl  # 首次运行安装（Windows）
```
