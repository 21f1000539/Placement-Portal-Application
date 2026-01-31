from functools import wraps
from flask import session, redirect, url_for

def login_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if "role" not in session or session["role"] != role:
                return redirect(url_for("index"))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


