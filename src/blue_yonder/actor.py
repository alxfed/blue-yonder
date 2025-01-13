# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from datetime import datetime, timezone
from time import sleep, time
from os import environ
import requests
from functools import wraps
from blue_yonder.utilities import split_uri, split_url


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
    list_url    = None
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

    # limits
    RateLimit           = None
    RateLimitRemaining  = None
    RateLimitReset      = None
    RateLimitPolicy     = None
    RateLimitPolicyW    = None

    def __init__(self, **kwargs):
        """ Create an Actor, pass the bluesky_handle and bluesky_password
        as kwargs if there are no environment variables;
        pass the previous session jwt as a keyword argument 'jwt' if you want
        to reuse sessions.
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
        self.upload_url     = self.pds_url + '/xrpc/com.atproto.repo.uploadBlob'
        self.list_url       = self.pds_url + '/xrpc/app.bsky.graph.getList'
        self.jwt            = kwargs.get('jwt', None)

        # Rate limits
        self.RateLimit          = 30
        self.RateLimitReset     = int(time()) - 1

        # Start configuring a blank Session
        self.session.headers.update({'Content-Type': 'application/json'})

        # If given an old session web-token - use _it_.
        if self.jwt:
            # We were given a web-token appropiate it.
            for key, value in self.jwt.items():
                setattr(self, key, value)

            # install the token into the Session.
            self.session.headers.update({'Authorization': 'Bearer ' + self.accessJwt})
            try:
                # Check the validity of the token by muting and unmuting
                # an unsuspecting victim.
                self.mute()
                self._update_limits(self.unmute())

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
        if not self._rate_limited():
            try:
                # Requesting permission to fly in the wild blue yonder.
                response = self.session.post(
                    url=session_url,
                    json=session_data)

                self._update_limits(response)

                response.raise_for_status()

                try:
                    # Get the handle and access / refresh JWT
                    self.jwt = response.json()
                    for key, value in self.jwt.items():
                        setattr(self, key, value)
                    # Adjust the Session. Install the cookie into the Session.
                    self.session.headers.update({"Authorization": "Bearer " + self.accessJwt})
                except Exception as e:
                    raise RuntimeError(f'Huston did not give you a JWT:  {e}')

            except Exception as e:
                raise RuntimeError(f'Huston does not identify you as a human, you are a UFO:  {e}')

        else:
            raise RuntimeError(f'Rate limited, wait {self.RateLimitReset - int(datetime.now(timezone.utc).timestamp())} seconds')

    @staticmethod
    def _check_rate_limit(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            until_refresh = self.RateLimitReset - int(datetime.now(timezone.utc).timestamp())
            if until_refresh < 0:
                return func(self, *args, **kwargs)
            elif self.RateLimitRemaining > 0:
                return func(self, *args, **kwargs)
            elif self.RateLimitRemaining == 0:
                if until_refresh < 10:
                    sleep(until_refresh)
                    return func(self, *args, **kwargs)
                else:
                    raise RuntimeError(f'Rate limited, wait {self.RateLimitReset - int(datetime.now(timezone.utc).timestamp())} seconds')
            else:
                raise RuntimeError(f'Rate limited, wait {self.RateLimitReset - int(datetime.now(timezone.utc).timestamp())} seconds')
        return wrapper

    def _rate_limited(self, wait: int = 10, **kwargs):
        """ Check the rate limits before making a request.
        """
        until_refresh = self.RateLimitReset - int(datetime.now(timezone.utc).timestamp())
        if until_refresh < 0:
            return False
        elif self.RateLimitRemaining > 0:
            return False
        elif self.RateLimitRemaining == 0:
            if until_refresh < wait:
                sleep(until_refresh)
                return False
            else:
                return True
        else:
            return True

    def _update_limits(self, response: requests.Response):
        rh = response.headers
        rlp, rlpw = rh['RateLimit-Policy'].split(';')
        rlpw = rlpw.split('=')[-1]
        self.RateLimit          = int(rh['RateLimit-Limit'])
        self.RateLimitRemaining = int(rh['RateLimit-Remaining'])
        self.RateLimitReset     = int(rh['RateLimit-Reset'])
        self.RateLimitPolicy    = int(rlp)
        self.RateLimitPolicyW   = int(rlpw)

    @_check_rate_limit
    def _post(self, text: str = None, **kwargs):
        """
            Post.
        :param text:
        reply and embed - in the kwargs
        :return:
        """
        # Pick up what's in the kwargs.
        text    = kwargs.get('text', text)
        reply   = kwargs.get('reply', None)
        embed   = kwargs.get('embed', None)

        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        # Prepare the record
        record = {
            '$type': 'app.bsky.feed.post',
            'text': text,
            'createdAt': now,
            'langs': ['en-GB', 'en-US']
        }
        if reply:
            record['reply'] = reply
        if embed:
            record['embed'] = embed

        # Prepare to post
        post_data = {
            'repo': self.did,  # self.handle,
            'collection': 'app.bsky.feed.post',
            'record': record
        }
        # Post
        try:
            # You can check the data that you will be posting at this point.
            response = self.session.post(url=self.post_url, json=post_data)
            # Read the limits left that were returned in the headers.
            self._update_limits(response)
            # Check whether the request was successful.
            response.raise_for_status()
            # Decode the result and update the state of the Actor object.
            result = response.json()
            self.last_uri = result['uri']
            self.last_cid = result['cid']
            self.last_rev = result['commit']['rev']

        except Exception as e:
            raise Exception(f"Error, with talking to Bluesky API:  {e}")
        return result

    def post(self, text: str = None, **kwargs):
        """ Post plain text.
        :param text: plain text string
        :return:
        """
        result = self._post(text=text, **kwargs)
        return result

    def reply(self, parent_post: dict, root_post: dict = None, text: str = None, **kwargs):
        """ Reply to a post with plain text.
        :param root_post:
        :param parent_post:
        :param kwargs:
        :return:
        """
        text = kwargs.get('text', text)
        new_kwargs = self._reply_kwargs(root_post=root_post, parent_post=parent_post, **kwargs)
        return self._post(text=text, **new_kwargs)

    def _reply_kwargs(self, parent_post: dict, root_post: dict = None, **kwargs) -> dict:
        """ Reply to a post with plain text.
        :param root_post: root post # {'uri': uri, 'cid': cid}
        :param post: post # {'uri': uri, 'cid': cid}
        :param text: plain text string
        :return: return of the _post method.
        """
        # now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        #
        # reply_data = {
        #     'repo': self.did,  # self.handle,
        #     'collection': 'app.bsky.feed.post',
        #     'record': {
        #         '$type': 'app.bsky.feed.post',
        #         'text': text,
        #         'createdAt': now,
        #         'reply': {
        #             'root': {
        #                 'uri': root_post['uri'],
        #                 'cid': root_post['cid']
        #             },
        #             'parent': {
        #                 'uri': post['uri'],
        #                 'cid': post['cid']
        #             }
        #         },
        #         'langs': ['en-GB', 'en-US']
        #     }
        # }
        #
        # try:
        #     response = self.session.post(
        #         url=self.post_url,
        #         json=reply_data)
        #     self._update_limits(response)
        #
        #     response.raise_for_status()
        #     res = response.json()
        #
        #     # Get the handle and access / refresh JWT
        #     self.last_uri = res['uri']
        #     self.last_cid = res['cid']
        #     self.last_rev = res['commit']['rev']
        #
        # except Exception as e:
        #     raise Exception(f"Error, with talking to Huston:  {e}")
        if not root_post:
            # thread = self.read_thread(uri=parent_post['uri'])
            post = self.read_post(uri=parent_post['uri'])
            reply = post['value'].get('reply', None)
            if reply:
                root_post = reply['root']
            else:
                root_post = parent_post
            ...
        reply_kwargs = {
            'reply': {
                'root': {
                    'uri': root_post['uri'],
                    'cid': root_post['cid']
                },
                'parent': {
                    'uri': parent_post['uri'],
                    'cid': parent_post['cid']
                }
            }
        }
        # result = self._post(text=text, reply=reply)
        return kwargs | reply_kwargs

    @staticmethod
    def _embed_record_kwargs(record: dict, **kwargs):
        embed_record = {
            'embed': {
                '$type': 'app.bsky.embed.record',
                'record': {
                    'uri': record['uri'],
                    'cid': record['cid']
                }
            }
        }
        return kwargs | embed_record

    @staticmethod
    def _embed_external_kwargs(url: str, title: str = None, description: str = None, thumb: dict = None, **kwargs):
        external = {
            'uri': url,
        }
        if title:
            external['title'] = title
        if description:
            external['description'] = description
        if thumb:
            # 'thumb': {
            #     '$type': 'blob',
            #     'ref': {
            #         '$link': 'bafkreiash5e...'
            #     },
            #     'mimeType': 'image/png',
            #     'size': 23527
            # }
            external['thumb'] = thumb
        embed_external = {
            'embed': {
                '$type': 'app.bsky.embed.external',
                'external': external
              }
        }
        return kwargs | embed_external

    def post_external(self, url: str, text: str = None,
                      title: str = None, description: str = None,
                      thumb: dict = None, **kwargs):
        """ Upload the thumbnail image before if you want
            to have a preview image.
        :param url:
        :param text:
        :param title:
        :param description:
        :param thumb:
        :param kwargs:
        :return:
        """
        new_kwargs = self._embed_external_kwargs(url=url, title=title,
                                                 description=description,
                                                 thumb=thumb, **kwargs)
        result = self._post(text=text, **new_kwargs)
        return result

    @staticmethod
    def _embed_quote_kwargs(embed_post: dict, **kwargs):
        quote = {
            'embed': {
                '$type': 'app.bsky.embed.record',
                'record': {
                    'uri': embed_post['uri'],
                    'cid': embed_post['cid']
                }
            }
        }
        return kwargs | quote

    @_check_rate_limit
    def quote_post(self, text: str, embed_post: dict, **kwargs):
        """ Embed a given post (with 'uri' and 'cid') into a new post.
        embed_post: {'uri': uri, 'cid': cid}
        text: string up to 300 characters
        output: {'uri': uri, 'cid': cid, ...} of a post with embedded post.
        """
        # now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        #
        # quote_data = {
        #     'repo': self.did,  # self.handle,
        #     'collection': 'app.bsky.feed.post',
        #     'record':
        #         {
        #             '$type': 'app.bsky.feed.post',
        #             'text': text,
        #             'createdAt': now,
        #             'embed': {
        #                 '$type': 'app.bsky.embed.record',
        #                 'record': {
        #                     'uri': embed_post['uri'],
        #                     'cid': embed_post['cid']
        #                 }
        #             }
        #         }
        # }
        # try:
        #     response = self.session.post(
        #         url=self.post_url,
        #         json=quote_data)
        #     self._update_limits(response)
        #
        #     response.raise_for_status()
        #     res = response.json()
        #
        #     # Get the last post attributes
        #     self.last_uri = res['uri']
        #     self.last_cid = res['cid']
        #     self.last_rev = res['commit']['rev']
        #
        # except Exception as e:
        #     raise Exception(f"Error, with talking to Huston:  {e}")
        new_kwargs = self._embed_quote_kwargs(embed_post=embed_post, **kwargs)
        result = self._post(text=text, **new_kwargs)

        return result

    @_check_rate_limit
    def upload_image(self, file_path, **kwargs):
        """
        """
        mime_type = kwargs.get('mime_type', 'image/png')

        with open(file_path, 'rb') as file:
            img_bytes = file.read()
        if len(img_bytes) > 1000000:
            raise Exception(f'The image file size too large. 1MB maximum.')

        self.session.headers.update({'Content-Type': mime_type})
        response = self.session.post(
            url=self.upload_url,
            data=img_bytes
        )
        self._update_limits(response)

        response.raise_for_status()
        result = response.json()
        self.last_blob = result['blob']
        # restore the default content type.
        self.session.headers.update({'Content-Type': 'application/json'})

        return self.last_blob

    @_check_rate_limit
    def post_image(self, text: str = None,
                   blob: dict = None,   # the blob of uploaded image
                   aspect_ratio: dict = None, # {'height':620,'width':620}
                   alt_text: str = 'No alternative text was provided',
                   reply: dict = None, **kwargs):
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
                        {
                            'alt': alt_text,
                            'aspectRatio': aspect_ratio if aspect_ratio else {'height':620,'width':620},
                            'image': blob
                        }
                    ]
                },
                'langs': ['en-GB', 'en-US']
            }
        }
        if reply:
            image_data['record']['reply'] = reply

        try:
            response = self.session.post(
                url=self.post_url,
                json=image_data)
            # read the returned limits left.
            self._update_limits(response)

            response.raise_for_status()
            res = response.json()

            # Update the last post attributes
            self.last_uri = res['uri']
            self.last_cid = res['cid']
            self.last_rev = res['commit']['rev']
        except Exception as e:
            raise Exception(f"Error, posting an image:  {e}")

        return res

    @_check_rate_limit
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

    @_check_rate_limit
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
        response = self.session.post(
            url=self.delete_url,
            json=like_data
        )
        self._update_limits(response)

        response.raise_for_status()
        res = response.json()
        return res

    @_check_rate_limit
    def mark_as_seen(self, uri: str = None, feed_context: str = None, **kwargs):
        """
        'app.bsky.feed.defs#blockedPost'
        """
        interaction_data = {
            'interactions': [
                {
                    'item': uri,
                    'event':'app.bsky.feed.defs#interactionSeen',
                    'feedContext': feed_context
                }
            ]
        }
        url_path = self.pds_url + '/xrpc/app.bsky.feed.sendInteractions'
        response = self.session.post(
            url=url_path,
            json=interaction_data
        )
        self._update_limits(response)

        response.raise_for_status()
        res = response.json()
        return res

    @_check_rate_limit
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
        try:
            response = self.session.post(url=self.delete_url, json=post_data)
            self._update_limits(response)

            response.raise_for_status()
            res = response.json()

        except Exception as e:
            raise Exception(f"Can not delete the post:  {e}")
        return res

    @_check_rate_limit
    def thread(self, posts_texts: list):
        """ A trill of posts.
        posts_texts: list of strings
        :return Nothing
        """
        # Create a first ('root') post.
        post_text = posts_texts.pop(0)
        self.post(text=post_text)
        root_post = {'uri': self.last_uri, 'cid': self.last_cid}

        for post_text in posts_texts:
            sleep(1)
            kwargs = self._reply_kwargs(
                root_post=root_post,
                parent_post={'uri': self.last_uri, 'cid': self.last_cid},
                text=post_text)
            self._post(**kwargs)

    def thread_of_images(self, paths_and_texts: list):
        """
            A trill of posts.
        """

        root_image = paths_and_texts.pop(0)
        self.upload_image(file_path=root_image['path'])
        self.post_image(text=root_image['text'], blob=self.last_blob, alt_text=root_image['alt_text'])
        first_uri = self.last_uri
        first_cid = self.last_cid
        first_rev = self.last_rev

        for path_and_text in paths_and_texts:
            self.upload_image(file_path=path_and_text['path'])
            sleep(1)
            reply = {
                'root': {
                    'uri': first_uri,
                    'cid': first_cid
                },
                'parent': {
                    'uri': self.last_uri,
                    'cid': self.last_cid
                }
            }
            self.post_image(
                text=path_and_text.get('text', ''),
                blob=self.last_blob,
                alt_text=path_and_text.get('alt_text', 'No alternative text was provided'),
                reply=reply)

    def last_100_posts(self, repo: str = None, **kwargs):
        """

        :param repo:
        :param kwargs:
        :return:
        """
        response = self.session.get(
            url=self.pds_url + '/xrpc/com.atproto.repo.listRecords',
            params={
                'repo': repo if repo else self.did,  # self if not given.
                'limit': 100,
                'reverse': False  # Last post first in the list
            }
        )
        # read the returned limits left.
        self._update_limits(response)

        response.raise_for_status()

        return response.json()

    @_check_rate_limit
    def read_post(self, uri: str = None, actor: str = None, rkey: str = None, **kwargs):
        """ Read a post with given uri in a given repo.
            Defaults to own repo.
        """
        if not rkey:
            actor, rkey = split_uri(uri)
            # rkey = uri.split("/")[-1]  # is the last part of the URI
        response = self.session.get(
            url=self.pds_url + '/xrpc/com.atproto.repo.getRecord',
            params={
                'repo': actor if actor else self.did,  # self if not given.
                'collection': 'app.bsky.feed.post',
                'rkey': rkey
            }
        )
        self._update_limits(response)
        response.raise_for_status()
        return response.json()

    @_check_rate_limit
    def read_thread(self, uri: str, url: str = None, **kwargs):
        """
        Read the whole thread of a post with given uri in a given repo. Defaults to own repo.
        """
        if not uri:
            uri = self.uri_from_url(url=url)
        response = self.session.get(
            url=self.pds_url + '/xrpc/app.bsky.feed.getPostThread',
            params={
                'uri': uri,  # self if not given.
                'depth': kwargs.get('depth', 10),  # kwv or 10
                'parentHeight': kwargs.get('parent_height', 100),  # kwv or 100
            }
        )
        self._update_limits(response)
        response.raise_for_status()

        result = response.json()
        thread = result.get('thread', '')
        #   threadgate = result.get('threadgate', None)  # typically not there.

        return thread

    def _get_profile(self, at_identifier: str = None, **kwargs):
        """
        Get profile of a given actor. Defaults to actor's own.
        """
        response = self.session.get(
            url=self.pds_url + '/xrpc/app.bsky.actor.getProfile',
            params={'actor': at_identifier if at_identifier else self.handle}
        )
        response.raise_for_status()
        return response.json()

    def uri_from_url(self, url: str, **kwargs):
        # chunks = url.split("/")
        # rkey = chunks[-1]
        # handle = chunks[-3]
        handle, rkey = split_uri(url)
        hshe = self._get_profile(at_identifier=handle)
        return f'at://{hshe["did"]}/app.bsky.feed.post/{rkey}'

    def url_from_uri(self, uri: str, **kwargs):
        # chunks = uri.split("/")
        # rkey = chunks[-1]
        # did = chunks[-3]
        did, rkey = split_uri(uri)
        hshe = self._get_profile(at_identifier=did)
        return f'https://bsky.app/profile/{hshe["handle"]}/post/{rkey}'

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

    def feed(self, feed_uri: str = None, max_results: int = 100, **kwargs):
        def fetch_feed(cursor: str = None, **kwargs):
            response = self.session.get(
                url=self.pds_url + '/xrpc/app.bsky.feed.getFeed',
                params={
                    'feed': feed_uri,
                    'limit': 50,
                    'cursor': cursor}
            )
            response.raise_for_status()
            return response.json()

        records = self._read_long_list(
            fetcher=fetch_feed,
            parameter='feed',
            max_results=max_results
        )
        return records

    @_check_rate_limit
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

    @_check_rate_limit
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

    @_check_rate_limit
    def get_lists(self, actor: str = None, **kwargs):
        self.lists = self._records(actor=actor, collection='app.bsky.graph.list')
        return self.lists

    @_check_rate_limit
    def mute(self, mute_actor: str = None, **kwargs):
        """
        Mutes the specified actor.
        """
        response = self.session.post(
            url=self.pds_url + '/xrpc/app.bsky.graph.muteActor',
            json={'actor': mute_actor if mute_actor else self.test_actor},  # mute_data
        )
        self._update_limits(response)
        # doesn't return anything besides the code
        response.raise_for_status()

    @_check_rate_limit
    def unmute(self, unmute_actor: str = None, **kwargs):
        """ Unmutes the specified actor.
        """
        response = self.session.post(
            url=self.pds_url + '/xrpc/app.bsky.graph.unmuteActor',
            json={'actor': unmute_actor if unmute_actor else self.test_actor},
        )
        self._update_limits(response)

        response.raise_for_status()
        return response  # this is for the __init__ check of JWT

    @_check_rate_limit
    def get_mutes(self, max_results: int = 10000, **kwargs):
        """
        """
        def fetch_mutes(cursor: str = None, **kwargs):
            response = self.session.get(
                url=self.pds_url + '/xrpc/app.bsky.graph.getMutes',
                params={'cursor': cursor}
            )
            self._update_limits(response)

            response.raise_for_status()
            return response.json()

        search_results = self._read_long_list(
            fetcher=fetch_mutes,
            parameter='mutes',
            max_results=max_results
        )

        return search_results

    @_check_rate_limit
    def mute_thread(self, thread: str = None, **kwargs):
        """
        Mutes the specified actor.
        """
        response = self.session.post(
            url=self.pds_url + '/xrpc/app.bsky.graph.muteThread',
            json={'root': thread},  # mute_data
        )
        self._update_limits(response)
        # doesn't return anything besides the code
        response.raise_for_status()

    @_check_rate_limit
    def unmute_thread(self, mute_thread: str = None, **kwargs):
        """
        Mutes the specified actor.
        """
        response = self.session.post(
            url=self.pds_url + '/xrpc/app.bsky.graph.unmuteThread',
            json={'root': mute_thread},  # mute_data
        )
        self._update_limits(response)
        # doesn't return anything besides the code
        response.raise_for_status()

    def _read_long_list(self, fetcher, parameter, max_results: int = 1000, **kwargs):
        """ Iterative requests with queries

        :param requestor: function that makes queries
        :param parameter:
        :return:
        """
        long_list = []
        cursor = None
        while True:
            if not self._rate_limited(**kwargs):
                try:
                    response = fetcher(cursor=cursor)
                except Exception as e:
                    raise Exception(f"Error in reading paginated list,  {e}")
                long_list.extend(response[parameter])
                if len(long_list) >= max_results:
                    break
                cursor = response.get('cursor', None)
                if not cursor:
                    break
            else:
                break

        return long_list

    def _records(self, actor: str = None, collection: str = None, max_results: int = 1000, **kwargs):
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

        records = self._read_long_list(
            fetcher=fetch_records,
            parameter='records',
            max_results=max_results
        )
        return records

    @_check_rate_limit
    def describe(self, actor: str = None, **kwargs):
        """
        """
        response = self.session.get(
            url=self.pds_url + '/xrpc/com.atproto.repo.describeRepo',
            params={'repo': actor if actor else self.did},
        )
        response.raise_for_status()
        return response.json()

    @_check_rate_limit
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
        self._update_limits(response)

        response.raise_for_status()
        return response.json()

    def list_members(self, uri: str = None, **kwargs):
        def fetch_members(cursor: str = None, **kwargs):
            response = self.session.get(
                url=self.list_url,
                params={
                    'list': uri,
                    'limit': 100,
                    'cursor': cursor}
            )
            response.raise_for_status()
            return response.json()

        members = self._read_long_list(
            fetcher=fetch_members,
            parameter='items')

        return members

    @_check_rate_limit
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
        self._update_limits(response)

        response.raise_for_status()
        return response.json()

    @_check_rate_limit
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
        self._update_limits(response)

        response.raise_for_status()
        return response.json()

    @_check_rate_limit
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
        self._update_limits(response)

        response.raise_for_status()

        return response.json()

    def list_feed(self, list_uri: str = None, **kwargs):
        """
        """
        def fetch_feed_posts(cursor: str = None, **kwargs):
            response = self.session.get(
                url=self.pds_url + '/xrpc/app.bsky.feed.getListFeed',
                params={
                    'list': list_uri,
                    'limit': 100,
                    'cursor': cursor}
            )
            self._update_limits(response)

            response.raise_for_status()
            return response.json()

        list_feed = self._read_long_list(
            fetcher=fetch_feed_posts,
            parameter='feed')

        return list_feed

    @_check_rate_limit
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
        self._update_limits(response)
        response.raise_for_status()
        return response.json()

    @_check_rate_limit
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
        self._update_limits(response)

        response.raise_for_status()
        return response.json()

    @_check_rate_limit
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
        self._update_limits(response)
        response.raise_for_status()

        return response.json()

    @_check_rate_limit
    def get_blocks(self, max_results: int = 10000, **kwargs):
        """
        """
        def fetch_blocks(cursor: str = None, **kwargs):
            response = self.session.get(
                url=self.pds_url + '/xrpc/app.bsky.graph.getBlocks',
                params={'cursor': cursor}
            )
            self._update_limits(response)

            response.raise_for_status()
            return response.json()

        search_results = self._read_long_list(
            fetcher=fetch_blocks,
            parameter='blocks',
            max_results=max_results
        )

        return search_results

    @_check_rate_limit
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
        self._update_limits(response)

        response.raise_for_status()
        return response.json()

    @_check_rate_limit
    def _unfollow_uri(self, uri: str = None, record_key: str = None, **kwargs):
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
        self._update_limits(response)

        response.raise_for_status()

        return response.json()

    @_check_rate_limit
    def unfollow(self, actor: str = None, records: list = None, **kwargs):
        """
        Unfollows the actor specified in the record.
        """
        if not records:
            records = self._records(actor=self.did, collection='app.bsky.graph.follow', max_results=10000)

        uri = None
        for record in records:
            if record['value']['subject'] == actor:
                uri = record['uri']
                break
        if uri:
            result = self._unfollow_uri(uri=uri)
        else:
            raise Exception('Actor has not been followed.')

        return result, records

    @_check_rate_limit
    def search_100_posts(self, query: dict):
        """
        Search for the first not more than 100 posts (because the paginated search is prohibited by Bluesky).

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
        header = {

        }

        response = self.session.get(
                url=self.pds_url + '/xrpc/app.bsky.feed.searchPosts',
                params=query
        )
        self._update_limits(response)

        response.raise_for_status()
        posts = response.json()['posts']
        return posts

    # limits are checked in the _real_long_list
    def search_posts(self, query: dict, max_results: int = 100):
        """
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

            cursor: string (optional)Optional pagination mechanism; may not necessarily allow scrolling through entire result set.

            Some recommendations can be found here: https://bsky.social/about/blog/05-31-2024-search
        """

        def fetch_posts(cursor: str = None, **kwargs):
            response = self.session.get(
                url=self.pds_url + '/xrpc/app.bsky.feed.searchPosts',
                params=query | {'cursor': cursor}
            )
            self._update_limits(response)

            response.raise_for_status()
            return response.json()

        search_results = self._read_long_list(
            fetcher=fetch_posts,
            parameter='posts',
            max_results=max_results
        )

        return search_results

    @_check_rate_limit
    def permissions(self, uri: str = None, **kwargs):
        """ Check the permissions of a thread.
        :param uri:
        :param kwargs:
        :return:
        """
        response = self.session.get(
            url=self.pds_url + '/xrpc/com.atproto.repo.listRecords',
            params={
                'repo': self.did,
                'collection': 'app.bsky.feed.threadgate',}
        )
        self._update_limits(response)

        response.raise_for_status()
        return response.json()

    @_check_rate_limit
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
        self._update_limits(response)

        response.raise_for_status()
        return response.json()

    @_check_rate_limit
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
            self._update_limits(response)

            response.raise_for_status()

        except Exception as e:
            raise Exception(f"Can not delete the restriction:  {e}")

        return response.json()


if __name__ == "__main__":
    """ Quick tests were here.
    """
    pass
    ...

