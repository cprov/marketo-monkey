#!/usr/bin/env python3

import argparse
import logging
import os
import pprint
import sys
import time
import urllib
import yaml

import editor
import requests


class MarketoMonkey():

    HEADERS = {
        'Content-Type': 'application/json; charset=UTF-8',
    }

    def __init__(self, config):
        self._config = config
        self._access_token = None

    @classmethod
    def config_from_yaml_file(klass, path):
        with open(path) as fd:
            return yaml.safe_load(fd)

    def _get_access_token(self):
        if self._access_token is None:
            url = urllib.parse.urljoin(
                self._config['service_root'], '/identity/oauth/token')
            params = {
                'grant_type': 'client_credentials',
                'client_id': self._config['client_id'],
                'client_secret': self._config['client_secret'],
            }
            url += '?' + urllib.parse.urlencode(params)
            self._access_token = requests.get(url).json()['access_token']
        return self._access_token

    def _prepare_url(self, path, **extra_params):
        url = urllib.parse.urljoin(self._config['service_root'], path)
        params = {
            'access_token': self._get_access_token(),
        }
        if extra_params:
            params.update(extra_params)
        url += '?' + urllib.parse.urlencode(params)
        return url

    def list_objects(self):
        url = self._prepare_url('/rest/v1/customobjects.json')
        return requests.get(url).json()

    def describe_object(self, name):
        url = self._prepare_url(
            '/rest/v1/customobjects/{}/describe.json'.format(name))
        return requests.get(url).json()

    def set_lead(self, **kwargs):
        lead = kwargs.copy()
        overrides = {
            'snapcraftio': True,
            'snapcraftioEnvironment': 'staging',
        }
        lead.update(overrides)
        url = self._prepare_url('/rest/v1/leads.json')
        payload = {'input': [lead]}
        return requests.post(url, json=payload, headers=self.HEADERS).json()

    def get_lead(self, lead_id):
        url = self._prepare_url('/rest/v1/lead/{}.json'.format(lead_id))
        return requests.get(url).json()

    def describe_lead(self):
        url = self._prepare_url('/rest/v1/leads/describe.json')
        return requests.get(url).json()

    def set_snap(self, **kwargs):
        snap = kwargs.copy()
        url = self._prepare_url('/rest/v1/customobjects/snap_c.json')
        payload = {'input': [snap]}
        return requests.post(url, json=payload, headers=self.HEADERS).json()

    def get_snap(self, marketoGUID):
        extra_params = {
            'filterType': 'idField',
            'filterValues': marketoGUID,
            'fields': ('emailAddress,snapName,revision,Confinement,channel,'
                       'marketoGUID,createdAt,updatedAt'),
        }
        url = self._prepare_url(
            '/rest/v1/customobjects/snap_c.json', **extra_params)
        return requests.get(url).json()

    def describe_snap(self):
        return self.describe_object('snap_c')


DEFAULT_CONFIG = b"""# Marketo-monkey configuration

service_root: https://<xxx-XXX-xxx>.mktorest.com
client_id: <CLIENT-ID>
client_secret: <CLIENT-SECRET>

"""


def main():
    parser = argparse.ArgumentParser(
        description='CLI tool to facilitate Marketo integration'
    )
    parser.add_argument(
        '--version', action='version',
        version='marketo-monkey "{}"'.format(os.environ.get('SNAP_VERSION', 'devel')))
    parser.add_argument('-v', '--debug', action='store_true',
                        help='Prints request and response headers')
    parser.add_argument('--edit-config', action='store_true',
                        help='Edit configuration')

    parser.add_argument('obj_name', choices=['lead', 'snap'])
    parser.add_argument('spec', nargs='?', metavar='field=value,field=value')

    args = parser.parse_args()

    if args.debug:
        # The http.client logger pollutes stdout.
        #from http.client import HTTPConnection
        #HTTPConnection.debuglevel = 1
        handler = requests.packages.urllib3.add_stderr_logger()
        handler.setFormatter(logging.Formatter('\033[1m%(message)s\033[0m'))

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
            print(('\033[31m\033[1m'
                   'Could not access the configuration file ...\n'
                   'Please edit {} manually.'
                   '\033[0m').format(config_path))
            return 1

    try:
        config = MarketoMonkey.config_from_yaml_file(config_path)
    except yaml.scanner.ScannerError:
        print(('\033[31m\033[1m'
               'Could not parse the configuration file ...\n'
               'Ensure {} is a valid YAML.'
               '\033[0m').format(config_path))
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
        print('{!r} object available fields:\n\t{}'.format(
            displayname, ', '.join(available_fields)))
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
            print('\033[31m\033[1m'
                  'Failed to create or modify lead!'
                  '\033[0m')
            for r in updated['result'][0]['reasons']:
                print('\t{}'.format(r['message']))
            return 1

        print('\033[32m'
              'Lead object {}!'
              '\033[0m'.format(updated['result'][0]['status']))
        fetched = mm.get_lead(lead_id)
        lead = fetched['result'][0]
        pprint.pprint(lead)
    else:
        updated = mm.set_snap(**spec)
        try:
            marketoGUID = updated['result'][0]['marketoGUID']
        except KeyError:
            print('\033[31m\033[1m'
                  'Failed to create or modify snap!'
                  '\033[0m')
            for r in updated['result'][0]['reasons']:
                print('\t{}'.format(r['message']))
            return 1

        print('\033[32m'
              'Snap object {}!'
              '\033[0m'.format(updated['result'][0]['status']))
        fetched = mm.get_snap(marketoGUID)
        snap = fetched['result'][0]
        pprint.pprint(snap)


if __name__ == '__main__':
    sys.exit(main())
