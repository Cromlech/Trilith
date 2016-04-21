# -*- coding: utf-8 -*-

from .utils import extract_params
from oauthlib.oauth2 import OAuth2Error
from oauthlib.oauth2 import AuthorizationEndpoint
from webob import Request, Response


def Bouncer(auth_grant, implicit_grant, bearer):

    endpoint = AuthorizationEndpoint(
        default_response_type='code',
        response_types={
            'code': auth_grant,
            'token': implicit_grant,
        },
        default_token_type=bearer,
    )

    def oauth2_authorize(environ, start_response):
        request = Request(environ)
        uri, http_method, body, headers = extract_params(request)
        try:
            headers, body, status = endpoint.create_authorization_response(
                uri, http_method, body, headers, scopes=["edit"])
            response = Response(headers=headers, body=body, status_int=status)
        except OAuth2Error as e:
            headers = {
                'Content-Type': 'application/json',
            }
            response = Response(
                headers=headers, body=body, status_int=e.status_code)
            
        return response(environ, start_response)

    return oauth2_authorize
