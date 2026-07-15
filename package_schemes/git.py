import subprocess
import tempfile

import putils

def verifyConfig(cfg):
    if not isinstance(cfg, str):
        return "config must be a string url."

# downloads a git repository from the given url, returning DownloadPkgResult on success
# if for some reason the repo could not be downloaded, returns None instead
# note: this will overwrite the existing repository
def download(name, url):
    output_path = putils.PACKAGE_FOLDER / name

    subprocess.run([
        "git",
        "clone",
        "--depth=1",
        url,
        str(output_path)
    ])

    commit = subprocess.run(
        [
            "git",
            "rev-parse",
            "HEAD"
        ],
        capture_output=True,
        text=True,
        cwd=str(output_path)
    ).stdout.split()[0]

    return {
        "commit": commit,
    }

# checks if a git repo needs an update
def needsUpdate(ini, cfg):
    remote = cfg
    commit_hash = ini["commit"]

    head_hash = subprocess.run(
        [
            'git',
            'ls-remote',
            remote,
            'HEAD'
        ],
        capture_output=True,
        text=True,
    ).stdout.split()[0]

    return head_hash != commit_hash

# checks how many commits away a git repo is from the current hash
def getUpdateCount(remote, commit_hash):
    with tempfile.TemporaryDirectory() as dir:
        clone_result = subprocess.run(
            [
                'git',
                'clone',
                '--bare',
                '--filter=blob:none',
                remote,
                dir
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ).returncode

        if clone_result != 0:
            raise ValueError(f"unable to clone repository at {remote}")

        result = subprocess.run(
            [
                'git',
                'rev-list',
                '--left-right',
                '--count',
                f'{commit_hash}...HEAD'
            ],
            capture_output=True,
            text=True,
            cwd=dir
        )

        if result.returncode != 0:
            return True

        ahead_behind_counts = result.stdout.split()

        return int(ahead_behind_counts[0]) + int(ahead_behind_counts[1])

