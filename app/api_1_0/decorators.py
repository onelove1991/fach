from functools import wraps
from flask import g

from .errors import forbidden

def permission_required(permisson):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permisson):
                return forbidden('Insufficient Permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator