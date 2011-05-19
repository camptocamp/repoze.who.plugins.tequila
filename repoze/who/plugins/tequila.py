from webob import Request, Response
from urllib2 import urlopen, HTTPError
from paste.httpexceptions import HTTPFound

import logging
logger = logging.getLogger()

def tequila_request(url, action, data):
    body = '\n'.join(["%s=%s"%(k,v) for k,v in data.iteritems()])
    try:
        response = urlopen(url + action, body)
    except HTTPError:
        return None
    
    body = response.read()
    return dict([tuple(line.split('=', 1)) for line in body.split('\n') if line])

class TequilaChallengerPlugin(object):

    def __init__(self, tequila_url, service, request, rememberer_name,
                 logout_handler_path, login_handler_path):
        self.tequila_url = tequila_url
        self.request = request
        self.service = service
        self.rememberer_name = rememberer_name

        self.logout_handler_path = logout_handler_path
        self.login_handler_path = login_handler_path

    # IIdentifier
    def identify(self, environ):
        request = Request(environ)

        identity = {}

        if request.path == self.logout_handler_path:
            headers = self.forget(environ, {})
            # fixme redirect
        elif request.path == self.login_handler_path:
            # back from the challenger, authenticate the key
            key = request.params.get('key')
            if key:
                identity = tequila_request(self.tequila_url, '/fetchattributes', {'key': str(key)})
                if identity is not None:
                    environ['repoze.who.application'] = HTTPFound(headers=[('Location', self.origin)])

        return identity

    def remember(self, environ, identity):
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer.remember(environ, identity)

    def forget(self, environ, identity):
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer.forget(environ, identity)

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        request = Request(environ)
        self.origin = request.path_url
        params = {
            'urlaccess': request.relative_url(self.login_handler_path),
            'service': self.service,
            'request': self.request
        }
        response = tequila_request(self.tequila_url, '/createrequest', params)
        redirect = self.tequila_url + "/requestauth?requestkey=%s"%response.get('key')

        return HTTPFound(headers=[('Location', redirect)])

    # IAuthenticatorPlugin
    def authenticate(self, environ, identity):
        # dummy authenticator
        return identity.get('uniqueid')

def make_plugin(tequila_url='https://tequila.epfl.ch/cgi-bin/tequila',
                service='Unknown service',
                request='uniqueid,name,firstname',
                rememberer_name=None,
                logout_handler_path='/logout',
                login_handler_path='/do_login'):

    if rememberer_name is None:
        raise ValueError('must include rememberer key (name of another IIdentifier plugin)')

    return TequilaChallengerPlugin(tequila_url, service, request, rememberer_name, 
                                   logout_handler_path, login_handler_path)
