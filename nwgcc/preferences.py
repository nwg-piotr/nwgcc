#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from tools import save_json, load_cli_commands, save_string


class PreferencesWindow(Gtk.Window):
    def __init__(self, preferences, preferences_path, cli_path):
        self.preferences = preferences
        self.preferences_file = preferences_path
        self.cli_path = cli_path
        self.cli_commands = load_cli_commands(self.cli_path)
        self.cli_textview = Gtk.TextView()

        super(PreferencesWindow, self).__init__()
        self.set_default_size(400, 100)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_modal(True)
        self.set_property("name", "preferences")

        self.connect("key-release-event", self.handle_keyboard)

        self.init_ui()

    def init_ui(self):
        self.set_title("Preferences")

        box_outer_v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=36)
        self.add(box_outer_v)

        box_outer_h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=36)
        box_outer_v.pack_start(box_outer_h, False, False, 10)

        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_outer_h.pack_start(v_box, True, True, 10)

        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_column_homogeneous(True)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("Command(s) to produce CLI label content:")
        grid.attach(label, 0, 0, 3, 1)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        text_buffer = Gtk.TextBuffer()
        text_buffer.set_text(self.cli_commands)
        self.cli_textview.set_buffer(text_buffer)

        scrolled_window.add(self.cli_textview)

        grid.attach(scrolled_window, 0, 1, 3, 1)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("COMPONENTS TO DISPLAY:")
        grid.attach(label, 0, 2, 1, 1)

        checkbutton = Gtk.CheckButton.new_with_label("CLI label")
        checkbutton.set_active(self.preferences["show_cli_label"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_cli_label")
        grid.attach(checkbutton, 0, 3, 1, 1)

        checkbutton = Gtk.CheckButton.new_with_label("Brightness slider")
        checkbutton.set_active(self.preferences["show_brightness_slider"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_brightness_slider")
        grid.attach(checkbutton, 1, 3, 1, 1)

        checkbutton = Gtk.CheckButton.new_with_label("Volume slider")
        checkbutton.set_active(self.preferences["show_volume_slider"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_volume_slider")
        grid.attach(checkbutton, 2, 3, 1, 1)

        checkbutton = Gtk.CheckButton.new_with_label("User info")
        checkbutton.set_active(self.preferences["show_user_line"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_user_line")
        grid.attach(checkbutton, 0, 4, 1, 1)

        checkbutton = Gtk.CheckButton.new_with_label("Wi-fi status")
        checkbutton.set_active(self.preferences["show_wifi_line"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_wifi_line")
        grid.attach(checkbutton, 1, 4, 1, 1)

        checkbutton = Gtk.CheckButton.new_with_label("Bluetooth status")
        checkbutton.set_active(self.preferences["show_bt_line"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_bt_line")
        grid.attach(checkbutton, 2, 4, 1, 1)

        checkbutton = Gtk.CheckButton.new_with_label("Battery level")
        checkbutton.set_active(self.preferences["show_battery_line"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_battery_line")
        grid.attach(checkbutton, 0, 5, 1, 1)

        checkbutton = Gtk.CheckButton.new_with_label("User rows")
        checkbutton.set_active(self.preferences["show_user_rows"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_user_rows")
        grid.attach(checkbutton, 1, 5, 1, 1)

        checkbutton = Gtk.CheckButton.new_with_label("User buttons")
        checkbutton.set_active(self.preferences["show_user_buttons"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_user_buttons")
        grid.attach(checkbutton, 2, 5, 1, 1)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(sep, 0, 6, 3, 1)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("WINDOW SETTINGS:")
        grid.attach(label, 0, 7, 1, 1)

        icon_set_combo = Gtk.ComboBoxText()
        icon_set_combo.append("light", "Light icons")
        icon_set_combo.append("dark", "Dark icons")
        icon_set_combo.append("gtk", "GTK icons")
        if self.preferences["icon_set"] == "light":
            icon_set_combo.set_active_id("light")
        elif self.preferences["icon_set"] == "dark":
            icon_set_combo.set_active_id("dark")
        elif self.preferences["icon_set"] == "gtk":
            icon_set_combo.set_active_id("gtk")
        icon_set_combo.connect("changed", self.on_icon_set_changed)
        grid.attach(icon_set_combo, 0, 8, 1, 1)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("Small icons size")
        grid.attach(label, 1, 7, 1, 1)

        spin_button = Gtk.SpinButton.new_with_range(0, 3600, 1)
        spin_button.set_value(self.preferences["icon_size_small"])
        spin_button.connect("value-changed", self.on_spin_value_changed, "icon_size_small")
        grid.attach(spin_button, 1, 8, 1, 1)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("Large icons size")
        grid.attach(label, 2, 7, 1, 1)

        spin_button = Gtk.SpinButton.new_with_range(0, 3600, 1)
        spin_button.set_value(self.preferences["icon_size_large"])
        spin_button.connect("value-changed", self.on_spin_value_changed, "icon_size_large")
        grid.attach(spin_button, 2, 8, 1, 1)

        checkbutton = Gtk.CheckButton.new_with_label("Use custom css")
        checkbutton.set_active(self.preferences["custom_styling"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "custom_styling")
        grid.attach(checkbutton, 0, 9, 1, 1)

        checkbutton = Gtk.CheckButton.new_with_label("Keep window open")
        checkbutton.set_active(self.preferences["dont_close"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "dont_close")
        grid.attach(checkbutton, 1, 9, 1, 1)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("CLI label refresh rate [s]")
        grid.attach(label, 0, 10, 1, 1)

        spin_button = Gtk.SpinButton.new_with_range(0, 3600, 1)
        spin_button.set_value(self.preferences["refresh_cli_seconds"])
        spin_button.connect("value-changed", self.on_spin_value_changed, "refresh_cli_seconds")
        grid.attach(spin_button, 0, 11, 1, 1)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("Sliders, Wi-Fi, BT [ms]")
        grid.attach(label, 1, 10, 1, 1)

        spin_button = Gtk.SpinButton.new_with_range(0, 1000, 1)
        spin_button.set_value(self.preferences["refresh_fast_millis"])
        spin_button.connect("value-changed", self.on_spin_value_changed, "refresh_fast_millis")
        grid.attach(spin_button, 1, 11, 1, 1)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("Battery refresh rate [s]")
        grid.attach(label, 2, 10, 1, 1)

        spin_button = Gtk.SpinButton.new_with_range(1, 60, 1)
        spin_button.set_value(self.preferences["refresh_slow_seconds"])
        spin_button.connect("value-changed", self.on_spin_value_changed, "refresh_slow_seconds")
        grid.attach(spin_button, 2, 11, 1, 1)

        cancel_button = Gtk.Button.new_with_label("Cancel")
        cancel_button.connect("clicked", self.on_cancel_button)
        grid.attach(cancel_button, 1, 12, 1, 1)

        apply_button = Gtk.Button.new_with_label("Apply")
        apply_button.connect("clicked", self.on_apply_button)
        grid.attach(apply_button, 2, 12, 1, 1)

        v_box.pack_start(grid, True, True, 10)

        self.show_all()

    def on_icon_set_changed(self, combo):
        self.preferences["icon_set"] = combo.get_active_id()

    def on_checkbutton_toggled(self, checkbutton, preferences_key):
        self.preferences[preferences_key] = checkbutton.get_active()

    def on_spin_value_changed(self, spin_button, preferences_key):
        self.preferences[preferences_key] = int(spin_button.get_value())

    def on_cancel_button(self, button):
        self.close()

    def on_apply_button(self, button):
        self.save_cli_commands()
        save_json(self.preferences, self.preferences_file)
        GLib.timeout_add(0, Gtk.main_quit)

    def save_cli_commands(self):
        buffer = self.cli_textview.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        self.cli_commands = self.cli_textview.get_buffer().get_text(start, end, True)
        save_string(self.cli_commands, self.cli_path)

    def handle_keyboard(self, item, event):
        if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
            self.close()
        return True
