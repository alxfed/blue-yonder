# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Actor, Another


my_actor = Actor()

profile = my_actor._get_profile(at_identifier='alxfed.bsky.social')
...