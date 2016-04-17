# -*- coding: utf-8 -*-

import logging

from cromlech.sqlalchemy import create_engine, SQLAlchemySession
from paste.urlmap import URLMap
from webob import Request

from trilith.admin import manager
from trilith.sql.oauth2.models import Base
from trilith.sql.oauth2.stores import Tokens, Grants, Clients, Users
from trilith.oauth2.validator import OAuth2RequestValidator
from trilith.oauth2.endpoints import TokenEndpoint


def ATM(validator):

    def oauth2_atm(environ, start_response):
        request = Request(environ)
        result = None
        return result
        
    return oauth2_atm


def Application(conf, dsn, accesses, zcml_file):

    ### Database
    # Bootstrap the SQL connection
    engine = create_engine(dsn, 'trilith')
    Base.metadata.bind = engine.engine
    with SQLAlchemySession(engine) as s:
        Base.metadata.create_all()

    # Create storages
    users = Users(engine)
    tokens = Tokens(engine)
    grants = Grants(engine)
    clients = Clients(engine)

    ### OAuth2 Machinery
    # Request Validator & Endpoints
    validator = OAuth2RequestValidator(
        clientgetter=clients.get,
        tokengetter=tokens.get,
        grantgetter=grants.get,
        usergetter=users.get,
        tokensetter=tokens.set,
        grantsetter=grants.set,
    )

    ### WSGI
    # Routing
    router = URLMap()
    router['/oauth2/token'] = ATM(validator)
    router['/manage'] = manager(
        accesses, zcml_file, users, clients, grants, tokens)

    return router
