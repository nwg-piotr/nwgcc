#!/usr/bin/env python3

# Dependencies: python-pyalsa
# Optional: bluez bluez-utils
# User defined commands: blueman-manager

import gi
import os
import sys
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
from pyalsa import alsamixer

from tools import cmd2string, get_volume, set_volume, bt_on, bt_service_enabled, get_battery, is_command

mixer = alsamixer.Mixer()
mixer.attach()
mixer.load()

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
    "get_bluetooth": "bluetoothctl show | grep Powered",
    "network": "nm-connection-editor",
    "bluetooth": "blueman-manager"
}

ICONS: dict = {
    "battery": "battery",
    "user": "system-users",
    "wifi-on": "network-wireless",
    "wifi-off": "network-wireless-offline",
    "bt-on": "bluetooth-active",
    "bt-off": "bluetooth-disabled"
}


def create_image(icon, size):
    if icon.startswith('/'):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon, size, size)
            image = Gtk.Image.new_from_pixbuf(pixbuf)
        except:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(config_dir, 'icon-missing.svg'),
                                                            size, size)
            image = Gtk.Image.new_from_pixbuf(pixbuf)
    else:
        try:
            if icon.endswith('.svg') or icon.endswith('.png'):
                icon = icon.split('.')[0]
            pixbuf = icon_theme.load_icon(icon, size, Gtk.IconLookupFlags.FORCE_SIZE)
            image = Gtk.Image.new_from_pixbuf(pixbuf)
        except:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(config_dir, 'icon-missing.svg'),
                                                            size, size)
            image = Gtk.Image.new_from_pixbuf(pixbuf)

    return image


def launch_from_row(widget, event, cmd):
    print("Executing '{}'".format(cmd))
    subprocess.Popen('exec {}'.format(cmd), shell=True)
    GLib.timeout_add(50, Gtk.main_quit)


class CustomRow(Gtk.EventBox):
    def __init__(self, name, cmd="", icon=None):
        Gtk.EventBox.__init__(self)
        self.hbox = Gtk.HBox()
        self.hbox.set_property("name", "row-normal")
        image = create_image(icon, ICON_SIZE_SMALL) if icon else None
        label = Gtk.Label()
        label.set_text(name)
        if image:
            self.hbox.pack_start(image, False, False, 5)
        self.hbox.pack_start(label, False, False, 4)
        self.add(self.hbox)
        if cmd:
            self.connect('button-press-event', launch_from_row, cmd)
            self.connect('enter-notify-event', self.on_enter_notify_event)
            self.connect('leave-notify-event', self.on_leave_notify_event)

    def on_enter_notify_event(self, widget, event):
        self.hbox.set_property("name", "row-selected")

    def on_leave_notify_event(self, widget, event):
        self.hbox.set_property("name", "row-normal")


class CustomButton(Gtk.Button):
    def __init__(self, name, cmd, icon):
        Gtk.Button.__init__(self)
        image = create_image(icon, ICON_SIZE_LARGE)
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

        self.init_ui()

    def init_ui(self):
        self.set_title("Control Center")
        self.set_default_size(200, 200)
        box_outer_v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=36)
        self.add(box_outer_v)

        box_outer_h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=36)
        box_outer_v.pack_start(box_outer_h, False, False, win_padding)

        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_outer_h.pack_start(v_box, True, True, win_padding)

        h_box = Gtk.HBox()
        image = create_image("audio-volume-medium", ICON_SIZE_SMALL)
        h_box.pack_start(image, False, False, 5)
        h_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL, min=0, max=100, step=1)
        h_scale.set_value(get_volume(mixer))
        h_box.pack_start(h_scale, True, True, 5)
        v_box.pack_start(h_box, True, True, 0)

        h_box = CustomRow("{}@{}".format(cmd2string(CLI_COMMANDS["get_user"]), cmd2string(CLI_COMMANDS["get_host"])),
                          icon=ICONS["user"])
        v_box.pack_start(h_box, True, True, 0)

        if is_command(CLI_COMMANDS["get_ssid"].split()[0]):
            ssid = ""
            try:
                ssid = cmd2string(CLI_COMMANDS["get_ssid"])
            except:
                pass
            if ssid:
                h_box = CustomRow(ssid, icon=ICONS["wifi-on"], cmd=CLI_COMMANDS["network"])
            else:
                h_box = CustomRow("Disconnected", icon=ICONS["wifi-off"], cmd=CLI_COMMANDS["network"])
            v_box.pack_start(h_box, True, True, 0)
        
        if bt_service_enabled() and is_command(CLI_COMMANDS["get_bluetooth"].split()[0]):
            if bt_on(CLI_COMMANDS["get_bluetooth"]):
                h_box = CustomRow("Enabled", icon=ICONS["bt-on"], cmd=CLI_COMMANDS["bluetooth"])
            else:
                h_box = CustomRow("Disabled", icon=ICONS["bt-off"], cmd=CLI_COMMANDS["bluetooth"])
            v_box.pack_start(h_box, True, True, 0)

        msg = ""
        perc_val = 0
        if is_command(CLI_COMMANDS["get_battery"].split()[0]):
            msg, perc_val = get_battery(CLI_COMMANDS["get_battery"])
        elif is_command(CLI_COMMANDS["get_battery_alt"].split()[0]):
            msg, perc_val = get_battery(CLI_COMMANDS["get_battery_alt"])
        print(perc_val)
        if msg:
            row = CustomRow(msg, icon=ICONS["battery"])
            v_box.pack_start(row, True, True, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        v_box.add(sep)

        if CUSTOM_COMMANDS:
            for pos in CUSTOM_COMMANDS:
                # btn = HorizontalButton(pos["name"], pos["cmd"], pos["icon"])
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


def main():
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()

    style_context.add_provider_for_screen(
        screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
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
    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())