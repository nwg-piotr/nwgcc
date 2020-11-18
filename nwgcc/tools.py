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


def bt_service_enabled():
    result = False
    if is_command("systemctl"):
        try:
            result = subprocess.check_output("systemctl is-enabled bluetooth.service", shell=True).decode(
                "utf-8").strip() == "enabled"
        except subprocess.CalledProcessError:
            # the command above returns the 'disabled` status w/ CalledProcessError, exit status 1
            pass
    return result


def cmd2string(cmd):
    return subprocess.check_output(cmd, shell=True).decode("utf-8").strip()


def is_command(cmd):
    cmd = "command -v {}".format(cmd)
    try:
        is_cmd = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        if is_cmd:
            return True
    except subprocess.CalledProcessError:
        return False
