#!/usr/bin/env python3

import subprocess
import signal
import sys

def gracefulExit(signum, frame):
    print(f"Received signal {signum}. Cancelling...")
    sys.exit(0)

signal.signal(signal.SIGTERM, gracefulExit)
signal.signal(signal.SIGINT, gracefulExit)

try:
    print("sudo dnf update")
    subprocess.run("sudo dnf update", shell=True)
    print("flatpak update")
    subprocess.run("flatpak update", shell=True)
finally:
    subprocess.run("pkill -SIGRTMIN+4 waybar", shell=True)

