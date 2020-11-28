#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

import shared
from tools import save_json, load_cli_commands, save_string, create_pixbuf


class PreferencesWindow(Gtk.Window):
    def __init__(self, pref, preferences_path, cli_path, config_data, config_file_path, icons_dict):
        self.pref = pref
        self.preferences = pref["preferences"]
        self.preferences_file = preferences_path
        self.cli_path = cli_path
        self.config_data = config_data
        self.config_file_path = config_file_path
        self.icons_dict = icons_dict
        self.cli_commands = load_cli_commands(self.cli_path)
        self.cli_textview = Gtk.TextView()

        super(PreferencesWindow, self).__init__()
        self.set_title("nwgcc: Preferences")
        self.set_default_size(400, 100)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_modal(True)
        self.set_property("name", "preferences")

        self.connect("key-release-event", self.handle_keyboard)

        self.init_ui()

    def init_ui(self):
        box_outer_v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=36)
        self.add(box_outer_v)

        box_outer_h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=36)
        box_outer_v.pack_start(box_outer_h, True, True, 20)

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

        hbox = Gtk.HBox()
        checkbutton = Gtk.CheckButton.new_with_label("User info")
        checkbutton.set_active(self.preferences["show_user_line"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_user_line")
        hbox.pack_start(checkbutton, False, False, 0)
        button = Gtk.Button()
        image = Gtk.Image.new_from_pixbuf(create_pixbuf(self.icons_dict["click-me"], 16))
        button.set_image(image)
        button.connect("clicked", self.on_edit_command_user)
        hbox.pack_end(button, False, False, 0)
        grid.attach(hbox, 0, 4, 1, 1)

        hbox = Gtk.HBox()
        checkbutton = Gtk.CheckButton.new_with_label("Wi-fi status")
        checkbutton.set_active(self.preferences["show_wifi_line"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_wifi_line")
        hbox.pack_start(checkbutton, False, False, 0)
        button = Gtk.Button()
        image = Gtk.Image.new_from_pixbuf(create_pixbuf(self.icons_dict["click-me"], 16))
        button.set_image(image)
        button.connect("clicked", self.on_edit_command_wifi)
        hbox.pack_end(button, False, False, 0)
        grid.attach(hbox, 1, 4, 1, 1)

        hbox = Gtk.HBox()
        checkbutton = Gtk.CheckButton.new_with_label("Bluetooth status")
        checkbutton.set_active(self.preferences["show_bt_line"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_bt_line")
        hbox.pack_start(checkbutton, False, False, 0)
        button = Gtk.Button()
        image = Gtk.Image.new_from_pixbuf(create_pixbuf(self.icons_dict["click-me"], 16))
        button.set_image(image)
        button.connect("clicked", self.on_edit_command_bluetooth)
        hbox.pack_end(button, False, False, 0)
        grid.attach(hbox, 2, 4, 1, 1)

        hbox = Gtk.HBox()
        checkbutton = Gtk.CheckButton.new_with_label("Battery level")
        checkbutton.set_active(self.preferences["show_battery_line"])
        checkbutton.connect("toggled", self.on_checkbutton_toggled, "show_battery_line")
        hbox.pack_start(checkbutton, False, False, 0)
        button = Gtk.Button()
        image = Gtk.Image.new_from_pixbuf(create_pixbuf(self.icons_dict["click-me"], 16))
        button.set_image(image)
        button.connect("clicked", self.on_edit_command_battery)
        hbox.pack_end(button, False, False, 0)
        grid.attach(hbox, 0, 5, 1, 1)

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

        button_box = Gtk.HBox(True, False)

        button = Gtk.Button.new_with_label("User rows")
        button.connect("clicked", self.on_user_rows_button)
        button_box.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_label("User buttons")
        button.connect("clicked", self.on_user_buttons_button)
        button_box.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_label("Icons")
        button.connect("clicked", self.on_icons_button)
        button_box.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_label("Cancel")
        button.connect("clicked", self.on_cancel_button)
        button_box.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_label("Apply")
        button.connect("clicked", self.on_apply_button)
        button_box.pack_start(button, True, True, 0)

        grid.attach(button_box, 0, 12, 3, 1)

        box_outer_h.pack_start(grid, True, True, 20)

        self.show_all()

    def on_edit_command_user(self, button):
        cew = CommandEditionWindow(self.preferences, "on-click-user")

    def on_edit_command_wifi(self, button):
        cew = CommandEditionWindow(self.preferences, "on-click-wifi")

    def on_edit_command_bluetooth(self, button):
        cew = CommandEditionWindow(self.preferences, "on-click-bluetooth")

    def on_edit_command_battery(self, button):
        cew = CommandEditionWindow(self.preferences, "on-click-battery")

    def on_icon_set_changed(self, combo):
        self.preferences["icon_set"] = combo.get_active_id()

    def on_checkbutton_toggled(self, checkbutton, preferences_key):
        self.preferences[preferences_key] = checkbutton.get_active()

    def on_spin_value_changed(self, spin_button, preferences_key):
        self.preferences[preferences_key] = int(spin_button.get_value())

    def on_user_rows_button(self, button):
        tew = TemplateEditionWindow(self.preferences, "User rows", self.config_data, self.config_file_path, "custom_rows")

    def on_user_buttons_button(self, button):
        tew = TemplateEditionWindow(self.preferences, "User buttons", self.config_data, self.config_file_path, "buttons")

    def on_icons_button(self, button):
        iew = IconsEditionWindow(self.icons_dict)

    def on_cancel_button(self, button):
        self.close()

    def on_apply_button(self, button):
        self.save_cli_commands()
        save_json(self.pref, self.preferences_file)
        save_json(self.config_data, self.config_file_path)
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


class TemplateEditionWindow(Gtk.Window):
    def __init__(self, preferences, win_name, config, config_file_path, config_key):
        self.preferences = preferences
        self.config = config
        self.config_file_path = config_file_path
        self.config_key = config_key

        self.grid = Gtk.Grid()
        self.box_outer_h = None
        self.empty_row = None

        self.data_rows = []
        self.local_data_copy = config[config_key].copy()

        super(TemplateEditionWindow, self).__init__()
        self.set_title("nwgcc: Edit {}".format(win_name))
        self.set_default_size(700, 100)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_modal(True)
        self.set_property("name", "preferences")

        self.connect("key-release-event", self.handle_keyboard)

        self.init_ui()

    def init_ui(self):
        box_outer_v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=36)
        box_outer_v.set_property("name", "user-form")
        self.add(box_outer_v)

        self.box_outer_h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=36)
        box_outer_v.pack_start(self.box_outer_h, True, True, 20)

        self.build_grid()

    def build_grid(self):
        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(10)
        self.grid.set_row_spacing(10)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("Label")
        self.grid.attach(label, 0, 0, 1, 1)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("Command")
        self.grid.attach(label, 1, 0, 1, 1)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("Icon name or path")
        self.grid.attach(label, 2, 0, 1, 1)

        self.data_rows = []
        if self.local_data_copy:
            for i in range(len(self.local_data_copy)):
                data_row = self.local_data_copy[i]
                row = self.GridRowContent(data_row["name"], data_row["cmd"], data_row["icon"])
                self.data_rows.append(row)

        for i in range(len(self.data_rows)):
            row = self.data_rows[i]
            self.grid.attach(row.name, 0, i + 1, 1, 1)
            self.grid.attach(row.command, 1, i + 1, 1, 1)
            self.grid.attach(row.icon, 2, i + 1, 1, 1)
            self.grid.attach(row.file_chooser_button, 3, i + 1, 1, 1)

            button = Gtk.Button()
            image = Gtk.Image.new_from_pixbuf(create_pixbuf("edit-delete-symbolic", self.preferences["icon_size_small"]))
            button.set_image(image)
            button.connect("clicked", self.on_del_button, i)
            self.grid.attach(button, 4, i + 1, 1, 1)

        self.empty_row = self.GridRowContent("", "", "")
        self.empty_row.name.set_placeholder_text("Enter new label")
        self.empty_row.command.set_placeholder_text("Enter new command")
        self.empty_row.icon.set_placeholder_text("Enter name or choose a file")

        # Empty row at the bottom
        new_row_idx = len(self.data_rows) + 1

        self.grid.attach(self.empty_row.name, 0, new_row_idx, 1, 1)
        self.grid.attach(self.empty_row.command, 1, new_row_idx, 1, 1)
        self.grid.attach(self.empty_row.icon, 2, new_row_idx, 1, 1)
        self.grid.attach(self.empty_row.file_chooser_button, 3, new_row_idx, 1, 1)

        button = Gtk.Button()
        image = Gtk.Image.new_from_pixbuf(create_pixbuf("list-add-symbolic", self.preferences["icon_size_small"]))
        button.set_image(image)
        button.connect("clicked", self.on_add_button)
        self.grid.attach(button, 4, new_row_idx, 1, 1)

        button = Gtk.Button()
        button.set_label("Cancel")
        button.connect("clicked", self.on_cancel_button)
        self.grid.attach(button, 3, new_row_idx + 1, 1, 1)

        button = Gtk.Button()
        button.set_label("Apply")
        button.connect("clicked", self.on_apply_button)
        self.grid.attach(button, 4, new_row_idx + 1, 1, 1)

        try:
            self.data_rows[0].name.select_region(0, 0)
        except:
            pass
        self.empty_row.name.grab_focus()

        self.box_outer_h.pack_start(self.grid, True, True, 20)
        self.show_all()

    def on_del_button(self, button, index):
        del self.local_data_copy[index]
        while True:
            if self.grid.get_child_at(0, 0) is not None:
                self.grid.remove_row(0)
            else:
                break
        self.box_outer_h.remove(self.grid)
        del self.grid
        self.build_grid()

    def on_add_button(self, button):
        name = self.empty_row.name.get_text()
        command = self.empty_row.command.get_text()
        icon = self.empty_row.icon.get_text()
        new: dict = {"name": name, "cmd": command, "icon": icon}
        self.local_data_copy.append(new)

        while True:
            if self.grid.get_child_at(0, 0) is not None:
                self.grid.remove_row(0)
            else:
                break
        self.box_outer_h.remove(self.grid)
        del self.grid
        self.build_grid()

    def on_cancel_button(self, button):
        self.close()

    def on_apply_button(self, button):
        # Assign values from Entry fields to the local data
        for i in range(len(self.data_rows)):
            row = self.data_rows[i]
            self.local_data_copy[i]["name"] = row.name.get_text()
            self.local_data_copy[i]["cmd"] = row.command.get_text()
            self.local_data_copy[i]["icon"] = row.icon.get_text()

        # Update actual config dictionary
        for i in range(len(self.local_data_copy)):
            self.config[self.config_key] = self.local_data_copy

        self.close()

    class GridRowContent(object):
        def __init__(self, name, command, icon):
            self.name = Gtk.Entry()
            self.name.set_property("name", "edit-field")
            self.name.set_text(name)
            self.name.set_width_chars(20)

            self.command = Gtk.Entry()
            self.command.set_property("name", "edit-field")
            self.command.set_text(command)
            self.command.set_width_chars(25)

            self.icon = Gtk.Entry()
            self.icon.set_property("name", "edit-field")
            self.icon.set_text(icon)
            self.icon.set_width_chars(40)
            self.icon.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, create_pixbuf(icon, 16))
            self.icon.connect("changed", self.on_icon_changed)

            self.file_chooser_button = Gtk.FileChooserButton("", Gtk.FileChooserAction.OPEN)
            self.file_chooser_button.set_width_chars(5)
            self.file_chooser_button.set_current_folder(shared.initial_path)
            self.file_chooser_button.connect("file-set", self.on_file_set)

        def on_icon_changed(self, entry):
            self.icon.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, create_pixbuf(entry.get_text(), 16))

        def on_file_set(self, file_chooser):
            path = file_chooser.get_filename()
            self.icon.set_text(path)
            self.icon.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, create_pixbuf(path, 16))
            shared.initial_path = "/".join(path.split("/")[:-1])

    def handle_keyboard(self, item, event):
        if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
            self.close()
        return True


class CommandEditionWindow(Gtk.Window):
    def __init__(self, preferences, preferences_key):
        self.preferences = preferences
        self.preferences_key = preferences_key
        self.command = None

        super(CommandEditionWindow, self).__init__()
        self.set_title("nwgcc: Edit command")
        self.set_default_size(10, 10)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_modal(True)
        self.set_property("name", "preferences")

        self.connect("key-release-event", self.handle_keyboard)

        self.init_ui()

    def init_ui(self):
        box_outer_v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box_outer_v.set_property("name", "user-form")
        self.add(box_outer_v)

        box_outer_h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box_outer_v.pack_start(box_outer_h, True, True, 0)

        hbox = Gtk.HBox()

        self.command = Gtk.Entry()
        self.command.set_property("name", "edit-field")
        self.command.set_placeholder_text("Enter new command")
        self.command.set_text(self.preferences[self.preferences_key])
        self.command.set_width_chars(25)
        hbox.pack_start(self.command, True, True, 10)

        button = Gtk.Button.new_with_label("Cancel")
        button.connect("clicked", self.on_cancel_button)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_label("Apply")
        button.connect("clicked", self.on_apply_button)
        hbox.pack_start(button, True, True, 0)

        box_outer_v.pack_start(hbox, True, True, 10)
        self.show_all()

    def on_cancel_button(self, button):
        self.close()

    def on_apply_button(self, button):
        self.preferences[self.preferences_key] = self.command.get_text()
        self.close()

    def handle_keyboard(self, item, event):
        if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
            self.close()
        return True


class IconsEditionWindow(Gtk.Window):
    def __init__(self, icons_dict):
        self.icons_dict = icons_dict
        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(10)
        self.grid.set_row_spacing(10)

        super(IconsEditionWindow, self).__init__()
        self.set_title("nwgcc: Edit icons")
        self.set_default_size(10, 10)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_modal(True)
        self.set_property("name", "preferences")

        self.connect("key-release-event", self.handle_keyboard)

        self.init_ui()

    def init_ui(self):
        box_outer_v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box_outer_v.set_property("name", "user-form")
        self.add(box_outer_v)

        box_outer_h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box_outer_v.pack_start(box_outer_h, True, True, 0)

        hbox = Gtk.HBox()

        label= Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("Icon")
        self.grid.attach(label, 0, 0, 1, 1)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_text("Icon name or path")
        self.grid.attach(label, 1, 0, 1, 1)

        cnt = 1
        for key in self.icons_dict:
            row = self.ContentRow(key, self.icons_dict[key])
            self.grid.attach(row.name, 0, cnt, 1, 1)
            self.grid.attach(row.icon, 1, cnt, 1, 1)
            self.grid.attach(row.file_chooser_button, 2, cnt, 1, 1)
            cnt += 1

        buttons_box = Gtk.HBox(spacing=4)

        button = Gtk.Button.new_with_label("Restore defaults")
        buttons_box.pack_start(button, False, False, 0)

        button = Gtk.Button.new_with_label("Apply")
        buttons_box.pack_end(button, False, False, 0)

        button = Gtk.Button.new_with_label("Cancel")
        button.connect("clicked", self.on_cancel_button)
        buttons_box.pack_end(button, False, False, 0)

        self.grid.attach(buttons_box, 0, cnt + 1, 3, 1)

        hbox.pack_start(self.grid, False, False, 20)
        box_outer_v.pack_start(hbox, True, True, 10)
        self.show_all()

    class ContentRow(object):
        def __init__(self, name, icon):
            self.name = Gtk.Label()
            self.name.set_halign(Gtk.Align.START)
            self.name.set_text(name)

            self.icon = Gtk.Entry()
            self.icon.set_property("name", "edit-field")
            self.icon.set_text(icon)
            self.icon.set_width_chars(40)
            self.icon.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, create_pixbuf(icon, 16))
            self.icon.connect("changed", self.on_icon_changed)

            self.file_chooser_button = Gtk.FileChooserButton("", Gtk.FileChooserAction.OPEN)
            self.file_chooser_button.set_width_chars(5)
            self.file_chooser_button.set_current_folder(shared.initial_path)
            self.file_chooser_button.connect("file-set", self.on_file_set)

        def on_icon_changed(self, entry):
            self.icon.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, create_pixbuf(entry.get_text(), 16))

        def on_file_set(self, file_chooser):
            path = file_chooser.get_filename()
            self.icon.set_text(path)
            self.icon.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, create_pixbuf(path, 16))
            shared.initial_path = "/".join(path.split("/")[:-1])

    def on_cancel_button(self, button):
        self.close()

    def handle_keyboard(self, item, event):
        if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
            self.close()
        return True