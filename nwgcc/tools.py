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


def bt_on(cmd):
    output = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
    return output.split()[1] == "yes"


def cmd2string(cmd):
    return subprocess.check_output(cmd, shell=True).decode("utf-8").strip()


def is_command(cmd):
    print("Command '{}' ".format(cmd), end="")
    cmd = "command -v {}".format(cmd)
    try:
        is_cmd = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        if is_cmd:
            print("found.")
            return True
    except subprocess.CalledProcessError:
        print("not found!")
        return False
