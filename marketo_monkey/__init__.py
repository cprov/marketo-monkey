import urllib
import yaml

import requests


name = 'marketo_monkey'
__all__ = [
    'MarketoMonkey',
    'MarketoMonkeyError',
]


class MarketoMonkeyError(Exception):

    def __init__(self, message, errors):
        super()
        self.message = message
        self.errors = errors

    @classmethod
    def from_response(cls, response, message):
        if response.status_code != requests.codes.ok:
            error = {
                'code': 'http-{}'.format(response.status_code),
                'message': response.text
            }
            raise cls('Marketo request failed.', [error])

        payload = response.json()

        if not payload['success']:
            raise cls(message, payload['errors'])

        if response.request.method != 'GET':
            status = payload['result'][0]['status']
            if status not in ('created', 'updated', 'deleted'):
                raise cls(message, payload['result'][0]['reasons'])

        return payload


class MarketoMonkey():

    HEADERS = {
        'Content-Type': 'application/json; charset=UTF-8',
    }

    def __init__(self, config):
        self._config = config
        self._access_token = None

    @classmethod
    def config_from_yaml_file(cls, path):
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

    def set_lead(self, **kwargs):
        lead = kwargs.copy()
        overrides = self._config.get('lead', {}).get('overrides', {})
        lead.update(overrides)
        url = self._prepare_url('/rest/v1/leads.json')
        payload = {'input': [lead]}
        r = requests.post(url, json=payload, headers=self.HEADERS)
        return MarketoMonkeyError.from_response(r, 'Failed to set lead')

    def get_lead(self, lead_id):
        info = self.get_lead_info()
        extra_params = {
            'fields': ','.join(info['available_fields']),
        }
        url = self._prepare_url(
            '/rest/v1/lead/{}.json'.format(lead_id), **extra_params)
        r = requests.get(url)
        return MarketoMonkeyError.from_response(r, 'Failed to get lead')

    def describe_lead(self):
        url = self._prepare_url('/rest/v1/leads/describe.json')
        r = requests.get(url)
        return MarketoMonkeyError.from_response(r, 'Failed to describe lead')

    def get_lead_info(self):
        r = self.describe_lead()
        # all leads fields with 'snap' in their name and
        # a fixed set of keys.
        available_fields = [
            f['rest']['name'] for f in r['result']
            if 'snap' in f['rest']['name'].lower()]
        available_fields += [
            'firstName', 'lastName', 'email', 'userDisplayName',
        ]
        return {
            'displayname': 'Lead',
            'available_fields': available_fields,
        }

    def set_snap(self, **kwargs):
        snap = kwargs.copy()
        url = self._prepare_url('/rest/v1/customobjects/snap_c.json')
        payload = {'input': [snap]}
        r = requests.post(url, json=payload, headers=self.HEADERS)
        return MarketoMonkeyError.from_response(r, 'Failed to set snap')

    def get_snap(self, marketo_guid):
        info = self.get_snap_info(include_read_only_fields=True)
        extra_params = {
            'filterType': 'idField',
            'filterValues': marketo_guid,
            'fields': ','.join(info['available_fields'])
        }
        url = self._prepare_url(
            '/rest/v1/customobjects/snap_c.json', **extra_params)
        r = requests.get(url)
        return MarketoMonkeyError.from_response(r, 'Failed to get snap')

    def describe_snap(self):
        url = self._prepare_url(
            '/rest/v1/customobjects/snap_c/describe.json')
        r = requests.get(url)
        return MarketoMonkeyError.from_response(r, 'Failed to describe snap')

    def get_snap_info(self, include_read_only_fields=False):
        r = self.describe_snap()
        return {
            'displayname': r['result'][0]['displayName'],
            'available_fields': [
                f['name'] for f in r['result'][0]['fields']
                if include_read_only_fields or f['updateable']],
            'searchable_fields': [
                s[0] for s in r['result'][0]['searchableFields']],
            }

    def get_snaps(self, **kwargs):
        info = self.get_snap_info(include_read_only_fields=True)
        if len(kwargs) != 1:
            errors = [
                {'code': 'unsupported-filter',
                 'message': 'Only one filter is supported, {} given'.format(
                     len(kwargs.keys()))},
                {'code': 'supported-filters',
                 'message': 'Supported filters: {}'.format(
                     ' | '.join(info['searchable_fields']))},
            ]
            raise MarketoMonkeyError('Failed to get snaps', errors=errors)

        k, v = kwargs.popitem()
        if k not in info['searchable_fields']:
            errors = [
                {'code': 'unknown-filter',
                 'message': 'Unknown filter: {!r}'.format(k)},
                {'code': 'supported-filters',
                 'message': 'Supported filters: {}'.format(
                     ' | '.join(info['searchable_fields']))},
            ]
            raise MarketoMonkeyError('Failed to get snaps', errors=errors)

        extra_params = {
            'filterType': k,
            'filterValues': v,
            'fields': ','.join(info['available_fields'])
        }
        url = self._prepare_url(
            '/rest/v1/customobjects/snap_c.json', **extra_params)
        r = requests.get(url)
        return MarketoMonkeyError.from_response(r, 'Failed to get snaps')

    def delete_snap(self, **kwargs):
        supported_filters = ('snapName',)
        if len(kwargs) != 1:
            errors = [
                {'code': 'unsupported-key',
                 'message': 'Only one filter is supported, {} given'.format(
                     len(kwargs.keys()))},
                {'code': 'supported-filters',
                 'message': 'Supported filters: {}'.format(
                     ' | '.join(supported_filters))}
            ]
            raise MarketoMonkeyError('Failed to delete snaps', errors=errors)

        k, v = kwargs.popitem()
        if k not in supported_filters:
            errors = [
                {'code': 'unknown-filter',
                 'message': 'Unknown filter: {!r}'.format(k)},
                {'code': 'supported-filters',
                 'message': 'Supported filters: {}'.format(
                     ' | '.join(supported_filters))},
            ]
            raise MarketoMonkeyError('Failed to delete snaps', errors=errors)

        payload = {
            "deleteBy": "dedupeFields",
            "input": [{k: v}],
        }
        url = self._prepare_url('/rest/v1/customobjects/snap_c/delete.json')
        r = requests.post(url, json=payload, headers=self.HEADERS)
        return MarketoMonkeyError.from_response(r, 'Failed to delete snaps')
