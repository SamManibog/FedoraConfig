#!/usr/bin/env python3

import subprocess
import sys

# send a notification on fail with the given body
def onFail(body):
    subprocess.run([
        "notify-send",
        "--app-name=Date & Time",
        "Unable to Sync Timezone",
        body,
    ])
    sys.exit()

# the result of ip-based timezone lookup
ipapiResult = subprocess.run(
    "curl -s https://ipapi.co/timezone",
    shell=True,
    capture_output=True,
    text=True
)

if ipapiResult.returncode != 0:
    onFail("Could not fetch timezone from server.");

timezone = ipapiResult.stdout

# the result of querying recognized timezones
timezoneListResult = subprocess.run(
    "timedatectl list-timezones",
    shell=True,
    capture_output=True,
    text=True
)

if timezoneListResult.returncode != 0:
    onFail("Could not load timezone list.");

timezoneList = timezoneListResult.stdout.split("\n")[:-1]

# for security, ensure that timezone valid
if timezone in timezoneList:
    subprocess.run([
        "timedatectl",
        "set-timezone",
        timezone
    ])
else:
    onFail(f"Fetched timezone was not recognized.");
