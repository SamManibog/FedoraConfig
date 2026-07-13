# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]; then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
if [ -d ~/.bashrc.d ]; then
    for rc in ~/.bashrc.d/*; do
        if [ -f "$rc" ]; then
            . "$rc"
        fi
    done
fi
unset rc

# yazi shell integration
function y() {
	local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
	command yazi "$@" --cwd-file="$tmp"
	IFS= read -r -d '' cwd < "$tmp"
	[ "$cwd" != "$PWD" ] && [ -d "$cwd" ] && builtin cd -- "$cwd"
	command rm -f -- "$tmp"
}

# make setup.py global
function home-setup() {
     python ~/FedoraConfig/setup.py "$@"
}

# make saver.py global
function home-copy() {
     python ~/FedoraConfig/saver.py "$@"
}

# set neovim as default editor
export EDITOR='nvim'
export VISUAL='nvim'

# export cs project locations
export PRO_PICKER_DIR_LOCATIONS='~/cs_projects'
export PRO_PICKER_LOCATIONS='~/.config/nvim'

