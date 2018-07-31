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

snapshots['test__Logout__pass 1'] = {
    'data': {
        'logout': {
            'loggedOut': True
        }
    }
}

snapshots['test__Logout__pass_expired_token 1'] = {
    'data': {
        'logout': {
            'loggedOut': True
        }
    }
}

snapshots['test__Logout__fail_invalid_token 1'] = {
    'data': {
        'logout': {
            'errors': '{"logout": "invalid token"}'
        }
    }
}

snapshots['test__Logout__fail_blacklist_token 1'] = {
    'data': {
        'logout': {
            'loggedOut': True
        }
    }
}

snapshots['test__Logout__fail_blacklist_token 2'] = {
    'data': {
        'logout': {
            'errors': '{"logout": "invalid token"}'
        }
    }
}

snapshots['test__Logout__fail_no_token_included 1'] = {
    'data': {
        'logout': {
            'errors': '{"logout": "you have not logged in"}'
        }
    }
}

snapshots['test__Logout__fail_no_auth_header_included 1'] = {
    'data': {
        'logout': {
            'errors': '{"logout": "you have not logged in"}'
        }
    }
}
