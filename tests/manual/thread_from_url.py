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
handle = post_url.split('/')[-3]

# somebody = Another()
uri = Another().uri_from_url(url=post_url)

# thread, threadgate = Another().read_thread(uri=uri)
url = Another().url_from_uri(uri=uri)
...
