# Blue Yonder
This is a Bluesky Python API for humans. It can be used for the simple automations that you _know_ should be implemented, but they are just 'not there' in a pretty annoying way. But you know how to program in Python... And you have an IDE like PyCharm(R) or VSCode...

Or, maybe, you are experimenting with Language Models and would like to see how _they_ will make your 'social presense' less stressful and more meaningful but assessing whether the content that you are about to see is worth looking at or it is something that you will wish to 'unsee' later...

## Here comes the Blue Yonder Python package
It has been built with a perspective of a person who does not need the professional jargon of software engineers or 'coders'. The logged in entity that performs actions on your behalf in the Bluesky network - posts, replies, likes, follows, blocks, mutes,etc. is called... you guessed it right, an Actor (not a 'Client' or 'User', God forbid); the other entity whose profile or content are of interest for you and should be brought into focus is called... you guessed it right again - Another. The collection of functions that let you interact with the Bluesky network is called 'yonder', you can import it as a whole or just the functions that you need.

## Installation
```Bash
  pip install blue-yonder
```
Note: the pip package name has a dash `-` between the words.

Then:
```Python
# Python

from blue_yonder import Actor
```

## How to use it
I didn't want to overload this repository and library with examples; you can use the 'template repository' with multiple examples, that I considered to be useful for myself when I was studying the Bluesky API. It is located [here](https://github.com/alxfed/butterfly). Just click the 'Use this template' button at the top of that page and create your own repository in your account that you can edit and use the way you deem fit.