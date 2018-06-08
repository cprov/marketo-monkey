#!/usr/bin/env python3

import argparse
import logging
import os
import pprint
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
        self._access_token = self._get_access_token()

    @classmethod
    def config_from_yaml_file(klass, path):
        with open(path) as fd:
            return yaml.safe_load(fd)

    def _get_access_token(self):
        url = urllib.parse.urljoin(
            self._config['service_root'], '/identity/oauth/token')
        params = {
            'grant_type': 'client_credentials',
            'client_id': self._config['client_id'],
            'client_secret': self._config['client_secret'],
        }
        url += '?' + urllib.parse.urlencode(params)
        return requests.get(url).json()['access_token']

    def _prepare_url(self, path, **extra_params):
        url = urllib.parse.urljoin(self._config['service_root'], path)
        params = {
            'access_token': self._access_token,
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

    def create_lead(self, **kwargs):
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

    def create_or_update_snap(self, **kwargs):
        snap = kwargs.copy()
        url = self._prepare_url('/rest/v1/customobjects/snap_c.json')
        payload = {'input': [snap]}
        return requests.post(url, json=payload, headers=self.HEADERS).json()

    def get_snap(self, marketo_snap_id):
        extra_params = {
            'filterType': 'idField',
            'filterValues': marketo_snap_id,
            'fields': ('emailAddress,snapName,revision,Confinement,channel,'
                       'marketoGUID,createdAt,updatedAt'),
        }
        url = self._prepare_url(
            '/rest/v1/customobjects/snap_c.json', **extra_params)
        return requests.get(url).json()


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
            print('Could not access the configuration file ...')
            print('Please edit {} manually'.format(config_path))
            return

    config = MarketoMonkey.config_from_yaml_file(config_path)

    mm = MarketoMonkey(config)

    #pprint.pprint(mm.list_objects())
    pprint.pprint(mm.describe_object('snap_c'))

    #lead = {
    #    'firstName': 'Foo',
    #    'lastName': 'Bar',
    #    'email': 'foo.bar@example.com',
    #    'company': '',
    #}
    #r = mm.create_lead(**lead)
    #pprint.pprint(r)
    #lead_id = r['result'][0]['id']
    #pprint.pprint(mm.get_lead(lead_id))
    #snap = {
    #    'emailAddress': 'foo.bar@example.com',
    #    'snapName': 'testing-snap',
    #    'revision': '10',
    #    'Confinement': 'devmode',
    #    'channel': '6.6.6/edge/radioactive',
    #}
    #r = mm.create_or_update_snap(**snap)
    #pprint.pprint(r)
    #marketoGUID = r['result'][0]['marketoGUID']
    #pprint.pprint(mm.get_snap(marketoGUID))



if __name__ == '__main__':
    main()
