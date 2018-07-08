# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_user_query_basic_profile 1'] = {
    'data': {
        'user': {
            'bio': None,
            'birthday': None,
            'createdAt': '2018-07-08T18:46:39.429274',
            'email': 'rory@email.com',
            'firstName': 'rory',
            'gender': 'MALE',
            'id': 'VXNlclR5cGU6MQ==',
            'lastName': 'williams',
            'maritalStatus': None,
            'updatedAt': '2018-07-08T18:46:39.429274',
            'username': None
        }
    }
}

snapshots['test_user_query_relationship_profile 1'] = {
    'data': {
        'user': {
            'blockedUsers': {
                'edges': [
                    {
                        'node': {
                            'id': 'VXNlclR5cGU6MQ==',
                            'name': 'rory williams'
                        }
                    }
                ],
                'totalCount': 1
            },
            'followers': {
                'edges': [
                    {
                        'node': {
                            'id': 'VXNlclR5cGU6MQ==',
                            'name': 'rory williams'
                        }
                    }
                ],
                'totalCount': 1
            },
            'followings': {
                'edges': [
                    {
                        'node': {
                            'id': 'VXNlclR5cGU6Mw==',
                            'name': 'doctor who'
                        }
                    },
                    {
                        'node': {
                            'id': 'VXNlclR5cGU6NA==',
                            'name': 'bill potts'
                        }
                    }
                ],
                'totalCount': 3
            },
            'friends': {
                'edges': [
                    {
                        'node': {
                            'id': 'VXNlclR5cGU6Mw==',
                            'name': 'doctor who'
                        }
                    },
                    {
                        'node': {
                            'id': 'VXNlclR5cGU6NA==',
                            'name': 'bill potts'
                        }
                    }
                ],
                'totalCount': 3
            },
            'id': 'VXNlclR5cGU6Mg==',
            'name': 'amy pond'
        }
    }
}

snapshots['test_user_query_friend_requests 1'] = {
    'data': {
        'user': {
            'friendRequests': {
                'edges': [
                    {
                        'node': {
                            'createdAt': '2018-07-08T18:46:40.657464',
                            'from': {
                                'id': 'VXNlclR5cGU6MQ==',
                                'name': 'rory williams'
                            },
                            'id': 'RnJpZW5kUmVxdWVzdFR5cGU6KDEsIDMp',
                            'to': {
                                'id': 'VXNlclR5cGU6Mw==',
                                'name': 'doctor who'
                            }
                        }
                    },
                    {
                        'node': {
                            'createdAt': '2018-07-08T18:46:40.656864',
                            'from': {
                                'id': 'VXNlclR5cGU6Mw==',
                                'name': 'doctor who'
                            },
                            'id': 'RnJpZW5kUmVxdWVzdFR5cGU6KDMsIDUp',
                            'to': {
                                'id': 'VXNlclR5cGU6NQ==',
                                'name': 'song river'
                            }
                        }
                    },
                    {
                        'node': {
                            'createdAt': '2018-07-08T18:46:40.656002',
                            'from': {
                                'id': 'VXNlclR5cGU6Mw==',
                                'name': 'doctor who'
                            },
                            'id': 'RnJpZW5kUmVxdWVzdFR5cGU6KDMsIDQp',
                            'to': {
                                'id': 'VXNlclR5cGU6NA==',
                                'name': 'bill potts'
                            }
                        }
                    }
                ],
                'totalCount': 3
            },
            'id': 'VXNlclR5cGU6Mw==',
            'name': 'doctor who'
        }
    }
}

snapshots['test_user_query_friend_suggestions 1'] = {
    'data': {
        'user': {
            'friendSuggestions': {
                'edges': [
                    {
                        'node': {
                            'createdAt': '2018-07-08T18:46:40.898702',
                            'from': {
                                'id': 'VXNlclR5cGU6Mw==',
                                'name': 'doctor who'
                            },
                            'id': 'RnJpZW5kU3VnZ2VzdGlvblR5cGU6KDIsIDQsIDMp',
                            'to': [
                                {
                                    'id': 'VXNlclR5cGU6Mg==',
                                    'name': 'amy pond'
                                },
                                {
                                    'id': 'VXNlclR5cGU6NA==',
                                    'name': 'bill potts'
                                }
                            ]
                        }
                    },
                    {
                        'node': {
                            'createdAt': '2018-07-08T18:46:40.897565',
                            'from': {
                                'id': 'VXNlclR5cGU6MQ==',
                                'name': 'rory williams'
                            },
                            'id': 'RnJpZW5kU3VnZ2VzdGlvblR5cGU6KDQsIDUsIDEp',
                            'to': [
                                {
                                    'id': 'VXNlclR5cGU6NA==',
                                    'name': 'bill potts'
                                },
                                {
                                    'id': 'VXNlclR5cGU6NQ==',
                                    'name': 'song river'
                                }
                            ]
                        }
                    }
                ],
                'totalCount': 2
            },
            'id': 'VXNlclR5cGU6NA==',
            'name': 'bill potts'
        }
    }
}
