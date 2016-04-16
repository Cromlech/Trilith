# -*- coding: utf-8 -*-


class Users(object):

    def __init__(self, engine):
        self.engine = engine
    
    def get(self, username, password, client, request, *args, **kwargs):
        import pdb
        pdb.set_trace()

    def set(self, user):
        pass
    

class Clients(object):

    def __init__(self, engine):
        self.engine = engine

    def get(self, client_id):
        import pdb
        pdb.set_trace()

    def set(self, client):
        pass


class Tokens(object):

    def __init__(self, engine):
        self.engine = engine
    
    def get(self, access_token=None, refresh_token=None):
        import pdb
        pdb.set_trace()

    def set(self, token, request, *args, **kwargs):
        pass
    

class Grants(object):

    def __init__(self, engine):
        self.engine = engine
    
    def get(self, client_id, code):
        import pdb
        pdb.set_trace()

    def set(self, client_id, code, request, *args, **kwargs):
        pass
