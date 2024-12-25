# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Actor, test_actor


text = 'This is a post with limited access'
my_actor = Actor(bluesky_handle='multilogue.bsky.social')
post = my_actor.post(text=text)
EXAMPLE_LIST_URI = 'at://did:plc:yjvzk3c3uanrlrsdm4uezjqi/app.bsky.graph.list/3lcxml5gmf32s'
rules = [
#     {'$type': 'app.bsky.feed.threadgate#mentionRule'},
#     {'$type': 'app.bsky.feed.threadgate#followingRule'},
    {'$type': 'app.bsky.feed.threadgate#listRule', 'list': EXAMPLE_LIST_URI}
 ]  # Nobody can interact with the post where rulesis an empty list - '[]'

result = my_actor.restrict(uri=post['uri'], rules=rules)

my_actor.delete_post(uri=post['uri'])
print('post deleted')
...