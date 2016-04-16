# -*- coding: utf-8 -*-

import os
import json
import logging

from crom import monkey, implicit
from cromlech.configuration.utils import load_zcml
from cromlech.dawnlight import DawnlightPublisher
from cromlech.dawnlight import ViewLookup
from cromlech.dawnlight import view_locator, query_view
from cromlech.i18n import Locale, load_translations_directories
from cromlech.i18n import get_localizer, get_environ_language
from cromlech.browser.interfaces import IPublicationRoot
from cromlech.webob import Request
from cromlech.dawnlight import traversable
from zope.interface import implementer, directlyProvides
from zope.proxy import getProxiedObject
from zope.location import Location, ILocation
from barrel import cooper


PUBLISHER = DawnlightPublisher(
    view_lookup=ViewLookup(view_locator(component_protector(query_view))),
    )


@traversable('users', 'clients', 'grants', 'tokens')
@implementer(IPublicationRoot)
class Admin(Location):

    def __init__(self, users, clients, grants, tokens):
        self.users = users
        self.clients = clients
        self.grants = grants
        self.tokens = tokens


def manager(accesses, users, clients, grants, tokens):

    @cooper.basicauth(users=accesses, realm='TrilithAdmin')
    def publisher(environ, start_response):
        locale = get_environ_language(environ) or 'fr_FR'
        localizer = get_localizer(locale)

        with Locale(locale, localizer):
            request = Request(environ)
            root = Admin(users, clients, grants, tokens)
            response = PUBLISHER.publish(request, root)
            return response(environ, start_response)

    return  publisher
