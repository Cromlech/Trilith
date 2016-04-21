# -*- coding: utf-8 -*-

def extract_params(request):
    headers = dict(request.headers)
    if 'wsgi.input' in headers:
        del headers['wsgi.input']
    if 'wsgi.errors' in headers:
        del headers['wsgi.errors']
    body = request.POST.mixed()
    return request.url, request.method, body, headers
