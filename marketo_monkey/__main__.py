
import argparse
import logging
import os
import pprint
import sys

import editor
import requests
import yaml

from colorama import init
from termcolor import colored


from marketo_monkey import (
    MarketoMonkey,
    MarketoMonkeyError,
)


DEFAULT_CONFIG = b"""# Marketo-monkey configuration

service_root: https://<xxx-XXX-xxx>.mktorest.com
client_id: <CLIENT-ID>
client_secret: <CLIENT-SECRET>

lead:
  overrides:
    - snapcraftio: true
    - snapcraftioEnvironment: staging

"""


def parse_spec(text):
    spec = {}
    for expr in text.split(','):
        if not expr or '=' not in expr:
            continue
        field, value = expr.split('=')
        spec[field] = value
    return spec


def main():
    parser = argparse.ArgumentParser(
        description='CLI tool to facilitate Marketo integration'
    )
    parser.add_argument(
        '--version', action='version',
        version='marketo-monkey "{}"'.format(
            os.environ.get('SNAP_VERSION', 'devel')))
    parser.add_argument('-v', '--debug', action='store_true',
                        help='Prints request and response headers')
    parser.add_argument('--edit-config', action='store_true',
                        help='Edit configuration')

    parser.add_argument('obj_name', nargs='?', choices=['lead', 'snap'])
    parser.add_argument('spec', nargs='?', metavar='field=value,field=value')

    args = parser.parse_args()

    init()

    if args.debug:
        # The http.client logger pollutes stdout.
        # from http.client import HTTPConnection
        # HTTPConnection.debuglevel = 1
        handler = requests.packages.urllib3.add_stderr_logger()
        handler.setFormatter(
            logging.Formatter(colored('%(message)s', 'yellow')))

    config_dir = os.path.abspath(os.environ.get('SNAP_USER_COMMON', '.'))
    config_path = os.path.join(config_dir, 'marketo-monkey.yaml')
    if not os.path.exists(config_path) or args.edit_config:
        kwargs = {
            'filename': config_path,
        }
        if not os.path.exists(config_path):
            kwargs['contents'] = DEFAULT_CONFIG
        try:
            editor.edit(**kwargs)
        except PermissionError:
            msg = (
                'Could not access the configuration file ...\n'
                'Please edit {} manually.').format(config_path)
            print(colored(msg, 'red'))
            return 1

    try:
        config = MarketoMonkey.config_from_yaml_file(config_path)
    except yaml.scanner.ScannerError:
        msg = (
            'Could not parse the configuration file ...\n'
            'Ensure {} is a valid YAML.').format(config_path)
        print(colored(msg, 'red'))
        return 1

    mm = MarketoMonkey(config)

    if args.obj_name is None:
        return

    try:

        if args.spec is None:
            if args.obj_name == 'lead':
                info = mm.get_lead_info()
            elif args.obj_name == 'snap':
                info = mm.get_snap_info()
            else:
                # Should never run due to argparse choices.
                msg = 'Unknown object name: {}'.format(args.obj_name)
                print(colored(msg, 'red'))
                return 1
            fields = ', '.join(sorted(info['available_fields']))
            msg = '{!r} object available fields:\n\t{}'.format(
                info['displayname'], fields)
            print(colored(msg, 'green'))
            return

        spec = parse_spec(args.spec)

        if args.obj_name == 'lead':
            updated = mm.set_lead(**spec)
            lead_id = updated['result'][0]['id']
            action = updated['result'][0]['status']
            msg = 'Lead object {!r} {}!'.format(lead_id, action)
            print(colored(msg, 'green'))
            lead = mm.get_lead(lead_id)['result'][0]
            pprint.pprint(lead)

        elif args.obj_name == 'snap':
            updated = mm.set_snap(**spec)
            marketo_guid = updated['result'][0]['marketoGUID']
            action = updated['result'][0]['status']
            msg = 'Snap object {!r} {}!'.format(marketo_guid, action)
            print(colored(msg, 'green'))
            snap = mm.get_snap(marketo_guid)['result'][0]
            pprint.pprint(snap)
        else:
            # Should never run due to argparse choices.
            msg = 'Unknown object name: {}'.format(args.obj_name)
            print(colored(msg, 'red'))
            return 1

    except MarketoMonkeyError as err:
        print(colored(err.message, 'red'))
        for e in err.errors:
            print(colored('\t{}'.format(e['message']), 'red'))
        return 1


if __name__ == '__main__':
    sys.exit(main())
