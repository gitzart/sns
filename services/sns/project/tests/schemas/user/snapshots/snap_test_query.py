# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_basic_profile 1'] = {
    'data': {
        'user': {
            'bio': None,
            'birthday': None,
            'email': 'rory@email.com',
            'firstName': 'rory',
            'gender': 'MALE',
            'id': 'VXNlclR5cGU6MQ==',
            'lastName': 'williams',
            'maritalStatus': None,
            'username': None
        }
    }
}

snapshots['test_relationship_profile 1'] = {
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

snapshots['test_friend_requests 1'] = {
    'data': {
        'user': {
            'friendRequests': {
                'edges': [
                    {
                        'node': {
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

snapshots['test_friend_suggestions 1'] = {
    'data': {
        'user': {
            'friendSuggestions': {
                'edges': [
                    {
                        'node': {
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
