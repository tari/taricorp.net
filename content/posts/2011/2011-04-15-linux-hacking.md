---
author: tari
comments: true
date: 2011-04-15 02:00:26+00:00
slug: linux-hacking
title: Pointless Linux Hacks
wordpress_id: 225
categories:
- Linux
- Software
tags:
- Hacking/Tweaking
- Software
---

I nearly always find it interesting to muck about in someone else's code, often
to add simple features or to make it do something silly, and the Linux kernel is
no exception to that. What follows is my own first adventure into patching Linux
to do my <del>evil</del> bidding.

Aside from mucking about in code for fun, digging through public source code
such as that provided by Linux can be very useful when developing something new.

## A short story

I was doing nothing of particular importance yesterday afternoon when I was
booting up my [previously mentioned](/2011/btrfs.html)
netbook. The machine usually runs on a straight framebuffer powered by
[KMS](https://wiki.archlinux.org/index.php/Kernel_Mode_Setting) on i915
hardware, and my kernel is configured to show the famous [Tux
logo](http://www.sjbaker.org/wiki/index.php?title=The_History_of_Tux_the_Linux_Penguin)
while booting.

Readers familiar with the logo behaviour might already see where I'm going with
this, but the kernel typically displays one copy of the logo for each processor
in the system (so a uniprocessor machine shows one tux, a quad-core shows four,
etc..). As a bit of a joke, then, suggested a friend, why not patch my kernel to
make it look like a much more powerful machine than it really is? Of course,
that's exactly what I did, and here's the patch for Linux 2.6.38.

```
--- drivers/video/fbmem.c.orig	2011-04-14 07:26:34.865849376 -0400
+++ drivers/video/fbmem.c	2011-04-13 13:06:28.706011678 -0400
@@ -635,7 +635,7 @@
 	int y;

 	y = fb_show_logo_line(info, rotate, fb_logo.logo, 0,
-			      num_online_cpus());
+			      4 * num_online_cpus());
 	y = fb_show_extra_logos(info, y, rotate);

 	return y;
```

Quite simply, my netbook now pretends to have an eight-core processor (the Atom
with SMT reports two logical cores) as far as the visual indications go while
booting up.

## Source-diving

Thus we come to source-diving, a term I've borrowed from the community of
[Nethack players](http://nethack.wikia.com/wiki/Source_diving) to describe the
process of searching for the location of a particular piece of code in some
larger project.

Diving in someone else's source is frequently useful, although I don't have any
specific examples of it in my own work at the moment. For an outside example,
have a look at
[musca](http://web.archive.org/web/20140909014359/http://aerosuidae.net/musca.html),
which is a tiling window manager for X which was written from scratch but used
ratpoison and dwm (two other X window managers) as models:

> Musca's code is actually written from scratch, but a lot of useful stuff was
> gleaned from reading the source code of those two excellent projects.

A personal recommendation for anyone seeking to go source-diving: become good
friends with grep. In the case of my patch above, the process went something
like this:

  * `grep -R LOGO_LINUX linux-2.6.38/` to find all references to `LOGO_LINUX` in
    the source tree.
  * Examine the related files, find `drivers/video/fbmem.c`, which contains the
    logo display code.
  * Find the part which controls the number of logos to display by searching
    that file for 'cpu', assuming (correctly) that it must call some outside
function to get the number of CPUs active in the system.
  * Patch line 638 (for great justice).

Next up in my source-diving adventures will be finding the code which controls
what happens when the user presses control+alt+delete, in anticipation of
sometime rewriting [fb-hitler](/projects/fb-hitler.html) into
a standalone kernel rather than a program running on top of Linux..
