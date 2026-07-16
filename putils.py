from pathlib import Path

# the folder in which to write binary files
BINARY_FOLDER = Path.home() / ".local/bin/"

# the folder in which to store package repositories
PACKAGE_FOLDER = Path.home() / ".local/opt/"

# package lock file
PACKAGE_LOCKFILE = Path.home() / ".config/FedoraConfig/locks.ini"

class Copy:
    def __init__(self, name, target):
        self.name = str(name)
        self.target = str(target)

class Symlink:
    def __init__(self, name, target):
        self.name = str(name)
        self.target = str(target)

class Script:
    def __init__(self, name, target, content):
        self.name = str(name)
        self.target = str(target)
        self.content = str(content)
