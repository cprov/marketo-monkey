
name = 'marketo_monkey'
__all__ = [
    'MarketoMonkey',
]


import urllib
import yaml


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
