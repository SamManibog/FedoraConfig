def verifyConfig(cfg):
    if "download" not in cfg or not callable(cfg["download"]):
        return "config must have a 'download' function with two arguments"
    if "needs_update" not in cfg or not callable(cfg["needs_update"]):
        return "config must have a 'needs_update' function with two arguments"

# downloads a git repository from the given url, returning DownloadPkgResult on success
# if for some reason the repo could not be downloaded, returns None instead
# note: this will overwrite the existing repository
def download(name, cfg):
    return cfg["download"](name, cfg)

# checks if a git repo needs an update
def needsUpdate(ini, cfg):
    return cfg["needs_update"](ini, cfg)
