# -*- coding: utf-8 -*-
"""
Flask application default configuration module

"""
from sys import exit
from werkzeug import ImmutableDict
from imp import new_module
from os.path import expanduser

FROZEN = False

CONFIG = {
    "SECRETS_FILE": '~/.pystil-secrets',
    "DEBUG": True,
    "TESTING": True,
    "BIND": "0.0.0.0",
    "SECRET_KEY": None,
    "DB_BACKEND": "postgresql",
    "DB_HOST": "localhost",
    "DB_NAME": None,
    "DB_USER": "pystil",
    "DB_PASSWORD": None,
    "DB_PORT": 5432,
    "THREADED": True,
    "LOG_FILE": None,
    "IP_DB": 'ip.db'
}


def freeze():
    """Freeze once and for all the config to cache computed keys"""
    global CONFIG, FROZEN

    if FROZEN:
        raise RuntimeError("Already Frozen")

    # Load secrets into CONFIG from a file
    secrets = new_module('config')
    secrets.__file__ = expanduser(CONFIG["SECRETS_FILE"])
    try:
        execfile(secrets.__file__, secrets.__dict__)
    except IOError, e:
        print e
        print "Unable to load secrets file: %s." % CONFIG["SECRETS_FILE"]
        print "Please copy .pystil-secrets to your home and fill it"
        print "Change the file location with CONFIG['SECRETS_FILE']"
        exit(1)
    else:
        for key in dir(secrets):
            CONFIG[key] = getattr(secrets, key)

    if not CONFIG["DB_NAME"]:
        CONFIG["DB_NAME"] = CONFIG["DB_USER"]

    CONFIG['DB_URL'] = make_db_url()

    CONFIG = ImmutableDict(CONFIG)
    FROZEN = True


def make_db_url():
    """Compute the database options."""
    if CONFIG["DB_BACKEND"] == "sqlite":
        return 'sqlite:///pystil.sqlite'
    else:
        return 'postgresql+psycopg2://%s:%s@%s:%d/%s' % (
            CONFIG["DB_USER"],
            CONFIG["DB_PASSWORD"],
            CONFIG["DB_HOST"],
            CONFIG["DB_PORT"],
            CONFIG["DB_NAME"])
