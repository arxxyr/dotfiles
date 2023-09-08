#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

PS1='[\u@\h \W]\$ '
alias config='/usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME'
. "$HOME/.cargo/env"

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
alias vi='nvim'
alias vim='nvim'
alias ll='ls -ll --color=auto'
alias ls='ls --color=auto'
alias ip='ip -color=auto'
alias grep='grep --color=auto'
alias diff='diff --color=auto'
alias lg='lazygit'
alias ra='ranger'
alias pyq='proxychains -q'
alias config='/usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME'
alias lg_cfg='lazygit --git-dir=$HOME/.cfg/ --work-tree=$HOME'

export MANPAGER="less -R --use-color -Dd+r -Du+b"
export LESS='-R --use-color -Dd+r$Du+b'

# autoload -U compinit && compinit

# rust
export PATH=$PATH:$HOME/.cargo/bin

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
# [[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# virtualenv and virtualenvwrapper
export WORKON_HOME=$HOME/.local/bin/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=$HOME/.local/bin/virtualenv
source $HOME/.local/bin/virtualenvwrapper.sh

# goproxy
export GOPROXY=https://proxy.golang.com.cn,direct

# config
alias config='/usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME'
alias lg_cfg='lazygit --git-dir=$HOME/.cfg/ --work-tree=$HOME'

# ranger
# export RANGER_LOAD_DEFAULT_RC=FALSE

# ruby
export PATH=$PATH:$HOME/.rbenv/bin

# black
export PATH=$PATH:$HOME/.local/bin


export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Add RVM to PATH for scripting. Make sure this is the last PATH variable change.
export PATH="$PATH:$HOME/.rvm/bin"

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('$HOME/miniconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        . "$HOME/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="$HOME/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# source /opt/ros/humble/setup.bash
# burger waffle waffle_pi
export TURTLEBOT3_MODEL=waffle

# >>> xmake >>>
[[ -s "$HOME/.xmake/profile" ]] && source "$HOME/.xmake/profile" # load xmake profile
# <<< xmake <<<



