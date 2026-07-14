from urllib.parse import urlsplit

import subprocess
import tempfile
import json

import putils

def verifyConfig(cfg):
    if "user" not in cfg or not isinstance(cfg["user"], str):
        return "config must specify a string user"

    if "repo" not in cfg or not isinstance(cfg["repo"], str):
        return "config must specify a string repo"

# gets the metadata for the latest release
def getLatestMetadata(user, repo):
    url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"

    json_str = subprocess.run(
        [
            "curl",
            "-s",
            url
        ],
        capture_output=True,
        text=True
    ).stdout

    return json.loads(json_str)

# downloads a git repository from the given url, returning DownloadPkgResult on success
# if for some reason the repo could not be downloaded, returns None instead
# note: this will overwrite the existing repository
def downloadRepo(name, cfg):
    user = cfg["user"]
    repo = cfg["repo"]

    meta = getLatestMetadata(user, repo)
    zip_url = meta["zipball_url"]
    version = meta["tag_name"]
    outputPath = putils.PACKAGE_FOLDER / name

    putils.downloadZip(zip_url, outputPath)

    return {
        "user": user,
        "repo": repo,
        "version": version,
    }

# checks if a git repo needs an update
def needsUpdate(ini):
    user = ini["user"]
    repo = ini["repo"]
    meta = getLatestMetadata(user, repo)

    return meta["tag_name"] != ini["version"]

