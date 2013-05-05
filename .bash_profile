export DEV=/data


# setup command prompt
PS1="\u@\h:\w> "

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
alias ls='ls -F'
alias ll='ls -lah'
alias lls='ll -trh'
alias bzip='bzip2'
alias bunzip='bunzip2'
alias rr='redis-cli get'
alias rk='redis-cli keys "*" | sort'
alias start_nginx='sudo service nginx start'
alias stop_nginx='sudo service nginx stop'
alias restart_nginx='sudo service nginx restart'
alias start_memcache='sudo service memcached start'
alias stop_memcache='sudo service memcached stop'
alias restart_memcache='sudo service memcached restart'
