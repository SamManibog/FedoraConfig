#!/usr/bin/env python3

import subprocess
import signal
import sys

# register a signal so we can ensure that exiting always sends a refresh signal
def gracefulExit(signum, frame):
    print(f"Received signal {signum}. Cancelling...")
    sys.exit(0)

signal.signal(signal.SIGTERM, gracefulExit)
signal.signal(signal.SIGINT, gracefulExit)

try:
    cmd = "sudo dnf -y update --refresh ; flatpak update -y"
    print(cmd)
    subprocess.run(cmd, shell=True)
finally:
    # send a refresh signal
    subprocess.run("pkill -SIGRTMIN+4 waybar", shell=True)
    subprocess.run("waybar-post-update.py", shell=True)

