from datetime import datetime, timedelta
from uuid import UUID, uuid4

import jwt

from flask import current_app, request
from sqlalchemy.dialects import postgresql

from project import db


class BlacklistToken(db.Model):
    __tablename__ = 'blacklist_tokens'

    id = db.Column(postgresql.UUID(as_uuid=True), primary_key=True)
    exp = db.Column(db.BigInteger, nullable=False)


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


def verify_auth_header():
    """Validate the Authorization header.

    :return: Token if the header is valid or raise Exception.
    """
    # Get auth header
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise Exception('login required')

    # Validate auth header
    try:
        type_, token = auth_header.split()
    except ValueError:
        raise Exception('incomplete auth header')

    # Check token type
    if type_.lower() not in ['bearer', 'jwt']:
        raise Exception('invalid token type')

    return token


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
