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

sortFlags = {
    "r": "recent",
    "o": "oldest",
    "a": "alphabetical",
    "A": "reverse-alphabetical",
}

# parses system args
def parseArgs(args):
    argObject = {
        "paths": [],
    }

    def parseGroup(flagGroup):
        for f in flagGroup:
            if f in dstFlags:
                if "saveDst" in argObject:
                    raise ValueError("You can only specify one of -s or -t")
                else:
                    argObject["saveDst"] = dstFlags[f]
            elif f in dstFlags:
                if "sort" in argObject:
                    raise ValueError("You can only specify one of -a, -A, -o, or -r")
                else:
                    argObject["sort"] = sortFlags[f]
            else:
                raise ValueError(f"Unrecognized flag '{f}'")

    last_idx = None
    for idx in range(1, len(args)):
        flag = args[idx]
        if flag == "--help":
            print(helpText)
            sys.exit()

        if flag[:1] == "-":
            parseGroup(flag[1:])
        else:
            last_idx = idx
            break;

    if last_idx != None:
        for idx in range(last_idx, len(args)):
            argObject["paths"].append(Path.cwd() / Path(args[idx]))

    if not "sort" in argObject:
        argObject["sort"] = "recent"

    return argObject

# get all entries in the current directory in sorted order
def getEntryList(sort):
    keyMap = {
        "recent": lambda x: x.stat(follow_symlinks=False).st_mtime,
        "oldest": lambda x: x.stat(follow_symlinks=False).st_mtime,
        "alphabetical": lambda x: x.stat(follow_symlinks=False).st_mtime,
        "reverse-alphabetical": lambda x: x.stat(follow_symlinks=False).st_mtime,
    }
    reverseMap = {
        "reverse-alphabetical": True,
        "recent": True,
    }

    entries = []
    for entry in Path.cwd().iterdir():
        if not entry.is_symlink():
            entries.append(entry)
    entries.sort(key=keyMap[sort], reverse=reverseMap[sort])

    return entries

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

def noPathsCli(sort, max):
    entries = getEntryList(sort)
    selectedEntries = askSelectedEntries(entries[:max])
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

def main(args):
    try:
        argObject = {}

        try:
            argObject = parseArgs(args)
        except ValueError as e:
            print(str(e))
            print(helpText)

        # determine which files are being copied
        if not argObject["paths"]:
            argObject["paths"] = noPathsCli(argObject["sort"], maxListed)

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
        if not "saveDst" in argObject:
            argObject["saveDst"] = askDstType()

        # make directories up to the parent directory
        pathData = None
        if cwd_is_in_home():
            pathData = pathMap["home"]
        else:
            pathData = pathMap["system"]

        logicalHome = pathData[argObject["saveDst"]]
        srcHomeRelativeParent = argObject["paths"][0].parent.relative_to(pathData["actual"])
        dstParent = logicalHome / srcHomeRelativeParent

        subprocess.run(f"mkdir -p {str(dstParent)}", shell=True)

        # recursively copy selected paths into the destination
        for src in argObject["paths"]:
            dst = logicalHome / src.relative_to(pathData["actual"])
            utils.cpImproved(src, dst, alwaysAsk=True)

    except KeyboardInterrupt:
        print("Stopping: interrupt recieved.")

if __name__ == "__main__":
    main(sys.argv)
