---
layout: page
title: fb-hitler
date: 2010-04-13 14:33:37.000000000 -06:00
categories: []
tags: []
status: publish
type: page
published: true
---

<figure>
    <img src="/images/2010/windows_7.png" alt="XKCD's 'Windows 7'" />
</figure>

fb-hitler is a small Linux-based utility I wrote a while ago to mimic the
functionality of Windows 7 as envisioned by [Randall Monroe](http://xkcd.com/).
Hacked up in a weekend of feverish documentation lookup with a little actual
coding thrown in.

## What's it do?

fb-hitler just grabs hold of a framebuffer, displays a picture of Hitler, then
flashes a different image when it receives a SIGINT.  It was designed to run as
a replacement for `init`, but I suppose you could run it normally if you really
wanted (with some hacks, anyway).

## Where do I get it?

Get the latest version here: [fb-hitler-0.1.tar.gz][targz]

## Bugs

They're plentiful, this program being the first thing I ever really hacked up
for a Linux framebuffer.  Notably, my color channels are wrong (the eyes are
supposed to flash red) and it can't set the framebuffer mode to the one it
wants.  Not to mention hiding the terminal's cursor doesn't work for whatever
reason.

I'll probably get around to cleaning it up and trying to fix these bugs at some point.

## Version History

[0.1][targz] [01/11/09]: Initial public release.

[targz]: /images/2010/fb-hitler-0.1.tar.gz
