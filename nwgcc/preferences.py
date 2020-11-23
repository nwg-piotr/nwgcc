#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from tools import save_json


class PreferencesWindow(Gtk.Window):
    def __init__(self, preferences, preferences_file):
        self.preferences = preferences
        self.preferences_file = preferences_file
        super(PreferencesWindow, self).__init__()
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_modal(True)
        self.set_property("name", "window")

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
        grid.attach(icon_set_combo, 0, 0, 1, 1)

        css_checkbutton = Gtk.CheckButton.new_with_label("Use custom css")
        css_checkbutton.set_active(self.preferences["custom_styling"])
        css_checkbutton.connect("toggled", self.on_css_toggled)
        grid.attach(css_checkbutton, 1, 0, 1, 1)

        cancel_button = Gtk.Button.new_with_label("Cancel")
        cancel_button.connect("clicked", self.on_cancel_button)
        grid.attach(cancel_button, 0, 1, 1, 1)

        apply_button = Gtk.Button.new_with_label("Apply")
        apply_button.connect("clicked", self.on_apply_button)
        grid.attach(apply_button, 1, 1, 1, 1)

        v_box.pack_start(grid, True, True, 10)

        self.show_all()

    def on_icon_set_changed(self, combo):
        self.preferences["icon_set"] = combo.get_active_id()

    def on_css_toggled(self, checkbutton):
        self.preferences["custom_styling"] = checkbutton.get_active()

    def on_cancel_button(self, button):
        self.close()

    def on_apply_button(self, button):
        save_json(self.preferences, self.preferences_file)
        GLib.timeout_add(0, Gtk.main_quit)

    def handle_keyboard(self, item, event):
        if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
            self.close()
        return True
