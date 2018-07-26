# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test__Login__fail_incorrect_email 1'] = {
    'data': {
        'login': {
            'errors': '{"login": "incorrect credentials"}'
        }
    }
}

snapshots['test__Login__fail_incorrect_password 1'] = {
    'data': {
        'login': {
            'errors': '{"login": "incorrect credentials"}'
        }
    }
}
