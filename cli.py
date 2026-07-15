import setup
import utils
import package_manager
import self_packages
import sys
import saver

def ensureConfigCallback(flags):
    if "-f" in flags:
        utils.listEnabledModules(redefine=True)
    else:
        utils.listEnabledModules()

def setupCallback(flags):
    num_flags = len(flags)

    if len(flags) != 1:
        sys.exit("You may must specify one flag for 'home setup' (run 'home setup --help' for a list of valid flags).")
    else:
        setup.runSetup(flags.pop()[1])

def installCallback(flags, args):
    force = "-f" in flags
    package_manager.installPackages(args, self_packages.packages, force=force)

def countUpdatesCallback():
    lockdata = package_manager.loadLockData()

    sum = 0
    for pkg in lockdata.sections():
        if package_manager.isPackageUpdatable(pkg, self_packages.packages, lockdata):
            sum += 1

    print(sum)

def copyCallback(flags):
    if len(flags) <= 0:
        saver.save("recent")

    elif len(flags) > 1:
        sys.exit("You may only specify one sort order")

    else:
        sortMap = {
            "-r": "recent",
            "-o": "oldest",
            "-a": "alphabetical",
            "-A": "reverse-alphabetical",
        }
        saver.save(sortMap[flags.pop()[1]])

# the descriptions of each command
# each description must have the fields:
#   desc - the description of the command
#   callback - the function to call when running the command
# each description may have the fields:
#   flags - a dictionary used to specify flags
#   argument - a string name for a single argument
#       if defined, a single argument may be passed
#   arguments - a string name for positional arguments
#       if defined, a list of positional arguments may be passed
#   argument? - same as argument, but optional
#   arguments? - same as arguments, but optional
commands = {
    "ensure-config": {
        "desc": "Ensures that the config file is defined, potentially providing a CLI to fill it out.",
        "flags": {
            "-f": "Always provide the config edit CLI, even if already defined."
        },
        "callback": ensureConfigCallback,
    },

    "setup": {
        "desc": "Sets up this config.",
        "flags": {
            "-a": "set up all (excluding disabled modules)",
            "-h": "set up home directories only",
            "-s": "set up system directories only",
            "-f": "set up fonts only",
            "-k": "set up flatpaks only",
            "-p": "set up packages only",
            "-r": "set up rpm fusion",
            "-z": "run post setup only",
        },
        "callback": setupCallback,
    },

    "install": {
        "desc": "Installs the given self-packaged PACKAGES.",
        "flags": {
            "-f": "force reinstallation",
        },
        "arguments": "PACKAGES",
        "callback": installCallback,
    },

    "count-updates": {
        "desc": "Returns the number of update available in self-packaged packages.",
        "callback": countUpdatesCallback,
    },

    "copy": {
        "desc": "A CLI to quickly copy files or folders from the PWD to this config.",
        "flags": {
            "-r": "sort list of fils by most recent modification",
            "-o": "sort list of files by oldest modification",
            "-a": "sort list of files alphabetically",
            "-A": "sort list of files reverse-alphabetically",
        },
        "callback": copyCallback,
    },
}

def commandSpecAcceptsArguments(spec):
    for k in ["argument", "arguments", "argument?", "arguments?"]:
        if k in spec:
            return True
    return False

def printMainHelp():
    print("Syntax: python cli.py [COMMAND]")
    print("Valid commands are:")
    for command in commands.keys():
        desc = commands[command]["desc"]
        print(f"\t{command} - {desc}")
    print("Each command can be passed the argument '--help' directly after the command for more details.")

def printCommandHelp(command):
    syntax = f"Syntax: python cli.py {command}"
    command_desc = commands[command]

    if "flags" in command_desc:
        syntax += " [FLAGS...]"

        if commandSpecAcceptsArguments(command_desc):
            syntax += " [--]"

    if "argument" in command_desc:
        syntax += f" [{command_desc["argument"]}]"
    elif "arguments" in command_desc:
        syntax += f" [{command_desc["arguments"]}...]"
    elif "argument?" in command_desc:
        syntax += f" <{command_desc["argument"]}>"
    elif "arguments?" in command_desc:
        syntax += f" <{command_desc["arguments"]}...>"

    print(syntax)
    print(command_desc["desc"])

    if "flag" in command_desc:
        flag = command_desc["flag"].keys()[0]
        desc = list(command_desc["flag"].values())[0]

        print()
        print(f"{flag} - {desc}")
    elif "flags" in command_desc:
        print()
        print("Valid FLAGS are:")
        for flag in command_desc["flags"]:
            desc = command_desc["flags"][flag]
            print(f"\t{flag} - {desc}")

def main():
    raw_args = sys.argv[1:]

    if len(raw_args) < 1 or raw_args[0] == "--help":
        printMainHelp()
        sys.exit(1)

    if raw_args[0] not in commands:
        utils.eprint(f"Invalid command '{raw_args[0]}'.")
        printMainHelp()
        sys.exit(1)

    command = raw_args[0]
    command_spec = commands[command]

    valid_flags = set({"--help"})
    if "flag" in command_spec:
        valid_flags |= set(command_spec["flag"].keys())
    elif "flags" in command_spec:
        valid_flags |= set(command_spec["flags"].keys())

    # parse flags and arguments
    flags = set()
    arguments = []
    for i in range(1, len(raw_args)):
        if raw_args[i] in valid_flags:
            flags.add(raw_args[i])
        elif raw_args[i] == "--":
            arguments = raw_args[i + 1:]
            break
        else:
            arguments = raw_args[i:]
            break

    # print help if flag is specified
    if "--help" in flags:
        printCommandHelp(command)
        sys.exit()

    # check that arguments are valid for the command
    argument_param = None
    if "argument" in command_spec:
        if len(arguments) != 1:
            utils.eprint(f"You must specify one {command_spec["argument"]}")
            printCommandHelp(command)
            sys.exit(1)
        argument_param = arguments[0]

    elif "argument?" in command_spec:
        if len(arguments) > 1:
            utils.eprint(f"You must specify at most one {command_spec["argument?"]}")
            printCommandHelp(command)
            sys.exit(1)
        argument_param = arguments.get(0, None)

    elif "arguments" in command_spec:
        if len(arguments) < 1:
            utils.eprint(f"You must specify {command_spec["argument"]}")
            printCommandHelp(command)
            sys.exit(1)
        argument_param = arguments

    elif "arguments?" in command_spec:
        argument_param = arguments

    elif len(arguments) > 0:
        utils.eprint(f"Got invalid flag '{arguments[0]}'")
        printCommandHelp(command)
        sys.exit(1)

    if "flags" in command_spec:
        if commandSpecAcceptsArguments(command_spec):
            command_spec["callback"](flags, argument_param)
        else:
            command_spec["callback"](flags)
    else:
        if commandSpecAcceptsArguments(command_spec):
            command_spec["callback"](argument_param)
        else:
            command_spec["callback"]()

if __name__ == "__main__":
    main()
