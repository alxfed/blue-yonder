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


class Another():
    """
    Represents an entity in the BlueSky environment.
    'Actor' (in their terminology) has a unique identifier, a handle,
    a display name, and other associated information.

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
            profile = self._get_profile(actor=actor)
            for key, value in profile.items():
                setattr(self, key, value)
        elif kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)
        else:
            ...

    def _get_profile(self, actor: str = None, **kwargs):
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

    def follows(self, actor: str = None, **kwargs):
        """
        """
        if not actor:
            actor = self.did if self.did else self.handle

        follows = []
        still_some = True
        cursor = None
        while still_some:
            response = requests.get(
                url=self.VIEW_API + '/xrpc/app.bsky.graph.getFollows',
                params={
                    'actor': actor,
                    'limit': 50,
                    'cursor': cursor}
            )
            response.raise_for_status()
            res = response.json()
            follows.extend(res['follows'])
            if 'cursor' in res:
                cursor = res['cursor']
            else:
                still_some = False
        return follows

    def followers(self, actor: str = None, **kwargs):
        """
        """
        if not actor:
            actor = self.did if self.did else self.handle

        followers = []
        still_some = True
        cursor = None
        while still_some:
            response = requests.get(
                url=self.VIEW_API + '/xrpc/app.bsky.graph.getFollowers',
                params = {
                    'actor': actor,
                    'limit': 50,
                    'cursor': cursor}
            )
            response.raise_for_status()
            res = response.json()
            followers.extend(res['followers'])
            if 'cursor' in res:
                cursor = res['cursor']
            else:
                still_some = False
        return followers

    def created_feeds(self, actor: str = None, **kwargs):
        """
        """
        if not actor:
            actor = self.did if self.did else self.handle
        response = requests.get(
            url=self.VIEW_API + '/xrpc/app.bsky.feed.getActorFeeds',
            params={'actor': actor}
        )
        response.raise_for_status()
        res = response.json()
        return res

    def lists(self, actor: str = None, **kwargs):
        """
        """
        if not actor:
            actor = self.did if self.did else self.handle
        response = requests.get(
            url=self.VIEW_API + '/xrpc/app.bsky.graph.getLists',
            params={'actor': actor}
        )
        response.raise_for_status()
        res = response.json()
        return res

    def authored(self, filter: list = None, **kwargs):
        """
        """
        if not filter:
            filter = [
                'posts_with_replies',
                'posts_no_replies',
                # 'posts_with_media',
                'posts_and_author_threads'
            ]
        response = requests.get(
            url=self.VIEW_API + '/xrpc/app.bsky.feed.getAuthorFeed',
            params={
                'actor': self.did,
                'limit': 50,
                'cursor': None,
                'filter': filter,
                'includePins': True
            }
        )
        response.raise_for_status()
        res = response.json()
        return res


if __name__ == '__main__':
    """ Quick tests
    """
    alex = Another(actor='did:plc:x7lte36djjyhereki5avyst7')
    # feed_id = {'id': '3ld6okch7p32l', 'pinned': True, 'type': 'feed', 'value': 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot'}
    select = [
        'posts_with_replies',
        'posts_no_replies',
        'posts_with_media',
        'posts_and_author_threads'
    ]
    feed = alex.authored(filter=select)
    lists = alex.lists()
    feeds = alex.created_feeds()
    followers = alex.followers()
    follows = alex.follows()
    ...