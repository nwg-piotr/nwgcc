# nwgcc
nwg Control Center is a higly customisable, GTK-based GUI, intended for use with window managers. 
It may serve as an extension to bars / panels, providing built-in and user-defined controls. 
Default theme may be overridden with custom css style sheets.

This is a work in progress, not yet production ready.

Main window, Nordic-bluish-accent GTK theme, custom icons Light:

![gui.png](https://scrot.cloud/images/2020/11/30/2020-11-30_223904.png)

Preferences window:

![gui-config.png](https://scrot.cloud/images/2020/11/30/2020-11-30_224038.png)

## TODO

- ~~avoid icon Gtk.Image objects re-creation on refresh if status unchanged~~
- alternative `get_volume` / `set_volume` if the pyalsa module unavailable
- bluetooth status detection on systemd-less systems
- grab the GTK theme menu item background color for use with the CustomRow objects, instead of the hardcoded value 