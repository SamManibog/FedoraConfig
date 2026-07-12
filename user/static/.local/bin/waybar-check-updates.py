#!/usr/bin/env python3

import subprocess
from datetime import datetime
import sys

statePath = "/tmp/waybar-check-updates"

timeFormat = "%I:%M %p"
hasUpdatesIcon = "󱑥"
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
        loadingTooltip = f'"tooltip": "Searching For Updates...\\n\\n{lastCheckedUpdates} Updates Since Last Check\\nLast Checked at {lastCheckedTime}"'
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
dnfSecurityCount = int(subprocess.run(
    "dnf --skip-file-locks check-update --security -q | grep -Ec 'updates$'",
    capture_output=True,
    text=True,
    shell=True
).stdout)
dnfOtherCount = dnfCount - dnfSecurityCount

# flatpak updates output a table if updates are found
# we just need to count lines except the header here we count newline chars
flatpakCount = int(subprocess.run(
    "flatpak remote-ls --updates | wc -l",
    capture_output=True,
    text=True,
    shell=True
).stdout)

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
            noWifiTooltip = f'"tooltip": "No Internet Service. Cannot Sync Updates.\\n\\n{lastCheckedUpdates} Updates Since Last Check\\nLast Checked at {lastCheckedTime}"'
        else:
            noWifiClasses = '"class": [ "no-wifi-updates", "no-updates" ]'
            noWifiTooltip = f'"tooltip": "No Internet Service. Cannot Sync Updates.\\n\\nNo Updates Since Last Check.\\nLast Checked at {lastCheckedTime}"'

    noInternetJson = f'{{"text": "{noInternetIcon}", {noWifiTooltip}, {noWifiClasses}, "percentage": 0}}'
    print(noInternetJson, flush=True)
    sys.exit()

# get final update widget
timestamp = datetime.now().strftime(timeFormat)

# determine tooltip and classes
tooltipCategories = []
if dnfSecurityCount > 0:
    tooltipCategories.append(f"{dnfSecurityCount} DNF Security Updates")
if dnfOtherCount > 0:
    tooltipCategories.append(f"{dnfOtherCount} Other DNF Updates")
if flatpakCount > 0:
    tooltipCategories.append(f"{flatpakCount} Flatpak Updates")

widgetTooltip = "No Updates."
widgetClass = '"no-updates"'
widgetIcon = noUpdatesIcon
if len(tooltipCategories) > 0:
    widgetTooltip = "\\n".join(tooltipCategories)
    widgetClass = '"has-updates"'
    widgetIcon = hasUpdatesIcon
    if dnfSecurityCount > 0:
        widgetClass = '[ "has-updates", "has-security-updates" ]'
if len(tooltipCategories) > 1:
    widgetTooltip += f"\\nTotal: {dnfCount + flatpakCount}"

widgetTooltip += f"\\n\\nLast Checked at {timestamp}"

outputJson = f'{{"text": "{widgetIcon}", "tooltip": "{widgetTooltip}", "class": {widgetClass}, "percentage": 0}}'
print(outputJson, flush=True)

# save state
with open(statePath, "w", encoding="utf-8") as stateFile:
    stateFile.write(f"{str(dnfCount + flatpakCount)}\n{timestamp}")
