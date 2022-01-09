from flask import Flask
from utils import auth
from utils import profile as pp
from pxyTools import dataIO
pp.reload()

app = Flask(__name__)


@app.route("/<string:profile>/<string:table>", methods=["POST"])
def create_table(profile, table):
    p, t = auth.esc(profile), auth.esc(table)
    if not auth.profile_exists(p):
        return "404: Profile not found.", 404
    if auth.is_admin(p, auth.get_token()):
        return pp.create_table(p, t)
    else:
        return "403: Unauthorized", 403


@app.route("/<string:profile>/<string:table>", methods=["DELETE"])
def delete_table(profile, table):
    p, t = auth.esc(profile), auth.esc(table)
    if not auth.profile_exists(p):
        return "404: Profile not found.", 404
    if auth.is_admin(p, auth.get_token()):
        return pp.delete_table(p, t)
    else:
        return "403: Unauthorized", 403


@app.route("/<string:profile>/<string:table>/<string:key>", methods=["PUT"])
def put_key(profile, table, key):
    p, t = auth.esc(profile), auth.esc(table)
    if not auth.profile_exists(p):
        return "404: Profile not found.", 404
    if auth.is_authorized(p, table, auth.get_token()):
        return pp.put(p, t, auth.esc(key))
    else:
        return "403: Unauthorized", 403


@app.route("/<string:profile>/<string:table>/<string:key>", methods=["GET"])
def get_key(profile, table, key):
    p, t = auth.esc(profile), auth.esc(table)
    if not auth.profile_exists(p):
        return "404: Profile not found.", 404
    if auth.is_authorized(p, table, auth.get_token()):
        return pp.get(p, t, auth.esc(key))
    else:
        return "403: Unauthorized", 403


@app.route("/<string:profile>/<string:table>/<string:key>", methods=["DELETE"])
def delete_key(profile, table, key):
    p, t = auth.esc(profile), auth.esc(table)
    if not auth.profile_exists(p):
        return "404: Profile not found.", 404
    if auth.is_authorized(p, table, auth.get_token()):
        return pp.delete(p, t, auth.esc(key))
    else:
        return "403: Unauthorized", 403


@app.route("/<string:profile>/_multi", methods=["POST"])
def multi(profile):
    p = auth.esc(profile)
    if not auth.profile_exists(p):
        return "404: Profile not found.", 404
    if auth.is_authorized(p, "*", auth.get_token()):
        return pp.multi(p)
    else:
        return "403: Unauthorized", 403


@app.route("/reload", methods=["GET"])
def reload_profiles():
    if auth.is_root(auth.get_token()):
        pp.reload()
        return "200: Profiles reloaded", 200
    else:
        return "403: Unauthorized", 403


if __name__ == '__main__':
    app_port = dataIO.load_json("config.json")["app_port"]
    app_ssl = "adhoc" if dataIO.load_json("config.json")["app_fake_ssl"] else None
    app.run(ssl_context=app_ssl, port=app_port)
