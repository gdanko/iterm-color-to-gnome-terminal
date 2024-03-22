#!/usr/bin/env python3

from pprint import pprint
import argparse
import uuid
import sys
import os
import common.util
import subprocess

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='The absolute path to the .dconf file generated with iterm-color-to-gnome-terminal.py', type=str, required=True)

    args = parser.parse_args()
    return args

def read_input(args):
    profile_id = str(uuid.uuid4())
    try:
        with open(args.input) as f: contents = f.read()
        return profile_id, contents.strip()
    except:
        return profile_id, None

def create_new_profile(profiles_list, profile_id, profile_contents):
    profile_path = f'/org/gnome/terminal/legacy/profiles:/:{profile_id}/'
    contents = profile_contents.split('\n')
    command = ['dconf', 'load', profile_path]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate(input='\n'.join(contents).encode('utf-8'))

    profile_list_path = '/org/gnome/terminal/legacy/profiles:/list'
    dconf_input = '[' + ','.join(["'"+item+"'" for item in profiles_list]) + ']'
    command = ['dconf', 'write', profile_list_path, dconf_input]
    returncode, stdout, stderr = common.util.execute_command(command)

    if returncode != 0:
        print(f'Failed to update {profile_list_path}: {common.util.sanitize_error(stderr)}')
        sys.exit(1)

def main():
    args = configure()
    if not (os.path.exists and os.path.isfile(args.input)):
        print(f'The path {args.input} does not exist or is not a file.')
        return 1

    profiles_dict = common.util.get_current_profiles()
    profiles_list = [value for _, value in profiles_dict.items()]
    profile_name = os.path.splitext(os.path.basename(args.input))[0]

    if profile_name in profiles_dict:
        print(f'The profile name {profile_name} already exists. Please select another name and try again.')
        return 0

    profile_id, profile_contents = read_input(args)
    if profile_id is not None and profile_contents is not None:
        profiles_list.append(profile_id)
        create_new_profile(profiles_list, profile_id, profile_contents)

    # Verify the profile was created
    profiles_dict = common.util.get_current_profiles()
    enabled = common.util.get_enabled_list()
    if profile_name in profiles_dict and profiles_dict[profile_name] == profile_id:
        print(f'The Gnome Terminal profile {profile_name} was successfully created.')
        if profile_id in enabled:
            print(f'The Gnome Terminal profile {profile_name} was successfully added to the enabled list.')
        else:
            print(f'The Gnome Terminal profile {profile_name} was NOT added to the enabled list.')
            return 1
    else:
        print(f'The Gnome Terminal profile {profile_name} was NOT created.')
        return 1

if __name__ == '__main__':
    sys.exit(main())
