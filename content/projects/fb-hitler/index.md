---
layout: page
title: fb-hitler
date: 2009-01-11
categories: []
tags: []
status: publish
type: page
published: true
---

<figure>
    <a href="https://xkcd.com/528/">
      <img src="/images/2010/windows_7.png" alt="XKCD's 'Windows 7'" />
    </a>
</figure>

fb-hitler is a small program inspired by [Windows 7 as envisioned by XKCD][explain] (making
a joke at the expense of Windows Vista) that displays a picture (of Adolf Hitler
in the pure form) and displays another picture when you press Ctrl+Alt+Delete
(normally the same picture with glowing eyes).

[explain]: https://www.explainxkcd.com/wiki/index.php/528:_Windows_7

I wrote the [first version](#original-version) of fb-hitler when that comic was
first published, and years later [revisited it](#fb-hitler-ng) in a more
technically sophisticated way.

## Original version

The original version of fb-hitler was implemented as a userspace application for
Linux, meant to be run as `init`. I hacked it up in a weekend of mostly reading
documentation back in 2009. I recorded a demo video of it at the time, which is
predictably poor quality when considering when it was created.

<figure>
<iframe width="560" height="315"
src="https://www.youtube-nocookie.com/embed/Rnp5Rk2yEh8" frameborder="0"
allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
allowfullscreen></iframe>
</figure>

This Linux version uses the fbdev subsystem to display an image, and needs to be
run as PID 1 in order to use `reboot(2)`. For reasons I never did debug, the
color channels are incorrect so what was meant to be red is in fact blue.

You can [view the code on GitLab](https://gitlab.com/taricorp/fb-hitler), or
[download the original source archive][targz].

[targz]: /images/2010/fb-hitler-0.1.tar.gz

## fb-hitler-ng

`fb-hitler-ng` is an updated version of the program that I wrote in 2017. This
new version in x86 assembly and is designed to be booted directly from legacy PC
BIOS. It can be run in [QEMU](https://www.qemu.org/) with relative ease:

```
$ qemu-system-i386 -fda fb-hitler-ng.bin -monitor stdio
```

Typing `sendkey ctrl-alt-delete` in the QEMU monitor will then flash the eyes by
sending that key sequence to the virtual machine.

<figure>
  <img alt="Adolf hitler in black and white; his eyes flash red occasionally."
       src="{{< resource "demo-ng.gif" >}}">
  <figcaption>
    QEMU looks like this when running the program.
  </figcaption>
</figure>

This version of fb-hitler is [also on GitLab, as
fb-hitler-ng](https://gitlab.com/taricorp/fb-hitler-ng/).
