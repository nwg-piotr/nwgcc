#!/usr/bin/env python3

# Dependencies: python-pyalsa
# Optional: bluez bluez-utils
# User defined commands: blueman-manager

import time
time_start = int(round(time.time() * 1000))
import gi
import os
import sys
import subprocess
import argparse

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

from tools import cmd2string, get_volume, set_volume, bt_on, bt_name, bt_service_enabled, get_battery, is_command, check_all_commands

ICON_SIZE_SMALL: int = 16
ICON_SIZE_LARGE: int = 24

config_dir = "/home/piotr/.config/sgtk-menu"
icon_theme = Gtk.IconTheme.get_default()
win_padding = 10

CUSTOM_COMMANDS: list = [
    {
        "name": "Wayfire Config Manager",
        "cmd": "wcm > /dev/null 2>&1",
        "icon": "/opt/wayfire/share/wayfire/icons/wayfire.png"
    },
    {
        "name": "Wallpaper Manager",
        "cmd": "azote > /dev/null 2>&1",
        "icon": "/usr/share/azote/indicator_attention.png"
    },
    {
        "name": "Lock screen",
        "cmd": "swaylock -f -c 000000",
        "icon": "system-lock-screen"
    }
]

BUTTONS: list = [
    {
        "name": "Preferences",
        "cmd": "swaylock -f -c 000000",
        "icon": "emblem-system"
    },
    {
        "name": "Exit",
        "cmd": "nwgbar -t exit-wayfire.json -c dock.css -o 0.0",
        "icon": "application-exit"
    }
]

CLI_COMMANDS: dict = {
    "get_user": "echo $USER",
    "get_host": "uname -n",
    "get_ssid": "iwgetid -r",
    "get_battery": "upower -i $(upower -e | grep BAT) | grep --color=never -E 'state|to\\ full|to\\ empty|percentage'",
    "get_battery_alt": "acpi",
    "get_bluetooth_status": "bluetoothctl show | grep Powered",
    "get_bluetooth_name": "bluetoothctl show | grep Name",
    "systemctl": "systemctl"
}

ON_CLICK: dict = {
    "wifi": "nm-connection-editor",
    "bluetooth": "blueman-manager",
    "battery": ""
}

ICONS: dict = {
    "battery": "battery",
    "battery-empty": "battery-empty",
    "battery-low": "battery-low",
    "battery-good": "battery-good",
    "battery-full": "battery-full",
    "user": "system-users",
    "wifi-on": "network-wireless",
    "wifi-off": "network-wireless-offline",
    "bt-on": "bluetooth-active",
    "bt-off": "bluetooth-disabled",
    "volume-low": "audio-volume-low",
    "volume-medium": "audio-volume-medium",
    "volume-high": "audio-volume-high",
    "volume-muted": "audio-volume-muted"
}


def create_pixbuf(icon, size):
    if icon.startswith('/'):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon, size, size)
        except:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(config_dir, 'icon-missing.svg'),
                                                            size, size)
    else:
        try:
            if icon.endswith('.svg') or icon.endswith('.png'):
                icon = icon.split('.')[0]
            pixbuf = icon_theme.load_icon(icon, size, Gtk.IconLookupFlags.FORCE_SIZE)
        except:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(config_dir, 'icon-missing.svg'),
                                                            size, size)
    return pixbuf


def launch_from_row(widget, event, cmd):
    print("Executing '{}'".format(cmd))
    subprocess.Popen('exec {}'.format(cmd), shell=True)
    GLib.timeout_add(50, Gtk.main_quit)


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
        print("getting values...")
        vol = get_volume()
        if vol > 70:
            icon = ICONS["volume-high"]
        elif vol > 30:
            icon = ICONS["volume-medium"]
        else:
            icon = ICONS["volume-low"]

        return vol, icon


class CustomRow(Gtk.EventBox):
    def __init__(self, name, cmd="", icon=""):
        Gtk.EventBox.__init__(self)
        self.hbox = Gtk.HBox()
        self.hbox.set_property("name", "row-normal")
        pixbuf = create_pixbuf(icon, ICON_SIZE_SMALL) if icon else None
        self.image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.label = Gtk.Label()
        self.label.set_text(name)
        if self.image:
            self.hbox.pack_start(self.image, False, False, 5)
        self.hbox.pack_start(self.label, False, False, 4)
        self.add(self.hbox)
        if cmd:
            self.connect('button-press-event', launch_from_row, cmd)
            self.connect('enter-notify-event', self.on_enter_notify_event)
            self.connect('leave-notify-event', self.on_leave_notify_event)

    def update(self):
        name, icon = self.get_values()
        self.label.set_text(name)
        pixbuf = create_pixbuf(icon, ICON_SIZE_SMALL)
        self.image.set_from_pixbuf(pixbuf)

    def on_enter_notify_event(self, widget, event):
        self.hbox.set_property("name", "row-selected")

    def on_leave_notify_event(self, widget, event):
        self.hbox.set_property("name", "row-normal")


class BatteryRow(CustomRow):
    def __init__(self, cmd=ON_CLICK["battery"]):
        name, icon = self.get_values()
        super().__init__(name, cmd, icon)

    def get_values(self):
        name = ""
        perc_val = 0
        if is_command(CLI_COMMANDS["get_battery"]):
            name, perc_val = get_battery(CLI_COMMANDS["get_battery"])
        elif is_command(CLI_COMMANDS["get_battery_alt"]):
            name, perc_val = get_battery(CLI_COMMANDS["get_battery_alt"])
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
            ssid = cmd2string(CLI_COMMANDS["get_ssid"])
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
        if bt_on(CLI_COMMANDS["get_bluetooth_status"]):
            name = bt_name(CLI_COMMANDS["get_bluetooth_name"])
            icon=ICONS["bt-on"]
        else:
            name = "disabled"
            icon = ICONS["bt-off"]

        return name, icon


class CustomButton(Gtk.Button):
    def __init__(self, name, cmd, icon):
        Gtk.Button.__init__(self)
        pixbuf = create_pixbuf(icon, ICON_SIZE_LARGE)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.set_property("name", "button")
        self.set_always_show_image(True)
        self.set_image(image)
        self.set_image_position(Gtk.PositionType.TOP)
        self.set_tooltip_text(name)
        self.connect("clicked", self.launch, cmd)

    def launch(self, widget, cmd):
        print("Executing '{}'".format(cmd))
        subprocess.Popen('exec {}'.format(cmd), shell=True)
        GLib.timeout_add(50, Gtk.main_quit)


class MyWindow(Gtk.Window):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.volume_row = None
        self.battery_row = None
        self.wifi_row = None
        self.bluetooth_row = None

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

        self.volume_row = VolumeRow()
        v_box.pack_start(self.volume_row, True, True, 0)

        h_box = CustomRow("{}@{}".format(cmd2string(CLI_COMMANDS["get_user"]), cmd2string(CLI_COMMANDS["get_host"])),
                          icon=ICONS["user"])
        v_box.pack_start(h_box, True, True, 0)

        if is_command(CLI_COMMANDS["get_ssid"]):
            self.wifi_row = WifiRow()
            v_box.pack_start(self.wifi_row, True, True, 0)
        
        if bt_service_enabled(CLI_COMMANDS) and is_command(CLI_COMMANDS["get_bluetooth_status"]):
            self.bluetooth_row = BluetoothRow()
            v_box.pack_start(self.bluetooth_row, True, True, 0)

        if is_command(CLI_COMMANDS["get_battery"].split()[0]) or is_command(CLI_COMMANDS["get_battery_alt"]):
            self.battery_row = BatteryRow()
            v_box.pack_start(self.battery_row, True, True, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        v_box.add(sep)

        if CUSTOM_COMMANDS:
            for pos in CUSTOM_COMMANDS:
                h_box = CustomRow(pos["name"], pos["cmd"], pos["icon"])
                v_box.pack_start(h_box, False, False, 0)

            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            v_box.add(sep)

        if BUTTONS:
            h_box = Gtk.HBox()
            for pos in BUTTONS:
                btn = CustomButton(pos["name"], cmd=pos["cmd"], icon=pos["icon"])
                h_box.pack_start(btn, True, False, 4)
            v_box.pack_start(h_box, True, True, 0)

        self.connect("destroy", Gtk.main_quit)


def refresh_frequently(window):
    window.volume_row.update()
    window.wifi_row.update()
    window.bluetooth_row.update()
    return True


def refresh_rarely(window):
    window.battery_row.update()
    return True


def main():
    parser = argparse.ArgumentParser(description="nwg Control Center")
    parser.add_argument("-d", "--debug", action="store_true", help="do checks, print results")
    args = parser.parse_args()

    if args.debug:
        check_all_commands(CLI_COMMANDS)

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()

    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
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
    GLib.timeout_add_seconds(1, refresh_frequently, win)
    GLib.timeout_add_seconds(5, refresh_rarely, win)
    time_current = int(round(time.time() * 1000)) - time_start
    print("Created in {} ms".format(time_current))
    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())