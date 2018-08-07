from datetime import datetime, timedelta
from uuid import UUID, uuid4

import jwt

from flask import current_app, g, request
from sqlalchemy.dialects import postgresql

from project import bcrypt, db
from project.api.models.user import User


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
    """"Decode the JWT token.

    :return: Token payload if the token is valid or raise Exception.
    """
    algo = current_app.config['JWT_ALGO']
    secret = current_app.config['SECRET_KEY']

    # Standard verification
    try:
        payload = jwt.decode(token, secret, algorithms=[algo])
    except jwt.ExpiredSignatureError:
        raise Exception('expired token')
    except jwt.InvalidTokenError:
        raise Exception('invalid token')

    # Extended `jti` verification
    try:
        UUID(hex=payload.get('jti'))
    except Exception:
        raise Exception('invalid token id')

    return payload


def full_token_check():
    """Make a full verification of the token.

    :return: Token payload if the token is valid or raise Exception.
    """
    token = verify_auth_header()
    payload = verify_token(token)

    # Blacklist check
    if BlacklistToken.query.get(payload['jti']):
        raise Exception('invalid token')
    return payload


def authenticate_password(email, password):
    """Password based authentication.

    :return: A new token if the given credentials are authentic,
        or raise Exception.
    """
    if not email.strip():
        raise Exception('incorrect credentials')

    user = User.query.filter_by(email=email).first()
    if not (user and bcrypt.check_password_hash(user.password, password)):
        raise Exception('incorrect credentials')

    return get_new_token(user.id)


def authenticate_token():
    """Token based authentication.

    Authenticate the incoming request and cache the reusable objects.

    Built as a business logic layer that does not depend on
    any API interface such as GraphQL, REST, and RPC.
    See http://graphql.github.io/learn/thinking-in-graphs

    With REST, use it inside a decorator, like so::

        from functools import wraps

        def login_required(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                authenticate_token()
                return f(*args, **kwargs)
            return decorated

    :return: None if the request is authentic, or raise Exception.
    """
    if getattr(g, 'is_authenticated', False):
        return None

    payload = full_token_check()

    viewer = User.get_by_id(payload['sub'])
    if viewer is None:
        raise Exception('invalid token')

    # Authentication went well, cache the objects.
    g.is_authenticated = True
    g.payload = payload
    g.viewer = viewer
