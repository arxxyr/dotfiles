# 配置原理


原文地址：
```
https://www.atlassian.com/git/tutorials/dotfiles
```

## 原标题：The best way to store your dotfiles: A bare Git repository

译者注：本文的 dotfiles 原意指的是一些隐藏的目录或者文件，但由于实际需要管理的一般是配置文件。所以在翻译中我就把 dotfile 引申为 配置文件。

声明：标题有点绝对，肯定也有解决该问题的其他好方法。我只是介绍下我认为比较好的方案。

最近我在 Hacker News 上看了很多人关于管理他们配置文件的方法。用户 StreakyCobra 所展示的方法非常棒，我也打算像他一样管理配置文件。而且条件很简单，我只要事先安装好 Git 即可。

对于这套方案，按照他的原话说就是：

没有用到任何额外的工具，也没有用到 symlinks，只是用到了版本管理工具。你可以为不同的电脑创建不同的分支，也可以在新电脑上直接获得已经保存的配置。

这个方案特别创建了用于保存配置文件的目录，并且在执行命令中均指定清楚了目录地址，所以不会对你其他的 git 操作产生影响。

## 从头开始
如果你还没有用 Git 仓库管理你的配置文件，你可以用下面的命令快速管理起来。
```
git init --bare $HOME/.cfg
alias config='/usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME'
config config --local status.showUntrackedFiles no
echo "alias config='/usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME'" >> $HOME/.bashrc
```
第一行会创建一个 ~/.cfg 文件夹，Git bare 仓库 会把这个文件夹给管理起来。

然后创建一个 alias，这句话的意思就是当我们在 shell 中执行 config，就等于执行 /usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME ，方便特别管理这个 .cfg 文件夹。

因为是手动指定 $HOME 里的文件并上传，所以我们将 status.showUntrackedFiles 关闭，这样在查看仓库状态的时候，不会因为其他文件导致显示还有文件没有提交。

由于 alias 是 shell 命令，不能持久化，所以要想重启后还能继续使用。需要把这个 alias 命令写到你现在用的 shell 的配置文件里。（原文里用的是 bash）

然后你就可以用 config 命令去添加、管理你的配置文件了。比如你要把 vim 和 bash 的配置文件都加到 Git 里，就像这样执行命令即可。
```
config status
config add .vimrc 
config commit -m "Add vimrc"
config add .bashrc
config commit -m "Add bashrc"
config push 
```
当然，在执行 config push 前，需要配置下远程仓库。为了照顾 Git 新手，我这边放一下我的操作步骤

```
config remote add origin https://github.com/FlintyLemming/FlintyConfig.git
config branch -M main
config push -u origin main
```
## 需要确认的事情
配置文件中已经包含了当前 shell 的配置文件，并且里面配置了刚才的 alias
把 .cfg 添加到 .gitignore 里，这样在拉取时就不会导致递归问题
```
echo ".cfg" >> .gitignore
```
## 在新环境上找回你的配置
如果你已经在云端仓库保存了你的配置文件，你可以按照下面的步骤取回来：


把仓库里的内容下载下来：

```
git clone --bare <git-repo-url> $HOME/.cfg
```

设置 alias：

```
alias config='/usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME'
```

checkout 云端的配置文件到你的 $HOME 目录下：

```
config checkout
```

上面这步可能会报错，就像这样：

```
error: The following untracked working tree files would be overwritten by checkout:    
    .bashrc     
    .gitignore 
Please move or remove them before you can switch branches. Aborting
```

这是因为你的 目录已经有这些文件了，发生了冲突。解决方法很简单：如果你不需要原来的文件，删掉即可；如果需要，就备份一下。这边提供一个冲突文件自动备份到特定文件夹下的方法：

```
mkdir -p .config-backup && \ config checkout 2>&1 | egrep "\s+\." | awk {'print $1'} | \ xargs -I{} mv {} .config-backup/{}
```

然后重新 checkout

```
config checkout
```

同样把 status.showUntrackedFiles 关闭：

```
config config --local status.showUntrackedFiles no
```

大功告成，现在你可以像之前一样管理配置文件了，就像这样：

```
config status 
config add .vimrc 
config commit -m "Add vimrc" 
config add .bashrc 
config commit -m "Add bashrc" 
config push
```
