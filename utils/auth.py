from flask import request, escape
from pxyTools import dataIO


def esc(s):
    if s is None:
        return None
    return str(escape(s)).strip()


def get_token():
    return request.headers.get("Authorization", "")


def _load_perms(profile):
    p = dataIO.load_json(f"profiles/{profile}.json")
    return p["tokens"]


def is_authorized(profile, table, token):
    p = _load_perms(profile)
    if token not in p:
        return False
    if "*" in p[token]:
        return True
    if table not in p[token]:
        return False
    return True


def is_admin(profile, token):
    p = _load_perms(profile)
    if token not in p:
        return False
    if "*" in p[token]:
        return True
    return False


def is_root(token):
    if dataIO.load_json("config.json")["root_token"] == token:
        return True
    return False


def profile_exists(profile):
    try:
        _load_perms(profile)
    except FileNotFoundError:
        return False
    else:
        return True
