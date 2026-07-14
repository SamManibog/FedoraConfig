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
        "runables": [
            Script("theHarvester", ".", 'uv run --project {file} theHarvester "$@"'),
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
        "runables": [
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
        "runables": [
            Script("Responder.py", "Responder.py", 'python {file} "$@"'),
        ],
    },
}
