#!/usr/bin/env python3

import subprocess
import sys

def onFail(body):
    subprocess.run([
        "notify-send",
        "--app-name=Date & Time",
        "Unable to Sync Timezone",
        body,
    ])
    sys.exit()

ipapiResult = subprocess.run(
    "curl -s https://ipapi.co/timezone",
    shell=True,
    capture_output=True,
    text=True
)

if ipapiResult.returncode != 0:
    onFail("Could not fetch timezone from server.");

timezone = ipapiResult.stdout

timezoneListResult = subprocess.run(
    "timedatectl list-timezones",
    shell=True,
    capture_output=True,
    text=True
)

if timezoneListResult.returncode != 0:
    onFail("Could not load timezone list.");

timezoneList = timezoneListResult.stdout.split("\n")[:-1]

if timezone in timezoneList:
    subprocess.run([
        "timedatectl",
        "set-timezone",
        timezone
    ])
else:
    onFail(f"Fetched timezone was not recognized.");
