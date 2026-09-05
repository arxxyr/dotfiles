# dotfiles

[简体中文](README.md) | English

Managed with [chezmoi](https://www.chezmoi.io/). Cross-platform (Linux / macOS / Windows).

```bash
sh -c "$(curl -fsLS get.chezmoi.io/lb)"
```

## Quick Start

### New Machine (One Command)

```bash
chezmoi init --apply git@github.com:arxxyr/dotfiles.git
```

### Daily Usage

```bash
chezmoi add ~/.zshrc              # Config changed? Auto commit & push
chezmoi add ~/.config/xxx/conf    # Add new config
chezmoi diff                      # See what changed
```

## Automated Setup (run_once)

`chezmoi init --apply` triggers per-OS `run_once_*` scripts that install the full toolchain.
All network installs go through the proxy (WSL: gateway auto-detected via `cc-proxy-host`;
other platforms: `127.0.0.1:10808`) and fall back to a direct connection on failure.
Every step is idempotent — already-installed tools are skipped.

| Component | Ubuntu/Debian (apt) | Arch (pacman) | macOS (brew) | Windows |
|---|---|---|---|---|
| Base CLI (zsh/fzf/ripgrep/btop/jq/zoxide/git/…) | apt | pacman | brew | — (CLI work lives in WSL) |
| SSH tunnel helper | `netcat-openbsd` (`nc -X`) | `openbsd-netcat` | `connect` (mac-only, keep) | — |
| Rust nightly | rustup official script, `--no-modify-path` | same | same | `rustup-init.exe` |
| uv | official script, `UV_NO_MODIFY_PATH=1` | pacman | official script | official `install.ps1` |
| eza | `cargo install` → GitHub release fallback | pacman | brew | — |
| yazi | official apt repo (nightly) → binary fallback | pacman | brew | — |
| Node.js LTS | official nvm script, `PROFILE=/dev/null` | same | brew `node` | winget `OpenJS.NodeJS.LTS` |
| Codex CLI | `npm install -g @openai/codex` | same | same | same |
| Claude Code | official installer (static binary → env proxy required) | same | same | official `install.ps1` |
| Neovim nightly | unstable PPA + vim/vi/editor alternatives | AUR `neovim-nightly-bin` (needs yay/paru) | `brew --HEAD` | not installed |
| Oh My Zsh + plugins | git clone | same | same | — |
| WezTerm (GUI terminal; skipped on WSL) | official fury repo (nightly) + x-terminal-emulator | pacman | — (unmanaged) | — |
| AUR helper (yay-bin) | — | AUR makepkg | — | — |
| Git / PowerShell 7 / Windows Terminal / PowerToys | — | — | — | winget with `--proxy` |

### Installed package list (exact names per package manager)

| Platform | Packages |
|---|---|
| Ubuntu/Debian (apt) | `zoxide zsh fzf ripgrep btop jq git wget curl unzip build-essential netcat-openbsd proxychains4 software-properties-common` |
| Arch (pacman) | `zoxide zsh eza fzf yazi uv ripgrep btop jq git wget curl unzip base-devel openbsd-netcat proxychains-ng` |
| macOS (brew) | `zoxide bash-completion xmake connect proxychains-ng eza fzf yazi ripgrep btop jq wget node` |
| Windows (winget) | `Git.Git` `OpenJS.NodeJS.LTS` `Microsoft.PowerShell` `Microsoft.WindowsTerminal` `Microsoft.PowerToys` |

Outside the package managers (all platforms, channels per the matrix above):

- **rust nightly** (rustup), **uv**, **Node.js LTS** (nvm; brew on mac), **Codex CLI** (npm), **Claude Code** (official installer)
- **eza** (cargo/binary on Ubuntu), **yazi** (official apt repo on Ubuntu), **Neovim nightly** (PPA / AUR / brew --HEAD)
- **Oh My Zsh** + plugins: `zsh-syntax-highlighting` `zsh-autosuggestions` `zsh-completions`

Conventions baked into the scripts:

- Installers must never touch managed rc files — PATH/env bootstrap lives in
  `~/.config/shell/profile.sh` (rustup `--no-modify-path`, `UV_NO_MODIFY_PATH=1`,
  nvm `PROFILE=/dev/null`).
- Windows winget proxy needs the admin setting `ProxyCommandLineOptions`; the script
  checks it first and triggers a one-time UAC elevation when missing.
- Windows deliberately skips nvim and the fzf/rg/eza/zoxide/yazi CLI family.
- apt installs are partitioned against unknown packages, so one missing name cannot
  void the whole transaction; failed components are collected and reported at the end.
- apt is forced to IPv4 globally (`/etc/apt/apt.conf.d/99force-ipv4`) to avoid update
  hangs on flaky IPv6 routes.

## Optional: full dev toolchain (embedded / OpenWrt builds)

> Everything from the former "manual bootstrap" is now automated in run_once:
> apt IPv4 forcing, WezTerm (fury repo + default-terminal alternatives, skipped on
> WSL), and the AUR helper (yay-bin) are installed by the setup scripts; the pip
> China mirror ships in the managed configs (POSIX: `~/.config/pip/pip.conf`;
> Windows: `%APPDATA%\pip\pip.ini`) — no `pip config set`.

Not part of the managed setup — install on build machines only:

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

## What's Managed

| Config | Path | Description |
|---|---|---|
| chezmoi itself | `~/.config/chezmoi/chezmoi.toml` | Generated from `.chezmoi.toml.tmpl` at the source root (chezmoi refuses to manage its own config as a regular file); autoCommit/autoPush disabled, commits are manual |
| zsh | `~/.zshrc`, `~/.p10k.zsh` | Zsh + Powerlevel10k (loads nvm) |
| bash | `~/.bashrc` | Bash config (loads nvm + completion) |
| shell | `~/.config/shell/profile.sh` | Shared PATH/env bootstrap (cargo, nvm, uv, custom scripts, kimi-code) |
| claude | `~/.claude/` | Claude Code settings (templated: WSL render drops hardcoded proxy) |
| codex | `~/.codex/AGENTS.md`, `~/.codex/config.toml`, `~/.codex/skills/` | Codex instructions (symlink to Claude's CLAUDE.md); config.toml uses a `modify_` script pinning only model/model_reasoning_effort/service_tier/project_doc_fallback_filenames/status_line, unions `[projects]`, passes nux counters through |
| kimi | `~/.kimi-code/config.toml`, `~/.kimi-code/tui.toml` | Kimi Code CLI (config.toml uses a `modify_` script — pins only the enforced keys, passes the rest through to the CLI; tui.toml fully managed. Credentials not managed) |
| agents | `~/.agents/skills/`, `~/.agents/AGENTS.md` | Shared agent skills (claude / codex); AGENTS.md symlinks to CLAUDE.md so kimi picks it up (its generic user-level location) |
| cargo | `~/.cargo/config.toml` | Rust cargo config (templated: no proxy line on WSL) |
| kitty | `~/.config/kitty/` | Kitty terminal |
| alacritty | `~/.config/alacritty/` | Alacritty terminal |
| wezterm | `~/.config/wezterm/` | WezTerm terminal |
| starship | `~/.config/starship.toml` | Starship prompt |
| lazygit | `~/.config/lazygit/` | Lazygit TUI |
| neofetch | `~/.config/neofetch/` | Neofetch + custom ASCII art |
| pip | `~/.config/pip/pip.conf` (POSIX), `%APPDATA%\pip\pip.ini` (Windows) | pip USTC mirror, both platforms |

## Custom Scripts

All in `~/.custom_scripts/`, cross-platform (Linux / macOS / Windows).

Proxy host is a single source of truth: `cc-proxy-host` prints the right address
(WSL NAT → default gateway, detected at runtime; everywhere else → `127.0.0.1`).
Every other script builds on it. Env-var layer stays `http://` (wget/pip/Node
compatible); proxychains and SSH tunneling use socks5.

**proxychains auto-config** (mac / Linux / WSL): login shells run
`export PROXYCHAINS_CONF_FILE="$(cc-pc --refresh)"` (see profile.sh); the variable
takes precedence over `/etc/proxychains4.conf`, so a bare `proxychains4 <cmd>` uses
the dynamic config — after a WSL reboot, a new terminal picks up the new gateway
automatically. `sudo` strips env vars; for root use `cc-install` / `cc-pc` (explicit
`-f` internally). macOS caveat: SIP blocks proxychains injection into system binaries
(`/usr/bin/*`); it works for brew-installed programs.

| Command | Description |
|---|---|
| `cc-proxy-host` | Print proxy host (WSL NAT → gateway, else 127.0.0.1) |
| `cc-claude [kill]` | Launch Claude Code with proxy / kill all Claude processes |
| `cc-codex [kill]` | Launch Codex CLI with proxy |
| `cc-kimi [kill]` | Launch Kimi Code CLI (K3 + max thinking + auto permission, no proxy) |
| `cc-codex-app` | macOS: set proxy env (launchctl) for Codex desktop app |
| `source cc-proxy [off]` | Set/unset proxy env + git proxy for current shell |
| `cc-pc <cmd>` | Run command through proxychains with dynamically generated conf |
| `cc-install <pkg>…` | Install packages via proxied apt / brew |
| `cc-update` | System update (apt / brew / winget) |
| `cc-synctime [offset]` | Sync time and set timezone (NTP is UDP — no proxy involved) |

```bash
cc-claude                    # Start Claude with proxy (host auto-detected)
cc-kimi                      # Start Kimi (K3 / max thinking / auto permission)
cc-kimi -c                   # Args starting with - pass through: resume last session
source cc-proxy              # Enable proxy env in current shell
source cc-proxy off          # Disable proxy
cc-pc git clone <url>        # One-off command through proxychains
cc-install btop              # Proxied apt/brew install
cc-update                    # apt / brew / winget upgrade
cc-synctime                  # UTC+8 (default); cc-synctime -5 → New York
```

## Cheat Sheet

```bash
# SSH permissions
chmod 0700 ~/.ssh
chmod 0644 ~/.ssh/authorized_keys
chmod 0644 ~/.ssh/id_ed25519.pub
chmod 0600 ~/.ssh/id_ed25519

# Git proxy
git config --global http.proxy http://127.0.0.1:1080
git config --global https.proxy http://127.0.0.1:1080
# Unset
git config --global --unset http.proxy
git config --global --unset https.proxy

# Git credential store
git config --global credential.helper store

# Remove CUDA
sudo apt --purge remove "*cuda*" "*cublas*" "*cufft*" "*cufile*" "*curand*" \
  "*cusolver*" "*cusparse*" "*gds-tools*" "*npp*" "*nvjpeg*" "nsight*" "*nvvm*"

# Remove NVIDIA drivers
sudo apt --purge remove "*nvidia*" "libxnvctrl*"
sudo apt autoremove -y
sudo apt install linux-headers-$(uname -r)
```

## Structure

```
dotfiles/
├── dot_*                            # Dotfiles (chezmoi naming)
├── private_dot_config/              # ~/.config/ contents
├── dot_custom_scripts/              # Cross-platform scripts (.tmpl)
├── dot_agents/skills/               # Shared agent skills (claude/codex symlink here)
├── dot_local/bin/create_env         # ~/.local/bin/env placeholder (uv PATH bootstrap)
├── .chezmoiignore.tmpl              # OS-specific file filtering
├── run_once_darwin_setup.sh.tmpl    # First-run setup (macOS)
├── run_once_linux_setup.sh.tmpl     # First-run setup (Linux)
└── run_once_windows_setup.ps1.tmpl  # First-run setup (Windows)
```
