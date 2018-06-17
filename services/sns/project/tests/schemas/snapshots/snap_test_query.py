# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_query_user_with_basic_info 1'] = {
    'data': {
        'user': {
            'bio': None,
            'birthday': None,
            'currentCity': None,
            'email': 'rory@email.com',
            'firstName': 'rory',
            'gender': 'MALE',
            'lastName': 'williams',
            'maritalStatus': None,
            'username': None
        }
    }
}

snapshots['test_query_user_with_relationship_info 1'] = {
    'data': {
        'user': {
            'firstName': 'amy',
            'followers': {
                'edges': [
                    {
                        'node': {
                            'firstName': 'rory',
                            'id': 'VXNlcjox',
                            'lastName': 'williams'
                        }
                    }
                ],
                'totalCount': 1
            },
            'followings': {
                'edges': [
                    {
                        'node': {
                            'firstName': 'rory',
                            'id': 'VXNlcjox',
                            'lastName': 'williams'
                        }
                    }
                ],
                'totalCount': 1
            },
            'friends': {
                'edges': [
                    {
                        'node': {
                            'firstName': 'rory',
                            'id': 'VXNlcjox',
                            'lastName': 'williams'
                        }
                    }
                ],
                'totalCount': 1
            },
            'lastName': 'pond'
        }
    }
}

snapshots['test_query_user_with_friend_request 1'] = {
    'data': {
        'user': {
            'firstName': 'doctor',
            'friendRequests': {
                'edges': [
                    {
                        'node': {
                            'from': {
                                'firstName': 'doctor',
                                'id': 'VXNlcjoz',
                                'lastName': 'who'
                            },
                            'id': 'RnJpZW5kUmVxdWVzdDooNCwgMyk=',
                            'message': None,
                            'to': {
                                'firstName': 'bill',
                                'id': 'VXNlcjo0',
                                'lastName': 'potts'
                            },
                            'unread': True
                        }
                    }
                ],
                'totalCount': 1
            },
            'lastName': 'who'
        }
    }
}

snapshots['test_query_user_with_friend_suggestion 1'] = {
    'data': {
        'user': {
            'firstName': 'bill',
            'friendSuggestions': {
                'edges': [
                    {
                        'node': {
                            'from': {
                                'firstName': 'song',
                                'id': 'VXNlcjo1',
                                'lastName': 'river'
                            },
                            'id': 'RnJpZW5kU3VnZ2VzdGlvbjooMywgNCwgNSk=',
                            'message': None,
                            'to': [
                                {
                                    'firstName': 'doctor',
                                    'id': 'VXNlcjoz',
                                    'lastName': 'who'
                                },
                                {
                                    'firstName': 'bill',
                                    'id': 'VXNlcjo0',
                                    'lastName': 'potts'
                                }
                            ],
                            'unread': True
                        }
                    }
                ],
                'totalCount': 1
            },
            'lastName': 'potts'
        }
    }
}
