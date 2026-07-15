# defines code related to saving files to setup

import subprocess
from pathlib import Path
import sys

import utils

helpText = ("Usage: saver.py [FLAGS] [PATHS...]\n"
    "Copy a file or directory from the home directory into the config\n"
    "\n"
    "With no PATHS, display a menu to select one or multiple folders\n"
    "\t-s save to the static directory\n"
    "\t-t save to the template directory\n"
    "\t-r when no PATHS, sort entries by most recent (default behavior)\n"
    "\t-o when no PATHS, sort entries by oldest\n"
    "\t-a when no PATHS, sort entries alphabetically\n"
    "\t-A when no PATHS, sort entries reverse alphabetically\n")

maxListed = 32

dstFlags = {
    "s": "static",
    "t": "template",
}

# get all entries in the current directory in sorted order
def getEntryList(sort):
    keyMap = {
        "recent": lambda x: x.stat(follow_symlinks=False).st_mtime,
        "oldest": lambda x: x.stat(follow_symlinks=False).st_mtime,
        "alphabetical": lambda x: x.stat(follow_symlinks=False).st_mtime,
        "reverse-alphabetical": lambda x: x.stat(follow_symlinks=False).st_mtime,
    }
    reverseMap = {
        "reverse-alphabetical",
        "recent",
    }

    entries = []
    for entry in Path.cwd().iterdir():
        if not entry.is_symlink():
            entries.append(entry)
    entries.sort(key=keyMap[sort], reverse=sort in reverseMap)

    return entries

# ask the user for the module that they want to copy to
def askTargetModule(module_list):
    print("Modules:")
    for idx in range(0, len(module_list)):
        module = module_list[idx]
        print(f"{str(idx).rjust(3)} - {module}")

    prompt = "Enter the index of the module you would like to edit.\n"
    while True:
        inputStr = input(prompt)
        if not inputStr:
            print("Received empty selection. Retry.")
            continue;

        inputNum = -1
        try:
            inputNum = int(inputStr)
        except ValueError:
            pass

        if inputNum < 0 or inputNum >= len(module_list):
            print(f"Received invalid selection '{inputStr}'. Retry.")
            continue;

        return inputNum

# ask the user for the module they want to copy to, and get its path
def getTargetModulePath():
    module_list = utils.listEnabledModules()
    module_paths = utils.getModulePaths(module_list)

    module_list.insert(0, "[MAIN]")

    return module_paths[askTargetModule(module_list)]

# ask the user for selected entries
def askSelectedEntries(entries):
    print("Entries:")
    for idx in range(0, len(entries)):
        entry = entries[idx]
        slash = ""
        if entry.is_dir():
            slash = "/"
        print(f"{str(idx).rjust(3)} - {entry}{slash}")

    prompt = "Enter a space-delimited list of entries to copy (by index).\n"
    while True:
        inputStr = input(prompt)
        inputStrList = inputStr.split()
        inputList = []
        for inputStr in inputStrList:
            num = int(inputStr)
            if num < 0 or num >= maxListed:
                print(f"Got invalid selection: {inputStr}.\n")
                continue;
            else:
                inputList.append(entries[num])
        if inputList:
            return inputList
        else:
            print("Received empty selection. Retry.")

def getPathsToCopy(sort):
    entries = getEntryList(sort)
    selectedEntries = askSelectedEntries(entries[:maxListed])
    return selectedEntries

def askDstType():
    char = None
    while not char in dstFlags:
        char = input("Enter a destination.\ns - staticFiles\nt - template\n")

    return dstFlags[char]

def cwd_is_in_home():
    try:
        Path.cwd().relative_to(Path.home())
        return True
    except ValueError:
        return False

def save(sort):
    try:
        # determine which files are being copied
        selected_paths = getPathsToCopy(sort)

        # determine which module is being modified
        module_path = getTargetModulePath()
        module_path_data = utils.getModuleSubdirectories(module_path)
        pathMap = {
            "home": {
                "static": module_path_data["staticUserFiles"],
                "template": module_path_data["templateUserFiles"],
                "actual": Path.home(),
            },
            "system": {
                "static": module_path_data["staticSystemFiles"],
                "template": module_path_data["templateSystemFiles"],
                "actual": Path("/"),
            }
        }

        # determine which module directory is being modified
        saveDst = askDstType()

        # make directories up to the parent directory
        pathData = None
        if cwd_is_in_home():
            pathData = pathMap["home"]
        else:
            pathData = pathMap["system"]

        logicalHome = pathData[saveDst]
        srcHomeRelativeParent = selected_paths[0].parent.relative_to(pathData["actual"])
        dstParent = logicalHome / srcHomeRelativeParent

        subprocess.run([
            "mkdir",
            "-p",
            str(dstParent)
        ])

        # recursively copy selected paths into the destination
        for src in selected_paths:
            dst = logicalHome / src.relative_to(pathData["actual"])
            utils.cpImproved(src, dst, alwaysAsk=True)

    except KeyboardInterrupt:
        print("Stopping: interrupt recieved.")
