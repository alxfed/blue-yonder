# Blue Yonder
This is a Bluesky Python API for humans. It can be used for the simple automations that you _know_ should be implemented, but they are just 'not there' in a pretty annoying way. But you know how to program in Python... And you have an IDE like PyCharm(R), VSCode or even Cursor or Windsurf...

Or, maybe, you are experimenting with Language Models and would like to see how _they_ will make your 'social presence' less stressful and more meaningful but assessing whether the content that you are about to see is worth looking at or it is something that you will wish you would be able to 'unsee' later...

## Here comes the Blue Yonder Python package
It has been built with a perspective of a person who does not need (or want any of) the professional jargon of software engineers or 'coders'. The logged in entity that performs **actions** on your behalf in the Bluesky network - posts, replies, likes, follows, blocks, mutes,etc. is called... you guessed it right, an **Actor** (not a 'Client' or 'User', God forbid); the **other** entity whose profile or content are of interest for you and should be brought into focus is called... you guessed it right again - **Another**. The collection of functions that let you interact with the Bluesky network is called **yonder**, you can import it as a whole or just the functions that you need.

## Installation
```Bash
  pip install blue-yonder
```
Note: the pip package name has a dash `-` between the words.

Then:
```Python
# Python

from blue_yonder import Actor, Another
```

## The idea of this package
The Bluesky network creators were so busy with their own view of their enterprise as 'an implementation of a protocol' that they didn't separate in their code and documentation the different logical levels of participation of entities in their network. In this package I tried to set apart the 'active participation' which consists of the actions (posts, uploads, likes, follows, blocks, mutes, etc.) by a (logged in) **Actor**... sorry for the reiteration of the 'act' root bounding with tautology... from the 'passive observation' of **Another** entity, its profile, posts, likes, followers, lists, feeds, etc. that can be done by a not logged into the Bluesky and, hence, 'anonymous' computer on the Internet . Besides that, on a yet another level, there are pure functions of the network/environment too - the search functions, and other utilities of the environment, which I stored in the **yonder** module, where you can import them from as a whole or individually.
 
## How to use it
I didn't want to overload this repository and library with examples; you can use the 'template repository' with multiple examples, that I considered to be useful for myself when I was studying the Bluesky API. It is located [here](https://github.com/alxfed/butterfly). Just click the 'Use this template' button at the top of that page and create your own repository in your (or your organization) account that you can edit and use the way you deem fit.