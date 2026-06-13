#!/usr/bin/env python3

import subprocess
from datetime import datetime
import sys

statePath = "/tmp/waybar-check-updates"

timeFormat = "%I:%M %p"
pendingUpdatesIcon = "󱑥"
loadingUpdatesIcon = "󰦗"
noUpdatesIcon = "󰗡"

# check if updates have been checked for previously
lastCheckedUpdates = None
try:
    with open(statePath, "r", encoding="utf-8") as stateFile:
        lines = stateFile.readlines()
        lastCheckedUpdates = int(lines[0])
except Exception:
    pass

# determine and print loading widget
loadingClasses = '"class": "loading-updates"'
loadingTooltip = '"tooltip": "Searching For Updates..."'
if lastCheckedUpdates != None:
    if lastCheckedUpdates > 0:
        loadingClasses = '"class": [ "loading-updates", "has-updates" ]'
        loadingTooltip = f'"tooltip": "Searching For Updates...\\nUpdates Since Last Check: {lastCheckedUpdates}"'
    else:
        loadingClasses = '"class": [ "loading-updates", "no-updates" ]'
        loadingTooltip = '"tooltip": "Searching For Updates...\\nNo Updates Since Last Check"'
loadingUpdatesJson = f'{{"text": "{loadingUpdatesIcon}", {loadingTooltip}, {loadingClasses}, "percentage": 0}}'
print(loadingUpdatesJson, flush=True)

# dnf updates can have special output, but all updates have lines ending in 'updates'
# so just count lines ending with 'updates'
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

# get final update widget
timestamp = datetime.now().strftime(timeFormat)
if dnfCount + flatpakCount <= 0:
    noUpdatesJson = f'{{"text": "{noUpdatesIcon}", "tooltip": "No Updates\\n\\nLast Check: {timestamp}", "class": "no-updates", "percentage": 0}}'
    print(noUpdatesJson, flush=True)
else:
    json = f'{{"text": "{pendingUpdatesIcon}", "tooltip": "DNF Updates: {dnfCount}\\nFlatpak Updates: {flatpakCount}\\nTotal Updates: {dnfCount + flatpakCount}\\n\\nLast Check: {timestamp}", "class": "has-updates", "percentage": 0}}'
    print(json, flush=True)

# save state
with open(statePath, "w", encoding="utf-8") as stateFile:
    stateFile.write(str(dnfCount + flatpakCount))
