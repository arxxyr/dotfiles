# dotfiles

Managed with [chezmoi](https://www.chezmoi.io/). Cross-platform (Linux + Windows).

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

## Bootstrap (Linux)

Fresh Ubuntu/Debian setup — run before `chezmoi init`:

```bash
# System packages
sudo apt update -y && sudo apt full-upgrade -y
sudo apt install -y ack antlr3 asciidoc autoconf automake autopoint binutils bison build-essential \
  bzip2 ccache clang cmake cpio curl device-tree-compiler ecj fastjar flex gawk gettext gcc-multilib \
  g++-multilib git gnutls-dev gperf haveged help2man intltool lib32gcc-s1 libc6-dev-i386 libelf-dev \
  libglib2.0-dev libgmp3-dev libltdl-dev libmpc-dev libmpfr-dev libncurses-dev libpython3-dev \
  libreadline-dev libssl-dev libtool libyaml-dev libz-dev lld llvm lrzsz mkisofs msmtp nano \
  ninja-build p7zip p7zip-full patch pkgconf python3 python3-pip python3-ply python3-docutils \
  python3-pyelftools qemu-utils re2c rsync scons squashfs-tools subversion swig texinfo uglifyjs \
  upx-ucl unzip vim wget xmlto xxd zlib1g-dev zstd clangd clang-tidy zsh ranger ripgrep fzf \
  neofetch python3-dev zoxide xsel btop net-tools proxychains4 jq

# Force apt to use IPv4
echo 'Acquire::ForceIPv4 "true";' | sudo tee /etc/apt/apt.conf.d/99force-ipv4 > /dev/null

# Neovim (unstable PPA)
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:neovim-ppa/unstable
sudo apt update && sudo apt install -y neovim

# WezTerm
curl -fsSL https://apt.fury.io/wez/gpg.key | sudo gpg --yes --dearmor -o /usr/share/keyrings/wezterm-fury.gpg
echo 'deb [signed-by=/usr/share/keyrings/wezterm-fury.gpg] https://apt.fury.io/wez/ * *' | sudo tee /etc/apt/sources.list.d/wezterm.list
sudo chmod 644 /usr/share/keyrings/wezterm-fury.gpg
sudo apt update && sudo apt install -y wezterm-nightly
sudo update-alternatives --config x-terminal-emulator

# Oh My Zsh + plugins
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-syntax-highlighting $ZSH_CUSTOM/plugins/zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-autosuggestions $ZSH_CUSTOM/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-completions $ZSH_CUSTOM/plugins/zsh-completions

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Python / Node / Rust tools
pip install pynvim black
sudo npm i -g neovim prettier
cargo install stylua

# pip mirror (China)
pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple

# Apply dotfiles
chezmoi init --apply git@github.com:arxxyr/dotfiles.git
source ~/.zshrc
```

### Arch Linux (optional)

```bash
sudo pacman -S --needed git base-devel && git clone https://aur.archlinux.org/yay.git && cd yay && makepkg -si
```

## What's Managed

| Config | Path | Description |
|---|---|---|
| zsh | `~/.zshrc`, `~/.p10k.zsh` | Zsh + Powerlevel10k |
| bash | `~/.bashrc` | Bash config |
| claude | `~/.claude/` | Claude Code settings |
| cargo | `~/.cargo/config.toml` | Rust cargo config |
| kitty | `~/.config/kitty/` | Kitty terminal |
| alacritty | `~/.config/alacritty/` | Alacritty terminal |
| wezterm | `~/.config/wezterm/` | WezTerm terminal |
| lazygit | `~/.config/lazygit/` | Lazygit TUI |
| ranger | `~/.config/ranger/` | Ranger file manager |
| neofetch | `~/.config/neofetch/` | Neofetch + custom ASCII art |
| pip | `~/.config/pip/pip.conf` | Pip mirror config |

## Custom Scripts

All in `~/.custom_scripts/`, cross-platform (Linux + Windows):

| Command | Description |
|---|---|
| `cc-claude` | Launch Claude Code with proxy |
| `cc-claude kill` | Kill all Claude processes |
| `source cc-proxy` | Set proxy for current terminal |
| `source cc-proxy off` | Disable proxy |
| `cc-update` | System update (apt / winget) |
| `cc-synctime [offset]` | Sync time and set timezone |

```bash
cc-claude                    # Start Claude with proxy
cc-claude kill               # Kill all Claude processes
source cc-proxy              # Enable proxy (default: 127.0.0.1:10808)
source cc-proxy off          # Disable proxy
cc-update                    # apt upgrade / winget upgrade
cc-synctime                  # UTC+8 (default)
cc-synctime -5               # UTC-5 (New York)
cc-synctime 0                # UTC
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
sudo apt-get --purge remove "*cuda*" "*cublas*" "*cufft*" "*cufile*" "*curand*" \
  "*cusolver*" "*cusparse*" "*gds-tools*" "*npp*" "*nvjpeg*" "nsight*" "*nvvm*"

# Remove NVIDIA drivers
sudo apt-get --purge remove "*nvidia*" "libxnvctrl*"
sudo apt-get autoremove -y
sudo apt install linux-headers-$(uname -r)
```

## Structure

```
dotfiles/
├── dot_*                            # Dotfiles (chezmoi naming)
├── private_dot_config/              # ~/.config/ contents
├── dot_custom_scripts/              # Cross-platform scripts (.tmpl)
├── .chezmoiignore.tmpl              # OS-specific file filtering
├── run_once_linux_setup.sh.tmpl     # First-run setup (Linux)
└── run_once_windows_setup.ps1.tmpl  # First-run setup (Windows)
```
