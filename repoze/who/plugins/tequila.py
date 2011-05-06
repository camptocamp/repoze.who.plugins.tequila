from webob import Request
from urllib2 import urlopen
from paste.httpexceptions import HTTPFound

class TequilaChallengerPlugin(object):
    def __init__(self, tequila_url, service, request, rememberer_name):
        self.tequila_url = tequila_url
        self.request = request
        self.service = service

        self.rememberer_name = rememberer_name

    def _tequila_request(self, action, data):
        body = '\n'.join(["%s=%s"%(k,v) for k,v in data.iteritems()])
        response = urlopen(self.tequila_url + action, body)
        body = response.read()
        return dict([tuple(line.split('=', 1)) for line in body.split('\n') if line])

    # IIdentifier
    def identify(self, environ):
        key = Request(environ).params.get('key')
        if key:
            return {'key': key}
        else:
            return None

    def remember(self, environ, identity):
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer.remember(environ, identity)

    def forget(self, environ, identity):
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer.forget(environ, identity)

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        params = {
            'urlaccess': Request(environ).path_url,
            'service': self.service,
            'request': self.request
        }
        response = self._tequila_request('/createrequest', params)
        redirect = self.tequila_url + "/requestauth?requestkey=%s"%response.get('key')

        return HTTPFound(headers=[('Location', redirect)])

    # IAuthenticatorPlugin
    def authenticate(self, environ, identity):
        key = identity.get('key')
        if key:
            identity.update(self._tequila_request('/fetchattributes', {'key': str(key)}))
            return key

def make_plugin(tequila_url='https://tequila.epfl.ch/cgi-bin/tequila',
                service='Unknown service',
                request='uniqueid,name,firstname',
                rememberer_name=None):

    if rememberer_name is None:
        raise ValueError('must include rememberer key (name of another IIdentifier plugin)')

    return TequilaChallengerPlugin(tequila_url, service, request, rememberer_name)
