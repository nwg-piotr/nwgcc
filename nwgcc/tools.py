#!/usr/bin/env python3

from pyalsa import alsamixer
import subprocess


def get_volume(mixer, channel="Master"):
    element = alsamixer.Element(mixer, channel)
    max_vol = element.get_volume_range()[1]

    return int(element.get_volume() * 100 / max_vol)


def set_volume(mixer, percent, channel="Master"):
    element = alsamixer.Element(mixer, channel)
    max_vol = element.get_volume_range()[1]
    element.set_volume_all(int(percent * max_vol / 100))


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
