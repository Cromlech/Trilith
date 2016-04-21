# -*- coding: utf-8 -*-

from .utils import extract_params
from oauthlib.oauth2 import TokenEndpoint
from webob import Request, Response


def ATM(auth_grant, password_grant, credentials_grant, refresh_grant, bearer):
    
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
