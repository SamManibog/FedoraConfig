# defines code related to saving files to setup

helpText = ("Usage: saver.py [FLAGS] [PATH]\n"
    "Copy a file or directory from the home directory into the config\n"
    "\n"
    "With no PATH, display a menu to select one or multiple folders\n"
    "\t-s save to the static directory\n"
    "\t-t save to the template directory\n"
    "\t-r when no PATH, sort entries by most recent (default behavior)\n"
    "\t-o when no PATH, sort entries by oldest\n"
    "\t-a when no PATH, sort entries alphabetically\n"
    "\t-A when no PATH, sort entries reverse alphabetically\n")

# parses system args
def parseArgs(args):
    argObject = {
        "saveDst": None,
        "sort": "recent",
        "path": None
    }

    for flag in args[1:-1]:
        if flag[:1] == "-":
            for f in flag[1:]:
                if f == "s":
                    argObject.saveDst = "static"
                elif f == "t":
                    argObject.saveDst = "template"
                elif f == "r":
                    argObject.sort = "recent"
                elif f == "o":
                    argObject.sort = "oldest"
                elif f == "a":
                    argObject.sort = "alphabetical"
                elif f == "A":
                    argObject.sort = "ralphabetical"
                else:
                    raise ValueError(f"Unrecognized flag '{f}'")
        else:
            raise ValueError(f"Expected flag. Got '{flag}'")

def main(args):
    argObject = {}

    try:
        argObject = parseArgs(args)
    except ValueError as e:
        print(str(e))
        print(helpText)

if __name__ == "__main__":
    main(sys.argv)
