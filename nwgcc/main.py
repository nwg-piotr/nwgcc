#!/usr/bin/env python3

"""
nwg Control Center
Copyright (c) 2020 Piotr Miller
e-mail: nwg.piotr@gmail.com
Project: https://github.com/nwg-piotr/nwgcc
License: GPL-3.0-or-later
"""

import time
time_start = int(round(time.time() * 1000))
import gi
import sys
import argparse

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, GLib

from nwgcc.tools import *
from nwgcc.preferences import PreferencesWindow

shared.dirname = os.path.dirname(__file__)
data_dir = get_data_dir()
commands_dir = os.path.join(data_dir, "commands")
config_dir = get_config_dir(data_dir)

# Copy default files if not found
init_config_files(os.path.join(shared.dirname, "configs"), config_dir)
copy_files(os.path.join(shared.dirname, "icons_light"), os.path.join(data_dir, "icons_light"))
copy_files(os.path.join(shared.dirname, "icons_dark"), os.path.join(data_dir, "icons_dark"))

# Init dictionaries from ~/.config/nwgcc/config.json
config_data = load_json(os.path.join(config_dir, "config.json"))

if "custom_rows" in config_data:
    CUSTOM_ROWS: dict = config_data["custom_rows"]
else:
    CUSTOM_ROWS = {}

if "buttons" in config_data:
    BUTTONS: dict = config_data["buttons"]
else:
    BUTTONS = {}

# Load preferences, icon and command definitions from ~/.local/share/nwgcc/preferences.json
# Check the file presence and validity first
pref: dict = init_preferences(os.path.join(shared.dirname, "preferences/preferences.json"),
                              os.path.join(data_dir, "preferences.json"))
preferences: dict = pref["preferences"]

if "icons" in pref:
    ICONS: dict = pref["icons"]
else:
    ICONS = {}
    print("ERROR: Icons dictionary missing from '{}'".format(os.path.join(config_dir, "config.json")))

if "commands" in pref:
    COMMANDS: dict = pref["commands"]
else:
    COMMANDS = {}
    print("ERROR: Commands dictionary missing from '{}'".format(os.path.join(config_dir, "config.json")))

# if path left empty, we use GTK icons
if preferences["icon_set"] == "light":
    shared.icons_path = os.path.join(data_dir, "icons_light")
elif preferences["icon_set"] == "dark":
    shared.icons_path = os.path.join(data_dir, "icons_dark")

# Init user-defined CLI commands list from the plain text file
CLI_COMMANDS: list = parse_cli_commands(os.path.join(config_dir, "cli_commands"))

shared.icon_theme = Gtk.IconTheme.get_default()


def launch_from_row(widget, event, cmd):
    print("Executing '{}'".format(cmd))
    subprocess.Popen('exec {}'.format(cmd), shell=True)
    if not preferences["dont_close"]:
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
            o = cmd2string(command)
            if len(o) > 38:
                o = "{}…".format(o[0:38])
            output += o
            if i < len(CLI_COMMANDS) - 1:
                output += "\n"
        self.set_text(output)


class CustomRow(Gtk.EventBox):
    def __init__(self, name, cmd="", icon=""):
        self.name = name
        self.icon = icon
        Gtk.EventBox.__init__(self)
        self.hbox = Gtk.HBox()

        if preferences["custom_styling"]:
            self.hbox.set_property("name", "row-normal")

        pixbuf = create_pixbuf(self.icon, preferences["icon_size_small"]) if icon else None
        self.image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.old_icon = icon  # We'll only update the image if icon != old_icon

        self.label = Gtk.Label()
        self.label.set_text(self.name)
        if self.image:
            self.hbox.pack_start(self.image, False, False, 5)
        self.hbox.pack_start(self.label, False, False, 4)
        if cmd:
            pixbuf = create_pixbuf(ICONS["click-me"], preferences["icon_size_small"])
            image = Gtk.Image.new_from_pixbuf(pixbuf)
            self.hbox.pack_end(image, False, False, 0)
            self.connect('button-press-event', launch_from_row, cmd)
            self.connect('enter-notify-event', self.on_enter_notify_event)
            self.connect('leave-notify-event', self.on_leave_notify_event)
        self.add(self.hbox)

        self.style_context = self.hbox.get_style_context()
        self.set_css_name("menuitem")

    def update(self):
        self.name, self.icon = self.get_values()
        self.label.set_text(self.name)
        if self.icon != self.old_icon:
            pixbuf = create_pixbuf(self.icon, preferences["icon_size_small"]) if self.icon else None
            self.image.set_from_pixbuf(pixbuf)
            self.old_icon = self.icon

    def on_enter_notify_event(self, widget, event):
        if preferences["custom_styling"]:
            self.hbox.set_property("name", "row-selected")
        else:
            self.style_context.set_state(Gtk.StateFlags.SELECTED)

    def on_leave_notify_event(self, widget, event):
        if preferences["custom_styling"]:
            self.hbox.set_property("name", "row-normal")
        else:
            self.style_context.set_state(Gtk.StateFlags.NORMAL)


class UserRow(CustomRow):
    def __init__(self, cmd=preferences["on-click-user"]):
        icon = ICONS["user"] if "user" in ICONS else ""
        name = "{}@{}".format(cmd2string(COMMANDS["get_user"]), cmd2string(COMMANDS["get_host"]))
        super().__init__(name, cmd, icon)

    def update(self):
        name = "{}@{}".format(cmd2string(COMMANDS["get_user"]), cmd2string(COMMANDS["get_host"]))
        self.label.set_text(name)


class BatteryRow(CustomRow):
    def __init__(self, cmd=preferences["on-click-battery"]):
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
            icon = ICONS["battery-full"] if "battery-full" in ICONS else "icon-missing"
        elif perc_val > 50:
            icon = ICONS["battery-good"] if "battery-good" in ICONS else "icon-missing"
        elif perc_val > 20:
            icon = ICONS["battery-low"] if "battery-low" in ICONS else "icon-missing"
        else:
            icon = ICONS["battery-empty"] if "battery-empty" in ICONS else "icon-missing"
        return name, icon


class WifiRow(CustomRow):
    def __init__(self, cmd=preferences["on-click-wifi"]):
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
            icon = ICONS["wifi-on"] if "wifi-on" in ICONS else "icon-missing"
        else:
            name = "disconnected"
            icon = ICONS["wifi-off"] if "wifi-off" in ICONS else "icon-missing"

        return name, icon


class BluetoothRow(CustomRow):
    def __init__(self, cmd=preferences["on-click-bluetooth"]):
        name, icon = self.get_values()
        super().__init__(name, cmd, icon)

    def get_values(self):
        if bt_on(COMMANDS["get_bt_status"]):
            name = bt_name(COMMANDS["get_bt_name"])
            icon = ICONS["bt-on"] if "bt-on" in ICONS else "icon-missing"
        else:
            name = "disabled"
            icon = ICONS["bt-off"] if "bt-off" in ICONS else "icon-missing"

        return name, icon


class VolumeRow(Gtk.HBox):
    def __init__(self):
        Gtk.HBox.__init__(self)
        vol, icon = self.get_values()
        self.old_icon = icon
        self.play_pause_icon = ICONS["media-playback-start"]
        self.play_pause_image = None
        pixbuf = create_pixbuf(icon, preferences["icon_size_small"]) if icon else None
        if pixbuf:
            self.image = Gtk.Image.new_from_pixbuf(pixbuf)
            self.pack_start(self.image, False, False, 5)

        self.scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL, min=0, max=100, step=1)
        self.scale.connect("value-changed", self.set_volume)
        if vol is not None:
            self.scale.set_value(vol)
        else:
            self.scale.set_value(0)
            self.scale.set_sensitive(False)
        self.pack_start(self.scale, True, True, 5)

        if preferences["show_playerctl"] and is_command(COMMANDS["playerctl"]):
            icon = ICONS["media-skip-backward"]
            pixbuf = create_pixbuf(icon, preferences["icon_size_small"]) if icon else None
            image = Gtk.Image.new_from_pixbuf(pixbuf)
            eb = Gtk.EventBox()
            eb.add(image)
            eb.connect('button-press-event', self.playerctl, "previous")
            self.pack_start(eb, False, False, 4)

            if self.playerctl_status() == "Paused" or self.playerctl_status() == "Stopped":
                self.play_pause_icon = ICONS["media-playback-start"]
            else:
                self.play_pause_icon = ICONS["media-playback-pause"]
            pixbuf = create_pixbuf(self.play_pause_icon, preferences["icon_size_small"]) if icon else None
            self.play_pause_image = Gtk.Image.new_from_pixbuf(pixbuf)
            eb = Gtk.EventBox()
            eb.add(self.play_pause_image)
            eb.connect('button-press-event', self.playerctl, "play-pause")
            self.pack_start(eb, False, False, 4)

            icon = ICONS["media-skip-forward"]
            pixbuf = create_pixbuf(icon, preferences["icon_size_small"]) if icon else None
            image = Gtk.Image.new_from_pixbuf(pixbuf)
            eb = Gtk.EventBox()
            eb.add(image)
            eb.connect('button-press-event', self.playerctl, "next")
            self.pack_start(eb, False, False, 4)

    def set_volume(self, widget):
        vol = self.scale.get_value()
        set_volume(vol, COMMANDS["set_volume_alt"])
        self.update()

    def update(self):
        vol, icon = self.get_values()
        if icon != self.old_icon:
            pixbuf = create_pixbuf(icon, preferences["icon_size_small"]) if icon else None
            if pixbuf:
                self.image.set_from_pixbuf(pixbuf)
                self.old_icon = icon

        if vol is not None:
            self.scale.set_value(vol)
        else:
            self.scale.set_value(0)
            self.scale.set_sensitive(False)

        if preferences["show_playerctl"]:
            if self.playerctl_status() == "Playing":
                icon = ICONS["media-playback-pause"]
            else:
                icon = ICONS["media-playback-start"]
            if icon != self.play_pause_icon:
                self.play_pause_icon = icon
                pixbuf = create_pixbuf(icon, preferences["icon_size_small"]) if icon else None
                if self.play_pause_image:
                    self.play_pause_image.set_from_pixbuf(pixbuf)

    def get_values(self):
        vol, switch = get_volume(COMMANDS["get_volume_alt"])
        if switch:
            if vol is not None:
                if vol > 70:
                    icon = ICONS["volume-high"] if "volume-high" in ICONS else "icon-missing"
                elif vol > 30:
                    icon = ICONS["volume-medium"] if "volume-medium" in ICONS else "icon-missing"
                else:
                    icon = ICONS["volume-low"] if "volume-low" in ICONS else "icon-missing"
            else:
                icon = ICONS["volume-muted"] if "volume-low" in ICONS else "icon-missing"
        else:
            icon = ICONS["volume-muted"] if "volume-low" in ICONS else "icon-missing"

        return vol, icon

    def playerctl_status(self):
        return cmd2string("playerctl status /dev/null 2>&1")

    def playerctl(self, widget, event, cmd):
        subprocess.call("playerctl {} /dev/null 2>&1".format(cmd), shell=True)


class BrightnessRow(Gtk.HBox):
    def __init__(self):
        Gtk.HBox.__init__(self)
        bri, icon = self.get_values()
        self.old_icon = icon
        pixbuf = create_pixbuf(icon, preferences["icon_size_small"]) if icon else None
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
        if icon != self.old_icon:
            pixbuf = create_pixbuf(icon, preferences["icon_size_small"]) if icon else None
            if pixbuf:
                self.image.set_from_pixbuf(pixbuf)
            self.old_icon = icon

        self.scale.set_value(bri)

    def get_values(self):
        bri = get_brightness(COMMANDS["get_brightness"])
        if bri > 70:
            icon = ICONS["brightness-high"] if "brightness-high" in ICONS else "icon-missing"
        elif bri > 30:
            icon = ICONS["brightness-medium"] if "brightness-medium" in ICONS else "icon-missing"
        else:
            icon = ICONS["brightness-low"] if "brightness-low" in ICONS else "icon-missing"

        return bri, icon


class CustomButton(Gtk.Button):
    def __init__(self, name, cmd, icon):
        Gtk.Button.__init__(self)
        self.set_property("name", "custom-button")
        pixbuf = create_pixbuf(icon, preferences["icon_size_large"])
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.set_always_show_image(True)
        self.set_image(image)
        self.set_image_position(Gtk.PositionType.TOP)
        self.set_tooltip_text(name)
        self.connect("clicked", self.launch, cmd)

    def launch(self, widget, cmd):
        if cmd:
            print("Executing '{}'".format(cmd))
            subprocess.Popen('exec {}'.format(cmd), shell=True)
        else:
            print("No command assigned")
        if not preferences["dont_close"] and cmd:
            GLib.timeout_add(50, Gtk.main_quit)


class PreferencesButton(CustomButton):
    def __init__(self):
        Gtk.Button.__init__(self)
        self.set_property("name", "custom-button")
        pixbuf = create_pixbuf("emblem-system-symbolic", preferences["icon_size_large"])
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.set_always_show_image(True)
        self.set_image(image)
        self.set_image_position(Gtk.PositionType.TOP)
        self.set_tooltip_text("Preferences")
        self.connect("clicked", self.launch)

    def launch(self, widget):
        preferences_window = PreferencesWindow(pref,
                                               os.path.join(data_dir, "preferences.json"),
                                               os.path.join(config_dir, "cli_commands"),
                                               config_data,
                                               os.path.join(config_dir, "config.json"),
                                               ICONS)
        preferences_window.show()


class MyWindow(Gtk.Window):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.cli_label = None
        self.brightness_row = None
        self.volume_row = None
        self.user_row = None
        self.battery_row = None
        self.wifi_row = None
        self.bluetooth_row = None
        self.preferences_btn = None
        self.set_property("name", "window")
        if shared.args.pointer:
            self.set_position(Gtk.WindowPosition.MOUSE)

        self.connect("key-release-event", self.handle_keyboard)

        self.init_ui()

    def init_ui(self):
        self.set_title("nwgcc: Control Center")
        self.set_default_size(300, 200)
        self.set_decorated(preferences["window_decorations"])

        box_outer_v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=36)
        self.add(box_outer_v)

        box_outer_h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=36)
        box_outer_v.pack_start(box_outer_h, False, False, 10)

        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_outer_h.pack_start(v_box, True, True, 10)

        if preferences["show_cli_label"] and CLI_COMMANDS:
            self.cli_label = CliLabel()
            v_box.pack_start(self.cli_label, True, True, 0)

            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            v_box.pack_start(sep, True, True, 6)

        if preferences["show_brightness_slider"] and is_command(COMMANDS["get_brightness"]):
            self.brightness_row = BrightnessRow()
            v_box.pack_start(self.brightness_row, True, True, 0)

        if preferences["show_volume_slider"]:
            self.volume_row = VolumeRow()
            v_box.pack_start(self.volume_row, True, True, 0)

        if preferences["show_cli_label"] or preferences["show_brightness_slider"] or preferences["show_volume_slider"]:
            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            v_box.pack_start(sep, True, True, 6)

        if preferences["show_user_line"]:
            self.user_row = UserRow()
            v_box.pack_start(self.user_row, True, True, 0)

        if preferences["show_wifi_line"] and is_command(COMMANDS["get_ssid"]):
            self.wifi_row = WifiRow()
            v_box.pack_start(self.wifi_row, True, True, 0)

        shared.bt_on = bt_service_enabled(COMMANDS) and is_command(COMMANDS["get_bt_status"])

        if shared.bt_on and preferences["show_bt_line"]:
            self.bluetooth_row = BluetoothRow()
            v_box.pack_start(self.bluetooth_row, True, True, 0)

        if preferences["show_battery_line"] and (is_command(COMMANDS["get_battery"].split()[0])
                                                 or is_command(COMMANDS["get_battery_alt"])):
            self.battery_row = BatteryRow()
            v_box.pack_start(self.battery_row, True, True, 0)

        if preferences["show_user_line"] or preferences["show_wifi_line"] \
                or preferences["show_bt_line"] or preferences["show_battery_line"]:
            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            v_box.pack_start(sep, True, True, 6)

        if preferences["show_user_rows"] and CUSTOM_ROWS:
            for pos in CUSTOM_ROWS:
                h_box = CustomRow(pos["name"], pos["cmd"], pos["icon"])
                v_box.pack_start(h_box, False, False, 0)

            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            v_box.pack_start(sep, True, True, 6)

        h_box = Gtk.HBox()
        # fixed Preferences button
        self.preferences_btn = PreferencesButton()
        h_box.pack_start(self.preferences_btn, True, False, 4)

        if preferences["show_user_buttons"] and BUTTONS:
            # user-defined buttons
            if BUTTONS:
                for pos in BUTTONS:
                    btn = CustomButton(pos["name"], cmd=pos["cmd"], icon=pos["icon"])
                    h_box.pack_start(btn, True, False, 4)
        v_box.pack_start(h_box, True, True, 6)

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


def version():
    try:
        v = pkg_resources.require("nwgcc")[0].version
    except:
        v = 'unknown'

    return v


def main():
    parser = argparse.ArgumentParser(description="nwg Control Center")
    parser.add_argument("-v", "--version", action="store_true", help="display version information")
    parser.add_argument("-d", "--debug", action="store_true", help="do checks, print results")
    parser.add_argument("-p", "--pointer", action="store_true",
                        help="place window at the mouse pointer position (Xorg only)")
    parser.add_argument("-s", "--settings", action="store_true", help="open preferences window")
    parser.add_argument("-css", type=str, default="style.css", help="custom css file name")

    shared.args = parser.parse_args()

    if shared.args.version:
        print("nwgcc version {}".format(version()))
        sys.exit(0)

    if shared.args.debug:
        check_all_commands(COMMANDS)

    if shared.icons_path:
        if "icons_light" in shared.icons_path:
            print("Icons: Custom light")
        elif "icons_dark" in shared.icons_path:
            print("Icons: Custom dark")
    else:
        print("Icons: GTK")

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    if preferences["custom_styling"]:
        css_path = os.path.join(config_dir, shared.args.css)
        try:
            provider.load_from_path(css_path)
            print("Style: '{}'".format(css_path))
        except:
            print("ERROR: couldn't load '{}', using GTK theme".format(css_path))
            preferences["custom_styling"] = False
    else:
        print("Style: GTK")

    win = MyWindow()
    win.show_all()

    if shared.args.settings:
        win.preferences_btn.launch(win.preferences_btn)

    # Refresh rows content in various intervals
    if preferences["refresh_fast_millis"] > 0:
        GLib.timeout_add(preferences["refresh_fast_millis"], refresh_frequently, win)
    if preferences["refresh_slow_seconds"] > 0:
        GLib.timeout_add_seconds(preferences["refresh_slow_seconds"], refresh_rarely, win)
    if preferences["refresh_cli_seconds"] > 0:
        GLib.timeout_add_seconds(preferences["refresh_cli_seconds"], refresh_cli, win)

    time_current = int(round(time.time() * 1000)) - time_start
    print("Ready in {} ms".format(time_current))

    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
