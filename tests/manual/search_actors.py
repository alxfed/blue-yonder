# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Actor, yonder


# actors = yonder.search_actors(query={'q': 'ML/AI', 'limit': 50}, max_results=1000)
my_actor = Actor(bluesky_handle='alxfed.bsky.social')
# 'https://bsky.app/profile/alxfed.bsky.social/lists/3ldz5oqihfq2a'
uri, did, handle, rkey = my_actor.uri_from_url(url='https://bsky.app/profile/alxfed.bsky.social/lists/3ldz5oqihfq2a')
lists = my_actor.get_lists()
...