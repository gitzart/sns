# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_mutation_user_create 1'] = {
    'data': {
        'createUser': {
            'user': {
                'email': 'rory@email.com',
                'firstName': 'rory',
                'gender': 'MALE',
                'id': 'VXNlcjox',
                'lastName': 'williams'
            }
        }
    }
}

snapshots['test_mutation_user_update 1'] = {
    'data': {
        'updateUser': {
            'user': {
                'email': 'amy@email.com',
                'firstName': 'amy',
                'gender': 'FEMALE',
                'id': 'VXNlcjox',
                'lastName': 'williams',
                'maritalStatus': 'MARRIED',
                'username': 'amy'
            }
        }
    }
}
