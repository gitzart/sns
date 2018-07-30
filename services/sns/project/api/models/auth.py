from datetime import datetime, timedelta
from uuid import UUID, uuid4

import jwt

from flask import current_app


def get_new_token(sub):
    """Create a new JSON web token."""
    now = datetime.utcnow()
    payload = {
        'jti': uuid4().hex,
        'iat': now,
        'exp': now + timedelta(seconds=current_app.config['JWT_EXP_SEC']),
        'sub': sub,
    }
    algo = current_app.config['JWT_ALGO']
    secret = current_app.config['SECRET_KEY']
    return jwt.encode(payload, secret, algorithm=algo).decode()


def verify_token(token):
    """"Decode the JWT token."""
    algo = current_app.config['JWT_ALGO']
    secret = current_app.config['SECRET_KEY']

    # Standard verification
    try:
        payload = jwt.decode(token, secret, algorithms=[algo])
    except jwt.ExpiredSignatureError:
        return 'expired'
    except jwt.InvalidTokenError:
        return 'invalid'

    # Extended `jti` verification
    try:
        UUID(hex=payload.get('jti'))
    except Exception:
        return 'invalid'

    return payload
