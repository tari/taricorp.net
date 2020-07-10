---
author: tari
comments: true
date: 2014-03-28 20:55:01+00:00
slug: reverse-engineering-renpy-packages
title: Reverse-engineering Ren'py packages
wordpress_id: 997
categories:
- Hacking/Tweaking
- Software
tags:
- python
- ren'py
- reverse engineering
- visual novels
---

Some time ago (September 3, 2013, apparently), I had just finished reading
[Analogue: A Hate Story](http://ahatestory.com/) (which I highly recommend, by
the way) and was particularly taken with the art. At that point it seems my
engineer's instincts kicked in and it seemed reasonable to reverse-engineer the
resource archives to extract the art for my own nefarious purposes.

<figure class="figure-right">
    <a href="/images/2014/analogue-achievements.jpg">
        <img src="/images/2014/analogue-achievements.jpg" alt="" />
    </a>
    <figcaption>
        Yeah, I really got into Analogue. That's all of the achievements.
    </figcaption>
</figure>

A little examination of the game files revealed a convenient truth: it was built
with [Ren'Py](http://www.renpy.org/), a (open-source) [visual
novel](https://en.wikipedia.org/wiki/Visual_novel) engine written in Python.
Python is a language I'm quite familiar with, so the actual task promised to be
well within my expertise.

## Code

Long story short, I've build some rudimentary tools for working with compiled
Ren'py data. You can get it from my [repository on
BitBucket](https://bitbucket.org/tari/renpy-rv). Technically-inclined readers
might also want to follow along in the code while reading.

## Background

There are a large number of games designed with Ren'py. It's an easy tool to get
started with and hack on, since the script language is fairly simple and because
it's open-source, more sophisticated users are free to bend it to their will. A
few examples of (in my opinion) high-quality things built with the engine:

  * [Long Live the Queen](http://hanakogames.com/llq.shtml)
  * [Analogue: A Hate Story](http://ahatestory.com/) and [Hate Plus](http://hateplus.com/)
  * [Dysfunctional Systems](http://www.dysfunctionalsystems.com/): Learning to Manage Chaos (and the [planned sequels](https://www.kickstarter.com/projects/dischan/dysfunctional-systems/))
  * [Katawa Shoujo](http://www.katawa-shoujo.com/)

Since visual novels tend to live or die on the combination of art and writing,
the ability to examine the assets outside the game environment offers
interesting possibilities.

Since it was handy, I started my experimentation with Analogue.

<!-- more -->

## RPA resource archives

The largest files distributed with the game were `.rpa` files, so I investigated
those first for finding art. As it turned out, this was exactly the place I
needed to look. Start by examining the raw data:

```sh
$ cd "Analogue A Hate Story/game"
$ ls
bytecode.rpyb
data.rpa
dlc1.rpa
nd.rpa
$ less data.rpa
RPA-3.0 00000000035f5c75 414154bb
<F0><AA><D6>^MީZ<A0><90><FB>^M6<B9><B7>^X<A3><82><F3>F<B0><DF>k8(<BF>ߦx<9C><D5>T
[snip]
```

There's an obvious file identifier (`RPA-3.0`), followed by a couple numbers and
a lot of compressed-looking data. The first number turns out to be very close to
the total file size, so it's probably some size or offset field, while the other
one looks like some kind of signature.

```sh
$ python -c 'print(0x35f5c75)'
56581237
$ stat -c %s data.rpa
56592058
```

At this point I simply referred to the Ren'Py source code, rather than waste
time experimenting on the data itself. Turns out the first number is the file
offset of the index, and the second one is a key used for simple obfuscation of
elements of the index (numbers are bitwise exclusive-or'd with the key). The
archive index itself is a
[DEFLATE](https://en.wikipedia.org/wiki/DEFLATE)-compressed block of
[pickled](https://docs.python.org/2/library/pickle.html) Python objects. The
index maps file names to tuples of offset and block length specifying where
within the archive file the data can be found.

With that knowledge in hand, it's short work to build a decoder for the index
data and dump it all to files. This is `rpa.py` in my tools. Extracting the
archives pulls out plenty of images and other media, as well as a number of
interesting-looking `.rpyb` files, which we'll discuss shortly.

### Cosplay

For a bit of amusement, I exercised my web-programming chops a little and built
a standalone web page for playing with the extracted costumes and expressions of
\*Hyun-ae and \*Mute, which I've included below. [Here's a
link](/images/2014/analogue/index.html) to the bare page for standalone
amusement as well.

<iframe style="min-height: 400px; max-height: 35em; height: 600px;"
        src="/images/2014/analogue/index.html">
</iframe>

## Script guts

The basic format of compiled scripts (`.rpyb` files) is similar to that of
resource packages. The entire thing is a tuple of `(data, statements)`, where
`data` is a dictionary of basic metadata and `statements` is a list of objects
representing the script's code.

The statements in this are just the Ren'py abstract syntax tree, so all the
objects come from the `renpy.ast` module. Unfortunately and as I'll discuss
later, the pickle format makes this representation hard to work with.

The structure of AST members is designed such that each object can have attached
bytecode. In practice this appears to never happen in archives. In my
investigations of the source, it appears that Ren'py only writes Python bytecode
as a performance enhancement, and most of it ends up in `bytecode.rpyb`. That
file appears to provide some sort of bytecode cache that overrides script files
in certain situations. For the purposes of reverse-engineering this is
fortunate-- Python bytecode is documented, but rather more difficult to
translate into something human-readable than the source code that is actually
present in RPYB archives.

Here's some of the Act 1 script from Analogue run through the current version of
my script decompiler:

```
## BEGIN Label 'dont_understand', params=None, hide=False
dont_understand:
    ## <class 'renpy.ast.Show'> -- don't know how to dump this!
    ## <class 'renpy.ast.Say'> -- don't know how to dump this!
    ## <class 'renpy.ast.Jump'> -- don't know how to dump this!
## BEGIN Label 'nothing', params=None, hide=False
nothing:
    python:
        shown_message = None

        for block in store.blocks:
            for message in block.contents:
                if message == _message:
                    shown_message = str(store.blocks.index(block)+1) + "-" + str(block.contents.index(message)+1)

        if shown_message:
            gray_out(shown_message)
    ## <class 'renpy.ast.With'> -- don't know how to dump this!
    ## <class 'renpy.ast.Show'> -- don't know how to dump this!
    ## <class 'renpy.ast.With'> -- don't know how to dump this!
    ## <class 'renpy.ast.Say'> -- don't know how to dump this!
```

Clearly there are a few things my decompiler needs to learn about. It does,
however, handle the more common block elements such as If statements. In any
case, the Python code embedded in these scripts tends to be more interesting
than the rest (which are mostly just dialogue and display manipulation) for the
purposes of reverse-engineering. If you're more interested in spoiling the game
for yourself, it's not as useful.

A few telling bits of logic from options.rpy:

```
init -3:
    ## BEGIN Python
    python hide:
        ## BEGIN PyCode, exec mode, from game/options.rpy
        renpy.demo_mode = True
init -1:
    ## BEGIN Python
    python hide:
        ## BEGIN PyCode, exec mode, from game/options.rpy
        config.developer = True




        config.screen_width = 1024
        if persistent.resolution == None:
            persistent.resolution = 2 
        if persistent.old_resolution == None:
            persistent.old_resolution = persistent.resolution

        if not persistent.resolution:
            config.screen_height = 600
        else:
            config.screen_height = 640

        if renpy.demo_mode:
            config.window_title = u"Analogue trial"
        else:
            config.window_title = u"Analogue: A Hate Story"

        config.name = "Analogue"
        config.version = "0.0"
```

The spacing here is interesting; I suspect (but haven't attempted to verify)
that the Ren'py script compiler strips comments since there haven't been any in
all of the scripts I've examined, so it's likely that the unusual empty blocks
in the code were comment blocks in a former life.

I've yet to dig much into what determines when `demo_mode` is set, but I doubt
it would be difficult to forcibly set (or clear) if one were so inclined. Not
that I condone such an action..

A little bit of interesting game-critical logic, also from Analogue (**caution:
minor spoilers**)

```python
store.radiation = 0
store.reactor_enabled = True
def interact_cb():
    if store.radiation and store.reactor_enabled:
        store.radiation_levels += 0.01

        if (any_read("7-*") or (store.current_character == "mute" and get_m("6-9").enabled)) and store.radiation_levels < 0.65:
            store.radiation_levels = 0.65

            store.radiation_levels = min (store.radiation_levels, 0.8)

config.interact_callbacks.append(interact_cb)
```

You can get some idea of how specialized Ren'py's execution environment is from
this code. Particularly, `store` is a magic value injected into the locals of
Python script blocks which maps to the RPY persistent variable store, which
stores most of the game state. `config` is a similar magic value providing a
handle to the engine configuration.

In this instance, `radiation` refers to a sort of hidden timer which forces the
player to solve a puzzle on expiration (assuming the preconditions have been
met), then make a decision which causes the plot to fork depending on that
decision. Elsewhere in the code, I found a few developer switches which allow
one to display the value of this countdown and reset or force it.

## Conclusions

As the [official
documentation](http://www.renpy.org/doc/html/build.html#archives) notes, the
process of resource compilation is not very secure but is enough to deter casual
copying. I've shown here that such a claim is entirely correct, though script
decompilation may be somewhat harder than the developers envisioned due to the
choice of pickle as a serialization format.

It's nothing particularly new to me, but a reminder to designers of software: if
it runs on your attacker's system, it can be hacked. It's not a question of
"if", but instead "how fast". I was mostly interested in extracting resources
with this project, which was quite easy. In that matter, I think the designers
of Ren'Py made a good design decision. The compiled archives and scripts are
much more robust against accidental modification in the face of curious users
than not compiling anything, but the developers do not expend undue effort
building something harder to break which would eventually be broken anyway by a
sufficiently determined attacker.

### Portability

As I alluded to earlier, the pickle representation makes the Ren'Py AST hard to
work with. This is because many of the objects contain references to the engine
state, which in turn implies most of the engine needs to be initialized when
unpickling the AST. To say the least, this is not easy- engine initialization is
not easily separated from game startup.

To illustrate the problem, observe that the Ren'Py developer kit is simply the
engine itself packaged with a game of sorts that provides help in getting a new
project set up by modifying the included scripts. There simply seems to be no
part of the engine that is designed to run without the rest of it running as
well.

In experimenting with different products built with Ren'Py, I've had to make
changes to some combination of the engine itself and my code in order to
bootstrap the engine state to a point where the AST can be successfully
unpickled. Suffice to say, this has hampered my progress somewhat, and led me to
consider slightly different avenues of attack.

The most promising of these would involve a semi-custom unpickler which avoids
instantiating actual Ren'Py objects; the only data that need be preserved is the
structural information, rather than the many hooks into engine state that are
also included in the pickle serialization. Further continuation of this project
is likely to take this approach to deserialization.

