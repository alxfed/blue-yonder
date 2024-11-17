# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from datetime import datetime, timezone
from os import getenv
from atproto import Client, models, client_utils


class Bird(Client):
    """
        The Bird is a 'client' of the blue sky,
        if flew into the wild blue yonder.
    """

    def __init__(self, bluesky_handle: str, bluesky_password: str, **kwargs):
        """
            Launch the Bird!

        :param bluesky_handle:
        :param bluesky_password:
        :param kwargs:
        """

        # if you have a Private Data Server specify it as a pds_url kw argument
        # otherwise it will use https://bsky.social
        self.pds_url = kwargs.get('pds_url', 'https://bsky.social')

        # Ask for a permission to fly in the wild blue yonder.
        try:
            # Initiate the Client class.
            super().__init__(base_url=self.pds_url)
            # Create a session of the Client class, then use all the methods of it.
            self.login(login=bluesky_handle, password=bluesky_password)
        except Exception as e:
            print(e)

    def chirp(self, text: str):
        """
            Chirp your message to the world.

        :param text:
        :return:
        """
        text_builder = client_utils.TextBuilder().text(text)

        try:
            result = self.send_post(text=text_builder)
        except Exception as e:
            raise Exception(f"Error, with talking to Huston:  {e}")
        return result

    def trill(self, chirps_text: list):
        """
            A trill of chirps.

        :param chirps:
        :return:
        """
        root = None
        last_uri = None
        last_cid = None
        last_rev = None

        chirp_text = chirps_text.pop(0)

        result = self.chirp(text=chirp_text)
        root = models.create_strong_ref(result)
        parent = root
        for chirp in chirps_text:
            reply = self.send_post(
                text=chirp,
                reply_to=models.AppBskyFeedPost.ReplyRef(
                    parent=parent,
                    root=root
                )
            )
            parent = models.create_strong_ref(reply)

    def listen_to_another(self, other_bird_handle: str):
        """
            Listen to another bird.

        :return:
        """
        # TODO: implement the listen method
        pass

    def chirp_back(self, root_chirp: dict, chirp: dict, text: str):
        """
            Chirp back.

        :param root_chirp:
        :param chirp:
        :param text:
        :return:
        """
        # TODO: implement the chirp_back method
        pass


if __name__ == "__main__":
    # kwargs = {
    #     'pds_url': 'https://bsky.social'
    # }
    bluebird = Bird(
        bluesky_handle=getenv('BLUESKY_HANDLE'),
        bluesky_password=getenv('BLUESKY_PASSWORD')
    )
    chirps = ['This is a first chirp of this trill...',
              'This is a second chirp of the trill...',
              'This is a third chirp of the trill...',
              'This is the end of the trill.']
    result = bluebird.trill(chirps_text=chirps)
    ...
