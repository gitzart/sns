import jwt
import time
import uuid

import pytest

from project.api.models.auth import (
    get_new_token,
    verify_auth_header,
    verify_token,
)
from project.config import TestingConfig


# Constant configurations
# ===============================================
# Somebody: You should use `current_app` instead.
# Me: I know! Just can't help it :D
# ===============================================
now = int(time.time())
algo = TestingConfig.JWT_ALGO
sec = TestingConfig.JWT_EXP_SEC
secret = TestingConfig.SECRET_KEY
sub = 10


@pytest.fixture(scope='module')
def app_context(app):
    with app.app_context():
        yield


pytestmark = pytest.mark.usefixtures('app_context')


def auth_header(type_, token=None):
    headers = {
        'empty': {'Authorization': ''},
        'incomplete': {'Authorization': 'Bearer'},
        'invalid_type': {'Authorization': f'Invalid {token}'},
        'bearer': {'Authorization': f'Bearer {token}'},
        'jwt': {'Authorization': f'JWT {token}'},
    }
    return headers.get(type_)


def test__get_new_token__return_string_type():
    token = get_new_token(sub)
    assert isinstance(token, str)


def test__get_new_token__include_UUID_JTI_field():
    payload = jwt.decode(get_new_token(sub), secret, algorithms=[algo])
    assert isinstance(payload['jti'], str)


def test__verify_auth_header__pass_bearer_token(app):
    token = get_new_token(sub)
    with app.test_request_context(headers=auth_header('bearer', token)):
        verified_token = verify_auth_header()
    assert verified_token == token


def test__verify_auth_header__pass_jwt_token(app):
    token = get_new_token(sub)
    with app.test_request_context(headers=auth_header('jwt', token)):
        verified_token = verify_auth_header()
    assert verified_token == token


def test__verify_auth_header__fail_no_header(app):
    with app.test_request_context():
        with pytest.raises(Exception) as e:
            verify_auth_header()
    assert 'login required' in str(e.value)


def test__verify_auth_header__fail_empty_header(app):
    with app.test_request_context(headers=auth_header('empty')):
        with pytest.raises(Exception) as e:
            verify_auth_header()
    assert 'login required' in str(e.value)


def test__verify_auth_header__fail_incomplete_header(app):
    with app.test_request_context(headers=auth_header('incomplete')):
        with pytest.raises(Exception) as e:
            verify_auth_header()
    assert 'incomplete auth header' in str(e.value)


def test__verify_auth_header__fail_invalid_token_type(app):
    token = get_new_token(sub)
    with app.test_request_context(headers=auth_header('invalid_type', token)):
        with pytest.raises(Exception) as e:
            verify_auth_header()
    assert 'invalid token type' in str(e.value)


def test__verify_token__pass():
    payload = verify_token(get_new_token(sub))
    assert isinstance(payload, dict)


def test__verify_token__fail_exclude_UUID_JTI_field():
    payload = {
        'iat': now,
        'exp': now + sec,
        'sub': sub,
    }
    token = jwt.encode(payload, secret, algorithm=algo)
    assert verify_token(token) == 'invalid'


def test__verify_token__fail_non_hex_UUID_JTI_field():
    payload = {
        'jti': uuid.uuid4().int,
        'iat': now,
        'exp': now + sec,
        'sub': sub,
    }
    token = jwt.encode(payload, secret, algorithm=algo)
    assert verify_token(token) == 'invalid'


def test__verify_token__fail_expired_token():
    payload = {
        'jti': uuid.uuid4().hex,
        'iat': now,
        'exp': now - sec,
        'sub': sub,
    }
    token = jwt.encode(payload, secret, algorithm=algo)
    assert verify_token(token) == 'expired'
