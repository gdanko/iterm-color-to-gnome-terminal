#!/usr/bin/env python3

from pprint import pprint

import os
import sys
import argparse
import plistlib

def _camel_case_split(str):
    words = [[str[0]]]
 
    for c in str[1:]:
        if words[-1][-1].islower() and c.isupper():
            words.append(list(c))
        else:
            words[-1].append(c)
 
    return [''.join(word) for word in words]

def _to_hex(value):
    return '%02X' % int(value * 255)

def _hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    rgb_tuple = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    r = str(rgb_tuple[0])
    g = str(rgb_tuple[1])
    b = str(rgb_tuple[2])
 
    return f'rgb({r},{g},{b})'

def _rgb_to_hex(values):
    r = _to_hex(values['Red Component'])
    g = _to_hex(values['Green Component'])
    b = _to_hex(values['Blue Component'])

    hex = f'#{r}{g}{b}'
    rgb = _hex_to_rgb(hex)
    return hex, rgb

def _create_gnome_terminal_profile(name, gconf_keys):
    profile_contents = {
        'audible-bell': False,
        'background-color': '',
        'backspace-binding': 'ascii-delete',
        'bold-color': '',
        'bold-color-same-as-fg': True,
        'bold-is-bright': True,
        'cell-height-scale': 1.0,
        'cell-width-scale': 1.0,
        'cjk-utf8-ambiguous-width': 'narrow',
        'cursor-background-color': '',
        'cursor-blink-mode': 'system',
        'cursor-colors-set': False,
        'cursor-foreground-color': '',
        'cursor-shape': 'block',
        'custom-command': '',
        'default-size-columns': 80,
        'default-size-rows': 25,
        'delete-binding': 'delete-sequence',
        'encoding': 'UTF-8',
        'exit-action': 'close',
        'foreground-color': '',
        'highlight-background-color': '',
        'highlight-colors-set': False,
        'highlight-foreground-color': '',
        'login-shell': False,
        'palette': [],
        'preserve-working-directory': 'never',
        'scroll-on-keystroke': True,
        'scroll-on-output': False,
        'scrollback-lines': 10000,
        'scrollback-unlimited': False,
        'scrollbar-policy': 'always',
        'text-blink-mode': 'always',
        'use-custom-command': False,
        'use-theme-colors': False,
        'use-theme-transparency': False,
        'use-transparent-background': False,
        'visible-name': os.path.basename(name),
    }

    for key, value in gconf_keys.items():
        if isinstance(value, list):
            profile_contents[key] = value
        else:
            profile_contents[key] = value

    profile_contents_list = [
        '[/]'
    ]

    for key, value in profile_contents.items():
        if type(value) == bool:
            profile_contents_list.append(f'{key}={str(value).lower()}')
        elif type(value) == str:
            profile_contents_list.append(f'{key}=\'{value}\'')
        elif type(value) == float or type(value) == int:
            profile_contents_list.append(f'{key}={value}')
        elif type(value) == list:
            profile_contents_list.append(f'{key}={value}')
    
    return '\n'.join(profile_contents_list)

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',  help='The path to the *.itermcolors file to convert', type=str, required=True)
    parser.add_argument('-n', '--name', help='The profile name (default is the input filename)', type=str, required=False)

    args = parser.parse_args()

    return args

def parse_color_information(args):
    gconf_keys = {}
    gconf_keys['palette'] = [None] * 16

    try:
        with open(args.input, 'rb') as f:
            file_contents = f.read()
    except Exception as e:
        print(f'Failed to parse the input file: {e}')
        sys.exit(1)

    colors = plistlib.loads(file_contents)

    for color_name, color_values in colors.items():
        color_value_hex, color_value_rgb = _rgb_to_hex(color_values)

        if color_name.startswith('Ansi'):
            color_index = int(color_name.replace('Ansi ', '').replace(' Color', ''))
            gconf_keys['palette'][color_index] = color_value_hex

        elif color_name == 'Background Color':
            gconf_keys['background-color'] = color_value_hex

        elif color_name == 'Foreground Color':
            gconf_keys['foreground-color'] = color_value_hex

        elif color_name == 'Bold Color':
            gconf_keys['bold-color'] = color_value_hex

    for index, value in enumerate(gconf_keys['palette']):
        if not value:
            print(f'warning: missing ANSI color {index}\n')
    
    return gconf_keys

def main():
    args = configure()
    gconf_keys = parse_color_information(args)

    profile_name = args.name if args.name else os.path.splitext(os.path.basename(args.input))[0]
    profile_name = ' '.join(_camel_case_split(profile_name))
    outfile = os.path.join(os.getcwd(), f'{profile_name}.dconf')
    profile = _create_gnome_terminal_profile(profile_name, gconf_keys)

    print(f'Writing {outfile}')
    with open(outfile, 'w') as fh:
        fh.write(f'{profile}\n')


if __name__ == '__main__':
    sys.exit(main())
