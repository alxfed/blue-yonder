# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Another
from blue_yonder.utilities import read_long_list


another = Another(bluesky_handle='observing-machine.bsky.social')
description = another._describe()
all_posts = another.authored()
...
