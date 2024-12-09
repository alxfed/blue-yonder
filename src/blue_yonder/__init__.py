# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from .client import Client
from .actors import Actor

Butterfly = Client  # playful
Bird = Client       # aliases

__all__ = [
    'Client',
    'Butterfly',
    'Bird',
    'Actor'
]
