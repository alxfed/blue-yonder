# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Actor, Another
from blue_yonder.utilities import split_url

# Thread url: https://bsky.app/profile/srushnlp.bsky.social/post/3lf45q745jk2w
# post in the middle url: https://bsky.app/profile/yoavartzi.com/post/3lf4huh3lf22w

post_url = 'https://bsky.app/profile/yoavartzi.com/post/3lf4huh3lf22w'
handle, rkey = split_url(post_url)

somebody = Another(bluesky_handle=handle)
his_posts = somebody.authored()

for post in his_posts:
    uri = post['post']['uri']
    key = uri.split('/')[-1]
    if key == rkey:
        break

thread, threadgate = somebody.read_thread(uri=uri)
...
