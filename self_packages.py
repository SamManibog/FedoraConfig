from putils import Copy
from putils import Script
from putils import Symlink
import putils

import subprocess
import tempfile
from pathlib import Path

def pkgMetasploitDownload(name, cfg):
    with tempfile.NamedTemporaryFile(delete_on_close=False, mode='w') as temp_file:
        temp_file.close()

        get_installer_cmd = f"curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > {temp_file.name}"
        install_cmd = f"sudo bash {temp_file.name}"
 
        subprocess.run(get_installer_cmd, shell=True)
        subprocess.run(install_cmd, shell=True)
        subprocess.run(f"ln -f -s /opt/metasploit-framework/bin/msfconsole {putils.BINARY_FOLDER / "msfconsole"}", shell=True)

    return {}

def pkgMetasploitNeedsUpdate(ini, cfg):
    return not Path("/opt/metasploit-framework/bin/msfconsole").exists()

packages = {
    "theHarvester": {
        "dependencies": [ 
            "uv",
            "python3-netaddr",
        ],
        "scheme": "github",
        "scheme_config": {
            "user": "laramies",
            "repo": "theHarvester",
        },
        "build": "uv sync",
        "exes": [
            Script("theHarvester", ".", 'uv run --project {target} theHarvester "$@"'),
            Script("restfulHarvest", ".", 'uv run --project {target} restfulHarvest "$@"'),
        ],
    },

    "nikto": {
        "dependencies": [ 
            "perl",
            "perl-JSON",
            "perl-XML-Writer",
        ],
        "scheme": "github",
        "scheme_config": {
            "user": "sullo",
            "repo": "nikto",
        },
        "exes": [
            Script("nikto", "program/nikto.pl", 'perl {target} "$@"'),
        ],
    },

    "Responder": {
        "dependencies": [ 
            "python3-pip",
            "python3-netifaces",
        ],
        "scheme": "git",
        "scheme_config": "https://github.com/lgandx/Responder",
        "build": "pip install -r requirements.txt",
        "exes": [
            Script("Responder.py", "Responder.py", 'python {target} "$@"'),
        ],
    },

    "metasploit": {
        "dependencies": [
            "ruby",
            "ruby-devel",
            "zlib-devel",
            "@development-tools",
        ],
        "scheme": "custom",
        "scheme_config": {
            "download": pkgMetasploitDownload,
            "needs_update": pkgMetasploitNeedsUpdate,
        },
    }
}
