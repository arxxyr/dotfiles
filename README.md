# dotfiles

Managed with [chezmoi](https://www.chezmoi.io/). Cross-platform (Linux + Windows).

## Quick Start

### New Machine

```bash
# Install chezmoi and apply all configs in one command
chezmoi init --apply git@github.com:arxxyr/dotfiles.git
```

### Daily Usage

```bash
# Config changed? Update and auto-push
chezmoi add ~/.zshrc

# Add new config file
chezmoi add ~/.config/xxx/config.yml

# See what changed
chezmoi diff
```

## What's Managed

| Config | Path | Description |
|---|---|---|
| zsh | `~/.zshrc`, `~/.p10k.zsh` | Zsh + Powerlevel10k |
| bash | `~/.bashrc` | Bash config |
| neovim | `~/.claude/` | Claude Code settings |
| cargo | `~/.cargo/config.toml` | Rust cargo config |
| kitty | `~/.config/kitty/` | Kitty terminal |
| alacritty | `~/.config/alacritty/` | Alacritty terminal |
| wezterm | `~/.config/wezterm/` | WezTerm terminal |
| lazygit | `~/.config/lazygit/` | Lazygit TUI |
| ranger | `~/.config/ranger/` | Ranger file manager |
| neofetch | `~/.config/neofetch/` | Neofetch + custom ASCII art |
| pip | `~/.config/pip/pip.conf` | Pip mirror config |

## Custom Scripts

All scripts live in `~/.custom_scripts/` and work on both Linux and Windows:

| Command | Description |
|---|---|
| `cc-claude` | Launch Claude Code with proxy |
| `cc-claude kill` | Kill all Claude processes |
| `cc-proxy` | Set proxy for current terminal (use with `source`) |
| `cc-proxy off` | Disable proxy |
| `cc-update` | System update (apt on Linux, winget on Windows) |
| `cc-synctime [offset]` | Sync time and set timezone by UTC offset |

### Examples

```bash
cc-claude                    # Start Claude with proxy
cc-claude kill               # Kill all Claude processes

source cc-proxy              # Enable proxy (default: 127.0.0.1:10808)
source cc-proxy off          # Disable proxy

cc-update                    # apt upgrade (Linux) / winget upgrade (Windows)

cc-synctime                  # Set UTC+8 (default)
cc-synctime -8               # Set UTC-8 (Los Angeles)
cc-synctime 0                # Set UTC
cc-synctime 9                # Set UTC+9 (Tokyo)
```

## Prerequisites

### Linux

```bash
sudo apt install -y zsh git curl

# Oh My Zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Zsh plugins
git clone https://github.com/zsh-users/zsh-syntax-highlighting $ZSH_CUSTOM/plugins/zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-autosuggestions $ZSH_CUSTOM/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-completions $ZSH_CUSTOM/plugins/zsh-completions
```

### Windows

```powershell
# PowerShell 7+
winget install Microsoft.PowerShell
```

## Structure

```
dotfiles/
├── dot_*                          # Dotfiles (chezmoi naming)
├── private_dot_config/            # ~/.config/ contents
├── dot_custom_scripts/            # Cross-platform scripts (.tmpl)
├── .chezmoiignore.tmpl            # OS-specific file filtering
├── run_once_linux_setup.sh.tmpl   # First-run setup (Linux)
└── run_once_windows_setup.ps1.tmpl # First-run setup (Windows)
```
