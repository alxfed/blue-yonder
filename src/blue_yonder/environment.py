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


def search_posts(query: dict):
    """
    Search for posts. Parameters:

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
    response = requests.get(
        url=APP_VIEW_API + '/xrpc/app.bsky.feed.searchPosts',
        params=query
    )
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    # list = [
    #     'did:plc:x7lte36djjyhereki5avyst7',
    #     'machina-ratiocinatrix.github.io'
    # ]
    # profiles = get_profiles(list)
    # now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    query = {
        'q': 'Dvoretzky',
        'sort': 'latest',
        'since': '2024-06-08T21:44:46Z',
        'until': '2024-12-08T21:44:46Z',
        'author': 'did:plc:x7lte36djjyhereki5avyst7',
        'limit': 100
    }
    posts = search_posts(query)
    ...