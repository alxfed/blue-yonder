# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from time import sleep
from datetime import datetime
from blue_yonder.utilities import read_long_list, split_uri, split_url, rename_key
import requests


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
    records_url     = 'https://bsky.social/xrpc/com.atproto.repo.listRecords'
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
    # lists and packs
    lists           = None

    def __init__(self, actor: str = None, bluesky_handle: str = None, **kwargs):
        """
        Profile attributes are in the kwargs (obtained by getProfile)
        actor: a bluesky did
                        - or -
        bluesky_handle: a bluesky handle
        """
        self.did = actor  # bluesky did
        self.handle = bluesky_handle
        if actor or bluesky_handle:
            profile = self._get_profile(actor=actor)
            for key, value in profile.items():
                setattr(self, key, value)
        elif kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)
        else:
            ...

    def _get_profile(self, at_identifier: str = None, **kwargs):
        """
        """
        response = requests.get(
            url=self.VIEW_API + '/xrpc/app.bsky.actor.getProfile',
            params = {'actor': at_identifier if at_identifier else self.handle}
        )
        response.raise_for_status()
        return response.json()

    def _describe(self, actor: str = None, **kwargs):
        """
        """
        response = requests.get(
            url="https://bsky.social" + '/xrpc/com.atproto.repo.describeRepo',
            params={'repo': actor if actor else self.did},
        )
        response.raise_for_status()
        return response.json()

    def _records(self, actor: str = None, collection: str = None, **kwargs):
        """
        A general function for getting records of a given collection.
        Defaults to own repo.
        """
        def fetch_records(cursor: str = None, **kwargs):
            response = requests.get(
                url=self.records_url,
                params={
                    'repo': actor if actor else self.did,
                    'collection': collection,
                    'limit': 50,
                    'cursor': cursor}
            )
            response.raise_for_status()
            return response.json()

        records = read_long_list(
            fetcher=fetch_records,
            parameter='records'
        )
        return records

    def get_lists(self, actor: str = None, **kwargs):
        self.lists = self._records(actor=actor, collection='app.bsky.graph.list')
        return self.lists

    def read_list(self, uri: str = None, max_results: int = 1000, **kwargs):
        """

        :param uri:
        :param kwargs:
        :return:
        """
        def fetch_members(cursor: str = None, **kwargs):
            response = requests.get(
                url=self.VIEW_API + '/xrpc/app.bsky.graph.getList',
                params={
                    'list': uri,
                    'limit': 50,
                    'cursor': cursor}
            )
            response.raise_for_status()
            return response.json()

        members = read_long_list(
            fetcher=fetch_members,
            parameter='items',
            max_results=max_results
        )
        return members

    def follows(self, actor: str = None, max_results: int = 2000, **kwargs):
        """
        """
        if not actor:
            actor = self.did if self.did else self.handle

        def fetch_follows(cursor: str = None, **kwargs):
            response = requests.get(
                url=self.VIEW_API + '/xrpc/app.bsky.graph.getFollows',
                params={
                    'actor': actor,
                    'limit': 50,
                    'cursor': cursor}
            )
            response.raise_for_status()
            return response.json()

        follows = read_long_list(
            fetcher=fetch_follows,
            parameter='follows',
            max_results=max_results
        )
        return follows

    def followers(self, actor: str = None, max_results: int = 1000, **kwargs):
        """
        """
        if not actor:
            actor = self.did if self.did else self.handle

        def fetch_followers(cursor: str = None, **kwargs):
            response = requests.get(
                url=self.VIEW_API + '/xrpc/app.bsky.graph.getFollowers',
                params = {
                    'actor': actor,
                    'limit': 50,
                    'cursor': cursor}
            )
            response.raise_for_status()
            return response.json()

        followers = read_long_list(
            fetcher=fetch_followers,
            parameter='followers',
            max_results=max_results
        )
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

        def fetch_posts(cursor: str = None, **kwargs):
            response = requests.get(
                url=self.VIEW_API + '/xrpc/app.bsky.feed.getAuthorFeed',
                params={
                    'actor': self.did,
                    'limit': 50,
                    'filter': filter,
                    'includePins': True,
                    'cursor': cursor
                }
            )
            response.raise_for_status()
            return response.json()

        posts = read_long_list(
            fetcher=fetch_posts,
            parameter='feed'
        )
        return posts

    def read_post(self, url: str = None, uri: str = None,
                  actor: str = None, rkey: str = None,
                  max_attempts: int = 3, ** kwargs):
        """ Read a post with given uri in a given repo.
            Defaults to own repo.
        """
        if not (rkey and actor):
            if url:
                _, actor, _, rkey = self.uri_from_url(url=url)
            if uri:
                actor, rkey, _ = split_uri(uri)

        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    url=self.VIEW_API + '/xrpc/com.atproto.repo.getRecord',
                    params={
                        'repo': actor if actor else self.did,  # self if not given.
                        'collection': 'app.bsky.feed.post',
                        'rkey': rkey
                    }
                )
                if response.ok:
                    result = rename_key(response.json(), '$type', 'type')
                    return result
            except Exception as e:
                # print(e)
                sleep(2)
        raise Exception(f"Failed reading postafter {max_attempts} attempts")

    def read_thread(self, url: str = None, uri: str = None,
                    max_attempts: int = 3, **kwargs):
        """
        Read the whole thread of a post with given its url or uri.
        """
        if not uri:
            uri, _, _, _ = self.uri_from_url(url=url)

        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    url=self.VIEW_API + '/xrpc/app.bsky.feed.getPostThread',
                    params={
                        'uri': uri,
                        'depth': kwargs.get('depth', 10),  # kwv or 10
                        'parentHeight': kwargs.get('parent_height', 100),  # kwv or 100
                    }
                )
                if response.ok:
                    result = response.json()
                    # thread = result.get('thread', '')
                    thread = rename_key(result, '$type', 'type')
                    # threadgate = result.get('threadgate', None)
                    return thread
            except Exception as e:
                # print(e)
                sleep(2)
        raise Exception(f"Failed reading thread after {max_attempts} attempts")

    def uri_from_url(self, url: str, **kwargs):
        handle, rkey, type = split_uri(url)
        hshe = self._get_profile(at_identifier=handle)
        did = hshe['did']
        if type == 'lists':
            uri = f'at://{did}/app.bsky.graph.list/{rkey}'
        else:
            uri = f'at://{did}/app.bsky.feed.post/{rkey}'
        return uri, did, handle, rkey

    def url_from_uri(self, uri: str, **kwargs):
        did, rkey, type = split_uri(uri)
        hshe = self._get_profile(at_identifier=did)
        handle = hshe['handle']
        if type == 'app.bsky.graph.list':
            uri = f'https://bsky.app/profile/{handle}/lists/{rkey}'
        else:
            uri = f'https://bsky.app/profile/{handle}/post/{rkey}'
        return uri, did, handle, rkey


if __name__ == '__main__':
    """ Quick tests
    """
    another = Another() #bluesky_handle='alxfed.bsky.social')
    #
    root_post_url = 'https://bsky.app/profile/off-we-go.bsky.social/post/3lh3iyof6as2f'
    post = another.read_post(url=root_post_url)
    thread = another.read_thread(url=root_post_url)

    ...