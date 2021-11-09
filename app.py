from flask import Flask
from utils import auth
from utils import profile as pp
pp.reload()

app = Flask(__name__)


@app.route("/<string:profile>/<string:table>", methods=["POST"])
def create_table(profile, table):
    p, t = auth.esc(profile), auth.esc(table)
    if not auth.profile_exists(p):
        return "404: Profile not found.", 404
    if auth.is_admin(p, auth.get_token()):
        pp.create_table(p, t)
        return "Succeeded (if the table didn't exist) (incomplete code)", 200
    else:
        return "403: Unauthorized", 403


@app.route("/<string:profile>/<string:table>", methods=["DELETE"])
def delete_table(profile, table):
    p, t = auth.esc(profile), auth.esc(table)
    if not auth.profile_exists(p):
        return "404: Profile not found.", 404
    if auth.is_admin(p, auth.get_token()):
        pp.delete_table(p, t)
        return "Succeeded (if the table existed) (incomplete code)", 200
    else:
        return "403: Unauthorized", 403


@app.route("/<string:profile>/<string:table>/<string:key>", methods=["PUT", "POST"])
def put_key(profile, table, key):
    p, t = auth.esc(profile), auth.esc(table)
    if not auth.profile_exists(p):
        return "404: Profile not found.", 404
    if auth.is_authorized(p, table, auth.get_token()):
        pp.put(p, t, auth.esc(key))
        return "Succeeded (if the database existed ofc) (incomplete code)", 200
    else:
        return "403: Unauthorized", 403


@app.route("/<string:profile>/<string:table>/<string:key>", methods=["GET"])
def get_key(profile, table, key):
    p, t = auth.esc(profile), auth.esc(table)
    if not auth.profile_exists(p):
        return "404: Profile not found.", 404
    if auth.is_authorized(p, table, auth.get_token()):
        v = pp.get(p, t, auth.esc(key))
        if v is None:
            return "404: Key not found.", 404
        return v
    else:
        return "403: Unauthorized", 403


@app.route("/<string:profile>/<string:table>/<string:key>", methods=["DELETE"])
def delete_key(profile, table, key):
    p, t = auth.esc(profile), auth.esc(table)
    if not auth.profile_exists(p):
        return "404: Profile not found.", 404
    if auth.is_authorized(p, table, auth.get_token()):
        pp.delete(p, t, auth.esc(key))
        return "Succeeded (if the database existed ofc) (incomplete code)", 200
    else:
        return "403: Unauthorized", 403


@app.route("/reload", methods=["GET"])
def reload_profiles():
    if auth.is_root(auth.get_token()):
        pp.reload()
        return "Succeeded", 200
    else:
        return "403: Unauthorized", 403


if __name__ == '__main__':
    app.run(ssl_context="adhoc", port=5050)
