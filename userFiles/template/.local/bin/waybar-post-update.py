#!/usr/bin/env python3

import subprocess

# fix grub timeout settings after a potential kernel update
def fixGrubTimeout():
    grubSettings = '''GRUB_TIMEOUT=0
GRUB_DISTRIBUTOR="$(sed 's, release .*$,,g' /etc/system-release)"
GRUB_DEFAULT=saved
GRUB_DISABLE_SUBMENU=true
GRUB_TERMINAL_OUTPUT="console"
GRUB_CMDLINE_LINUX="rhgb quiet"
GRUB_DISABLE_RECOVERY="true"
GRUB_ENABLE_BLSCFG=true'''
    print("Removing Grub Timeout")
    subprocess.run([
        "sudo",
        "sh",
        "-c",
        f"cat << 'EOF' > /etc/default/grub\n{grubSettings}\nEOF"
    ])
    subprocess.run(f"sudo grub2-mkconfig -o /boot/grub2/grub.cfg", shell=True)

# fixGrubTimeout()
