# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from datetime import datetime, timezone
from os import environ
from time import sleep
import requests
from json import dumps, loads
# from .client import Client


class Actor():
    """
    Represents an Actor in the BlueSky environment.
    Actor has a unique identifier, a handle, and other associated information.

    Attributes:
        associated (dict)       : Additional information about the Actor.
        did (str)               : The unique identifier of the Actor.
        handle (str)            : The handle of the Actor.
        displayName (str)       : The display name of the Actor.
        labels (list)           : A list of labels associated with the Actor.
        createdAt (datetime)    : The date and time the Actor was created.
        description (str)       : A description of the Actor.
        indexedAt (datetime)    : The date and time the Actor was last indexed.
        followersCount (int)    : The number of followers the Actor has.
        followsCount (int)      : The number of accounts the Actor follows.
        postsCount (int)        : The number of posts the Actor has.
        pinnedPost (dict)       : The pinned post of the Actor.

    Methods:
        get_profile(actor: str = None):
            Retrieves the profile of the Actor.
    """

    VIEW_API        = 'https://public.api.bsky.app'
    associated      = None
    did             = None
    handle          = None
    displayName     = None
    labels          = None
    createdAt       = None
    description     = None
    indexedAt       = None
    followersCount  = None
    followsCount    = None
    postsCount      = None
    pinnedPost      = None

    def __init__(self, actor: str = None, **kwargs):
        """
        Profile attributes are in the kwargs (obtained by getProfile)
        """
        if actor:
            profile = self.get_profile(actor=actor)
            for key, value in profile.items():
                setattr(self, key, value)
        elif kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)
        else:
            ...

    def get_profile(self, actor: str = None, **kwargs):
        """
        """
        if not actor:
            actor = self.did if self.did else self.handle
        response = requests.get(
            url=self.VIEW_API + '/xrpc/app.bsky.actor.getProfile',
            params = {'actor': actor}
        )
        response.raise_for_status()
        res = response.json()
        for key, value in res.items():
            setattr(self, key, value)
        return res


if __name__ == '__main__':
    # at_identifier = {'handle': 'alxfed.bsky.social'}
    # actor = Actor(**at_identifier)
    profile = {
        'did': 'did:plc:x7lte36djjyhereki5avyst7',
        'handle': 'alxfed.bsky.social',
        'displayName': 'Alex Fedotov',
        'avatar': 'https://cdn.bsky.app/img/avatar/plain/did:plc:x7lte36djjyhereki5avyst7/bafkreido54oo5qxqtj7z6npkcycsc6uf66ly7jbybytpjjrlchv7jxhohe@jpeg',
        'associated': {'lists': 4, 'feedgens': 1, 'starterPacks': 0, 'labeler': False, 'chat': {'allowIncoming': 'all'}},
        'labels': [],
        'createdAt': '2024-06-15T14:23:24.408Z',
        'description': 'AI Dialogue Facilitator\nPh. D. in Physics and Mathematics. Data Scientist since 1978\nChicago, IL, since 2003.\n\nIn the past Twitter - @alxfed',
        'indexedAt': '2024-11-28T13:17:16.343Z',
        'banner': 'https://cdn.bsky.app/img/banner/plain/did:plc:x7lte36djjyhereki5avyst7/bafkreiaixxnlszzxefchi7nbbkco72vebx2ijvqza7pxl2yrkr76aqmm6u@jpeg',
        'followersCount': 181,
        'followsCount': 1560,
        'postsCount': 201,
        'pinnedPost': {'cid': 'bafyreibaeqfeggsxmcz2krmio33mqq2rrpahx47qa2iy6xcmo3eri4qtgm', 'uri': 'at://did:plc:x7lte36djjyhereki5avyst7/app.bsky.feed.post/3lbflilk6kc23'}
    }
    # instantiated = Actor(**profile)
    actor = Actor(actor='did:plc:x7lte36djjyhereki5avyst7')
    ...