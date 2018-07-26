from datetime import datetime, timedelta

import jwt

from flask import current_app


def get_new_token(sub):
    """Create a new JSON web token."""
    now = datetime.utcnow()
    payload = {
        'iat': now,
        'exp': now + timedelta(seconds=current_app.config['JWT_EXP_SEC']),
        'sub': sub,
    }
    algo = current_app.config['JWT_ALGO']
    secret = current_app.config['SECRET_KEY']
    return jwt.encode(payload, secret, algorithm=algo).decode()
