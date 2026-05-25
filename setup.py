import os
from pathlib import Path
import tempfile
import subprocess

# =======================================================================================================
#       .d$$$$$b.  d$$$$$$$b  d$$$$$$$$$b  d$$$$$$$$$b  d$$$$$$$b  d$o   d$b   o$$$$$o.  .d$$$$$b.
#       $$$   `$$  $$$""""""  `""'$$$'""`  `""'$$$'""`  `""$$$""`  $$$$  $$$  d$$*`*$$$  $$$   `$$
#       `$$$bo.    $$$xxxx,       $$$          $$$         $$$     $$$^$ $$$  $$$        `$$$bo.  
#          `^+$$b  $$$****`       $$$          $$$         $$$     $$$ $,$$$  $$$  ^$$b     `^+$$b
#       $bo,,,d$$  $$$,,,,,,      $$$          $$$      ,,,$$$,,,  $$$  $$$$  &$$x,o$$$  $bo,,,d$$
#       `^$$$$$^`  ^$$$$$$$^      ^$^          ^$^      *$$$$$$$*  ^$^   ^$^  `$$$$* ^*  `^$$$$$^`
#
#   				                        EDIT THIS SECTION
# =======================================================================================================

# the list of packages to be installed
# can be provided as a string or a dictionary
# if a dictionary, it must contain a key "pkg" or "pkgs" that is either a string or list of string packages
# if a dictionary, it may
#   1) contain a key "copr" to define the copr host of the package
#   2) contain a key "after" which may be a bash command provided as a string or a callable
pkgs = [
    "git-core",
    "kitty",
    {
        "pkg": "neovim",
        "after": "git clone https://github.com/SamManibog/nvim ~/.config/nvim",
    },
    {
        "pkg": [ "niri", "waybar", "wpctl", "wofi" ],
        "after": "systemctl --user add-wants niri.service dms", 
    },
    {
        "pkg": "yazi",
        "copr": "varlad/yazi",
    },
]

nerdFonts = [
    "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/CommitMono.zip",
]

# =======================================================================================================
#                             o$$$$$o.   o$$$$$o.  d$$$$$$o.  d$$$$$$$b
#                            d$$*`*$$$  d$$*`*$$$  $$$``*$$$  $$$""""""
#                            $$$        $$$   $$$  $$$   $$$  $$$xxxx, 
#                            $$$   ,,,  $$$   $$$  $$$   $$$  $$$****` 
#                            *$$bod$$I  Y$$bod$$Y  $$$ood$$Y  $$$,,,,,,
#                             *$$$$$*    *$$$$$*   ^$$$$$$*   ^$$$$$$$^
#
# 			                 	       PRESERVE THIS SECTION
# =======================================================================================================

# the location to look for config files to copy into the home directory
configFilesLocation = "./configFiles"

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

# cleans a list or single package into a list of string package names
def cleanPackageInput(pkgInput):
    if isString(pkgInput):
        return [ pkgInput ]
    elif isList(pkgInput):
        return list(filter(isString, pkgInput))
    else:
        return []

# install a list of packages, passed as a list of strings
def installPackages(pkgList):
    # the list of well-formed packages
    goodPkgs = cleanPackageInput(pkgList)

    # the command used to install basePkgs
    goodPkgsCmd = f"sudo dnf install {" ".join(goodPkgs)}"

    # install base packages
    subprocess.run(goodPkgsCmd, shell=True)

# install a special package
def installSpecialPackage(pkgConfig):
    # ensure that we have a valid package list
    pkgList = []
    if "pkgs" in pkgConfig:
        pkgList = pkgConfig["pkgs"]
    elif "pkg" in pkgConfig:
        pkgList = pkgConfig["pkg"]
    pkgList = cleanPackageInput(pkgList)
    if not pkgList:
        eprint("ERROR: Invalid package config received (no valid package list found)")
        return

    # check that after is valid, if it exists
    after = None
    if "after" in pkgConfig:
        after = pkgConfig["after"]
        if not callable(after) and not isString(after):
            eprint("ERROR: Invalid package config received (value provided as after is not callable nor a string)")
            return

    # check for copr definition and enable if found
    if "copr" in pkgConfig:
        copr = pkgConfig["copr"]

        # ensure valid copr (is a string)
        if not isString(copr):
            eprint("ERROR: Invalid package config received (provided copr host is not a string)")
            return

        # run command to enable copr host
        coprCmd = f"sudo dnf copr enable {copr}"
        subprocess.run(coprCmd, shell=True)

    # install packages
    installPackages(pkgList)

    # run after command
    if after:
        if callable(after):
            after()
        else:
            subprocess.run(after, shell=True)

# runs the setup steps for downloading packages
def setupPackages():
    # the list of "normal" packages
    basePkgs = list(filter(isString, pkgs))

    # ensure git is installed, CRUCIAL step
    basePkgs.append("git")

    # install normal packages
    installPackages(basePkgs)

    # the list of "special" packages with extra instructions
    specialPkgs = list(filter(isDict, pkgs))

    # install special packages
    for pkgConfig in specialPkgs:
        installSpecialPackage(pkgConfig)

# runs the setup steps for updating the home directory
def setupHomeDirectory():
    # copy this directory structure recursively and interactively into home, as long as this script isn't running from home directory
    if os.getcwd() == os.path.expanduser("~"):
        print("Running Quick Setup from home directory, copying step skipped.")
    else:
        subprocess.run(f"cp -ri {configFilesLocation}/. ~", shell=True)

# runs the setup steps for downloading nerdfonts
def setupNerdFonts():
    fontDir = "~/.local/share/fonts"
    subprocess.run(f"mkdir -p {fontDir}", shell=True)

    for url in nerdFonts:
        if not isString(url):
            eprint("ERROR: Got invalid font data (nonString url)")
            break;
        
        with tempfile.TemporaryDirectory() as tempDir:
            subprocess.run(f"curl --output-dir {tempDir} -LO {url}", shell=True)

            zipfiles = list(Path(tempDir).glob('*.zip'))

            if zipfiles:
                zip = zipfiles[0]
                name = zip.stem
                outputPath = os.path.join(fontDir, name)
                subprocess.run(f"unzip {str(zip)} -d {outputPath}", shell=True)
            else:
                eprint(f"ERROR: Unable to zipfile download from {url}")
                break;

    subprocess.run("fc-cache -f -v", shell=True)
            
# sets up all fonts
def setupFonts():
    setupNerdFonts()

# runs all setup steps
def setupAll():
    setupPackages()
    setupHomeDirectory()
    setupFonts()

def main():
    prompt = (
        "Press a key to select a setup option:\n"
            "a - set up all\n"
            "d - set up home directory only\n"
            "p - set up packages only\n"
            "f - set up fonts only\n"
            "q - quit\n"
    )

    cancelWarning = "Setup Cancelled."

    actionMap = {
        "a": setupAll,
        "d": setupHomeDirectory,
        "p": setupPackages,
        "f": setupFonts,
    }

    try:
        char = None
        while char != "q":
            char = input(prompt)

            if char in actionMap:
                actionMap[char]()
                print("Quick Setup Complete!")
                return
        if char == "q":
            print(cancelWarning)
    except KeyboardInterrupt:
        print(cancelWarning)

if __name__ == "__main__":
    main()
