import subprocess
import sys

pipepath = "/tmp/wobpipe"

mode = sys.argv[1]

def getOutput(cmd):
    return subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    ).stdout

def parseVolume(volumeOutput):
    substr = volumeOutput[8:-1]

    # true when device is muted
    if substr[-1] == "]":
        return 0.0
    else:
        return float(substr)

current = None
max = None
fraction = None
if mode == "o":
    # audio out
    current = parseVolume(getOutput("wpctl get-volume @DEFAULT_AUDIO_SINK@"))
    max = 1.0
elif mode == "i":
    # audio in
    current = parseVolume(getOutput("wpctl get-volume @DEFAULT_AUDIO_SOURCE@"))
    max = 2.0
elif mode == "b":
    # brightness
    current = float(getOutput("brightnessctl g")[:-1])
    max = float(getOutput("brightnessctl m")[:-1])
else:
    print(
        "got invalid mode, mode should be one of...\n"
            "o (audio output)\n"
            "i (audio input)\n"
            "b (brightness)",
        file=sys.stderr
    )

if max == 0:
    fraction = 1.0
else:
    fraction = current / max

percent = str(round(fraction * 100))

subprocess.run(f"truncate -s 0 {pipepath} ; echo '{percent}' > {pipepath}", shell=True)

