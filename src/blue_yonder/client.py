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


handle      = environ.get('BLUESKY_HANDLE')      # the handle of a poster, linker, liker
password    = environ.get('BLUESKY_PASSWORD')    # the password of this poster
actor       = environ.get('BLUESKY_ACTOR')       # the actor whose feeds will be used in tests
pds_url     = environ.get('PDS_URL', 'https://bsky.social')  # the URL of a Private Data Server


class Client(object):
    """
        The 'clients' of the blue sky are Birds and Butterflies.
    """
    session     = requests.Session()
    post_url    = None
    upload_url  = None
    did         = None
    accessJwt   = None
    refreshJwt  = None
    handle      = None
    jwt         = None

    #recent
    last_uri    = None
    last_cid    = None
    last_rev    = None
    last_blob   = None

    # default actor for testing
    actor   = 'did:plc:x7lte36djjyhereki5avyst7'

    def __init__(self, **kwargs):
        """
            Launch the Butterfly!
        """
        self.did        = None
        self.handle     = kwargs.get('bluesky_handle',      handle)
        self.password   = kwargs.get('bluesky_password',    password)
        self.actor      = kwargs.get('bluesky_actor',       actor)
        # if you have a Private Data Server specify it as a pds_url kw argument
        self.pds_url    = kwargs.get('pds_url',             pds_url)
        self.post_url   = self.pds_url + '/xrpc/com.atproto.repo.createRecord'
        # If given an old session web-token - use _it_.
        self.jwt        = kwargs.get('jwt', None)

        # Start configuring a blank Session
        self.session.headers.update({'Content-Type': 'application/json'})
        # self.post_url = self.pds_url + '/xrpc/com.atproto.repo.createRecord'

        if self.jwt:
            # We were given a web-token, install the cookie into the Session.
            self.accessJwt  = self.jwt['accessJwt']
            self.did        = self.jwt['did']
            self.session.headers.update({'Authorization': 'Bearer ' + self.accessJwt})
            try:
                self.mute()
                self.unmute()
            except Exception as e:
                self.get_jwt()
        else:
            # No, we were not, let's create a new session.
            self.get_jwt()

    def get_jwt(self):
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
                self.handle = self.jwt['handle']
                self.accessJwt = self.jwt['accessJwt']
                self.refreshJwt = self.jwt['refreshJwt']  # Don't know how to use it yet.
                self.did = self.jwt['did']

                # Adjust the Session. Install the cookie into the Session.
                self.session.headers.update({"Authorization": "Bearer " + self.accessJwt})
            except Exception as e:
                raise RuntimeError(f'Huston did not give us a JWT:  {e}')

        except Exception as e:
            raise RuntimeError(f'Huston does not approve:  {e}')

    def publish_jwt(self):
        return self.jwt

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

    def get_posts_list(self):
        response = self.session.get(
            url=self.pds_url + '/xrpc/com.atproto.repo.listRecords',
            params={
                'repo': self.did,
                'collection': 'app.bsky.feed.post',
                'limit': 100,
                'reverse': False  # Last post first in the list
            }
        )
        response.raise_for_status()
        return response.json()

    def read_post(self, uri: str, repo: str = None, **kwargs):
        """
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
        """
        response = self.session.get(
            url=self.pds_url + '/xrpc/app.bsky.actor.getProfile',
            params = {
                'actor': actor if actor else self.handle
            }
        )
        response.raise_for_status()
        return response.json()

    def get_preferences(self, actor: str = None, **kwargs):
        """
        """
        response = self.session.get(
            url=self.pds_url + '/xrpc/app.bsky.actor.getPreferences',
            params = {'actor': actor if actor else self.handle}
        )
        response.raise_for_status()
        return response.json()

    def put_preferences(self, actor: str = None, preferences: dict = None, **kwargs):
        """
        """
        response = self.session.post(
            url=self.pds_url + '/xrpc/app.bsky.actor.putPreferences',
            json=preferences
        )
        response.raise_for_status()

    def mute(self, mute_actor: str = None, **kwargs):
        """
        """
        response = self.session.post(
            url=self.pds_url + '/xrpc/app.bsky.graph.muteActor',
            json={'actor': mute_actor if mute_actor else self.actor},  # mute_data
        )
        response.raise_for_status()

    def unmute(self, unmute_actor: str = None, **kwargs):
        response = self.session.post(
            url=self.pds_url + '/xrpc/app.bsky.graph.unmuteActor',
            json={'actor': unmute_actor if unmute_actor else self.actor},
        )
        response.raise_for_status()


if __name__ == "__main__":
    """
    Quick test.
    """
    butterfly = Client()
    # res = butterfly.mute()
    # res_2 = butterfly.unmute()
    # res = butterfly.get_preferences()
    # good = butterfly.put_preferences(preferences=res)
    # GETs from pds_url or public_url = 'https://public.api.bsky.app/'
    # result = butterfly.get_profile(actor=actor)
    # uploaded_blob = butterfly.upload_image(file_path='../../page_001.png', mime_type='image/png')
    # image_post_text = 'This is a post with an embedded image of a page.'
    # image_result = butterfly.post_image(text=image_post_text, blob=uploaded_blob, alt_text='This is the image of page 001.')
    posts_texts = [
        'First', 'Second', 'Third', 'Fourth'
    ]
    thread_result = butterfly.thread(posts_texts=posts_texts)
    result = butterfly.post(text="This is a flap of the butterfly's wings that caused the hurricane.")
    list_result = butterfly.get_posts_list()
    read_result = butterfly.read_post(uri=list_result['records'][0]['uri'])
    result_del = butterfly.delete_post(uri=list_result['records'][0]['uri'])
    # reply_result = butterfly.reply(root_post=quote, post=quote, text='This is a reply to a post.')
    # other_result = butterfly.quote_post(embed_post=quote, text='This is a post with an embedded post.')
    ...
