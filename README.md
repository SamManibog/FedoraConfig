# My Fedora Linux Configuration

## Installation

It is recommended to install these dotfiles with Fedora Workstation as the base desktop environment.

Ensure git is installed then run the following commands:
```bash
git clone git@github.com:SamManibog/FedoraConfig.git ~/FedoraConfig
cd ~/FedoraConfig
python setup.py
```

Note: Make sure to run these exact commands. Some functionality requires that this repo is found in the folder '~/FedoraConfig'

## File Structure

 - setup.py - the installation script for this configuration.
 - options.py - user-specifiable options for this configuration.
 - staticUserFiles - a directory containing files to be copied exactly to the home directory
 - templateUserFiles - like static user files, but will never overwrite existing files
 - afterUserFiles - a directory containing .py for running functions after files are written or overwritten

## Using afterUserFiles

Each file in afterUserFiles should be a .py file that corresponds to a file or directory in
staticUserFiles or templateUserFiles. Its name should be an exact match of the corresponding
file or directory, but with ".py" appended.

Each of these files will be imported as a python module, which must have two functions:
"always" and "callback". If "always" returns true, then "callback" will be called every
time the desktop loading step occurs. If "always" returns false, then "callback" will be
be called only when the corresponding file is overwritten. "callback" should take a single
positional argument, which will be the Path object of the corresponding file in the home
directory.

This directory is useful for applying file permissions, dynamic configurations, or
downloading web content.

## Useful Bash Functions

This configuration provides two functions to your .bashrc: home-setup and home-copy.

home-setup is an alias for the install script, `python setup.py`.

home-copy is an alias for `python saver.py`. Run `home-copy --help` for more information.

