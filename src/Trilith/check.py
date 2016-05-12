# -*- coding: utf-8 -*-

import json
from .utils import extract_params
from oauthlib.oauth2 import ResourceEndpoint
from webob import Request, Response


def Defender(bearer):

    endpoint = ResourceEndpoint(
        default_token='Bearer',
        token_types={'Bearer': bearer},
    )

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
                'scopes': tuple(oauth2_request.access_token.scope),
            }

        response = Response(
            headers=headers, body=json.dumps(body), status_int=code)
        return response(environ, start_response)

    return oauth2_defender
