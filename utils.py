# defines common utility functions for setup

import os
import sys
import subprocess
from pathlib import Path
import filecmp
import difflib
import configparser

CONFIG_PATH = Path.home() / ".config/FedoraConfig"
MODULE_CONFIG_PATH = Path.home() / ".config/FedoraConfig/modules.ini"

# check if an object is a string
def isString(obj):
    return isinstance(obj, str)

# check if an object is a list
def isList(obj):
    return isinstance(obj, list)

# check if an object is a dictionary
def isDict(obj):
    return isinstance(obj, dict)

# convience method to print to stderr
def eprint(obj):
    print(obj, file=sys.stderr)

# prints a colored diff of the two lists of strings
def printColoredDiff(file1_lines, file2_lines, fromfile='', tofile=''):
    # define ANSI color
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"

    # Generate the standard unified diff
    diff = difflib.unified_diff(
        file1_lines,
        file2_lines, 
        fromfile=fromfile,
        tofile=tofile
    )

    diffLines = list(diff)
    if fromfile == '' or tofile == '':
        diffLines = diffLines[2:]

    # Print each line with corresponding colors
    for line in diffLines:
        stripped = line.rstrip('\n')
        if stripped.startswith('+'):
            print(f"{GREEN}{stripped}{RESET}")
        elif stripped.startswith('-'):
            print(f"{RED}{stripped}{RESET}")
        elif stripped.startswith('@'):
            print(f"{CYAN}{stripped}{RESET}")
        else:
            print(stripped)

def askYesNo(prompt):
    char = None
    while True:
        char = input(f"{prompt} [y/n] ")

        if char.lower() == "y":
            return True
        if char.lower() == "n":
            return False

# improve the linux cp function by skipping copy if contents match
# if the copy replaces a file with different contents, prints a diff
# after is a callback with two positional parameters
#   1) path - the path of the file being written or skipped (the destination)
#   2) written - whether or not a write operation occurred
def cpImproved(
    src,
    dst,
    recursive=True,
    allowOverwrite=True,
    alwaysAsk=False,
    sudo=False,
    after=lambda *args: None
):
    srcPath = Path(src)
    dstPath = Path(dst)
    sudoPrefix = ""
    if sudo:
        sudoPrefix = "sudo "

    if srcPath.is_file():
        # base case: src is a file

        if dstPath.is_file():
            # check if files are different
            if filecmp.cmp(srcPath, dstPath, shallow=False):
                print(f"skipped '{str(dstPath)}' (exact copy)")
                after(dstPath, False)
                return

            if not allowOverwrite:
                print(f"skipped '{str(dstPath)}' (overwrite disabled)")
                after(dstPath, False)
                return

            # get a diff between the files
            with open(srcPath, 'r', encoding='utf-8') as srcFile, open(dstPath, 'r', encoding='utf-8') as dstFile:
                srcLines = srcFile.readlines()
                dstLines = dstFile.readlines()
                    
                print(f"attempting to overwrite '{str(dstPath)}'")
                print("difference:")
                printColoredDiff(
                    dstLines, 
                    srcLines
                )

            # prompt user to confirm copy
            print()
            if askYesNo(f"overwrite '{str(dstPath)}'?"):
                subprocess.run(f"{sudoPrefix}cp {str(srcPath)} {str(dstPath)}", shell=True)
                print(f"wrote '{str(dstPath)}'")
                after(dstPath, True)

        else:
            # dst does not exist
            shouldWrite = True
            if alwaysAsk:
                shouldWrite = askYesNo(f"write file '{str(dstPath)}'?")

            if shouldWrite:
                subprocess.run(f"{sudoPrefix}cp {str(srcPath)} {str(dstPath)}", shell=True)
                print(f"wrote '{str(dstPath)}'")
                after(dstPath, True)

    elif srcPath.is_dir():
        # inductive case: src is a folder

        didWrite = False

        if not dstPath.is_dir():
            shouldWrite = True
            if alwaysAsk:
                shouldWrite = askYesNo(f"make dirctory '{str(dstPath)}'?")

            if shouldWrite:
                subprocess.run(f"{sudoPrefix}mkdir {str(dstPath)}", shell=True)
                print(f"made directory '{str(dstPath)}'")
                didWrite = True
            else:
                return

        if not recursive:
            return

        with os.scandir(srcPath) as entryIter:
            for entry in entryIter:
                cpImproved(
                    srcPath / entry.name,
                    dstPath / entry.name,
                    allowOverwrite=allowOverwrite,
                    alwaysAsk=alwaysAsk,
                    sudo=sudo,
                    after=after
                )

        after(dstPath, didWrite)
    else:
        eprint(f"Copy source path '{str(srcPath)}' not found.")

# returns an object with the subdirectories of the module in the given folder
def getModuleSubdirectories(module_path):
    module_path = Path(module_path)
    return {
        "staticUserFiles": module_path / "./user/static",
        "templateUserFiles": module_path / "./user/template",
        "afterUserFiles": module_path / "./user/after",

        "staticSystemFiles": module_path / "./system/static",
        "templateSystemFiles": module_path / "./system/template",
        "afterSystemFiles": module_path / "./system/after",
    }

# gets an array containing the names of each module defined in this repo
def definedModules():
    folder_path = Path(__file__).parent / "modules"
    if not Path(folder_path).exists():
        return []
    return [entry.name for entry in os.scandir(folder_path) if entry.is_dir()]

# prompts the user for which modules they want to enable
# returns a list containing the names of each newly enabled module
def promptEnableModules(defined_modules):
    if len(defined_modules) <= 0:
        return []

    print("It looks like this is your first time setting up this system.")

    if not askYesNo("Would you like to enable any modules before setup?"):
        return []

    enabled = []
    for module in defined_modules:
        if askYesNo(f"Would you like to enable module '{module}'?"):
            enabled.append(module)
        
    return enabled

# returns the enabled modules from the passed .ini file path
# this may modify the passed file if...
#   1) there are modules enabled in the file that are not defined in this repo (removes them)
#   2) there are modules in this repo that are not explicitly disabled in the file (adds them as disabled)
def listEnabledModules(redefine=False):
    defined = definedModules()
    enabled = []

    default_settings = {}
    for module in defined:
        default_settings[module] = "no";

    # the initial configuration
    config = configparser.ConfigParser(defaults=default_settings, allow_unnamed_section=True)
    if Path(MODULE_CONFIG_PATH).exists() and not redefine:
        config.read(MODULE_CONFIG_PATH)
    else:
        subprocess.run(["mkdir", "-p", CONFIG_PATH])
        config[configparser.UNNAMED_SECTION] = {}
        for module in promptEnableModules(defined):
            config.set(configparser.UNNAMED_SECTION, module, str(True))

    # put put config file into new config file (to remove unrecognized options)
    new_config = configparser.ConfigParser(allow_unnamed_section=True)
    new_config[configparser.UNNAMED_SECTION] = {}
    for module in defined:
        is_enabled = config.getboolean(configparser.UNNAMED_SECTION, module, fallback=False)
        new_config.set(configparser.UNNAMED_SECTION, module, str(is_enabled))
        if is_enabled:
            enabled.append(module)

    # write the new file
    subprocess.run(["touch", MODULE_CONFIG_PATH])
    with open(str(MODULE_CONFIG_PATH), 'w') as configfile:
        new_config.write(configfile)

    return enabled

# gets the path to all folders of enabled modules, the top level directory folder is prepended automatically
def getModulePaths(module_list):
    paths = list(map(lambda name: Path(__file__).parent / "modules" / name, module_list))
    paths.insert(0, Path(__file__).parent)
    return paths

