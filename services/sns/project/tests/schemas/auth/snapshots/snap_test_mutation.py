# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test__Login__fail_incorrect_credentials 1'] = {
    'data': {
        'login': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'incorrect credentials',
            'path': [
                'login'
            ]
        }
    ]
}

snapshots['test__Logout__pass 1'] = {
    'data': {
        'logout': {
            'ok': True
        }
    }
}

snapshots['test__Logout__fail_login_required 1'] = {
    'data': {
        'logout': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'login required',
            'path': [
                'logout'
            ]
        }
    ]
}
