#!/usr/bin/env python3

from pyalsa import alsamixer
import os
import subprocess
import json
from shutil import copyfile


def get_config_dir():
    """
    Determine config dir path, create if not found, then create sub-dirs
    """
    xdg_config_home = os.getenv('XDG_CONFIG_HOME')
    config_home = xdg_config_home if xdg_config_home else os.path.join(os.getenv("HOME"), ".config")
    config_dir = os.path.join(config_home, "nwgcc")
    if not os.path.isdir(config_dir):
        print("Creating '{}'".format(config_dir))
        os.mkdir(config_dir)

    # Icon folders
    icon_folder = os.path.join(config_dir, "icons_light")
    if not os.path.isdir(icon_folder):
        print("Creating '{}'".format(icon_folder))
        os.mkdir(icon_folder)

    icon_folder = os.path.join(config_dir, "icons_dark")
    if not os.path.isdir(os.path.join(config_dir, "icons_dark")):
        print("Creating '{}'".format(icon_folder))
        os.mkdir(icon_folder)

    return config_dir


def get_data_dir():
    """
    Determine absolute path to ~/.local/share/nwgcc, create if not found
    """
    data_dir = os.path.join(os.getenv("HOME"), ".local/share/nwgcc")
    if not os.path.isdir(data_dir):
        print("Creating '{}'".format(data_dir))
        os.mkdir(data_dir)
    # dir for txt files containing built-in commands
    commands_dir = os.path.join(data_dir, "commands")
    if not os.path.isdir(commands_dir):
        print("Creating '{}'".format(commands_dir))
        os.mkdir(commands_dir)

    return data_dir, commands_dir


def init_config_files(src_dir, config_dir):
    """
    Copy default config files if not found
    :param src_dir: resources
    :param config_dir: ~/.config/nwgcc
    """
    file = os.path.join(config_dir, "config.json")
    if not os.path.isfile(file):
        print("File '{}' not found, copying default".format(file))
        copyfile(os.path.join(src_dir, "config.json"), file)

    file = os.path.join(config_dir, "cli_commands")
    if not os.path.isfile(file):
        print("File '{}' not found, copying default".format(file))
        copyfile(os.path.join(src_dir, "cli_commands"), file)

    file = os.path.join(config_dir, "style.css")
    if not os.path.isfile(file):
        print("File '{}' not found, copying default".format(file))
        copyfile(os.path.join(src_dir, "style.css"), file)


def copy_files(src_dir, dest_dir):
    src_files = os.listdir(src_dir)
    for file in src_files:
        if not os.path.isfile(os.path.join(dest_dir, file)):
            copyfile(os.path.join(src_dir, file), os.path.join(dest_dir, file))
            print("Copying '{}'".format(os.path.join(dest_dir, file)))


def get_volume(channel="Master"):
    mixer = alsamixer.Mixer()
    mixer.attach()
    mixer.load()

    element = alsamixer.Element(mixer, channel)
    max_vol = element.get_volume_range()[1]
    vol = int(round(element.get_volume() * 100 / max_vol, 0))
    del mixer

    return vol


def set_volume(percent, channel="Master"):
    mixer = alsamixer.Mixer()
    mixer.attach()
    mixer.load()

    element = alsamixer.Element(mixer, channel)
    max_vol = element.get_volume_range()[1]
    element.set_volume_all(int(percent * max_vol / 100))
    del mixer


def get_brightness(cmd):
    brightness = None
    output = cmd2string(cmd)
    try:
        brightness = int(round(float(output), 0))
    except:
        pass

    return brightness


def set_brightness(cmd, value):
    subprocess.call("{} {}".format(cmd, value), shell=True)


def get_battery(cmd):
    msg = ""
    perc_val = 0
    if cmd.split()[0] == "upower":
        bat = []
        try:
            bat = cmd2string(cmd).splitlines()
        except:
            pass
        state, time, percentage = "", "", ""
        for line in bat:
            line = line.strip()
            if "time to empty" in line:
                line = line.replace("time to empty", "time_to_empty")
            parts = line.split()

            if "percentage:" in parts[0]:
                percentage = parts[1]
                perc_val = int(percentage.split("%")[0])
            if "state:" in parts[0]:
                state = parts[1]
            if "time_to_empty:" in parts[0]:
                time = " ".join(parts[1:])
        msg = "{} {} {}".format(percentage, state, time)
    elif cmd.split()[0] == "acpi":
        bat = ""
        try:
            bat = cmd2string(cmd).splitlines()[0]
        except:
            pass
        if bat:
            parts = bat.split()
            msg = " ".join(parts[2:])
            perc_val = int(parts[3].split("%")[0])

    return msg, perc_val


def bt_on(cmd):
    output = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
    return output.split()[1] == "yes"


def bt_name(cmd):
    output = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
    return output.split()[1]


def bt_service_enabled(commands_dict):
    result = False
    if is_command(commands_dict["systemctl"]):
        try:
            result = subprocess.check_output("systemctl is-enabled bluetooth.service", shell=True).decode(
                "utf-8").strip() == "enabled"
        except subprocess.CalledProcessError:
            # the command above returns the 'disabled` status w/ CalledProcessError, exit status 1
            pass

    return result


def cmd2string(cmd):
    return subprocess.check_output(cmd, shell=True).decode("utf-8").strip()


def is_command(cmd, verbose=False):
    cmd = cmd.split()[0]  # strip arguments
    if verbose:
        print("  '{}' ".format(cmd), end="")
    cmd = "command -v {}".format(cmd)
    try:
        is_cmd = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        if is_cmd:
            if verbose:
                print("found")

            return True

    except subprocess.CalledProcessError:
        if verbose:
            print("not found!")

        return False


def check_all_commands(commands_dict):
    print("Checking commands availability:")
    commands = []  # some commands may be the same w/ another arguments - let's skip them
    for key in commands_dict:
        command = commands_dict[key].split()[0]
        if command not in commands:
            commands.append(command)
    for command in commands:
        is_command(command, verbose=True)


def load_json(path):
    """
    :param path: patch to a json file
    :return: dict
    """
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return {}


def save_json(src_dict, path):
    with open(path, 'w') as f:
        json.dump(src_dict, f, indent=2)


def parse_cli_commands(path):
    with open(path) as file_in:
        lines = []
        for line in file_in:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("//"):
                lines.append(line)
        file_in.close()

    return lines


def load_commands(path):
    src_files = os.listdir(path)
    output = {}
    for file in src_files:
        pth = os.path.join(path, file)
        if file != "README":
            with open(pth, 'r') as p:
                data = p.read()
                output[file] = data.splitlines()[0]
            p.close()

    return output
