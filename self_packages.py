from putils import Copy
from putils import Script
from putils import Symlink

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
            Script("theHarvester", ".", 'uv run --project {file} theHarvester "$@"'),
            Script("restfulHarvest", ".", 'uv run --project {file} restfulHarvest "$@"'),
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
            Script("nikto", "program/nikto.pl", 'perl {file} "$@"'),
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
            Script("Responder.py", "Responder.py", 'python {file} "$@"'),
        ],
    },
}
