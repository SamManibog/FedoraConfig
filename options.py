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
pkgs = [
    "git-core",
    "kitty",
    "blueman",
    "bottles",
    "google-roboto-fonts",
    "pavucontrol",
    "thunderbird",
    "steam",
    {
        "pkg": "ffmpeg-free",
        "after": "sudo dnf swap ffmpeg-free ffmpeg --allowerasing",
    },
    {
        "pkg": [
            "audacity",
            "blender",
            "gimp",
            "inkscape",
            "openshot",
        ],
    },
    {
        "pkg": [
            "libreoffice-writer",
            "libreoffice-calc",
            "libreoffice-impress",
            "libreoffice-draw",
            "libreoffice-base",
            "libreoffice-math",
        ],
    },
    {
        "pkg": [
            "libimobiledevice",
            "ifuse",
            "usbmuxd",
        ],
    },
    {
        "pkg": "neovim",
        "after": "git clone git@github.com:SamManibog/nvim.git ~/.config/nvim",
    },
    {
        "pkg": "SwayNotificationCenter",
        "copr": "erikreider/SwayNotificationCenter",
    },
    {
        "pkg": [
            "niri",
            "waybar",
            "wpctl",
            "brightnessctl",
            "gammastep",
            "fuzzel",
            "swayidle",
            "swaylock",
            "swaybg",
            "jq",
            "xdg-desktop-portal-gtk",
            "xdg-desktop-portal-gnome",
            "gnome-keyring",
            "nm-applet",
        ],
    },
    {
        "pkg": "yazi",
        "copr": "varlad/yazi",
    },
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
    "com.spotify.Client",
    "org.onlyoffice.desktopeditors",
]

# the urls to fetch fonts from
fontUrls = [
    "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/CommitMono.zip",
]

# the relative location to look for config files to copy into the home directory
# these files will ask permission before overwriting
staticUserFilesPath = "./staticUserFiles"

# the relative location to look for config files to copy into the home directory
# these files will be skipped if already present in the home directory
templateUserFilesPath = "./templateUserFiles"

# the function to run after all config functions are run
import subprocess
def after():
    # set dark theme
    darkThemeCmd = "gsettings set org.gnome.desktop.interface color-scheme prefer-dark"
    print(darkThemeCmd)
    subprocess.run(darkThemeCmd, shell=True)
