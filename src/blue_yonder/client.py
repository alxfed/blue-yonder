# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from datetime import datetime, timezone
from os import getenv
import requests


class Client(object):
    """
        The 'clients' of the blue sky are Birds and Butterflies.
    """
    session     = requests.Session()
    post_url    = None
    did         = None
    accessJwt   = None
    refreshJwt  = None
    handle      = None
    jwt         = None

    def __init__(self, bluesky_handle: str, bluesky_password: str, **kwargs):
        """
            Launch the Butterfly!

        :param bluesky_handle:
        :param bluesky_password:
        :param kwargs:
        """

        # if you have a Private Data Server specify it as a pds_url kw argument
        self.pds_url = kwargs.get('pds_url', 'https://bsky.social')

        # Start configuring a blank Session
        self.session.headers.update({'Content-Type': 'application/json'})

        # chech whether we were given an old session
        self.accessJwt = kwargs.get('accessJwt', None)
        if self.accessJwt:
            # Yes, we were, so install the cookie into the Session.
            self.session.headers.update({"Authorization": "Bearer " + self.accessJwt})
        else:
            # No, we were not, let's create a new session.
            session_url = self.pds_url + '/xrpc/com.atproto.server.createSession'
            session_data = {'identifier': bluesky_handle, 'password': bluesky_password}

            # Request a permission to fly in the wild blue yonder.
            try:
                response = self.session.post(
                    url=session_url,
                    json=session_data)
                response.raise_for_status()
                try:
                    res = response.json()
                    # Get the handle and access / refresh JWT
                    self.jwt            = res
                    self.handle         = res['handle']
                    self.accessJwt      = res['accessJwt']
                    self.refreshJwt     = res['refreshJwt']  # Don't know how to use it yet.
                    self.did            = res['did']
                    # Adjust the Session.
                    self.post_url       = self.pds_url + '/xrpc/com.atproto.repo.createRecord'
                    # Install the cookie in the Session.
                    self.session.headers.update({"Authorization": "Bearer " + self.accessJwt})
                except Exception as e:
                    raise RuntimeError(f'Error, with talking to Huston:  {e}')
            except Exception as e:
                print(e)

    def publish_jwt(self):
        return self.jwt

    def post(self, text: str = None, many: list = None, **kwargs):
        """
            Post.
        :param text:
        :return:
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        if not many and text:
            post_data = {
                "repo": self.did, # self.handle,
                "collection": "app.bsky.feed.post",
                "record":
                    {
                        "$type": "app.bsky.feed.post",
                        "text": text,
                        "createdAt": now
                    }
            }
        elif many:
            post_data = {}
            for post in many:
                chunk =self.post_a_post(post)
        else:
            raise Exception("You need to specify either text or grain.")

        post_url = self.pds_url + '/xrpc/com.atproto.repo.createRecord'

        try:
            response = self.session.post(
                url=post_url,
                json=post_data)

            response.raise_for_status()
            res = response.json()

            # Get the handle and access / refresh JWT
            self.last_uri = res['uri']
            self.last_cid = res['cid']
            self.last_rev = res['commit']['rev']

        except Exception as e:
            raise Exception(f"Error, with talking to Huston:  {e}")
        return response.json()

    def thread(self, posts_text: list):
        """
            A trill of posts.

        :param posts:
        :return:
        """
        last_uri = None
        last_cid = None
        last_rev = None

        post_text = posts_text.pop(0)

        self.post(text=post_text)

    def reply(self, root_post: dict, post: dict, text: str):
        """
            post back.

        :param root_post:
        :param post:
        :param text:
        :return:
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        reply_data = {
            "repo": self.did,  # self.handle,
            "collection": "app.bsky.feed.post",
            "record":
                {
                    "$type": "app.bsky.feed.post",
                    "text": text,
                    "createdAt": now
                }
        }

        post_url = self.pds_url + '/xrpc/com.atproto.repo.createRecord'

        try:
            response = self.session.post(
                url=post_url,
                json=reply_data)

            response.raise_for_status()
            res = response.json()

            # Get the handle and access / refresh JWT
            self.last_uri = res['uri']
            self.last_cid = res['cid']
            self.last_rev = res['commit']['rev']

        except Exception as e:
            raise Exception(f"Error, with talking to Huston:  {e}")
        return response.json()

    def quote_post(self, text: str):
        """
            post back.

        :param root_post:
        :param text:
        :return:
        """
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        quote_data = {
            "repo": self.did,  # self.handle,
            "collection": "app.bsky.feed.post",
            "record":
                {
                    "$type": "app.bsky.feed.post",
                    "text": text,
                    "createdAt": now,
                    "embed": {
                        "$type": "app.bsky.embed.record",
                        "record": {
                            "uri": 'at://did:plc:x7lte36djjyhereki5avyst7/app.bsky.feed.post/3lbadvvi4ja2z',
                            "cid": 'bafyreidmtjniejo3jdpxl5wmen2yhwcbheu5jwdauhl2ocueglpokz5pdm'
                        }
                    }
                }
        }

        post_url = self.pds_url + '/xrpc/com.atproto.repo.createRecord'

        try:
            response = self.session.post(
                url=post_url,
                json=quote_data)

            response.raise_for_status()
            res = response.json()

            # Get the handle and access / refresh JWT
            self.last_uri = res['uri']
            self.last_cid = res['cid']
            self.last_rev = res['commit']['rev']

        except Exception as e:
            raise Exception(f"Error, with talking to Huston:  {e}")
        return response.json()


if __name__ == "__main__":
    # kwargs = {
    #     'pds_url': 'https://bsky.social'
    # }
    butterfly = Client(
        bluesky_handle=getenv('BLUESKY_HANDLE'),
        bluesky_password=getenv('BLUESKY_PASSWORD')
    )
    result = butterfly.post(text='This is a flap of the butterfly wings that caused the hurricane.')
    other_result = butterfly.quote_post(text='This is a post with an embedded post.')
    ...
