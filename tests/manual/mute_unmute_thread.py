# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Actor, test_actor


my_actor = Actor()
another_actor = Actor(bluesky_handle='multilogue.bsky.social')
post = another_actor.post(text='This is a post')
thread = post['uri']
mute = my_actor.mute_thread(thread=thread)
unmute = my_actor.unmute_thread(thread=thread)
...
