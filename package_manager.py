import subprocess
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import configparser

import putils
from putils import Copy
from putils import Script
from putils import Symlink

import git_pkg_scheme
import github_pkg_scheme

# ways packages can be downloaded
# each should have a field:
#   output_path - a function that gets the output path of a package based on its specification
#   download - a function to download a package based on the passed specification
#   needs_update - a function to check if a package needs to be updated, based on its lockfile data
#   (optional) fields - a list of fields that the scheme must have
PKG_SCHEMES = {
    "git": {
        "verify_config": git_pkg_scheme.verifyConfig,
        "download": git_pkg_scheme.downloadRepo,
        "needs_update": git_pkg_scheme.needsUpdate,
    },
    "github": {
        "verify_config": github_pkg_scheme.verifyConfig,
        "download": github_pkg_scheme.downloadRepo,
        "needs_update": github_pkg_scheme.needsUpdate,
    },
}

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

    config_verification = pkg_scheme["verify_config"](pkg["scheme_config"])
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
    subprocess.run(["ln", "-s", target, link])

def installScript(script, package_dir):
    target = str(Path(package_dir) / script.target)
    binary = str(putils.BINARY_FOLDER / script.name)

    content = script.content.format(file=target)

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
                    stack.push(dep)
                else:
                    deps.add(dep)
    return deps

# installs the given self-defined packages (skips dnf dependencies)
def installSelfDefinedPackage(name, pkg_dictionary):
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
            installPackageNoDeps(pkg, pkg_dictionary[pkg])

# installs the given package, but does not install dependencies
def installPackageNoDeps(name, pkg):
    if "installed" in pkg:
        return

    print(f"Installing package '{name}'.")

    output_path = putils.PACKAGE_FOLDER / name

    # clear existing files
    subprocess.run(["rm", "-rf", output_path])
    subprocess.run(["mkdir", "-p", putils.PACKAGE_FOLDER])

    # download stuff
    download_protocol = PKG_SCHEMES[pkg["scheme"]]["download"]
    download_result = download_protocol(name, pkg["scheme_config"])
    if download_result == None:
        return

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
def installSelfDefinedPackages(names, pkg_dictionary):
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
        installSelfDefinedPackage(name, pkg_dictionary)

def formatLockfileName(scheme):
    return f"{scheme}-lock.ini"

def loadSchemeLockData(scheme):
    lockdata = configparser.ConfigParser()
    lockdata.read(putils.PACKAGE_LOCK_FOLDER / formatLockfileName(scheme))
    return lockdata

# loads all lockfile data into a config, organized by scheme
def loadAllLockData():
    config = {}

    for scheme in PKG_SCHEMES.keys():
        config[scheme] = loadSchemeLockData(scheme)

    return config

# checks all packages for updates, returning the number of updates available
def checkAllUpdates(lockData):
    total = 0

    for scheme in PKG_SCHEMES.keys():
        check_func = PKG_SCHEMES[scheme]["needs_update"]
        scheme_pkgs = lockData[scheme]
        for package_name in scheme_pkgs.sections():
            if check_func(scheme_pkgs[package_name]):
                total += 1

    return total

# install all packages from the given list
def installPackages(pkgs, pkg_dictionary):
    befores = []
    coprs = []
    dnf_pkgs = []
    self_pkgs = []
    afters = []

    # sort into steps
    for pkg in pkgs:
        if isinstance(pkg, str):
            if pkg in pkg_dictionary:
                self_pkgs.append(pkg)
            else:
                dnf_pkgs.append(pkg)

        elif isinstance(pkg, dict):
            if pkg["pkg"] in pkg_dictionary:
                self_pkgs.append(pkg["pkg"])
            else:
                dnf_pkgs.append(pkg["pkg"])

            if "copr" in pkg:
                coprs.append(pkg["copr"])
            if "before" in pkg:
                befores.append(pkg["before"])
            if "after" in pkg:
                afters.append(pkg["after"])
        
        else:
            raise ValueError("Invalid package definition found.")

    for before in befores:
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

    installSelfDefinedPackages(self_pkgs, pkg_dictionary)

    for after in afters:
        print(after)
        subprocess.run(after, shell=True)

# print(getOutputFolderName(URL))
# print(gitNeedsUpdate(URL, HASH))
# print(multithreadCalls(gitNeedsUpdate, arg_list_thing))

import self_packages

installPackages([ "theHarvester", "nikto", "Responder" ], self_packages.packages)
