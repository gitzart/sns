import jwt
import time
import uuid

import pytest

from flask import g

from project.api.models.auth import (
    BlacklistToken,
    authenticate,
    full_token_check,
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


def test__verify_token__fail_expired_token():
    payload = {
        'jti': uuid.uuid4().hex,
        'iat': now,
        'exp': now - sec,
        'sub': sub,
    }
    token = jwt.encode(payload, secret, algorithm=algo).decode()
    with pytest.raises(Exception) as e:
        verify_token(token)
    assert 'expired token' in str(e.value)


def test__verify_token__fail_empty_token():
    token = ''
    with pytest.raises(Exception) as e:
        verify_token(token)
    assert 'invalid token' in str(e.value)


def test__verify_token__fail_integer_token():
    token = 12345678910
    with pytest.raises(Exception) as e:
        verify_token(token)
    assert 'invalid token' in str(e.value)


def test__verify_token__fail_invalid_token():
    token = f'invalid-{get_new_token(sub)}'
    with pytest.raises(Exception) as e:
        verify_token(token)
    assert 'invalid token' in str(e.value)


def test__verify_token__fail_no_uuid_jti_field():
    payload = {
        'iat': now,
        'exp': now + sec,
        'sub': sub,
    }
    token = jwt.encode(payload, secret, algorithm=algo).decode()
    with pytest.raises(Exception) as e:
        verify_token(token)
    assert 'invalid token id' in str(e.value)


def test__verify_token__fail_empty_uuid_jti_field():
    payload = {
        'jti': '',
        'iat': now,
        'exp': now + sec,
        'sub': sub,
    }
    token = jwt.encode(payload, secret, algorithm=algo).decode()
    with pytest.raises(Exception) as e:
        verify_token(token)
    assert 'invalid token id' in str(e.value)


def test__verify_token__fail_integer_uuid_jti_field():
    payload = {
        'jti': uuid.uuid4().int,
        'iat': now,
        'exp': now + sec,
        'sub': sub,
    }
    token = jwt.encode(payload, secret, algorithm=algo).decode()
    with pytest.raises(Exception) as e:
        verify_token(token)
    assert 'invalid token id' in str(e.value)


def test__full_token_check__pass(app, db):
    token = get_new_token(sub)
    with app.test_request_context(headers=auth_header('bearer', token)):
        payload = full_token_check()
    assert isinstance(payload, dict)


def test__full_token_check__fail_blacklist_token(app, db):
    token = get_new_token(sub)
    payload = verify_token(token)

    # Blacklist the token
    db.session.add(BlacklistToken(id=payload['jti'], exp=payload['exp']))
    db.session.commit()

    with app.test_request_context(headers=auth_header('bearer', token)):
        with pytest.raises(Exception) as e:
            full_token_check()
    assert 'invalid token' in str(e.value)


def test__authenticate__pass(setup, app, db):
    amy_id = 2
    token = get_new_token(amy_id)
    payload = verify_token(token)

    with app.test_request_context(headers=auth_header('bearer', token)):
        assert authenticate() is None

    assert g.is_authenticated
    assert g.payload == payload
    assert g.viewer.first_name == 'amy'


def test__authenticate__fail_user_not_found(app, db):
    rory_id = 1
    token = get_new_token(rory_id)

    with app.test_request_context(headers=auth_header('bearer', token)):
        with pytest.raises(Exception) as e:
            authenticate()

    assert 'invalid token' in str(e.value)
    assert not hasattr(g, 'is_authenticated')
    assert not hasattr(g, 'payload')
    assert not hasattr(g, 'viewer')
