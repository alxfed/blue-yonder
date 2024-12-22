# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder import Actor, test_actor


TEXT1 = 'This is a post that will later have limited access'
TEXT2 = 'This is a reply with limited access to the post with limited access'


def main():
    # create an actor
    my_actor = Actor(bluesky_handle='multilogue.bsky.social')

    # post the text
    post = my_actor.post(text=TEXT1)

    # set rules
    """ Set the rules of interaction with a thread. List of up to 5 rules.
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

    rules1 = [
        {'$type': 'app.bsky.feed.threadgate#listRule',
         'list': 'at://did:plc:yjvzk3c3uanrlrsdm4uezjqi/app.bsky.graph.list/3lcxml5gmf32s'},
        {'$type': 'app.bsky.feed.threadgate#mentionRule'}
    ]
    # set permissions for the post created before.
    my_actor.restrict(uri=post['uri'], rules=rules1)

    # reply to the post
    reply = my_actor.reply(root_post=post, post=post, text=TEXT2)

    # restrict interactions with the reply
    rules2 = [
        {'$type': 'app.bsky.feed.threadgate#mentionRule'}
    ]
    my_actor.restrict(uri=reply['uri'], rules=rules2)

    # unrestrict interactions with the reply
    my_actor.unrestrict(uri=reply['uri'])

    # delete the reply
    my_actor.delete_post(uri=reply['uri'])
    print('reply deleted')

    # unrestrict interactions with the post
    my_actor.unrestrict(uri=post['uri'])

    # delete the post
    my_actor.delete_post(uri=post['uri'])
    print('post deleted... everything deleted.')


if __name__ == '__main__':
    main()
    ...