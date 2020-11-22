#!/usr/bin/env python3

# Dependencies: python-pyalsa
# Optional: bluez bluez-utils
# For user defined commands: blueman bluez bluez-utils

import time
time_start = int(round(time.time() * 1000))
import gi
import sys
import argparse

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

from tools import *

ICON_SIZE_SMALL: int = 16
ICON_SIZE_LARGE: int = 24
# "light" or "dark"; no value means: use GTK icon name
ICON_SET: str = "light"

# 0 for no refresh
REFRESH_FAST_MILLIS: int = 500
REFRESH_SLOW_SECONDS: int = 5
REFRESH_CLI_SECONDS: int = 1800

debug = False

dirname = os.path.dirname(__file__)
config_dir = get_config_dir()
data_dir, commands_dir = get_data_dir()

# Copy default files if not found
init_config_files(os.path.join(dirname, "configs"), config_dir)
copy_files(os.path.join(dirname, "icons_light"), os.path.join(config_dir, "icons_light"))
copy_files(os.path.join(dirname, "icons_dark"), os.path.join(config_dir, "icons_dark"))
copy_files(os.path.join(dirname, "commands"), commands_dir)

config_data = load_json(os.path.join(config_dir, "config.json"))

# Init dictionaries from ~/.config/nwgcc/config.json
ICONS: dict = config_data["icons"]
if "custom_rows" in config_data:
    CUSTOM_ROWS: dict = config_data["custom_rows"]
else:
    CUSTOM_ROWS = {}
if "buttons" in config_data:
    BUTTONS: dict = config_data["buttons"]
else:
    BUTTONS = {}

del config_data

# Load commands from ~/.local/share/nwgcc/preferences.json
# Check the file presence and validity first
preferences: dict = init_preferences(os.path.join(dirname, "preferences/preferences.json"),
                               os.path.join(data_dir, "preferences.json"))

ON_CLICK: dict = init_preferences(os.path.join(dirname, "preferences/on_click.json"),
                               os.path.join(data_dir, "on_click.json"))

# Load commands from ~/.local/share/nwgcc/commands/
COMMANDS: dict = load_commands(commands_dir)

icons_path = ""
if ICON_SET == "light":
    icons_path = os.path.join(config_dir, "icons_light")
elif ICON_SET == "dark":
    icons_path = os.path.join(config_dir, "icons_dark")
if icons_path:
    print("Icons path: '{}'".format(icons_path))
else:
    print("GTK icons in use")


# Init user-defined CLI commands list from the plain text file
CLI_COMMANDS: list = parse_cli_commands(os.path.join(config_dir, "cli_commands"))

custom_styling: bool = True
icon_theme = Gtk.IconTheme.get_default()
win_padding: int = 10


def create_pixbuf(icon, size):
    path = ""
    if ICON_SET == "light":
        path = os.path.join(config_dir, "icons_light")
    elif ICON_SET == "dark":
        path = os.path.join(config_dir, "icons_dark")

    # full path given
    if icon.startswith('/'):
        if path:
            icon = os.path.join(path, icon)
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon, size, size)
        except:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(dirname, 'icons_light/icon-missing.svg'),
                                                            size, size)
    # just name given
    else:
        # In case someone wrote 'name.svg' instead of just 'name' in the "icons" dictionary (config_dir/config.json)
        if icon.endswith(".svg"):
            icon = "".join(icon.split(".")[:-1])
        if path:
            icon = os.path.join(path, (icon + ".svg"))
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon, size, size)
            except:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(dirname, 'icons_light/icon-missing.svg'),
                                                                size, size)
        else:
            try:
                pixbuf = icon_theme.load_icon(icon, size, Gtk.IconLookupFlags.FORCE_SIZE)
            except:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(config_dir, 'icon-missing.svg'),
                                                            size, size)
    return pixbuf


def launch_from_row(widget, event, cmd):
    print("Executing '{}'".format(cmd))
    subprocess.Popen('exec {}'.format(cmd), shell=True)
    GLib.timeout_add(50, Gtk.main_quit)


class CliLabel(Gtk.Label):
    def __init__(self):
        Gtk.Label.__init__(self)
        self.set_justify(Gtk.Justification.CENTER)
        self.set_property("name", "cli-label")
        self.update()

    def update(self):
        output = ""
        for i in range(len(CLI_COMMANDS)):
            command = CLI_COMMANDS[i]
            output += cmd2string(command)
            if i < len(CLI_COMMANDS) - 1:
                output += "\n"
        self.set_text(output)


class CustomRow(Gtk.EventBox):
    def __init__(self, name, cmd="", icon=""):
        self.name = name
        self.icon = icon
        Gtk.EventBox.__init__(self)
        self.hbox = Gtk.HBox()
        self.hbox.set_property("name", "row-normal")
        pixbuf = create_pixbuf(self.icon, ICON_SIZE_SMALL) if icon else None
        self.image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.label = Gtk.Label()
        self.label.set_text(self.name)
        if self.image:
            self.hbox.pack_start(self.image, False, False, 5)
        self.hbox.pack_start(self.label, False, False, 4)
        self.add(self.hbox)
        if cmd:
            self.connect('button-press-event', launch_from_row, cmd)
            self.connect('enter-notify-event', self.on_enter_notify_event)
            self.connect('leave-notify-event', self.on_leave_notify_event)

    def update(self):
        self.name, self.icon = self.get_values()
        self.label.set_text(self.name)
        pixbuf = create_pixbuf(self.icon, ICON_SIZE_SMALL) if self.icon else None
        self.image.set_from_pixbuf(pixbuf)

    def on_enter_notify_event(self, widget, event):
        self.hbox.set_property("name", "row-selected")

    def on_leave_notify_event(self, widget, event):
        self.hbox.set_property("name", "row-normal")


class UserRow(CustomRow):
    def __init__(self, cmd=ON_CLICK["user"], icon=ICONS["user"]):
        name = "{}@{}".format(cmd2string(COMMANDS["get_user"]), cmd2string(COMMANDS["get_host"]))
        super().__init__(name, cmd, icon)

    def update(self):
        name = "{}@{}".format(cmd2string(COMMANDS["get_user"]), cmd2string(COMMANDS["get_host"]))
        self.label.set_text(name)


class BatteryRow(CustomRow):
    def __init__(self, cmd=ON_CLICK["battery"]):
        name, icon = self.get_values()
        super().__init__(name, cmd, icon)

    def get_values(self):
        name = ""
        perc_val = 0
        if is_command(COMMANDS["get_battery"]):
            name, perc_val = get_battery(COMMANDS["get_battery"])
        elif is_command(COMMANDS["get_battery_alt"]):
            name, perc_val = get_battery(COMMANDS["get_battery_alt"])
        if perc_val > 95:
            icon = ICONS["battery-full"]
        elif perc_val > 50:
            icon = ICONS["battery-good"]
        elif perc_val > 20:
            icon = ICONS["battery-low"]
        else:
            icon = ICONS["battery-empty"]
        return name, icon


class WifiRow(CustomRow):
    def __init__(self, cmd=ON_CLICK["wifi"]):
        name, icon = self.get_values()
        super().__init__(name, cmd, icon)

    def get_values(self):
        ssid = ""
        try:
            ssid = cmd2string(COMMANDS["get_ssid"])
        except:
            pass
        if ssid:
            name = ssid
            icon=ICONS["wifi-on"]
        else:
            name = "disconnected"
            icon = ICONS["wifi-off"]

        return name, icon


class BluetoothRow(CustomRow):
    def __init__(self, cmd=ON_CLICK["bluetooth"]):
        name, icon = self.get_values()
        super().__init__(name, cmd, icon)

    def get_values(self):
        if bt_on(COMMANDS["get_bluetooth_status"]):
            name = bt_name(COMMANDS["get_bluetooth_name"])
            icon=ICONS["bt-on"]
        else:
            name = "disabled"
            icon = ICONS["bt-off"]

        return name, icon


class VolumeRow(Gtk.HBox):
    def __init__(self):
        Gtk.HBox.__init__(self)
        vol, icon = self.get_values()
        pixbuf = create_pixbuf(icon, ICON_SIZE_SMALL) if icon else None
        if pixbuf:
            self.image = Gtk.Image.new_from_pixbuf(pixbuf)
            self.pack_start(self.image, False, False, 5)

        self.scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL, min=0, max=100, step=1)
        self.scale.connect("value-changed", self.set_volume)
        self.scale.set_value(vol)
        self.pack_start(self.scale, True, True, 5)

    def set_volume(self, widget):
        vol = self.scale.get_value()
        set_volume(vol)
        self.update()

    def update(self):
        vol, icon = self.get_values()
        pixbuf = create_pixbuf(icon, ICON_SIZE_SMALL) if icon else None
        if pixbuf:
            self.image.set_from_pixbuf(pixbuf)
        self.scale.set_value(vol)

    def get_values(self):
        vol = get_volume()
        if vol > 70:
            icon = ICONS["volume-high"]
        elif vol > 30:
            icon = ICONS["volume-medium"]
        else:
            icon = ICONS["volume-low"]

        return vol, icon


class BrightnessRow(Gtk.HBox):
    def __init__(self):
        Gtk.HBox.__init__(self)
        bri, icon = self.get_values()
        pixbuf = create_pixbuf(icon, ICON_SIZE_SMALL) if icon else None
        if pixbuf:
            self.image = Gtk.Image.new_from_pixbuf(pixbuf)
            self.pack_start(self.image, False, False, 5)

        self.scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL, min=0, max=100, step=1)
        self.scale.connect("value-changed", self.set_brightness)
        self.scale.set_value(bri)
        self.pack_start(self.scale, True, True, 5)

    def set_brightness(self, widget):
        bri = self.scale.get_value()
        set_brightness(COMMANDS["set_brightness"], bri)
        self.update()

    def update(self):
        bri, icon = self.get_values()
        pixbuf = create_pixbuf(icon, ICON_SIZE_SMALL) if icon else None
        if pixbuf:
            self.image.set_from_pixbuf(pixbuf)
        self.scale.set_value(bri)

    def get_values(self):
        bri = get_brightness(COMMANDS["get_brightness"])
        if bri > 90:
            icon = ICONS["brightness-full"]
        elif bri > 50:
            icon = ICONS["brightness-high"]
        elif bri > 20:
            icon = ICONS["brightness"]
        else:
            icon = ICONS["brightness-low"]

        return bri, icon


class CustomButton(Gtk.Button):
    def __init__(self, name, cmd, icon):
        Gtk.Button.__init__(self)
        pixbuf = create_pixbuf(icon, ICON_SIZE_LARGE)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.set_always_show_image(True)
        self.set_image(image)
        self.set_image_position(Gtk.PositionType.TOP)
        self.set_tooltip_text(name)
        self.connect("clicked", self.launch, cmd)

    def launch(self, widget, cmd):
        print("Executing '{}'".format(cmd))
        subprocess.Popen('exec {}'.format(cmd), shell=True)
        GLib.timeout_add(50, Gtk.main_quit)


class PreferencesButton(CustomButton):
    def __init__(self):
        Gtk.Button.__init__(self)
        pixbuf = create_pixbuf("emblem-system", ICON_SIZE_LARGE)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.set_always_show_image(True)
        self.set_image(image)
        self.set_image_position(Gtk.PositionType.TOP)
        self.set_tooltip_text("Preferences")
        self.connect("clicked", self.launch)

    def launch(self, widget):
        print("Preferences button clicked")


class MyWindow(Gtk.Window):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.brightness_row = None
        self.volume_row = None
        self.user_row = None
        self.battery_row = None
        self.wifi_row = None
        self.bluetooth_row = None
        self.set_property("name", "window")

        self.connect("key-release-event", self.handle_keyboard)

        self.init_ui()

    def init_ui(self):
        self.set_title("Control Center")
        self.set_default_size(300, 200)

        box_outer_v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=36)
        self.add(box_outer_v)

        box_outer_h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=36)
        box_outer_v.pack_start(box_outer_h, False, False, win_padding)

        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_outer_h.pack_start(v_box, True, True, win_padding)

        if CLI_COMMANDS:
            self.cli_label = CliLabel()
            v_box.pack_start(self.cli_label, True, True, 0)

            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            v_box.add(sep)

        if is_command(COMMANDS["get_brightness"]):
            self.brightness_row = BrightnessRow()
            v_box.pack_start(self.brightness_row, True, True, 0)

        self.volume_row = VolumeRow()
        v_box.pack_start(self.volume_row, True, True, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        v_box.add(sep)

        self.user_row = UserRow()
        v_box.pack_start(self.user_row, True, True, 0)

        if is_command(COMMANDS["get_ssid"]):
            self.wifi_row = WifiRow()
            v_box.pack_start(self.wifi_row, True, True, 0)
        
        if is_command(COMMANDS["get_bluetooth_status"]) and bt_service_enabled(COMMANDS):
            self.bluetooth_row = BluetoothRow()
            v_box.pack_start(self.bluetooth_row, True, True, 0)

        if is_command(COMMANDS["get_battery"].split()[0]) or is_command(COMMANDS["get_battery_alt"]):
            self.battery_row = BatteryRow()
            v_box.pack_start(self.battery_row, True, True, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        v_box.add(sep)

        if CUSTOM_ROWS:
            for pos in CUSTOM_ROWS:
                h_box = CustomRow(pos["name"], pos["cmd"], pos["icon"])
                v_box.pack_start(h_box, False, False, 0)

            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            v_box.add(sep)

        h_box = Gtk.HBox()
        # fixed Preferences button
        btn = PreferencesButton()
        h_box.pack_start(btn, True, False, 4)
        if BUTTONS:
            # user-defined buttons
            if BUTTONS:
                for pos in BUTTONS:
                    btn = CustomButton(pos["name"], cmd=pos["cmd"], icon=pos["icon"])
                    h_box.pack_start(btn, True, False, 4)
        v_box.pack_start(h_box, True, True, 0)

        self.connect("destroy", Gtk.main_quit)

    def handle_keyboard(self, item, event):
        if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()
        return True


def refresh_frequently(window):
    if window.brightness_row:
        window.brightness_row.update()
    if window.volume_row:
        window.volume_row.update()
    if window.wifi_row:
        window.wifi_row.update()
    if window.bluetooth_row:
        window.bluetooth_row.update()
    return True


def refresh_rarely(window):
    if window.battery_row:
        window.battery_row.update()
    return True


def refresh_cli(window):
    if window.cli_label:
        window.cli_label.update()
    return True


def main():
    parser = argparse.ArgumentParser(description="nwg Control Center")
    parser.add_argument("-d", "--debug", action="store_true", help="do checks, print results")
    parser.add_argument("-css", type=str, default="style.css", help="custom css file name")

    args = parser.parse_args()

    global debug
    debug = args.debug

    if debug:
        check_all_commands(COMMANDS)

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    if custom_styling:
        css_path = os.path.join(config_dir, args.css)
        try:
            provider.load_from_path(css_path)
            print("Custom css: '{}'".format(css_path))
        except:
            print("ERROR: couldn't load '{}'".format(css_path))
            css = b"""
                #row-normal {
                    padding: 2px;
                }
                #row-selected {
                    background-color: #eb4d4b;
                    padding: 2px;
                    color: #eee
                }
                """
            provider.load_from_data(css)
    else:
        print("Custom styling turned off")
        css = b"""
                        #row-normal {
                            padding: 2px;
                        }
                        #row-selected {
                            background-color: #eb4d4b;
                            padding: 2px;
                            color: #eee
                        }
                        """
        provider.load_from_data(css)

    win = MyWindow()
    win.show_all()

    # Refresh rows content in various intervals
    if REFRESH_FAST_MILLIS > 0:
        GLib.timeout_add(REFRESH_FAST_MILLIS, refresh_frequently, win)
    if REFRESH_SLOW_SECONDS > 0:
        GLib.timeout_add_seconds(REFRESH_SLOW_SECONDS, refresh_rarely, win)
    if REFRESH_CLI_SECONDS > 0:
        GLib.timeout_add_seconds(REFRESH_CLI_SECONDS, refresh_cli, win)

    time_current = int(round(time.time() * 1000)) - time_start
    print("Ready in {} ms".format(time_current))

    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())