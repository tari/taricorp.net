---
author: tari
comments: true
date: 2012-01-25 04:39:19+00:00
slug: rtorrent-scripting-considered-harmful
title: rtorrent scripting considered harmful
wordpress_id: 495
categories:
- Software
tags:
- linux
- rtorrent
- Software
- storage
- tnadm
---

As best I can tell, whomever designed the scripting system for rtorrent did so
in a manner contrived to make it as hard to use as possible.  It seems that = is
the function application operator, and precedence is stated by using a few
levels of distinct escaping. For example:

    # Define a method 'tnadm_complete', which executes 'baz' if both 'foo' and 'bar' return true.
    system.method.insert=tnadm_complete,simple,branch={and="foo=,bar=",baz=}

With somewhat more sane design, it might look more like this:

    system.method.insert(tnadm_complete, simple, branch(and(foo(),bar()),baz()))

That still doesn't help the data-type ambiguity problems ('tnadm_complete' is a
string here, but not obviously so), but it's a bit better in readability. I
haven't tested whether the escaping with {} can be nested, but I'm not confident
that it can.

In any case, that's just a short rant since I just spent about two hours
wrapping my brain around it. Hopefully that work turns into some progress on a
new project concept, otherwise it was mostly a waste. As far as the divergence
meter goes, I'm currently debugging a lack of communication between my
in-circuit programmer and the microcontroller.

Incidentally, the [rtorrent community wiki](http://community.rutorrent.org/) is
a rather incomplete but still useful reference for this sort of thing, while
[gi-torrent](https://code.google.com/p/gi-torrent/wiki/rTorrent_XMLRPC_reference)
provides a reasonably-organized overview of the XMLRPC methods available (which
appear to be what the scripting exposes), and the [Arch
wiki](https://wiki.archlinux.org/index.php/RTorrent#Manage_completed_files) has
a few interesting examples.
