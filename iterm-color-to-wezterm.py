#!/usr/bin/env python3

from pprint import pprint

import glob
import json
import os
import plistlib
import re
import sys

def camel_to_spaces(profile_name):
    # Convert the first character to lowercase
    profile_name = profile_name[0].lower() + profile_name[1:]
    # Replace all uppercase characters followed by lowercase characters with a space and the uppercase character in lowercase
    return re.sub(r'(?<=[a-zA-Z])(?=[A-Z])', ' ', profile_name)

def _to_hex(value):
    return "%02X" % int(value * 255)

def _rgb_to_hex(values):
    r = _to_hex(values["Red Component"])
    g = _to_hex(values["Green Component"])
    b = _to_hex(values["Blue Component"])

    return f"#{r}{g}{b}"

def main():
    wezterm_colors = {}
    schemes_directory = "/home/gdanko/git/iTerm2-Color-Schemes/schemes"
    outfile = "/home/gdanko/wezterm-color-schemes.json"

    os.chdir(schemes_directory)
    for filename in glob.glob("*.itermcolors"):
        profile_name = camel_to_spaces(os.path.splitext(filename)[0])
        profile_name = os.path.splitext(filename)[0]
        wezterm_colors[profile_name] = {}
        with open(filename, "rb") as fp:
            file_contents = fp.read()
            colors = plistlib.loads(file_contents)
            for color_name, color_values in colors.items():
                color_value_hex = _rgb_to_hex(color_values).lower()

                if color_name == "Background Color":
                    wezterm_colors[profile_name]["background"] = color_value_hex
                elif color_name == "Bold Color":
                    wezterm_colors[profile_name]["bold"] = color_value_hex
                elif color_name == "Cursor Color":
                    wezterm_colors[profile_name]["cursor_bg"] = color_value_hex
                elif color_name == "Cursor Text Color":
                    wezterm_colors[profile_name]["cursor_fg"] = color_value_hex
                elif color_name == "Foreground Color":
                    wezterm_colors[profile_name]["foreground"] = color_value_hex
                elif color_name == "Selected Text Color":
                    wezterm_colors[profile_name]["selection_bg"] = color_value_hex
                elif color_name == "Selection Color":
                    wezterm_colors[profile_name]["selection_fg"] = color_value_hex

    keys = list(wezterm_colors.keys())
    keys.sort()
    sorted = {i: wezterm_colors[i] for i in keys}
    with open(outfile, "w") as fh:
        fh.write(json.dumps(sorted, indent=4))
        fh.write("\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())

