from pprint import pprint
import subprocess
import sys

def execute_command(command=[], input=''):
    foo = input.split('\n')
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(input='\n'.join(foo).encode('utf-8'))

    return process.returncode, stderr.decode('utf-8').strip(), stdout.decode('utf-8').strip()

def text_between(text, character):
    split_text = text.split(f'{character}')
    between_text = split_text[1::2]  # discard the last element if the quotes are unbalanced
    if len(split_text) % 2 == 0 and between_quotes and not text.endswith('"'):
        between_text.pop()  # discard the last item if the quotes are unbalanced
    return between_text

def get_enabled_list():
    # dconf read /org/gnome/terminal/legacy/profiles:/list
    command = ['dconf', 'read', '/org/gnome/terminal/legacy/profiles:/list']
    returncode, stderr, stdout = execute_command(command)

    if returncode != 0:
        print(f'Failed to read the list of loaded profiles: {common.util.sanitize_error(stderr)}')
        sys.exit(1)

    list_items = text_between(stdout, "'")
    if isinstance(list_items, list):
        return list_items
    return None

def sanitize_error(error):
    return error.split('\n')[0].replace('error: ', '')

def dump_profile(uuid):
    profile_path = f'/org/gnome/terminal/legacy/profiles:/:{uuid}/'
    command = ['dconf', 'dump', profile_path]
    returncode, stderr, stdout = execute_command(command)
    if returncode != 0:
        print(f'Failed to dump the profile for uuid {uuid}: {sanitize_error(stderr)}')
        sys.exit(1)

    for kvpair in stdout.split('\n'):
        bits = kvpair.split('=')
        if len(bits) == 2:
            if bits[0] == 'visible-name':
                return bits[1].lstrip("'").rstrip("'")
    return None

def get_current_profiles():
    profiles_path = '/org/gnome/terminal/legacy/profiles:/'
    command = ['dconf', 'list', profiles_path]
    returncode, stderr, stdout = execute_command(command=command)

    if returncode != 0:
        print(f'Failed to get the current list of profiles: {sanitize_error(stderr)}')
        exit(1)

    uuids = stdout.split('\n')
    uuids = [uuid.lstrip(':').rstrip('/') for uuid in uuids if uuid.startswith(':') and uuid.endswith('/')]

    profiles = {}

    for uuid in uuids:
        profile_name = dump_profile(uuid)
        if profile_name is not None:
            profiles[profile_name] = uuid
    
    return profiles
