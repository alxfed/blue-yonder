# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Actor, test_actor


my_actor = Actor(bluesky_handle='alxfed.bsky.social')
blocks = my_actor.get_blocks(max_results=20000)
...
