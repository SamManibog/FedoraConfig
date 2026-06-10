# defines common utility functions for setup

import os
import sys
import subprocess
from pathlib import Path
import filecmp
import difflib

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
    after=lambda *args: None
):
    srcPath = Path(src)
    dstPath = Path(dst)

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
                subprocess.run(f"cp {str(srcPath)} {str(dstPath)}", shell=True)
                print(f"wrote '{str(dstPath)}'")
                after(dstPath, True)

        else:
            # dst does not exist
            shouldWrite = True
            if alwaysAsk:
                shouldWrite = askYesNo(f"write file '{str(dstPath)}'?")

            if shouldWrite:
                subprocess.run(f"cp {str(srcPath)} {str(dstPath)}", shell=True)
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
                subprocess.run(f"mkdir {str(dstPath)}", shell=True)
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
                    after=after
                )

        after(dstPath, didWrite)
    else:
        eprint(f"Copy source path '{str(srcPath)}' not found.")
