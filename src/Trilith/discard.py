# -*- coding: utf-8 -*-

from .utils import extract_params
from oauthlib.oauth2 import RevocationEndpoint
from webob import Request, Response


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
