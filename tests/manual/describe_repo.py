# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Actor, test_actor


my_actor = Actor()

description = my_actor.describe()
# collection = 'app.bsky.feed.generator'
collection = 'app.bsky.feed.threadgate'
records = my_actor._records(collection=collection)
...