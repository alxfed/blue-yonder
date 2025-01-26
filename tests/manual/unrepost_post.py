# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Actor, Another


my_actor = Actor(bluesky_handle='observing-machine.bsky.social')
description = my_actor.describe()
records = my_actor._records(collection='app.bsky.feed.repost')

another_actor = Another(bluesky_handle='observing-machine.bsky.social')

authored = another_actor.authored()

repost_uri = records[0]['uri']
# repost = my_actor.repost(uri=repost_uri)
unrepost = my_actor.unrepost(uri=repost_uri)
...