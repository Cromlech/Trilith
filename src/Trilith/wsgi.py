# -*- coding: utf-8 -*-

import uuid
import logging
import json

from cromlech.sqlalchemy import create_engine, SQLAlchemySession
from paste.urlmap import URLMap
from webob import Request, Response

from trilith.admin import manager
from trilith.sql.oauth2.models import Base
from trilith.sql.oauth2.stores import Tokens, Grants, Clients, Users
from trilith.oauth2.validator import OAuth2RequestValidator
from trilith.oauth2.endpoints import TokenEndpoint

from oauthlib.oauth2 import BearerToken
from oauthlib.oauth2 import AuthorizationCodeGrant
from oauthlib.oauth2 import ImplicitGrant
from oauthlib.oauth2 import ResourceOwnerPasswordCredentialsGrant
from oauthlib.oauth2 import ClientCredentialsGrant
from oauthlib.oauth2 import RefreshTokenGrant

from oauthlib.oauth2 import AuthorizationEndpoint
from oauthlib.oauth2 import TokenEndpoint
from oauthlib.oauth2 import ResourceEndpoint
from oauthlib.oauth2 import RevocationEndpoint


def uuid4_token(request):
    return str(uuid.uuid4())


def extract_params(request):
    headers = dict(request.headers)
    if 'wsgi.input' in headers:
        del headers['wsgi.input']
    if 'wsgi.errors' in headers:
        del headers['wsgi.errors']
    body = request.POST.mixed()
    return request.url, request.method, body, headers


def Discarder(validator):
    
    endpoint = RevocationEndpoint(validator)

    def oauth2_discarder(environ, start_response):
        request = Request(environ)
        uri, http_method, body, headers = extract_params(request)
        headers, body, status = endpoint.create_revocation_response(
            uri, http_method, body, headers,
        )
        response = Response(headers=headers, body=body, status_int=status)
        return response(environ, start_response)

    return oauth2_discarder


def ATM(validator, expires_in):

    auth_grant = AuthorizationCodeGrant(validator)
    password_grant = ResourceOwnerPasswordCredentialsGrant(validator)
    credentials_grant = ClientCredentialsGrant(validator)
    refresh_grant = RefreshTokenGrant(validator)
    bearer = BearerToken(validator, uuid4_token, expires_in, uuid4_token)
    
    endpoint = TokenEndpoint(
        default_grant_type='authorization_code',
        grant_types={
            'authorization_code': auth_grant,
            'password': password_grant,
            'client_credentials': credentials_grant,
            'refresh_token': refresh_grant,
        },
        default_token_type=bearer)

    def oauth2_atm(environ, start_response):
        request = Request(environ)
        uri, http_method, body, headers = extract_params(request)
        credentials = {}
        headers, body, status = endpoint.create_token_response(
            uri, http_method, body, headers, credentials
        )
        response = Response(headers=headers, body=body, status_int=status)
        return response(environ, start_response)
        
    return oauth2_atm


def  Defender(validator, expires_in):
    bearer = BearerToken(validator, uuid4_token, expires_in, uuid4_token)
    endpoint = ResourceEndpoint(
        default_token='Bearer',
        token_types={'Bearer': bearer})

    def oauth2_defender(environ, start_response):
        request = Request(environ)
        uri, http_method, body, headers = extract_params(request)
        valid, oauth2_request = endpoint.verify_request(
            uri, http_method, body, headers)

        headers = {
            'Content-Type': 'application/json',
        }
        if not valid:
            code = 401
            body = {
                'error': oauth2_request.error_message
            }
        else:
            code = 200
            body = {
                'client_id': oauth2_request.access_token.client_id,
                'expires': oauth2_request.access_token.expires.strftime(
                    "%Y-%m-%d %H:%M:%S"),
            }
        
        response = Response(
            headers=headers, body=json.dumps(body), status_int=code)
        return response(environ, start_response)

    return oauth2_defender


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
        clients=clients,
        tokens=tokens,
        grants=grants,
        users=users,
    )

    ### WSGI
    # Routing
    router = URLMap()
    router['/oauth2/token'] = ATM(validator, expires_in=300)
    router['/oauth2/guard'] = Defender(validator, expires_in=300)
    router['/oauth2/trash'] = Discarder(validator)
    router['/manage'] = manager(
        accesses, zcml_file, users, clients, grants, tokens)

    return router
