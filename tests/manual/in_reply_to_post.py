# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Actor

post = 'https://bsky.app/profile/machina-ratiocinatrix.github.io/post/3lbk3us5yzk2j'
reply = "This is a reply to Machina's post"

my_actor = Actor()

post = (
    my_actor.in_reply_to(post)
    .post(reply)
)
...

