
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


from marketo_monkey import MarketoMonkey


DEFAULT_CONFIG = b"""# Marketo-monkey configuration

service_root: https://<xxx-XXX-xxx>.mktorest.com
client_id: <CLIENT-ID>
client_secret: <CLIENT-SECRET>

lead:
  overrides:
    - snapcraftio: true
    - snapcraftioEnvironment: staging

"""


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

    parser.add_argument('obj_name', choices=['lead', 'snap'])
    parser.add_argument('spec', nargs='?', metavar='field=value,field=value')

    args = parser.parse_args()

    if args.debug:
        # The http.client logger pollutes stdout.
        # from http.client import HTTPConnection
        # HTTPConnection.debuglevel = 1
        handler = requests.packages.urllib3.add_stderr_logger()
        handler.setFormatter(logging.Formatter(colored('%(message)s', 'yellow')))

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

    if args.spec is None:
        if args.obj_name == 'lead':
            available_fields = [
                'firstName', 'lastName', 'email', 'company',
            ]
            displayname = 'Lead'
        else:
            r = mm.describe_snap()
            available_fields = [
                f['name'] for f in r['result'][0]['fields']
                if not f['crmManaged']]
            displayname = r['result'][0]['displayName']
        msg = '{!r} object available fields:\n\t{}'.format(
            displayname, ', '.join(available_fields))
        print(colored(msg, 'green'))
        return

    spec = {}
    for expr in args.spec.split(','):
        if not expr or '=' not in expr:
            continue
        field, value = expr.split('=')
        spec[field] = value

    if args.obj_name == 'lead':
        updated = mm.set_lead(**spec)
        try:
            lead_id = updated['result'][0]['id']
        except KeyError:
            msg = 'Failed to create or modify lead!'
            print(colored(msg, 'red'))
            for r in updated['result'][0]['reasons']:
                print(colored('\t{}'.format(r['message']), 'red'))
            return 1

        msg = 'Lead object {}!'.format(updated['result'][0]['status'])
        print(colored(msg, 'green'))
        fetched = mm.get_lead(lead_id)
        lead = fetched['result'][0]
        pprint.pprint(lead)

    elif args.obj_name == 'snap':
        updated = mm.set_snap(**spec)
        try:
            marketo_guid = updated['result'][0]['marketoGUID']
        except KeyError:
            msg = 'Failed to create or modify snap!'
            print(colored(msg, 'red'))
            for r in updated['result'][0]['reasons']:
                print(colored('\t{}'.format(r['message']), 'red'))
            return 1

        msg = 'Snap object {}!'.format(updated['result'][0]['status'])
        print(colored(msg, 'green'))
        fetched = mm.get_snap(marketo_guid)
        snap = fetched['result'][0]
        pprint.pprint(snap)


if __name__ == '__main__':
    sys.exit(main())
