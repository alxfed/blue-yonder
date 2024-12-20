# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from .actor import Actor
from .another import Another
from .yonder import (search_100_posts,
                     search_actors,
                     feed,
                     list_feed)
from .utilities import read_long_list, read_rate_limits

Butterfly   = Actor     # playful
Flower      = Another   # aliases

__all__ = [
    'Actor',
    'Butterfly',
    'Another',
    'Flower',
    'search_100_posts',
    'read_long_list',
    'read_rate_limits',
]
