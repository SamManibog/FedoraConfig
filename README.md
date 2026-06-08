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

setup.py is the installation script for this configuration.

setup.py will copy files from ./configFiles into the home directory.
