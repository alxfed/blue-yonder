# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from blue_yonder.utilities import split_url, split_uri
from blue_yonder import Actor, Another

external_link_post_text = 'I created this template repository with the help of `blue_yonder` package.'
THUMBNAIL_FILE  = './images/butterfly_big.jpg'
MIME_TYPE       = 'image/jpeg'
image_alt_text  = 'This is an image of a butterfly.'
title           = 'Butterfly'
description     = """Butterfly is a template repository with examples of how to use `blue_yonder`
package. It is a collection of Python scripts for the Bluesky social network. """
url             = 'https://github.com/alxfed/butterfly'


my_actor = Actor()

# height = 1707, width = 2560, jpeg, size = 654769 # not necessary for a thumbnail !!!
# url = 'https://github.com/alxfed/butterfly'

uploaded_blob = my_actor.upload_image(file_path=THUMBNAIL_FILE, mime_type=MIME_TYPE)

# Post a post with an embedded image
post_with_image = my_actor.post_external(
    url=url,                        # required, url of the external page;
    text=external_link_post_text,   # required, pass an empty string '' if not needed;
    title=title,                    # required, non-empty string;
    description=description,        # required, non-empty string;
    thumb=uploaded_blob             # optional, don't pass this parameter if not needed.
)
...