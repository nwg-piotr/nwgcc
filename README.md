# nwgcc
nwg Control Center is a higly customisable, GTK-based GUI, intended for use with window managers. 
It may serve as an extension to bars / panels, providing built-in and user-defined controls. 
Default theme may be overridden with custom css style sheets.

This is a work in progress, not yet production ready.

Main window, Nordic-bluish-accent GTK theme, custom icons Light:

![gui.png](https://scrot.cloud/images/2020/12/02/2020-12-02_022723.png)

Preferences window:

![gui-config.png](https://scrot.cloud/images/2020/11/30/2020-11-30_224038.png)

## Dependencies: 
- `python>=3.6`
- `python-gobject`
- `gtk3`
- `python-setuptools` (build)

## Components use optional dependencies:
- Brightness slider: `light`
- Volume slider: `alsa`, `alsa-utils`, `python-pyalsa` (recommended if available; if not - amixer command will be used)
- Wi-fi status: `wireless_tools`
- Bluetooth status: `bluez`, `bluez-utils`

Sample user defined commands use `blueman` and `NetworkManager`.
