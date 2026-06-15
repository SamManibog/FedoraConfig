#!/usr/bin/env python3

import subprocess
from datetime import datetime
import sys

statePath = "/tmp/waybar-check-updates"

timeFormat = "%I:%M %p"
pendingUpdatesIcon = "󱑥"
loadingUpdatesIcon = "󰦗"
noUpdatesIcon = "󰸡"
noInternetIcon = "󰗖"

# check if updates have been checked for previously
lastCheckedUpdates = None
lastCheckedTime = None
try:
    with open(statePath, "r", encoding="utf-8") as stateFile:
        lines = stateFile.readlines()
        lastCheckedUpdates = int(lines[0])
        lastCheckedTime = str(lines[1])
except Exception:
    pass

if lastCheckedUpdates == None or lastCheckedTime == None:
    lastCheckedUpdates = None
    lastCheckedTime = None

# determine and print loading widget
loadingClasses = '"class": "loading-updates"'
loadingTooltip = '"tooltip": "Searching For Updates..."'
if lastCheckedUpdates != None:
    if lastCheckedUpdates > 0:
        loadingClasses = '"class": [ "loading-updates", "has-updates" ]'
        loadingTooltip = f'"tooltip": "Searching For Updates...\\n\\nUpdates Since Last Check: {lastCheckedUpdates}\\nLast Check: {lastCheckedTime}"'
    else:
        loadingClasses = '"class": [ "loading-updates", "no-updates" ]'
        loadingTooltip = f'"tooltip": "Searching For Updates...\\n\\nNo Updates Since Last Check.\\nLast Checked: {lastCheckedTime}"'

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

# if we don't have internet print no internet widget
hasInternet = subprocess.run(
    "ping -c 1 8.8.8.8",
    shell=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL).returncode == 0

if not hasInternet:
    noWifiClasses = '"class": "no-wifi-updates"'
    noWifiTooltip = '"tooltip": "No Internet Service. Cannot Sync Updates."'
    if lastCheckedUpdates != None:
        if lastCheckedUpdates > 0:
            noWifiClasses = '"class": [ "no-wifi-updates", "has-updates" ]'
            noWifiTooltip = f'"tooltip": "No Internet Service. Cannot Sync Updates.\\n\\nUpdates Since Last Check: {lastCheckedUpdates}\\nLast Check: {lastCheckedTime}"'
        else:
            noWifiClasses = '"class": [ "no-wifi-updates", "no-updates" ]'
            noWifiTooltip = f'"tooltip": "No Internet Service. Cannot Sync Updates.\\n\\nNo Updates Since Last Check.\\nLast Check: {lastCheckedTime}"'

    noInternetJson = f'{{"text": "{noInternetIcon}", {noWifiTooltip}, {noWifiClasses}, "percentage": 0}}'
    print(noInternetJson, flush=True)
    sys.exit()

# get final update widget
timestamp = datetime.now().strftime(timeFormat)

if dnfCount + flatpakCount <= 0:
    noUpdatesJson = f'{{"text": "{noUpdatesIcon}", "tooltip": "No Updates.\\n\\nLast Check: {timestamp}", "class": "no-updates", "percentage": 0}}'
    print(noUpdatesJson, flush=True)
else:
    json = f'{{"text": "{pendingUpdatesIcon}", "tooltip": "DNF Updates: {dnfCount}\\nFlatpak Updates: {flatpakCount}\\nTotal Updates: {dnfCount + flatpakCount}\\n\\nLast Check: {timestamp}", "class": "has-updates", "percentage": 0}}'
    print(json, flush=True)

# save state
with open(statePath, "w", encoding="utf-8") as stateFile:
    stateFile.write(f"{str(dnfCount + flatpakCount)}\n{timestamp}")
