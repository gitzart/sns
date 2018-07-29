# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test__CreateUser__pass 1'] = {
    'data': {
        'createUser': {
            '__typename': 'UserMutationSuccess',
            'user': {
                'birthday': '1985-01-01',
                'email': 'rory@русски4ever.орг',
                'gender': 'MALE',
                'id': 'VXNlclR5cGU6MQ==',
                'name': 'Рори Williams'
            }
        }
    }
}

snapshots['test__CreateUser__fail_input_validation 1'] = {
    'data': {
        'createUser': {
            '__typename': 'MutationError',
            'errors': '{"birthday": "min value is 1898-01-01", "email": "contains misplaced character (-)", "firstName": "value does not match regex \'^((?![\\\\d_])[\\\\w ]){1,50}$\'", "lastName": "all space value not allowed", "password": "value does not match regex \'^[\\\\w\\\\ \\\\!\\\\\\"\\\\#\\\\$\\\\%\\\\&\\\\\'\\\\(\\\\)\\\\*\\\\+\\\\,\\\\-\\\\.\\\\/\\\\:\\\\;\\\\<\\\\=\\\\>\\\\?\\\\@\\\\[\\\\\\\\\\\\]\\\\^_\\\\`\\\\{\\\\|\\\\}\\\\~]{6,}$\'"}'
        }
    }
}

snapshots['test__CreateUser__fail_email_uniqueness 1'] = {
    'data': {
        'createUser': {
            '__typename': 'MutationError',
            'errors': '{"email": "email address already exists"}'
        }
    }
}

snapshots['test__UpdateUser__pass 1'] = {
    'data': {
        'updateUser': {
            '__typename': 'UserMutationSuccess',
            'user': {
                'bio': "Doctor's mine now, bitches!",
                'id': 'VXNlclR5cGU6NQ==',
                'maritalStatus': 'MARRIED',
                'name': 'song Who',
                'username': 'melodywho'
            }
        }
    }
}

snapshots['test__UpdateUser__fail_invalid_ID 1'] = {
    'data': {
        'updateUser': {
            '__typename': 'MutationError',
            'errors': '{"id": "invalid ID"}'
        }
    }
}

snapshots['test__UpdateUser__fail_user_existence 1'] = {
    'data': {
        'updateUser': {
            '__typename': 'MutationError',
            'errors': '{"id": "user with the given ID does not exist"}'
        }
    }
}

snapshots['test__UpdateUser__fail_input_validation 1'] = {
    'data': {
        'updateUser': {
            '__typename': 'MutationError',
            'errors': '{"username": "contains misplaced character (.)"}'
        }
    }
}

snapshots['test__UpdateUser__fail_username_uniqueness 1'] = {
    'data': {
        'updateUser': {
            '__typename': 'MutationError',
            'errors': '{"username": "username already exists"}'
        }
    }
}
