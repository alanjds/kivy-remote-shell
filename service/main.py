import os
# Hack to allow import from main app dir:
_parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, _parentdir)

# install_twisted_rector must be called before importing  and using the reactor
#from kivy.support import install_twisted_reactor
#install_twisted_reactor()

from twisted.internet import reactor
from twisted.cred import portal, checkers
from twisted.conch import manhole, manhole_ssh

import json

import sl4acompat.androidhelper as sl4a

# get the argument passed
arg = os.getenv('PYTHON_SERVICE_ARGUMENT')

rpc_details = json.loads(arg)
droid = sl4a.Android(*rpc_details) # [host, port, handshake]
droid.makeToast('NOTICE: SL4A service connected')

def getManholeFactory(namespace, **passwords):
    realm = manhole_ssh.TerminalRealm()
    def getManhole(_):
        return manhole.ColoredManhole(namespace)
    realm.chainedProtocolFactory.protocolFactory = getManhole
    p = portal.Portal(realm)
    p.registerChecker(
        checkers.InMemoryUsernamePasswordDatabaseDontUse(**passwords))
    f = manhole_ssh.ConchFactory(p)
    return f

print 'Creating twisted reactor'
connection = reactor.listenTCP(8000, getManholeFactory(globals(), admin='kivy'))

print 'Twisted reactor starting'
reactor.run()
print 'Twisted reactor stopped'
