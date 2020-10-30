export DEV=~/dev

# setup command prompt
export PS1="\u@\h:\w> "
#export PS1="\e[0;31m\u@\h:\w> \e[m "
#export PS1='\[$(tput setaf 1)\]\u@\h:\[$blue$bold\]\w>\[$(tput sgr0)\] '

# history searching
bind '"\e[A": history-search-backward'
bind '"\e[B": history-search-forward'

#
# shortcuts
#

alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias cdd='cd $DEV'
alias vi='vim'
alias ls='ls -aF'
alias ll='ls -laFHh'
alias lls='ll -trh'
alias bzip='bzip2'
alias bunzip='bunzip2'

