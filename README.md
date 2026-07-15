# My Fedora Linux Configuration

## Installation

It is recommended to install these dotfiles with Fedora Workstation as the base desktop environment.

Ensure git is installed then run the following commands:
```bash
git clone git@github.com:SamManibog/FedoraConfig.git ~/FedoraConfig
cd ~/FedoraConfig
python cli.py setup -a
```

Note: Make sure to run these exact commands. Some functionality requires that this repo is found in the folder '~/FedoraConfig'

## File Structure

 - `cli.py` - the CLI for the configuration and package management systems (see [Using The CLI](#using-the-cli))
 - `options.py` - user-specifiable options for this configuration.
 - `user/` & `system/` - directories used to fill the home and root directories, respectively. These directories have the following structure: `static/` - a directory containing files to be copied exactly to the root or home directory
     - `template/` - like `static/`, but will never overwrite existing files
     - `after/` - a directory containing .py files for running functions after files are written or overwritten (see [Using "after" Directories](#using-"after"-directories))
 - `modules/` - a directory used to define modules (see [Defining Modules](#defining-modules))
 - `self_packages.py` - a python module used to define packages for the built-in package management system (see [Defining Packages](#defining-packages))
 - `package_schemes/` - a directory used to define packaging schemes (see [Defining Packaging Schemes](#defining-packaging-schemes))

## Using "after" Directories

Each file in an `after/` directory should be a .py file that corresponds to a file or directory in
the associated static or template directories. Its name should be an exact match of the corresponding
file or directory, but with ".py" appended.

Each of these files will be imported as a python module, which must have two functions:
`always()` and `callback()`. If `always()` returns true, then `callback()` will be called every
time the desktop loading step occurs. If "always" returns false, then `callback()` will be
be called only when the corresponding file is overwritten. `callback()` should take a single
positional argument, which will be the Path object of the corresponding file in the home
directory.

This directory is useful for applying file permissions, dynamic configurations, or
downloading web content.

## Defining Modules

Modules are optional configuration add-ons that mimic the structure of the root folder.
If you know how to use options.py, `user/`, and `system/` in the root directory, then you know how
to define modules. Just create a folder with your modules name in the `modules/` directory, and
use options.py, `user/`, and `system/` as you would in the root folder.

## Defining Packages

Packages may be defined in the self_packages.py python module. This module contains a single
attribute called packages, which serves as a map from each package's name to it's definition.

Package definitions must have two fields:
 - scheme - a `str` that matches one of the names in the schemes defined [here](#schemes)
 - scheme_config - a value that corresponds with the selected scheme

Package definitions may also have several other fields:
 - dependencies - a list of dependencies of the package (either a dnf package or another self-defined package), passed as `str`
 - build - a bash script to run from the directory downloaded by the package scheme
 - exes - a list that tells the package manager what executables are defined by the package and how to execute them, valid executable types are defined [here](#executables)

### Schemes

Schemes are means of downloading repositories into the `~/.local/opt/` folder. As of right now, there
are three acceptable schemes.

#### git

The 'git' scheme is used to download a git repository from a url via cloning.
Its best usecases are for basic git repositries that you would like to be on the bleeding edge
or github repositories with a weak release cycle.

The associated scheme_config is just the `str` url of the repository that you would like to clone.

#### github

The 'github' scheme is used to download a github repositories by their latest release.
Its best usecase is for github repositories that you would like to keep relatively stable.

The associated scheme_config is a dictionary with the following fields:
 - user - the user who owns the repository
 - repo - the name of the repository

#### custom

The 'custom' scheme is used to quickly define a packaging scheme not previously defined.
Use this scheme when the package has a unique installation process (otherwise, consider
defining [your own packaging scheme](#defining-packaging-schemes).

The associated scheme_config is a dictionary with fields that correspond to functions in
packaging schemes. See [Defining Packaging Schemes](#defining-packaging-schemes) for more details on these fields.
 - download - a python function corresponding to the `download()` function in a packaging scheme
 - needs_update - a python function corresponding to the `needsUpdate()` function in a packaging scheme

### Executables

There are accepted python classes that are acceptable entries to the exes folder. All of them are
defined in the putils.py python module, which is imported at the top of self_packages.py.

#### Copy

Used to copy an executable from the downloaded repository into PATH.
Copy works best for executables that aren't dependent on the file structure of the original repository.

Copy's constructor takes two arguments in the following order:
 1. name - the name of the output executable in PATH
 1. target - the path of the executable to by copied relative to the root of the downloaded repository

#### Script

Used to define a bash script which is used to call its associated executable.
Script works best for executables that are dependent on the file structure of the original repository.

Script's constructor takes three arguments in the following order:
 1. name - the name of the output execute in PATH
 2. target - the path of the "file of interest" (see 'content' below) relative to the root of the downloaded repository
 1. content - the actual script to run, which will be compiled as a python fstring with target in scope (you can use '{target}' and it will expand to the full path of 'target' above)

#### Symlink

Used to create a symlink to an executable from the downloaded repository in PATH.

Symlink's constructor takes two arguments in the following order:
 1. name - the name of the output symlink in PATH
 1. target - the path of the file to be linked relative to the root of the downloaded repository

## Defining Packaging Schemes

Schemes are means of downloading repositories into the `~/.local/opt/` folder. If multiple packages
have similar downloading steps, it's a good idea to define your own packaging scheme.

Packaging schemes are defined as python modules in the packaging_schemes folder.
Each module should be the name you want to call your scheme plus the .py file extension.

Packaging schemes require three functions, `verifyConfig()`, `download()`, and `needsUpdate()`,
which are described in-depth in the subsections below.

#### verifyConfig()

The `verifyConfig()` function is used to ensure that a package's scheme_config field is valid.

It takes one argument, which is the scheme_config of an arbitrary package using this scheme.

It should return either a `str` error message or `None` if the config is valid.

#### download()

The `download()` function is responsible for downloading a package and installing it into the
`~/.local/opt/name-of-package` folder.

This function takes two arguments in the following order.
 1. name - the name of the package to download, which should match the name (not the path) of the output folder
 1. cfg - the scheme_config of the package to download

This function should return a FLAT dictionary, meaning it may not contain any nested
lists or dictionaries. This dictionary will be written in .ini format to the lockfile for the package.
When paired with the package's config, he output of this function should be sufficient
for the `needsUpdate()` function to determine whether a package needs an update.

#### needsUpdate()

The `needsUpdate()` function is responsible for determining whether a package needs an update.

This function takes two arguments in the following order.
 1. ini - the contents of the lockfile for this package, this argument should not be modified
 1. cfg - the scheme_config of the package being checked

 This function should return a boolean; `True` if the package can be updated or `False` if not.

## Using the CLI

This configuration provides the home() in to your .bashrc as an alias for cli.py

Run  `home --help` for a complete description of the cli's capabilities.
