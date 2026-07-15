import subprocess
import tempfile
import utils
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

url = "https://api.github.com/repos/sullo/nikto/zipball/2.6.0"
output = "/home/sman/test/test2/nikto-curled"

# downloads and extracts a zip file from a url to the specified directory
def downloadZip(url, output_directory):
    with tempfile.TemporaryDirectory() as downloadDir:
        zipfile = None
        try:
            subprocess.run([
                "curl",
                "--output-dir", 
                downloadDir,
                "-LO", 
                url
            ])
            zipfile = str(list(Path(downloadDir).glob('*'))[0])
        except:
            utils.eprint(f"ERROR: Unable to download zipfile from {url}")

        with tempfile.TemporaryDirectory() as unzipDir:
            subprocess.run([
                "unzip",
                zipfile,
                "-d",
                unzipDir
            ])

            unzipped = list(Path(unzipDir).glob('*'))[0]

            subprocess.run([
                "mv",
                str(unzipped),
                str(output_directory)
            ])

