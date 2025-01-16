# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""

from blue_yonder import Actor

"""post record currently can contain:
    images (app.bsky.embed.images)
    external link (app.bsky.embed.external)
    record - for instance a quote post (app.bsky.embed.record)
    record alongside some media like images (app.bsky.embed.recordWithMedia)
"""
post = 'https://bsky.app/profile/alxfed.bsky.social/post/3lec2nfhxdk24'
post_for_embed = 'https://bsky.app/profile/multilogue.bsky.social/post/3lfngdvswe725'
post_with_media = 'https://bsky.app/profile/alxfed.bsky.social/post/3ldceovs2hs2x'
link_to_external_page = 'https://www.noemamag.com/artificial-general-intelligence-is-already-here/'
images = [
    {'text': '', 'path': './images/page_001.png', 'alt_text': 'Page 1'},
    {'text': '', 'path': './images/page_002.png', 'alt_text': 'Page 2'},
    {'text': '', 'path': './images/page_003.png', 'alt_text': 'Page 3'},
]
reply = 'This is a reply to the complex reply post with embedded content'
external_link_post_text = 'I created this template repository with the help of `blue_yonder` package.'
THUMBNAIL_FILE  = './images/butterfly_big.jpg'
MIME_TYPE       = 'image/jpeg'
image_alt_text  = 'This is an image of a butterfly.'
title           = 'Butterfly'
description     = """Butterfly is a template repository with examples of how to use `blue_yonder`
package. It is a collection of Python scripts for the Bluesky social network. """
url             = 'https://github.com/alxfed/butterfly'
# height = 1707, width = 2560, jpeg, size = 654769 # not necessary for a thumbnail !!!
# url = 'https://github.com/alxfed/butterfly'



def main():
    my_actor = Actor()
    new_post = (
        my_actor.in_reply_to(post)
        .with_embedded(         # !!! Comment out all except the one you need !!!
            # post_for_embed,     # url of the post on Bluesky to embed
            ### post_with_media,    # (useless right now because there are no other media types besides images);
            # image,              # url of an image to embed, alt text optional
            # images,             # list of images with alt texts
            # link_to_external_page, # url of the external link, along with the 'site card' info.
        )
        .post(reply)
    )
    return new_post


if __name__ == '__main__':
    main()
    ...