# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Actor, Another, test_actor


my_actor = Actor(bluesky_handle='alxfed.bsky.social')
actor_did = 'did:plc:62lmbfwjtvopjdkk7dzm3tsg'
another_did = 'did:plc:v7nrkiz4bxov5sv7fauunjin'
who_that_is = Another(actor=actor_did)
who_the_other_id = Another(actor=another_did)
done, records = my_actor.unfollow(actor=actor_did)
commit, result = my_actor.unfollow(actor=another_did, records=records)
...