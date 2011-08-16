#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""
pystil - An elegant site web traffic analyzer
"""
from flask import current_app, session, request, Response


def auth_route(app):
    """This function return the route decorator with ldap checking"""
    import ldap
    ldap_ = ldap.open(app.config["LDAP_HOST"])

    def check_auth(username, password):
        """This function is called to check if a username /
        password combination is valid against the LDAP.
        """
        user = ldap_.search_s(app.config["LDAP_PATH"],
                              ldap.SCOPE_ONELEVEL, "uid=%s" % username)
        if not user:
            current_app.logger.warn("Unknown user %s" % username)
            return False
        try:
            ldap_.simple_bind_s(user[0][0], password)
        except ldap.INVALID_CREDENTIALS:
            current_app.logger.warn("Invalid credentials for %s" % username)
            return False
        session["user"] = user[0][1]['uid'][0]
        return True

    def authenticate():
        """Sends a 401 response that enables basic auth"""
        return Response(
        'Login Required', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

    def route(*args, **kwargs):
        """Decorator acting like a route but with auth checking"""
        def auth(fun):
            """Auth decorator"""
            if hasattr(fun, '_has_auth_'):
                decorated = fun
            else:
                def decorated(*fargs, **fkwargs):
                    """Auth decoratorated"""
                    auth = request.authorization
                    if (not auth or
                        not check_auth(auth.username, auth.password)):
                        return authenticate()
                    return fun(*fargs, **fkwargs)
                decorated.__name__ = fun.__name__
                decorated._has__auth_ = True

            app.route(*args, **kwargs)(decorated)
            return decorated
        return auth

    return route
