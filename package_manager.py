import subprocess
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import configparser
import importlib
import re

import putils
from putils import Copy
from putils import Script
from putils import Symlink

import package_schemes.git
import package_schemes.github
import package_schemes.custom

class PackageScheme:
    def __init__(self, verifyConfig, download, needsUpdate):
        self.verifyConfig = verifyConfig
        self.download = download
        self.needsUpdate = needsUpdate

def importSchemes():
    schemes_path = Path(__file__).parent / "package_schemes/"

    schemes = {}

    scheme_names = [file.stem for file in schemes_path.iterdir() if file.is_file()]

    for scheme in scheme_names:
        mod = importlib.import_module(f".{scheme}", package="package_schemes")
        schemes[scheme] = mod

    return schemes

# ways packages can be downloaded
# each should have a field:
#   output_path - a function that gets the output path of a package based on its specification
#   download - a function to download a package based on the passed specification
#   needs_update - a function to check if a package needs to be updated, based on its lockfile data
#   (optional) fields - a list of fields that the scheme must have
PKG_SCHEMES = importSchemes()

#{
#    "git": {
#        "verify_config": git.verifyConfig,
#        "download": git.downloadRepo,
#        "needs_update": git.needsUpdate,
#    },
#
#    "github": {
#        "verify_config": github.verifyConfig,
#        "download": github.downloadRepo,
#        "needs_update": github.needsUpdate,
#    },
#
#    "custom": {
#        "verify_config": custom.verifyConfig,
#        "download": custom.downloadRepo,
#        "needs_update": custom.needsUpdate,
#    },
#}

# runs a function on the list of argument lists to the given function on multiple threads
def multithreadCalls(func, arguments, max_workers=3):
    def spreadFunc(args):
        return func(*args)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # executor.map applies fetch_data to every item in urls
        return list(executor.map(spreadFunc, arguments))

# verifies the contents of a package
def verifyPackage(name, pkg_dictionary):
    if name not in pkg_dictionary:
        raise ValueError(f"No package named '{name}' is defined.")

    pkg = pkg_dictionary[name]

    def raiseError(msg):
        items = ""
        for key, value in pkg.items():
            items += f"\t{key}: {value}\n"

        raise ValueError(f"{msg}\nContents:\n{items}")

    if "scheme" not in pkg:
        raiseError(f"Invalid package '{name}' specifies no scheme.")

    pkg_scheme = PKG_SCHEMES[pkg["scheme"]]
    if "scheme_config" not in pkg:
        raiseError(f"Invalid package '{name}' is missing scheme config.")

    config_verification = pkg_scheme.verifyConfig(pkg["scheme_config"])
    if config_verification:
        raiseError(f"Package '{name}' has invalid scheme config: {config_verification}")

    if pkg_scheme == None:
        raiseError(f"Invalid package '{name}' has invalid scheme '{pkg["scheme"]}'.")

    if "dependencies" in pkg:
        for dep in pkg["dependencies"]:
            if not isinstance(dep, str):
                raiseError(f"Invalid package '{name}' has invalid dependency '{dep}'.")

    if "exes" in pkg:
        exes = pkg["exes"]
        if not isinstance(exes, list):
            exes = [exes]
        for exe in exes:
            if not isinstance(exe, Symlink) and not isinstance(exe, Script) and not isinstance(exe, Copy):
                raiseError(f"Invalid package '{name}' has invalid executable.")

def installCopy(copy, output):
    target = str(Path(package_dir) / copy.target)
    copy = str(putils.BINARY_FOLDER / copy.name)

    subprocess.run(["chmod", "+x", target])
    subprocess.run(["cp", target, copy])

def installSymlink(sym, package_dir):
    target = str(Path(package_dir) / sym.target)
    link = str(putils.BINARY_FOLDER / sym.name)

    subprocess.run(["chmod", "+x", target])
    subprocess.run(["ln", "-f", "-s", target, link])

def installScript(script, package_dir):
    target = str(Path(package_dir) / script.target)
    binary = str(putils.BINARY_FOLDER / script.name)

    content = script.content.format(target=target)

    with open(binary, "w") as file:
        file.write(content)
    subprocess.run(["chmod", "+x", binary])

# gets the set of dnf package dependencies from a self-defined package
def getSelfDefinedDnfDependents(name, pkg_dictionary):
    deps = set()

    stack = [ name ]

    while len(stack) > 0:
        pkg_name = stack.pop()
        pkg = pkg_dictionary[pkg_name]
        
        if "dependencies" in pkg:
            for dep in pkg["dependencies"]:
                if dep in pkg_dictionary:
                    stack.append(dep)
                else:
                    deps.add(dep)
    return deps

# installs the given self-defined packages (skips dnf dependencies)
def installSelfDefinedPackage(name, pkg_dictionary, lockdata):
    deps_by_depth = []
    next_queue = []
    deps_queue = []
    depth = 0

    if name in pkg_dictionary:
        deps_queue = [ name ]

    while len(deps_queue) > 0:
        deps_by_depth.append(deps_queue)
        next_queue = []

        for queued_name in deps_queue:
            verifyPackage(queued_name, pkg_dictionary)

            queued = pkg_dictionary[queued_name]
            queued["depth"] = depth

            if "dependencies" in queued:
                for dep_name in queued["dependencies"]:
                    if dep_name not in pkg_dictionary:
                        continue

                    next_queue.append(dep_name)

                    dep = pkg_dictionary[dep_name]

                    if "installed" in dep:
                        continue

                    if "depth" in dep and dep["depth"] <= depth:
                        raise ValueError(f"Circular dependencies detected: {queued_name} {dep_name}")
        deps_queue = next_queue
        depth += 1

    while len(deps_by_depth) > 0:
        pkg_list = deps_by_depth.pop()

        for pkg in pkg_list:
            installPackageNoDeps(pkg, pkg_dictionary[pkg], lockdata)

# installs the given package, but does not install dependencies
def installPackageNoDeps(name, pkg, lockdata):
    if "installed" in pkg:
        return

    print(f"Installing package '{name}'.")

    output_path = putils.PACKAGE_FOLDER / name

    # clear existing files
    subprocess.run(["rm", "-rf", output_path])
    subprocess.run(["mkdir", "-p", putils.PACKAGE_FOLDER])

    # download stuff
    download_protocol = PKG_SCHEMES[pkg["scheme"]].download
    download_result = download_protocol(name, pkg["scheme_config"])
    if download_result == None:
        return

    lockdata[name] = download_result

    if "build" in pkg:
        build_cmds = pkg["build"]

        with tempfile.NamedTemporaryFile(mode='w+') as temp_file:
            temp_file.write(build_cmds)
            temp_file.flush()
            res = subprocess.run(["bash", temp_file.name], cwd=output_path)

    if "exes" in pkg:
        exes = pkg["exes"]
        if not isinstance(exes, list):
            exes = [ exes ]

        for exe in pkg["exes"]:
            if isinstance(exe, Symlink):
                installSymlink(exe, output_path)

            if isinstance(exe, Script):
                installScript(exe, output_path)
                
            if isinstance(exe, Copy):
                installCopy(exe, output_path)

    pkg["installed"] = True
    print(f"Package '{name}' installed.")

# installs the given self-defined packages (skips dnf dependencies)
def installSelfDefinedPackages(names, pkg_dictionary, lockdata):
    dnf_deps = set()
    for name in names:
        dnf_deps |= getSelfDefinedDnfDependents(name, pkg_dictionary)
    dnf_deps = list(dnf_deps)

    if len(dnf_deps) > 0:
        print(f"sudo dnf install -y {" ".join(dnf_deps)}")
        subprocess.run([
            "sudo",
            "dnf",
            "install",
            "-y",
            *dnf_deps
        ])

    for name in names:
        installSelfDefinedPackage(name, pkg_dictionary, lockdata)

# loads all lockfile data into a config, organized by scheme
def loadLockData():
    lockdata = configparser.ConfigParser()
    lockdata.read(putils.PACKAGE_LOCKFILE)
    return lockdata

# checks if a self-defined package is updatable
def isPackageUpdatable(pkg, pkg_dictionary, lockdata):
    scheme = pkg_dictionary[pkg]["scheme"]
    if pkg in lockdata:
        check_func = PKG_SCHEMES[scheme].needsUpdate
        return check_func(lockdata[pkg], pkg_dictionary[pkg]["scheme_config"])
    else:
        return True

# checks if a copr is enabled by name
def coprIsEnabled(copr):
    coprList = subprocess.run(
        "dnf copr list",
        capture_output=True,
        text=True,
        shell=True
    ).stdout

    coprRegexUncompiled = f"{copr}.*"
    coprRegex = re.compile(coprRegexUncompiled)
    match = re.search(coprRegex, coprList)

    if match:
        disabledRegex = r"\(disabled\)"
        return not re.search(disabledRegex, match.group(0))
    else:
        return False

# install all packages from the given list
def installPackages(pkgs, pkg_dictionary, force=False):
    lockdata = loadLockData()

    befores = []
    coprs = []
    dnf_pkgs = []
    self_pkgs = []
    afters = []

    # sort into steps
    for pkg in pkgs:
        if isinstance(pkg, str):
            if pkg in pkg_dictionary:
                if force or isPackageUpdatable(pkg, pkg_dictionary, lockdata):
                    self_pkgs.append(pkg)
            else:
                dnf_pkgs.append(pkg)

        elif isinstance(pkg, dict):
            if pkg["pkg"] in pkg_dictionary:
                if force or isPackageUpdatable(pkg["pkg"], pkg_dictionary, lockdata):
                    self_pkgs.append(pkg["pkg"])
            else:
                dnf_pkgs.append(pkg["pkg"])

            if "copr" in pkg and not coprIsEnabled(pkg["copr"]):
                coprs.append(pkg["copr"])
            if "before" in pkg:
                befores.append(pkg["before"])
            if "after" in pkg:
                afters.append(pkg["after"])
        
        else:
            raise ValueError("Invalid package definition found.")

    for before in befores:
        if callable(before):
            before()
        else:
            print(before)
            subprocess.run(before, shell=True)

    for copr in coprs:
        coprCmd = f"sudo dnf copr enable {copr}"
        print(coprCmd)
        subprocess.run(coprCmd, shell=True)

    if len(dnf_pkgs) > 0:
        print(f"sudo dnf install -y {" ".join(dnf_pkgs)}")
        subprocess.run([
            "sudo",
            "dnf",
            "install",
            "-y",
            *dnf_pkgs
        ])

    installSelfDefinedPackages(self_pkgs, pkg_dictionary, lockdata)

    for after in afters:
        if callable(after):
            after()
        else:
            print(after)
            subprocess.run(after, shell=True)

    subprocess.run(["mkdir", "-p", putils.PACKAGE_LOCKFILE.parent])
    with open(putils.PACKAGE_LOCKFILE, "w") as f:
        lockdata.write(f)
