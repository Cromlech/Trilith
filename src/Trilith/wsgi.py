# -*- coding: utf-8 -*-

import uuid
import logging

from cromlech.sqlalchemy import create_engine, SQLAlchemySession
from paste.urlmap import URLMap

from trilith.admin import manager
from trilith.sql.oauth2.models import Base
from trilith.sql.oauth2.stores import Tokens, Grants, Clients, Users
from trilith.oauth2.validator import OAuth2RequestValidator

from oauthlib.oauth2 import BearerToken
from oauthlib.oauth2 import AuthorizationCodeGrant
from oauthlib.oauth2 import ImplicitGrant
from oauthlib.oauth2 import ResourceOwnerPasswordCredentialsGrant
from oauthlib.oauth2 import ClientCredentialsGrant
from oauthlib.oauth2 import RefreshTokenGrant

from . import check, discard, ticket, authorization


def uuid4_token(request):
    return str(uuid.uuid4())


def Application(conf, dsn, accesses, zcml_file, ticket_ttl):

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
        clients=clients,
        tokens=tokens,
        grants=grants,
        users=users,
    )

    ## Endpoints
    auth_grant = AuthorizationCodeGrant(validator)
    bearer = BearerToken(validator, uuid4_token, int(ticket_ttl), uuid4_token)
    credentials_grant = ClientCredentialsGrant(validator)
    implicit_grant = ImplicitGrant(validator)
    password_grant = ResourceOwnerPasswordCredentialsGrant(validator)
    refresh_grant = RefreshTokenGrant(validator)

    ### WSGI
    # Routing
    router = URLMap()
    router['/oauth2/cashier'] = ticket.ATM(
        auth_grant, password_grant, credentials_grant, refresh_grant, bearer)
    router['/oauth2/sentinel'] = check.Defender(bearer)
    router['/oauth2/shredder'] = discard.Discarder(validator)
    router['/oauth2/bouncer'] = authorization.Bouncer(
        auth_grant, implicit_grant, bearer)
    router['/manage'] = manager(
        accesses, zcml_file, users, clients, grants, tokens)

    return router
