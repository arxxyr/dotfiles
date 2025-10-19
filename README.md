# .cfg

## 在新环境上找回你的配置
如果你已经在云端仓库保存了你的配置文件，你可以按照下面的步骤取回来：

```
sudo apt update -y
sudo apt full-upgrade -y
sudo apt install -y ack antlr3 asciidoc autoconf automake autopoint binutils bison build-essential \
  bzip2 ccache clang cmake cpio curl device-tree-compiler ecj fastjar flex gawk gettext gcc-multilib \
  g++-multilib git gnutls-dev gperf haveged help2man intltool lib32gcc-s1 libc6-dev-i386 libelf-dev \
  libglib2.0-dev libgmp3-dev libltdl-dev libmpc-dev libmpfr-dev libncurses-dev libpython3-dev \
  libreadline-dev libssl-dev libtool libyaml-dev libz-dev lld llvm lrzsz mkisofs msmtp nano \
  ninja-build p7zip p7zip-full patch pkgconf python3 python3-pip python3-ply python3-docutils \
  python3-pyelftools qemu-utils re2c rsync scons squashfs-tools subversion swig texinfo uglifyjs \
  upx-ucl unzip vim wget xmlto xxd zlib1g-dev zstd clangd clang-tidy zsh ranger ripgrep fzf  \
  neofetch python3-dev zoxide xsel btop net-tools proxychains4 jq

# 安装 neovim 
sudo apt install software-properties-common
sudo add-apt-repository ppa:neovim-ppa/unstable
sudo apt update
sudo apt install neovim -y

# 安装 wezterm
curl -fsSL https://apt.fury.io/wez/gpg.key | sudo gpg --yes --dearmor -o /usr/share/keyrings/wezterm-fury.gpg
echo 'deb [signed-by=/usr/share/keyrings/wezterm-fury.gpg] https://apt.fury.io/wez/ * *' | sudo tee /etc/apt/sources.list.d/wezterm.list
sudo chmod 644 /usr/share/keyrings/wezterm-fury.gpg

sudo apt update
sudo apt install wezterm-nightly -y
sudo update-alternatives --config x-terminal-emulator

# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 强制 apt 使用 ipv4 下载
echo 'Acquire::ForceIPv4 "true";' | sudo tee /etc/apt/apt.conf.d/99force-ipv4 > /dev/null

```

把仓库里的内容下载下来：

```
git clone --bare git@github.com:arxxyr/dotfiles.git $HOME/.cfg
```

安装oh-my-zsh
```
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```
```
git clone https://github.com/zsh-users/zsh-syntax-highlighting $ZSH_CUSTOM/plugins/zsh-syntax-highlighting
```
```
git clone https://github.com/zsh-users/zsh-autosuggestions $ZSH_CUSTOM/plugins/zsh-autosuggestions
```
```
git clone https://github.com/zsh-users/zsh-completions $ZSH_CUSTOM/plugins/zsh-completions
```


rust
```
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```


设置 alias：

```
alias config='/usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME'
```

checkout 云端的配置文件到你的 $HOME 目录下：

```
config checkout
config submodule update --init --recursive
```
把 status.showUntrackedFiles 关闭：
```
config config --local status.showUntrackedFiles no
```
激活环境
```
source "$HOME/.zshrc"
```
或者
```
source "$HOME/.bashrc"
```
配置pip
```
pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple
```


安装yay
```
# sudo pacman -S --needed git base-devel && git clone https://aur.archlinux.org/yay.git && cd yay && makepkg -si
```

python支持
```
pip install pynvim black
```
npm
```
sudo npm i -g neovim
```
```
sudo npm i -g prettier
```
rust
```
cargo install stylua
```

## Good bash

To chmod .ssh
```
chmod 0700 ~/.ssh
chmod 0644 ~/.ssh/authorized_keys 
chmod 0644 ~/.ssh/id_ed25519.pub 
chmod 0600 ~/.ssh/id_ed25519
```

To remove CUDA Toolkit:
```
sudo apt-get --purge remove "*cuda*" "*cublas*" "*cufft*" "*cufile*" "*curand*" \
 "*cusolver*" "*cusparse*" "*gds-tools*" "*npp*" "*nvjpeg*" "nsight*" "*nvvm*"
```
To remove NVIDIA Drivers:
```
sudo apt-get --purge remove "*nvidia*" "libxnvctrl*"
```
To clean up the uninstall:
```
sudo apt-get autoremove -y
```

```
sudo apt remove --purge '^nvidia-.*'
sudo apt remove --purge '^libnvidia-.*'
sudo apt remove --purge '^cuda-.*'
sudo apt install linux-headers-$(uname -r)

git config --global credential.helper store

git config --global http.proxy http://127.0.0.1:1080
git config --global https.proxy http://127.0.0.1:1080
git config --global --unset http.proxy
git config --global --unset https.proxy
```

time 

```
sudo apt-get install ntpdate					    # 在Ubuntu下更新本地时间
sudo ntpdate time.windows.com
sudo hwclock --localtime --systohc			# 将本地时间更新到硬件上
timedatectl
```
