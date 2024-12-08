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
        display_name (str)      : The display name of the Actor.
        labels (list)           : A list of labels associated with the Actor.
        created_at (datetime)   : The date and time the Actor was created.
        description (str)       : A description of the Actor.
        indexed_at (datetime)   : The date and time the Actor was last indexed.
        followers_count (int)   : The number of followers the Actor has.
        follows_count (int)     : The number of accounts the Actor follows.
        posts_count (int)       : The number of posts the Actor has.
        pinned_post (dict)      : The pinned post of the Actor.

    Methods:
        get_profile(actor: str = None):
            Retrieves the profile of the Actor.
    """

    APP_VIEW_API = 'https://public.api.bsky.app'
    associated      = None
    did             = None
    handle          = None
    display_name    = None
    labels          = None
    created_at      = None
    description     = None
    indexed_at      = None
    followers_count = None
    follows_count   = None
    posts_count     = None
    pinned_post     = None

    def __init__(self, **kwargs):
        self.handle = kwargs.get('handle', None)
        self.did    = kwargs.get('did', None)
        if self.did:
            self.get_profile(actor=self.did)
        elif self.handle:
            self.get_profile(actor=self.handle)
        else:
            ...

    def get_profile(self, actor: str = None, **kwargs):
        """
        """
        if not actor:
            actor = self.did if self.did else self.handle
        response = requests.get(
            url=self.APP_VIEW_API + '/xrpc/app.bsky.actor.getProfile',
            params = {'actor': actor}
        )
        response.raise_for_status()
        r = response.json()
        self.associated     = r.get('associated', None)
        self.did            = r.get('did', None)
        self.handle         = r.get('handle', None)
        self.display_name   = r.get('displayName', None)
        self.labels         = r.get('labels', None)
        self.created_at     = r.get('createdAt', None)
        self.description    = r.get('description', None)
        self.indexed_at     = r.get('indexedAt', None)
        self.followers_count= r.get('followersCount', None)
        self.follows_count  = r.get('followsCount', None)
        self.posts_count    = r.get('postsCount', None)
        self.pinned_post    = r.get('pinnedPost', None)
        return response.json()


if __name__ == '__main__':
    at_identifier = {'handle': 'alxfed.bsky.social'}
    actor = Actor(**at_identifier)
    profile = actor.get_profile()
    ...