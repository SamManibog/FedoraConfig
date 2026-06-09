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

Each file in afterUserFiles should be a .py files that corresponds to a file or directory in
staticUserFiles or templateUserFiles. Its name should be an exact match of the corresponding
file or directory, but with .py appended. Each of these files will be imported as a python
module and then called using the '()' operator. This call will pass a single parameter that
matches the path of the newly written file or directory.

This directory is useful for applying file permissions, dynamic configurations, or
downloading web content.



