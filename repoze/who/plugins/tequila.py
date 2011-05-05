from urllib2 import urlopen
from paste.httpexceptions import HTTPFound

class TequilaChallengerPlugin(object):
    def __init__(self, tequila_url):
        self.tequila_url = tequila_url or 'http://tequila.epfl.ch/cgi-bin/tequila'
        
    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        data = [
            ('urlaccess', 'http://www.example.com/foo/bar'),
            ('service', 'My service'),
            ('request', ''),
        ]
        response = urlopen(self.tequila_url + '/createrequest', 
                           data='\n'.join(["%s=%s"%(k,v) for k,v in data]))
        # fixme: check if response code is 200
        key = response.read().strip().replace('key=', '')
        # fixme: check key
        redirect = self.tequila_url + "/requestauth?requestkey=%s"%key

        return HTTPFound(headers=[('Location', redirect)])

def make_plugin(tequila_url=None):
    return TequilaChallengerPlugin(tequila_url)
