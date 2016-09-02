import requests
from ereuse_devicehub.resources.account.domain import AccountDomain
from ereuse_devicehub.resources.event.device import DeviceEventDomain
from ereuse_devicehub.resources.submitter.submitter import Submitter
from ereuse_devicehub.resources.submitter.translator import Translator
from requests.auth import HTTPBasicAuth


class ThSubmitter(Submitter):
    def __init__(self, token: str, app):
        config = app.config
        domain = config['DEVICEHUB_PROJECT']['TH_DOMAIN']
        translator = THTranslator(config)
        debug = config.setdefault('TH_DEBUG', False)
        super().__init__(token, app, domain, translator, None, debug)
        self.embedded.update({'project': 1, 'to': 1, 'byUser': 1})

    def generate_url(self, original_resource, translated_resource) -> str:
        url = '{}/transferhub/events/devices/'.format(self.domain)
        url += 'allocate' if translated_resource['@type'] == DeviceEventDomain.new_type('Allocate') else 'receive'
        return url + '?_format=json'

    def _post(self, resource: dict, url: str, **kwargs):
        kwargs['headers'] = {'Cache-Control': 'no-cache'}
        super()._post(resource, url, **kwargs)

    def submit(self, resource_id: str, database: str, resource_name: str, actual_account: dict):
        self.auth = ThAuth(actual_account['email'], actual_account['password'], self.domain)
        super().submit(resource_id, database, resource_name)


class ThAuth(HTTPBasicAuth):
    """
        Apart from the Basic Auth, obtains and appends a Token in a X-CSRF-Token header.
    """
    def __init__(self, username, password, domain):
        super().__init__(username, password)
        self.domain = domain
        self.token = None

    def __call__(self, r):
        if self.token is None:
            self.token = requests.get('{}/rest/session/token'.format(self.domain))
        r.headers['X-CSRF-Token'] = self.token
        return super().__call__(r)


class THTranslator(Translator):
    def __init__(self, config):
        generic_resource = {
            'url': (self.url('events'), '_id'),
            'date': (self.identity,),
            'byUser': (self.url('accounts'),),
            'created': (self.identity, '_created'),
            'errors': (self.identity, '_errors'),
            'secured': (self.identity,),
            'incidence': (self.identity,),
            'devices': (self.for_all(self.device),),
            'geo': (self.identity,),
            '@type': (self.identity,),
            'sameAs': (self.identity,),
            'project': (self.inner_field('sameAs'),),
            'description': (self.identity,)
        }
        pfx = DeviceEventDomain.new_type
        translation_dict = {
            pfx('Allocate'): {
                'to': (self.inner_field('sameAs'),)
            },
            pfx('Receive'): {
                'receiver': (self.url('accounts'),),
                'type': (self.identity,),
                'place': (self.url('places'),)
            },
        }
        super().__init__(config, generic_resource, translation_dict)
