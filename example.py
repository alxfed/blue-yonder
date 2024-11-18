# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from os import getenv
from blue_yonder import Bird


def chunk_text(text, max_length=297):
    """
    Split a long text into chunks of maximum length without splitting words.

    Args:
        text (str): The input text.
        max_length (int): The maximum length of each chunk. Defaults to 297.

    Returns:
        list: A list of text chunks.
    """
    chunks = []
    current_chunk = ""

    for word in text.split():
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk += word + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word + " "

    if current_chunk:
        chunks.append(current_chunk.strip()+'...')

    return chunks


if __name__ == "__main__":
    long_text = """Idea
	As the topical analysis or outline in each chapter indicates, the great ideas are not simple objects of thought. Each of the great ideas seems to have a complex interior structure - an order of parts involving related meanings and diverse positions which, when they are opposed to one another, determine the basic issues in that area of thought.
	The great ideas are also the conceptions by which we think about things. They are the terms in which we state fundamental problems; they are the notions we employ in defining issues and discussing them. They represent the principal content of our thought. They are what we think as well as what we think about.
	If, in addition to its objects and content, we wish to think about thought itself - its acts or processes - we shall find in the tradition of the great books a number of related terms which indicate the scope of such inquiry. Some of them are: idea, judgment, understanding, and reasoning; perception, memory, and imagination; sense and mind. Here we are concerned with one of these - the idea IDEA. It is probably the most elementary of all these related terms, for according to different conceptions of the nature and origin of ideas, the analysis of thought and knowledge will vary. Different positions will be taken concerning the faculties by which men know, the acts and processes of thinking, and the limits of human understanding.
    """

    chirps = chunk_text(long_text)

    bluebird = Bird(
        bluesky_handle=getenv('BLUESKY_HANDLE'),
        bluesky_password=getenv('BLUESKY_PASSWORD')
    )

    result = bluebird.trill(chirps_text=chirps)
    ...