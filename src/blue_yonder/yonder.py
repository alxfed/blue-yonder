# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder.utilities import read_long_list
import requests


APP_VIEW_API = 'https://public.api.bsky.app'


def get_profiles(actors: list):
    """
    Retrieves the profiles of the list of actors.

    :param actors: list of at-identifiers (dids or handles).
    :return: list of profiles
    """
    if len(actors) <= 25:
        response = requests.get(
            url=APP_VIEW_API + '/xrpc/app.bsky.actor.getProfiles',
            params={'actors': actors}
        )
        response.raise_for_status()
        return response.json()['profiles']
    else:
        raise Exception('Too many actors.')


def get_feed_generator(uri: str = None):
    response = requests.get(
        url=APP_VIEW_API + '/xrpc/app.bsky.feed.getFeedGenerator',
        params={'feed': uri}
    )
    response.raise_for_status()
    return response.json()


def get_feed_skeleton(uri: str = None):
    response = requests.get(
        url=APP_VIEW_API + '/xrpc/app.bsky.feed.getFeedSkeleton',
        params={
            'feed': uri,
            'limit': 50,
            'cursor': None
        }
    )
    response.raise_for_status()
    return response.json()


def feed(uri: str = None, max_results: int = 100, **kwargs):
    """
    feedContext:
        t-nature
        t-science
        t-tv
        t-music
        nettop
    """
    def fetch_feed(cursor: str = None, **kwargs):
        response = requests.get(
            url=APP_VIEW_API + '/xrpc/app.bsky.feed.getFeed',
            params={
                'feed': uri,
                'limit': 50,
                'cursor': cursor
            }
        )
        response.raise_for_status()
        return response.json()

    records = read_long_list(
        fetcher=fetch_feed,
        parameter='feed',
        max_results=max_results
    )
    return records


def list_feed(list_uri: str = None, max_results: int = 100, **kwargs):
    """
    feedContext:
        t-nature
        t-science
        t-tv
        t-music
        nettop
    """
    def fetch_list_feed(cursor: str = None, **kwargs):
        response = requests.get(
            url=APP_VIEW_API + '/xrpc/app.bsky.feed.getListFeed',
            params={
                'list': list_uri,
                'limit': 50,
                'cursor': cursor
            }
        )
        response.raise_for_status()
        return response.json()

    records = read_long_list(
        fetcher=fetch_list_feed,
        parameter='feed',
        max_results=max_results
    )
    return records


def search_actors(query: dict, max_results: int = 100, **kwargs):
    """ Search for actors. Parameters:

        q: string (required) Search query string; syntax, phrase, boolean, and faceting is unspecified, but Lucene query syntax is recommended.

        limit: integer (optional) Possible values: >= 1 and <= 100. Default value: 25

        cursor: string (optional)Optional pagination mechanism; may not necessarily allow scrolling through entire result set.

        Some recommendations can be found here: https://bsky.social/about/blog/05-31-2024-search
    """
    def fetch_actors(cursor: str = None, **kwargs):
        response = requests.get(
            url=APP_VIEW_API + '/xrpc/app.bsky.actor.searchActors',
            params={
                'q': query['q'],
                'limit': query['limit'],
                'cursor': cursor}
        )
        response.raise_for_status()
        return response.json()

    actors = read_long_list(
        fetcher=fetch_actors,
        parameter='actors',
        max_results=max_results
    )
    return actors


if __name__ == '__main__':
    # Quick tests
    actors = search_actors(query={'q': 'AI', 'limit': 50}, max_results=1000)
    ...
    uri = 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot'
    feed = feed(uri=uri, max_results=1000)
    # getFeedreturns
    list_of_dictionaries   = feed['feed']
    cursor                 = feed['cursor']  # str
    # Every post dictionary consists of
    feedContext = list_of_dictionaries[0]['feedContext']
    post        = list_of_dictionaries[0]['post']
    # Every post dictionary contains:
    uri   = post['uri']
    cid   = post['cid']
    author  = post['author']
    record  = post['record']
    # Record consists of
    text    = record['text']
    # other fields of a post...
    embed   = post['embed']
    labels  = post['labels']
    threadgate = post['threadgate']
    ...