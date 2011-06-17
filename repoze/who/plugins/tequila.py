from webob import Request, Response
from urlparse import urljoin
from urllib2 import urlopen, HTTPError
from paste.httpexceptions import HTTPFound

def tequila_request(url, action, data):
    body = '\n'.join(["%s=%s"%(k,v) for k,v in data.iteritems()])
    try:
        response = urlopen(url + action, body)
    except HTTPError:
        return None

    body = response.read()
    return dict([tuple(line.split('=', 1)) for line in body.split('\n') if line])

class TequilaChallengerPlugin(object):

    def __init__(self, tequila_url, service, request, allows, 
                 rememberer_name, session_name, login_handler_path, 
                 logout_handler_path, logged_out_url):
        self.tequila_url = tequila_url
        self.request = request
        self.service = service
        self.allows = allows
        self.rememberer_name = rememberer_name
        self.session_name = session_name

        self.login_handler_path = login_handler_path
        self.logout_handler_path = logout_handler_path
        self.logged_out_url = logged_out_url

    # IIdentifier
    def identify(self, environ):
        request = Request(environ)
        identity = {}

        if request.path == urljoin(request.path, self.logout_handler_path):
            headers = self.forget(environ, [])
            headers.append(('Location', self.logged_out_url))
            environ['repoze.who.application'] = HTTPFound(headers=headers)

        elif request.path == urljoin(request.path, self.login_handler_path):
            # back from the challenger, authenticate the key
            key = request.params.get('key')
            if key:
                identity = tequila_request(self.tequila_url, '/fetchattributes', {'key': str(key)})
                if identity is not None:
                    identity['repoze.who.userid'] = identity.get('uniqueid')
                    environ['repoze.who.application'] = HTTPFound(headers=[('Location', self.came_from)])

        elif not self.rememberer_name:
            session = environ.get(self.session_name)
            identity = session.get('repoze.who.plugins.tequila')

        return identity

    def remember(self, environ, identity):
        if self.rememberer_name:
            rememberer = environ['repoze.who.plugins'][self.rememberer_name]
            return rememberer.remember(environ, identity)
        else:
            session = environ.get(self.session_name)
            session['repoze.who.plugins.tequila'] = identity
            session.save()
            return []

    def forget(self, environ, identity):
        if self.rememberer_name:
            rememberer = environ['repoze.who.plugins'][self.rememberer_name]
            return rememberer.forget(environ, identity)
        else:
            session = environ.get(self.session_name)
            if 'repoze.who.plugins.tequila' in session:
                del session['repoze.who.plugins.tequila']
                session.save()
            return []

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        request = Request(environ)
        self.came_from = request.path_url
        params = {
            'urlaccess': request.relative_url(self.login_handler_path),
            'service': self.service,
            'request': self.request
        }
        if self.allows is not None:
            params.update({'allows': self.allows})

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
                allows=None,
                rememberer_name=None,
                session_name='beaker.session',
                login_handler_path='/do_login',
                logout_handler_path='/logout',
                logged_out_url='/'):

    return TequilaChallengerPlugin(tequila_url, service, request, allows,
                                   rememberer_name, session_name,
                                   login_handler_path, logout_handler_path, logged_out_url)
