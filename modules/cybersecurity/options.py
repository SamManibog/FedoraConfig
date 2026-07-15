# =======================================================================================================
#       .d$$$$$b.  d$$$$$$$b  d$$$$$$$$$b  d$$$$$$$$$b  d$$$$$$$b  d$o    d$b   o$$$$$o.  .d$$$$$b.
#       $$$   `$$  $$$^^^^^"  "^^^$$$^^^"  "^^^$$$^^^"  "^^$$$^^"  $$$$v  $$$  d$$*`*$$$  $$$   `$$
#       `$$$bo.    $$$xxxx,       $$$          $$$         $$$     $$$^$v $$$  $$$        `$$$bo.  
#          `^+$$b  $$$****`       $$$          $$$         $$$     $$$ ^$v$$$  $$$  ^$$b     `^+$$b
#       $bo,,,d$$  $$$xxxxo,      $$$          $$$      ,ox$$$xo,  $$$  ^$$$$  &$$x,o$$$  $bo,,,d$$
#       `^$$$$$^`  ^$$$$$$$^      ^$^          ^$^      *$$$$$$$*  ^$^    ^$^  `$$$$* ^*  `^$$$$$^`
#
#   				                        EDIT THIS FILE
# =======================================================================================================

# the list of packages to be installed
# can be provided as a string or a dictionary
# if a dictionary, it must contain a key "pkg" or "pkgs" that is either a string or list of string packages
# if a dictionary, it may
#   1) contain a key "copr" to define the copr host of the package
#   2) contain a key "after" which may be a bash command provided as a string or a callable
#   3) contain a key "before" which may be a bash command provided as a string or a callable
pkgs = [
    # network tools
    "nmap",
    "arp-scan",
    "net-tools",
    "netcat",
    "impacket",
    "theHarvester",
    "nikto",
    "Responder",

    # password cracking tools
    "hashcat",
    "hydra",
]

# the list of flatpak remotes to add
# note that flathub is enabled by default
# stored as dictionaries with two keys:
#   "name": the name of the remote
#   "url": the url of the remote
flatpakRemotes = [
]

# the flatpaks to install
# can be provided as a string or a dictionary
# if a dictionary, it must contain a key "flatpak" or "flatpaks" that is either a string or list of string packages
# if a dictionary, it may
#   1) contain a key "remote" to define the remote that holds the package (default is "flathub")
#   2) contain a key "after" which may be a bash command provided as a string or a callable
flatpaks = [
]

# the urls to fetch fonts from
fontUrls = [
]

# the function to run after all config functions are run
def after():
    pass
