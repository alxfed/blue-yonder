# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder.utilities import split_url, split_uri
from blue_yonder import Actor, Another


my_actor = Actor()

# post = my_actor.post(text='This is a plain text post in a new way')
url = 'https://bsky.app/profile/multilogue.bsky.social/post/3lfbbfnwbys2c'


reply = my_actor.reply(text='This is a reply', parent_post=post)
...