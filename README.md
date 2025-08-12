# .cfg


## 在新环境上找回你的配置
如果你已经在云端仓库保存了你的配置文件，你可以按照下面的步骤取回来：

```
sudo pacman -S --needed git lazygit zsh clang cmake llvm unzip neovim ranger ripgrep fzf neofetch python xsel npm wget
```
```
sudo pacman -S --needed alacritty kitty
```
```
curl -o- https://bootstrap.pypa.io/get-pip.py | python
```
```
python -m pip install --upgrade pip
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

安装 powerlevel10k
```
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
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
安装python virtualenv
```
pip install virtualenv virtualenvwrapper -i https://pypi.mirrors.ustc.edu.cn/simple
```


安装yay
```
sudo pacman -S --needed git base-devel && git clone https://aur.archlinux.org/yay.git && cd yay && makepkg -si
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

uv
```
curl -LsSf https://astral.sh/uv/install.sh | sh
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
