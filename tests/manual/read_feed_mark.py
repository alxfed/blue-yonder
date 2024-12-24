# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Actor, test_actor


my_actor = Actor()

feed_preferences = my_actor.feed_preferences()
whats_hot = feed_preferences[0]
feed_uri = whats_hot['value']

feed = my_actor.feed(feed_uri)
post_dict = feed[0]
feed_context = post_dict['feedContext']
post_uri = post_dict['post']['uri']

my_actor.mark_as_seen(uri=post_uri, feed_context=feed_context)

# Will it appear in the feed again?
reread_feed = my_actor.feed(feed_uri)
first_post_dict = reread_feed[0]
new_feed_context = post_dict['feedContext']
new_post_uri = first_post_dict['post']['uri']
...