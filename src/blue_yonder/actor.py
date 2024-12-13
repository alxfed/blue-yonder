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
from collections import defaultdict


handle      = environ.get('BLUESKY_HANDLE')     # the handle of a poster, linker, liker
password    = environ.get('BLUESKY_PASSWORD')   # the password of this poster
test_actor  = environ.get('BLUESKY_TEST_ACTOR', 'did:plc:x7lte36djjyhereki5avyst7')
pds_url     = environ.get('PDS_URL', 'https://bsky.social')  # the URL of a Private Data Server


class Actor:
    """
        The 'clients' of the blue sky are Birds and Butterflies.
    """
    session     = requests.Session()
    post_url    = None
    upload_url  = None
    update_url  = None
    delete_url  = None
    did         = None
    accessJwt   = None
    refreshJwt  = None
    handle      = None
    jwt         = None

    # preferences
    preferences = None
    feeds       = None

    # authored
    authored_feeds = None

    # lists
    lists       = None

    #recent
    last_uri    = None
    last_cid    = None
    last_rev    = None
    last_blob   = None

    def __init__(self, **kwargs):
        """
            Create an Actor
        """

        self.did            = None
        self.handle         = kwargs.get('bluesky_handle',      handle)
        self.password       = kwargs.get('bluesky_password',    password)
        self.test_actor     = kwargs.get('test_actor',          test_actor)
        # if you have a Private Data Server specify it as a pds_url kw argument
        self.pds_url        = kwargs.get('pds_url',             pds_url)
        self.records_url    = self.pds_url + '/xrpc/com.atproto.repo.listRecords'
        self.post_url       = self.pds_url + '/xrpc/com.atproto.repo.createRecord'
        self.delete_url     = self.pds_url + '/xrpc/com.atproto.repo.deleteRecord'
        self.update_url     = self.pds_url + '/xrpc/com.atproto.repo.putRecord'
        self.jwt            = kwargs.get('jwt', None)

        # Start configuring a blank Session
        self.session.headers.update({'Content-Type': 'application/json'})

        # If given an old session web-token - use _it_.
        if self.jwt:
            # We were given a web-token, install the cookie into the Session.
            for key, value in self.jwt.items():
                setattr(self, key, value)
            self.session.headers.update({'Authorization': 'Bearer ' + self.accessJwt})
            try:
                self.mute()
                self.unmute()
            except Exception:
                self._get_token()
        else:
            # No, we were not, let's create a new session.
            self._get_token()

    def _get_token(self):
        """
        Initiate a session, get a JWT, ingest all the parameters
        :return:
        """
        session_url = self.pds_url + '/xrpc/com.atproto.server.createSession'
        session_data = {'identifier': self.handle, 'password': self.password}

        # Requesting permission to fly in the wild blue yonder.
        try:
            response = self.session.post(
                url=session_url,
                json=session_data)
            response.raise_for_status()
            try:
                # Get the handle and access / refresh JWT
                self.jwt = response.json()
                for key, value in self.jwt.items():
                    setattr(self, key, value)
                # Adjust the Session. Install the cookie into the Session.
                self.session.headers.update({"Authorization": "Bearer " + self.accessJwt})
            except Exception as e:
                raise RuntimeError(f'Huston did not give us a JWT:  {e}')

        except Exception as e:
            raise RuntimeError(f'Huston does not identify you as a human, you are a UFO:  {e}')

    def post(self, text: str = None, **kwargs):
        """
            Post.
        :param text:
        :return:
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        # Prepare to post
        post_data = {
            'repo':         self.did,   # self.handle,
            'collection':   'app.bsky.feed.post',
            'record':
                {
                    '$type': 'app.bsky.feed.post',
                    'text': text,
                    'createdAt': now
                }
        }
        try:
            response = self.session.post(url=self.post_url, json=post_data)
            response.raise_for_status()
            res = response.json()
            self.last_uri = res['uri']
            self.last_cid = res['cid']
            self.last_rev = res['commit']['rev']

        except Exception as e:
            raise Exception(f"Error, with talking to Huston:  {e}")
        return res

    def like(self, uri: str = None, cid: str = None, **kwargs):
        """
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        like_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.feed.like',
            'record':
                {
                    '$type': 'app.bsky.feed.like',
                    'createdAt': now,
                    'subject': {
                        'uri': uri,
                        'cid': cid
                    }
                }
        }

        try:
            response = self.session.post(
                url=self.post_url,
                json=like_data)

            response.raise_for_status()
            res = response.json()

        except Exception as e:
            raise Exception(f"Error, with talking to Huston:  {e}")

        return res

    def unlike(self, uri: str = None, record_key: str = None, **kwargs):
        """
        """
        if uri:
            record_key = uri.split("/")[-1]
        # Prepare to post
        elif record_key:
            pass
        else:
            raise Exception('Either uri or record_key must be given.')

        like_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.feed.like',
            'rkey': record_key
        }
        url_to_del = self.pds_url + '/xrpc/com.atproto.repo.deleteRecord'
        response = self.session.post(
            url=url_to_del,
            json=like_data
        )
        response.raise_for_status()
        res = response.json()
        return res

    def delete_post(self, uri: str = None, record_key: str = None, **kwargs):
        """
        """
        if uri:
            record_key = uri.split("/")[-1]
        # Prepare to post
        post_data = {
            'repo':         self.did,   # self.handle,
            'collection':   'app.bsky.feed.post',
            'rkey':         record_key
        }

        url_to_del = self.pds_url + '/xrpc/com.atproto.repo.deleteRecord'
        try:
            response = self.session.post(url=url_to_del, json=post_data)
            response.raise_for_status()
            res = response.json()

        except Exception as e:
            raise Exception(f"Can not delete the post:  {e}")
        return res

    def thread(self, posts_texts: list):
        """
            A trill of posts.
        """
        first_uri = None
        first_cid = None
        first_rev = None

        post_text = posts_texts.pop(0)
        self.post(text=post_text)
        first_uri = self.last_uri
        first_cid = self.last_cid
        first_rev = self.last_rev

        for post_text in posts_texts:
            sleep(1)
            self.reply(root_post={'uri': first_uri, 'cid': first_cid}, post={'uri': self.last_uri, 'cid': self.last_cid}, text=post_text)

    def reply(self, root_post: dict, post: dict, text: str):
        """
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        reply_data = {
            'repo':         self.did,   # self.handle,
            'collection':   'app.bsky.feed.post',
            'record': {
                '$type': 'app.bsky.feed.post',
                'text': text,
                'createdAt': now,
                'reply': {
                    'root': {
                        'uri': root_post['uri'],
                        'cid': root_post['cid']
                    },
                    'parent': {
                        'uri': post['uri'],
                        'cid': post['cid']
                    }
                }
            }
        }

        try:
            response = self.session.post(
                url=self.post_url,
                json=reply_data)

            response.raise_for_status()
            res = response.json()

            # Get the handle and access / refresh JWT
            self.last_uri = res['uri']
            self.last_cid = res['cid']
            self.last_rev = res['commit']['rev']

        except Exception as e:
            raise Exception(f"Error, with talking to Huston:  {e}")

        return res

    def quote_post(self, embed_post: dict, text: str):
        """
        Embed a given post (with 'uri' and 'cid') into a new post.
        embed_post: {'uri': uri, 'cid': cid}
        text: string up to 300 characters

        output: {'uri': uri, 'cid': cid, ...}
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        quote_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.feed.post',
            'record':
                {
                    '$type': 'app.bsky.feed.post',
                    'text': text,
                    'createdAt': now,
                    'embed': {
                        '$type': 'app.bsky.embed.record',
                        'record': {
                            'uri': embed_post['uri'],
                            'cid': embed_post['cid']
                        }
                    }
                }
        }
        try:
            response = self.session.post(
                url=self.post_url,
                json=quote_data)

            response.raise_for_status()
            res = response.json()

            # Get the last post attributes
            self.last_uri = res['uri']
            self.last_cid = res['cid']
            self.last_rev = res['commit']['rev']

        except Exception as e:
            raise Exception(f"Error, with talking to Huston:  {e}")

        return res

    def upload_image(self, file_path, **kwargs):
        """
        """
        mime_type = kwargs.get('mime_type', 'image/png')
        self.upload_url = self.pds_url + '/xrpc/com.atproto.repo.uploadBlob'

        with open(file_path, 'rb') as file:
            img_bytes = file.read()
        if len(img_bytes) > 1000000:
            raise Exception(f'The image file size too large. 1MB maximum.')

        headers = {
            'Content-Type': mime_type,
            'Authorization': 'Bearer ' + self.jwt['accessJwt']
        }
        upload_url = self.upload_url
        self.session.headers.update({'Content-Type': mime_type})

        response = self.session.post(
            url=self.upload_url,
            # headers=headers,
            data=img_bytes)

        response.raise_for_status()
        res = response.json()
        self.last_blob = res['blob']
        # restore the default content type.
        self.session.headers.update({'Content-Type': 'application/json'})
        return self.last_blob

    def post_image(self, text: str = None,
                   blob: dict = None,   # the blob of uploaded image
                   alt_text: str = '', **kwargs):
        """
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        image_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.feed.post',
            'record': {
                '$type': 'app.bsky.feed.post',
                'text': text,
                'createdAt': now,
                'embed': {
                    '$type': 'app.bsky.embed.images',
                    'images': [
                        {'alt': alt_text,'image': blob}
                    ]
                }
            }
        }
        try:
            response = self.session.post(
                url=self.post_url,
                json=image_data)

            response.raise_for_status()
            res = response.json()

            # Get the last post attributes
            self.last_uri = res['uri']
            self.last_cid = res['cid']
            self.last_rev = res['commit']['rev']
        except Exception as e:
            raise Exception(f"Error, posting an image:  {e}")

        return res

    def last_posts(self, repo: str = None, **kwargs):
        response = self.session.get(
            url=self.pds_url + '/xrpc/com.atproto.repo.listRecords',
            params={
                'repo': repo if repo else self.did,  # self if not given.
                'limit': 100,
                'reverse': False  # Last post first in the list
            }
        )
        response.raise_for_status()
        return response.json()

    def read_post(self, uri: str, repo: str = None, **kwargs):
        """
        Read a post with given uri in a given repo. Defaults to own repo.
        """
        rkey = uri.split("/")[-1]  # is the last part of the URI
        response = self.session.get(
            url=self.pds_url + '/xrpc/com.atproto.repo.getRecord',
            params={
                'repo': repo if repo else self.did,  # self if not given.
                'collection': 'app.bsky.feed.post',
                'rkey': rkey
            }
        )
        response.raise_for_status()
        return response.json()

    def get_profile(self, actor: str = None, **kwargs):
        """
        Get profile of a given actor. Defaults to actor's own.
        """
        response = self.session.get(
            url=self.pds_url + '/xrpc/app.bsky.actor.getProfile',
            params={'actor': actor if actor else self.handle}
        )
        response.raise_for_status()
        return response.json()

    def feed_preferences(self, **kwargs):
        """
           Extracts feed preferences from the preferences.
        :param kwargs:
        :return:
        """
        preference_type = 'app.bsky.actor.defs#savedFeedsPrefV2'
        preferences_list = self._get_preferences()
        self.feeds = next((item for item in preferences_list if item['$type'] == preference_type), None)['items']
        return self.feeds

    # def timeline(self, **kwargs):
    #     """ Right now the only default timeline is 'following'
    #     """
    #     timeline_posts = []
    #     still_some = True
    #     cursor = None
    #     while still_some:
    #         response = requests.get(
    #             url=self.pds_url + '/xrpc/app.bsky.feed.getTimeline',
    #             params={
    #                 'algorithm': None,
    #                 'limit': 50,
    #                 'cursor': cursor}
    #         )
    #         response.raise_for_status()
    #         res = response.json()
    #         timeline_posts.extend(res['followers'])
    #         if 'cursor' in res:
    #             cursor = res['cursor']
    #         else:
    #             still_some = False
    #     return timeline_posts

    def _get_preferences(self, **kwargs):
        """
        Retrieves the current account's preferences from the Private Data Server.
        Returns:
            dict: A dictionary containing the user's preferences.
        Raises:
            requests.exceptions.HTTPError: If the request to the Private Data Server fails.
        """
        response = self.session.get(
            url=self.pds_url + '/xrpc/app.bsky.actor.getPreferences'
        )
        response.raise_for_status()
        self.preferences = response.json()['preferences']
        return self.preferences

    def _put_preferences(self, preferences: dict = None, **kwargs):
        """
        Updates the current account's preferences on the Private Data Server.
        Args:
            preferences (dict): A dictionary containing the new preferences. Defaults to None.
        Returns:
            None.
        Raises:
            requests.exceptions.HTTPError: If the request to the Private Data Server fails.
        """
        response = self.session.post(
            url=self.pds_url + '/xrpc/app.bsky.actor.putPreferences',
            json=preferences
        )
        # The only thing this endpoint returns are codes. Nothing to return.
        response.raise_for_status()

    def get_lists(self, actor: str = None, **kwargs):
        self.lists = self.records(collection='app.bsky.graph.list')
        return self.lists

    def mute(self, mute_actor: str = None, **kwargs):
        """
        Mutes the specified actor.
        """
        response = self.session.post(
            url=self.pds_url + '/xrpc/app.bsky.graph.muteActor',
            json={'actor': mute_actor if mute_actor else self.test_actor},  # mute_data
        )
        response.raise_for_status()

    def unmute(self, unmute_actor: str = None, **kwargs):
        """ Unmutes the specified actor.
        """
        response = self.session.post(
            url=self.pds_url + '/xrpc/app.bsky.graph.unmuteActor',
            json={'actor': unmute_actor if unmute_actor else self.test_actor},
        )
        response.raise_for_status()

    def records(self, actor: str = None, collection: str = None, **kwargs):
        """
        A general function for getting records of a given collection.
        Defaults to own repo.
        """
        records = []
        still_some = True
        cursor = None
        while still_some:
            response = requests.get(
                url=self.records_url,
                params={
                    'repo': actor if actor else self.did,
                    'collection': collection,
                    'limit': 50,
                    'cursor': cursor}
            )
            response.raise_for_status()
            res = response.json()
            records.extend(res['records'])
            if 'cursor' in res:
                cursor = res['cursor']
            else:
                still_some = False

        return records

    def describe(self, actor: str = None, **kwargs):
        """
        """
        response = self.session.get(
            url=self.pds_url + '/xrpc/com.atproto.repo.describeRepo',
            params={'repo': actor if actor else self.did},
        )
        response.raise_for_status()
        return response.json()

    def create_list(self, list_name: str = None,
                    description: str = None,
                    purpose: str = None, **kwargs):
        """

        :param list_name:
        :param description:
        :param purpose:
            "app.bsky.graph.defs#modlist",
            "app.bsky.graph.defs#curatelist",
            "app.bsky.graph.defs#referencelist"
        :param kwargs:
        :return:
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        create_list_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.graph.list',
            'record':
                {
                    '$type':    'app.bsky.graph.list',
                    'purpose': purpose if purpose else 'app.bsky.graph.defs#curatelist',
                    'name':     list_name,
                    'description': description,
                    'createdAt': now
                }
        }

        response = self.session.post(
            url=self.pds_url + '/xrpc/com.atproto.repo.createRecord',
            json=create_list_data
        )
        response.raise_for_status()
        return response.json()

    def list_members(self, uri: str = None, **kwargs):
        members = []
        still_some = True
        cursor = None
        while still_some:
            response = requests.get(
                url=self.records_url,
                params={
                    'list': uri,
                    'limit': 100,
                    'cursor': cursor}
            )
            response.raise_for_status()
            res = response.json()
            members.extend(res['items'])
            if 'cursor' in res:
                cursor = res['cursor']
            else:
                still_some = False

        return members

    def delete_list(self, uri: str = None, record_key: str = None, **kwargs):
        """
        """
        if uri:
            record_key = uri.split("/")[-1]
        elif record_key:
            pass
        else:
            raise Exception('Either uri or record_key must be given.')

        # Prepare to post
        list_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.graph.list',
            'rkey': record_key
        }

        response = self.session.post(
            url=self.delete_url,
            json=list_data
        )
        response.raise_for_status()
        return response.json()

    def add_to_list(self, actor: str, list_uri: str, **kwargs):
        """
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        list_add_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.graph.listitem',
            'record':
                {
                    '$type': 'app.bsky.graph.listitem',
                    'createdAt': now,
                    'subject': actor,
                    'list': list_uri
                }
        }

        response = self.session.post(
            url=self.pds_url + '/xrpc/com.atproto.repo.createRecord',
            json=list_add_data
        )
        response.raise_for_status()
        return response.json()

    def remove_from_list(self, uri: str = None, record_key: str = None, **kwargs):
        """
        """
        if uri:
            record_key = uri.split("/")[-1]
        elif record_key:
            pass
        else:
            raise Exception('Either uri or record_key must be given.')

        # Prepare to post
        post_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.graph.listitem',
            'rkey': record_key
        }
        response = self.session.post(
            url=self.delete_url,
            json=post_data
        )
        response.raise_for_status()

        return response.json()

    def list_feed(self, list_uri: str = None, **kwargs):
        """
        """
        list_feed = []
        still_some = True
        cursor = None
        while still_some:
            response = requests.get(
                url=self.pds_url + '/xrpc/app.bsky.feed.getListFeed',
                params={
                    'list': list_uri,
                    'limit': 100,
                    'cursor': cursor}
            )
            response.raise_for_status()
            res = response.json()
            list_feed.extend(res['items'])
            if 'cursor' in res:
                cursor = res['cursor']
            else:
                still_some = False

        return list_feed

    def block_list(self, block_list: str = None, **kwargs):
        """
        Blocks the specified list.

        Args:
            block_list (str, optional): The list to block. Defaults to None.

        Returns:
            dict: The response from the server, containing the created block record.

        Raises:
            Exception: If the block operation fails.
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        block_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.graph.listblock',
            'record':
                {
                    '$type': 'app.bsky.graph.listblock',
                    'createdAt': now,
                    'subject': block_list
                }
        }

        response = self.session.post(
            url=self.pds_url + '/xrpc/com.atproto.repo.createRecord',
            json=block_data  # {'actor': block_actor if block_actor else self.actor},
        )
        response.raise_for_status()
        return response.json()

    def block(self, block_actor: str = None, **kwargs):
        """
        Blocks the specified actor.

        Args:
            block_actor (str, optional): The actor to block. Defaults to None.

        Returns:
            dict: The response from the server, containing the created block record.

        Raises:
            Exception: If the block operation fails.
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        block_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.graph.block',
            'record':
                {
                    '$type': 'app.bsky.graph.block',
                    'createdAt': now,
                    'subject': block_actor
                }
        }

        response = self.session.post(
            url=self.pds_url +'/xrpc/com.atproto.repo.createRecord',
            json=block_data  # {'actor': block_actor if block_actor else self.actor},
        )
        response.raise_for_status()
        return response.json()

    def unblock(self, uri: str = None, record_key: str = None, **kwargs):
        """
        """
        if uri:
            record_key = uri.split("/")[-1]
        elif record_key:
            pass
        else:
            raise Exception('Either uri or record_key must be given.')

        # Prepare to post
        post_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.graph.block',
            'rkey': record_key
        }

        response = self.session.post(
            url=self.delete_url,
            json=post_data
        )
        response.raise_for_status()

        return response.json()

    def follow(self, follow_actor: str = None, **kwargs):
        """
        Follows the specified actor.

        Args:
            follow_actor (str, optional): The actor to block. Defaults to None.

        Returns:
            dict: The response from the server, containing the created block record.

        Raises:
            Exception: If the block operation fails.
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        follow_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.graph.follow',
            'record':
                {
                    '$type': 'app.bsky.graph.follow',
                    'createdAt': now,
                    'subject': follow_actor
                }
        }

        response = self.session.post(
            url=self.pds_url +'/xrpc/com.atproto.repo.createRecord',
            json=follow_data  # {'actor': block_actor if block_actor else self.actor},
        )
        response.raise_for_status()
        return response.json()

    def unfollow(self, uri: str = None, record_key: str = None, **kwargs):
        """
        Unfollows the actor specified in the record.
        """
        if uri:
            record_key = uri.split("/")[-1]
        elif record_key:
            pass
        else:
            raise Exception('Either uri or record_key must be given.')

        # Prepare to post
        unfollow_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.graph.follow',
            'rkey': record_key
        }

        response = self.session.post(
            url=self.delete_url,
            json=unfollow_data
        )
        response.raise_for_status()

        return response.json()

    def search_posts(self, query: dict):
        """
        Search for the first not more than100 posts (because the paginated search is prohibited by Bluesky).

        Search for posts. Parameters of the query:

            q: string (required) Search query string; syntax, phrase, boolean, and faceting is unspecified, but Lucene query syntax is recommended.

            sort: string (optional) Possible values: [top, latest]. Specifies the ranking order of results. Default value: latest.

            since: string (optional) Filter results for posts after the indicated datetime (inclusive). Expected to use 'sortAt' timestamp, which may not match 'createdAt'. A datetime.

            until: string (optional) Filter results for posts before the indicated datetime (not inclusive). Expected to use 'sortAt' timestamp, which may not match 'createdAt'. A datetime.

            mentions: at-identifier (optional) Filter to posts which mention the given account. Handles are resolved to DID before query-time. Only matches rich-text facet mentions.

            author: at-identifier (optional) Filter to posts by the given account. Handles are resolved to DID before query-time.

            lang: language (optional) Filter to posts in the given language. Expected to be based on post language field, though server may override language detection.

            domain: string (optional) Filter to posts with URLs (facet links or embeds) linking to the given domain (hostname). Server may apply hostname normalization.

            url: uri (optional) Filter to posts with links (facet links or embeds) pointing to this URL. Server may apply URL normalization or fuzzy matching.

            tag: string[] Possible values: <= 640 characters. Filter to posts with the given tag (hashtag), based on rich-text facet or tag field. Do not include the hash (#) prefix. Multiple tags can be specified, with 'AND' matching.

            limit: integer (optional) Possible values: >= 1 and <= 100. Default value: 25

            Some recommendations can be found here: https://bsky.social/about/blog/05-31-2024-search
            but that was posted long before the scandal and the disabling of pagination.
        """

        response = self.session.get(
                url=self.pds_url + '/xrpc/app.bsky.feed.searchPosts',
                params=query
        )
        response.raise_for_status()
        return response.json()['posts']

    def permissions(self, uri: str = None, **kwargs):
        response = self.session.get(
            url=self.pds_url + '/xrpc/com.atproto.repo.listRecords',
            params={
                'repo': self.did,
                'collection': 'app.bsky.feed.threadgate',}
        )
        response.raise_for_status()
        return response.json()

    def restrict(self, uri: str = None, rules: list = None, **kwargs):
        """
        Set the rules of interaction with a thread. List of up to 5 rules.
        The possible rules are:
        1. If anybody can interact with the thread there is no record.
        2. {'$type': 'app.bsky.feed.threadgate#mentionRule'},
        3. {'$type': 'app.bsky.feed.threadgate#followingRule'},
        4. {'$type': 'app.bsky.feed.threadgate#listRule',
         'list': 'at://did:plc:yjvzk3c3uanrlrsdm4uezjqi/app.bsky.graph.list/3lcxml5gmf32s'}
        5. if nobody (besides the actor) can interact with the post 'allow' is an empty list - '[]'

        uri: the uri of the post
        rules: the list of rules (as dictionaries), up to 5 rules.
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        threadgate_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.feed.threadgate',
            'rkey': uri.split("/")[-1],
            'record':
                {
                    '$type':        'app.bsky.feed.threadgate',
                    'createdAt':    now,
                    'post':         uri,
                    'allow':        rules
                }
        }

        response = self.session.post(
            url=self.update_url,
            json=threadgate_data  #
        )
        response.raise_for_status()
        return response.json()

    def unrestrict(self, uri: str = None, record_key: str = None, **kwargs):
        """
        Delete the record restricting access to a thread.
        record_key: the key of the record
          - or -
        uri: the uri of the record
        """
        if uri:
            record_key = uri.split("/")[-1]
        # Prepare to post
        post_data = {
            'repo':         self.did,   # self.handle,
            'collection':   'app.bsky.feed.threadgate',
            'rkey':         record_key
        }
        try:
            response = self.session.post(
                url=self.delete_url,
                json=post_data)
            response.raise_for_status()

        except Exception as e:
            raise Exception(f"Can not delete the restriction:  {e}")
        return response.json()


if __name__ == "__main__":
    """
    Quick test.
    """
    # query = {
    #     'q': 'AI',
    #     'sort': 'latest',
    #     'since': '2024-11-05T21:44:46Z',
    #     'until': '2024-12-10T21:44:46Z',
    #     'limit': 100
    # }
    my_actor = Actor() # bluesky_handle='alxfed.bsky.social')
    res = my_actor.records(collection='app.bsky.graph.list')
    some_list = 'https://bsky.app/profile/eugeneyan.com/lists/3lbxx6amyfk2j'

    created_list = my_actor.create_list(
        list_name='Test List',
        description='Automated creation of a list.',
    )
    list_uri = created_list['uri']
    record_of_addition =my_actor.add_to_list(actor=test_actor, list_uri=list_uri)
    my_actor.remove_from_list(uri=record_of_addition['uri'])
    result = my_actor.delete_list(uri=list_uri)
    # my_actor.add_to_list(actor='reasoning-machine.bsky.social', list_uri=list_uri)

    # res = my_actor.block_list()
    # feeds = my_actor.timeline()
    # {'id': '3ld6okch7p32l', 'pinned': True, 'type': 'feed', 'value': 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot'}

    ...

    # diction = {item if item['$type'] in typosos else None for item in listos}
    ...
    # post = my_actor.post(text='This is a post with limited access')
    # EXAMPLE_LIST_URI = 'at://did:plc:yjvzk3c3uanrlrsdm4uezjqi/app.bsky.graph.list/3lcxml5gmf32s'
    # rules = [
    #     {'$type': 'app.bsky.feed.threadgate#mentionRule'},
    #     {'$type': 'app.bsky.feed.threadgate#followingRule'},
    #     {'$type': 'app.bsky.feed.threadgate#listRule', 'list': EXAMPLE_LIST_URI}
    # ]  # Nobody can interact with the post is an empty list - '[]'
    """{'preferences':[
    {'$type': 'app.bsky.actor.defs#savedFeedsPref', 'pinned': ['at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot', 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/with-friends', 'at://did:plc:hxg2smawgiuu42lkthu2n6iv/app.bsky.feed.generator/aaaggycjj6hf2', 'at://did:plc:x7lte36djjyhereki5avyst7/app.bsky.feed.generator/aaagg5vugsigc', 'at://did:plc:552sltcbj2n32vqfg2zkjnyj/app.bsky.feed.generator/aaafjfyjlteum', 'at://did:plc:rwkarouaeku2g6qkvqkirwa5/app.bsky.feed.generator/MLSky'], 
    'saved': ['at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/bsky-team', 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/with-friends', 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot', 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/hot-classic', 'at://did:plc:tenurhgjptubkk5zf5qhi3og/app.bsky.feed.generator/mutuals', 'at://did:plc:tenurhgjptubkk5zf5qhi3og/app.bsky.feed.generator/catch-up', 'at://did:plc:hxg2smawgiuu42lkthu2n6iv/app.bsky.feed.generator/aaaggycjj6hf2', 'at://did:plc:x7lte36djjyhereki5avyst7/app.bsky.feed.generator/aaagg5vugsigc', 'at://did:plc:mzbt67ojwwerred6cl63tovy/app.bsky.feed.generator/aaaggd6qkteau', 'at://did:plc:552sltcbj2n32vqfg2zkjnyj/app.bsky.feed.generator/aaafjfyjlteum', 'at://did:plc:rwkarouaeku2g6qkvqkirwa5/app.bsky.feed.generator/MLSky']},
    
    {'$type': 'app.bsky.actor.defs#savedFeedsPrefV2', 'items': [
    {'type': 'feed', 'value': 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot', 'pinned': True, 'id': '3kuxtwubbzc2x'}, 
    {'type': 'timeline', 'value': 'following', 'pinned': True, 'id': '3kuxtwubcyk2x'}, 
    {'type': 'feed', 'value': 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/with-friends', 'pinned': True, 'id': '3lbq7vseyps2m'}, 
    {'type': 'feed', 'value': 'at://did:plc:552sltcbj2n32vqfg2zkjnyj/app.bsky.feed.generator/aaafjfyjlteum', 'pinned': True, 'id': '3lbuvklomjc2t'}, 
    {'type': 'feed', 'value': 'at://did:plc:rwkarouaeku2g6qkvqkirwa5/app.bsky.feed.generator/MLSky', 'pinned': True, 'id': '3lc2girn66s2a'}, 
    {'type': 'feed', 'value': 'at://did:plc:hxg2smawgiuu42lkthu2n6iv/app.bsky.feed.generator/aaaggycjj6hf2', 'pinned': False, 'id': '3lbrlg3nuf22l'}, 
    {'type': 'feed', 'value': 'at://did:plc:x7lte36djjyhereki5avyst7/app.bsky.feed.generator/aaagg5vugsigc', 'pinned': False, 'id': '3lbrmsbjfe22t'}, 
    {'type': 'feed', 'value': 'at://did:plc:mzbt67ojwwerred6cl63tovy/app.bsky.feed.generator/aaaggd6qkteau', 'pinned': False, 'id': '3lbrhvzysjc2a'}, 
    {'type': 'feed', 'value': 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/bsky-team', 'pinned': False, 'id': '3lbqfsayodc2n'}]}
    """
    # result = my_actor.allowed(uri=post['uri'], rules=rules)
    # posts = my_actor.search_posts(query)
    # records = my_actor.records(collection='app.bsky.feed.post')
    # records = my_actor.permissions()
    # posts = my_actor.get_posts_list()
    # posts_content = []
    # for post in posts['records']:
    #     content = my_actor.read_post(post['uri'])
    #     posts_content.append(content)
    # for record in records['records']:
    #     my_actor.unrestrict(uri=record['uri'])
    description = my_actor.describe()
    # followed = my_actor.follow(follow_actor=test_actor)
    # unfollowed = my_actor.unfollow(uri=followed['uri'])
    # post = my_actor.post(text='This is a post')
    # like = my_actor.like(**post)
    # unlike = my_actor.unlike(uri=like['uri'])
    # preferences = my_actor.get_preferences()
    # my_actor.put_preferences(preferences)
    ...
