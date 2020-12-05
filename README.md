# nwgcc
nwg Control Center is a highly customisable, GTK-based GUI, intended for use with window managers. 
It may serve as an extension to bars / panels, providing built-in and user-defined controls. 
Default theme may be overridden with custom css style sheets.

**This software is aimed at power users.**

Main window, Nordic-bluish-accent GTK theme, custom icons Light:

![gui.png](https://scrot.cloud/images/2020/12/02/2020-12-02_022723.png)

Preferences window:

![gui-config.png](https://scrot.cloud/images/2020/11/30/2020-11-30_224038.png)

## Dependencies: 
- `python` (python3)
- `python-gobject`
- `gtk3`
- `python-setuptools`

## Components:

For built-in components to work, you need dependencies as below. If you don't need one, you may skip installing
related packages (e.g. on a desktop machine, you probably don't need the brightness slider).

- **Brightness slider**: `light`
- **Volume slider**: `alsa`, `alsa-utils`, `python-pyalsa` (the latter is not necessary, but 
  recommended if available; otherwise the `amixer` command output will be parsed)
- **Wi-fi status**: `wireless_tools`
- **Bluetooth status**: `bluez`, `bluez-utils`

**Sample user defined commands** use `blueman` and `NetworkManager`.

## Installation

This software is still in alpha stage of development, and has not yet been packaged for any Linux distribution.

### Arch Linux 
You may use the [PKGBUILD](https://github.com/nwg-piotr/nwgcc/blob/master/PKGBUILD) file to build 
the `nwgcc-git` package from the `master` branch. It's recommendable, as you'll be able to uninstall easily. 

### Other Linux distributions

```text
git clone https://github.com/nwg-piotr/nwgcc.git
cd nwgcc
sudo python setup.py install --optimize=1
```

**To remove:**

```text
sudo rm -r /usr/lib/python3.9/site-packages/nwgcc*
sudo rm /usr/bin/nwgcc
```

## Running

```text
$ nwgcc -h
usage: nwgcc [-h] [-v] [-d] [-p] [-css CSS]

nwg Control Center

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  display version information
  -d, --debug    do checks, print results
  -p, --pointer  place window at the mouse pointer position (Xorg only)
  -css CSS       custom css file name
```

Click the Preferences button to adjust the window to your needs.

To report a bug or request a feature, please [sumbit an issue](https://github.com/nwg-piotr/nwgcc/issues).