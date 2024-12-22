# Blue Yonder
This is a Bluesky Python API for humans. It can be used for the simple automations that you _know_ should be implemented, but they are just 'not there' in a pretty annoying way. But you know how to program in Python... And you have an IDE like PyCharm(R), VSCode or even Cursor or Windsurf...

<br>Or, maybe, you are experimenting with instructing Language Models and would like to see whether _they_ will make your 'social presence' less stressful and more meaningful by assessing whether the content that you are about to see is worth looking at or it is something that you will wish you would be able to 'unsee' later...

<br>Here comes the Blue Yonder Python package. It has been built with a perspective of a person who does not need (or want any of) the professional jargon of software engineers and 'coders'. The logged in entity that performs **actions** is called **Actor**; the **other** entity whose profile is brought into focus is called **Another**. It's that simple.

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
The Bluesky network creators were so busy with their own perception of their enterprise as 'an implementation of a protocol' that they didn't separate in their code and documentation the different logical levels of participation of entities in the network. In this package I tried to set apart the 'active participation' which consists of the actions (posts, uploads, likes, follows, blocks, mutes, etc.) by a (_logged in_) **Actor**... sorry for the reiteration of the 'act' root bounding with tautology... from the 'passive observation' of **Another** entity, its profile, posts, likes, followers, lists, feeds, etc. that can be done by a _not logged into the Bluesky and, hence, 'anonymous'_ computer with Internet connection. Besides that, on a yet another level, there are pure functions of the network/environment too - the search functions and other utilities of the environment, which I stored in the **yonder** module, where you can import them from as a whole or individually. The package is a work in progress and will keep changing without notice.
 
## How to use it
I didn't want to overload this repository and library, you can use the 'template repository' with multiple examples, that I considered to be useful for myself when I was studying the Bluesky API. It is located [here](https://github.com/wild-blue-yonder/butterflies). Just click the 'Use this template' button at the top of that page and create your own repository in your (or your organization) account that you can edit and use the way you deem fit. I will keep working on it too, so you can be sure that it will be updated as I make changes.