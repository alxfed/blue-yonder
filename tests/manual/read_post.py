# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Another


post_url = 'https://bsky.app/profile/vinric.bsky.social/post/3lhqgrltdzs2q'

post = Another().read_post(url=post_url)
...