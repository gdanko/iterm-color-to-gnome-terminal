#!/usr/bin/env python3

from pprint import pprint
import argparse
import uuid
import sys
import os
# from subprocess import Popen, PIPE, STDOUT
import subprocess

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='The absolute path to the .dconf file generated with iterm-color-to-gnome-terminal.py', type=str, required=True)

    args = parser.parse_args()
    return args

def execute_command(command=[], input=''):
    foo = input.split('\n')
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(input='\n'.join(foo).encode('utf-8'))

    return process.returncode, stderr.decode('utf-8').strip(), stdout.decode('utf-8').strip()

def get_current_profiles():
    profiles_path = '/org/gnome/terminal/legacy/profiles:/'
    command = ['dconf', 'list', profiles_path]
    returncode, stderr, stdout = execute_command(command=command)

    if returncode != 0:
        print(f'An error has occurred: {stderr}')
        exit(1)

    profiles = stdout.split('\n')
    profiles = [profile.lstrip(':').rstrip('/') for profile in profiles if profile.startswith(':') and profile.endswith('/')]

    return profiles

def read_input(args):
    profile_id = str(uuid.uuid4())
    pofile_contents = None
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
    returncode, stdout, stderr = execute_command(command)

    if returncode != 0:
        print(f'Failed to update {profile_list_path}: {stderr}')
        exit(1)

def main():
    args = configure()
    if not (os.path.exists and os.path.isfile(args.input)):
        print(f'The path {args.input} does not exist or is not a file')
        sys.exit(1)

    profiles_list = get_current_profiles()
    profile_id, profile_contents = read_input(args)
    if profile_id is not None and profile_contents is not None:
        profiles_list.append(profile_id)
        create_new_profile(profiles_list, profile_id, profile_contents)


if __name__ == '__main__':
    sys.exit(main())
