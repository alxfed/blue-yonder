# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from .actor import Actor, test_actor
from .another import Another
from .yonder import (search_actors,
                     get_feed_generator,
                     get_feed_skeleton,
                     feed,
                     list_feed)
from .utilities import read_long_list, _read_rate_limits

Butterfly   = Actor     # playful
Flower      = Another   # aliases

__all__ = [
    'Actor',
    'Butterfly',
    'Another',
    'Flower',
    'search_actors',
    'feed',
    'list_feed',
    'read_long_list',
    '_read_rate_limits',
    'test_actor',
]
