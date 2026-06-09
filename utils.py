# defines common utility functions for setup

import os
import sys
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
def printColoredDiff(file1_lines, file2_lines, fromfile="file1", tofile="file2"):
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

    # Print each line with corresponding colors
    for line in diff:
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
def cpImproved(src, dst, recursive=True, allowOverwrite=True):
    srcPath = Path(src).expanduser()
    dstPath = Path(dst).expanduser()

    if srcPath.is_file():
        # base case: src is a file

        if dstPath.is_file():
            # check if files are different
            if filecmp.cmp(srcPath, dstPath, shallow=False):
                print(f"skipped '{str(dstPath)}' (exact copy)")
                return

            if not allowOverwrite:
                print(f"skipped '{str(dstPath)}' (overwrite disabled)")
                return

            # get a diff between the files
            with open(srcPath, 'r', encoding='utf-8') as srcFile, open(dstPath, 'r', encoding='utf-8') as dstFile:
                srcLines = srcFile.readlines()
                dstLines = dstFile.readlines()
                    
                print(f"attempting to overwrite '{str(dstPath)}'")
                print("difference:")
                printColoredDiff(
                    srcLines, 
                    dstLines, 
                    fromfile=str(srcPath), 
                    tofile=str(dstPath)
                )

            # prompt user to confirm copy
            print()
            if askYesNo(f"overwrite '{str(dstPath)}'?"):
                subprocess.run(f"cp {str(srcPath)} {str(dstPath)}", shell=True)
                print(f"wrote '{str(dstPath)}'")

        else:
            # automatic copy because dst does not exist
            subprocess.run(f"cp {str(srcPath)} {str(dstPath)}", shell=True)
            print(f"wrote '{str(dstPath)}'")

    elif srcPath.is_dir():
        # inductive case: src is a folder

        if not dstPath.is_dir():
            subprocess.run(f"mkdir {str(dstPath)}", shell=True)
            print(f"made directory '{str(dstPath)}'")

        if not recursive:
            return

        with os.scandir(srcPath) as entryIter:
            for entry in entryIter:
                cpImproved(srcPath / entry.name, dstPath / entry.name, allowOverwrite=allowOverwrite)
    else:
        eprint(f"Copy source path '{str(srcPath)}' not found.")
