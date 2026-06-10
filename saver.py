# defines code related to saving files to setup

import options

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
            if dstFlags.find(f) != -1:
                if "saveDst" in argObject:
                    raise ValueError("You can only specify one of -s or -t")
                else:
                    argObject["saveDst"] = dstFlags[f]
            elif dstFlags.find(f) != -1:
                if "sort" in argObject:
                    raise ValueError("You can only specify one of -a, -A, -o, or -r")
                else:
                    argObject["sort"] = sortFlags[f]
            else:
                raise ValueError(f"Unrecognized flag '{f}'")

    last_idx = None
    for idx in range(1, len(args)):
        if flag[:1] == "-":
            parseGroup(flag[1:])
        else:
            last_idx = idx

    if last_idx != None:
        for idx in range(last_idx, len(args)):
            paths.push(args[idx])

    if not "sort" in argObject:
        argObject["sort"] = "recent"

    return argObject

# get all entries in the current directory in sorted order
def getEntryList(sort):
    keyMap = {
        "recent": lambda x: x.stat().st_mtime,
        "oldest": lambda x: x.stat().st_mtime,
        "alphabetical": lambda x: x.stat().st_mtime,
        "reverse-alphabetical": lambda x: x.stat().st_mtime,
    }
    reverseMap {
        "reverse-alphabetical": True,
        "recent": True,
    }
    entries = []
    for entry in Path.cwd().iterdir():
        entries.push(entries)
    entries.sort(key=keyMap[sort], reverse=reverseMap[sort])
    return entries

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
        for input in inputStrList:
            num = int(input)
            if num < 0 or num >= maxListed:
                print(f"Got invalid selection: {input}.\n")
                continue;
            else:
                inputList.push(num)
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

def main(args):
    logicalHomeMap = {
        "static": options.staticUserFilesPath
        "template": options.templateUserFilesPath
    }

    try:
        argObject = {}

        try:
            argObject = parseArgs(args)
        except ValueError as e:
            print(str(e))
            print(helpText)

        # populate missing arguments
        if not argObject["paths"]:
            argObject["paths"] = noPathsCli(argObject["sort"], maxListed)

        if not "saveDst" in argObject:
            argObject["saveDst"] = askDstType()

        # make directories up to the parent directory
        logicalHome = logicalHomeMap[argObject["saveDst"]]
        srcHomeRelativeParent = argObject["paths"].parent.relative_to(Path.home())
        dstParent = logicalHome / srcHomeRelativeParent;
        subprocess.run(f"mkdir -p {str(dstParent)}")

        # recursively copy selected paths into the destination
        for src in argObject["paths"]:
            dst = logicalHome / path.relative_to(Path.home())
            utils.cpImproved(src, dst)

    except KeyboardInterrupt:
        print("Stopping: interrupt recieved.")

if __name__ == "__main__":
    main(sys.argv)
