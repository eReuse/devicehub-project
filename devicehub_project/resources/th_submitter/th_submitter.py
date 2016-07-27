import requests
from ereuse_devicehub.resources.event.device import DeviceEventDomain
from ereuse_devicehub.resources.submitter.submitter import Submitter
from ereuse_devicehub.resources.submitter.translator import Translator
from requests.auth import HTTPBasicAuth


class ThSubmitter(Submitter):
    def __init__(self, token: str, app, **kwargs):
        config = app.config
        domain = config['DEVICEHUB_PROJECT']['TH_DOMAIN']
        translator = THTranslator(config)
        account = config['DEVICEHUB_PROJECT']['TH_ACCOUNT']
        auth = ThAuth(account['username'], account['password'], domain)
        debug = config.setdefault('TH_DEBUG', False)
        super().__init__(token, app, domain, translator, auth, debug)


class ThAuth(HTTPBasicAuth):
    """
        Apart from the Basic Auth, obtains and appends a Token in a X-CSRF-Token header.
    """
    def __init__(self, username, password, domain):
        super().__init__(username, password)
        self.domain = domain

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
            'device': (self.hid_or_url,),
            'geo': (self.identity,),
            '@type': (self.identity,)
        }
        pfx = DeviceEventDomain.new_type
        translation_dict = {
            pfx('Allocate'): {
                'to': (self.url('accounts'),)
            },
            pfx('Receive'): {
                'receiver': (self.url('accounts'),),
                'type': (self.identity,),
                'place': (self.url('places'),)
            },
        }
        super().__init__(config, generic_resource, translation_dict)