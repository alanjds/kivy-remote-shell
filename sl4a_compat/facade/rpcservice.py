#coding: utf-8

def start(public=False, handshake=False, external=True):
    raise NotImplementedError('Should start an RPC and return (host, port, handshake) tuple')
    return host, port, handshake
