#!/usr/bin/env python3

import subprocess
import sys

pendingUpdatesIcon = "󱑥"
loadingUpdatesIcon = "󰦗"
noUpdatesIcon = "󰗡"

loadingUpdatesJson = f'{{"text": "{loadingUpdatesIcon}", "tooltip": "Searching For Updates...", "class": "loading-updates", "percentage": 0}}'
noUpdatesJson = f'{{"text": "{noUpdatesIcon}", "tooltip": "No Updates", "class": "no-updates", "percentage": 0}}'

print(loadingUpdatesJson, flush=True)

# dnf updates can have special output, but all updates have lines ending in 'update'
dnfCount = int(subprocess.run(
    "dnf --skip-file-locks check-update --refresh -q | grep -Ec 'updates$'",
    capture_output=True,
    text=True,
    shell=True
).stdout)

# flatpak updates output a table if updates are found
# we just need to count lines except the header
flatpakCount = int(subprocess.run(
    "flatpak remote-ls --updates | wc -l",
    capture_output=True,
    text=True,
    shell=True
).stdout)
if flatpakCount > 0:
    flatpakCount -= 1

if dnfCount + flatpakCount <= 0:
    print(noUpdatesJson, flush=True)
else:
    json = f'{{"text": "{pendingUpdatesIcon}", "tooltip": "DNF Updates: {dnfCount}\\nFlatpak Updates: {flatpakCount}\\nTotal Updates: {dnfCount + flatpakCount}", "class": "has-updates", "percentage": 0}}'
    print(json, flush=True)
