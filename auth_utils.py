import secrets
from flask import *
import db_utils
from functools import wraps

def generate_token():
    return secrets.token_hex(32)  # 64-char random token

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("auth_token")
        if not token:
            return redirect("/login")

        rows = db_utils.select_query(
            """
            SELECT user_id FROM auths
            WHERE token=%s AND (expires_at IS NULL OR expires_at > NOW())
            """,
            (token,),
        )
        if not rows:
            return redirect("/login")

        request.user_id = rows[0]["user_id"]
        return f(*args, **kwargs)
    return wrapper