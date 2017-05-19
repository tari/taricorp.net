---
author: tari
comments: true
date: 2011-08-31 02:35:45+00:00
slug: never-do-this
title: How not to distribute software
wordpress_id: 236
categories:
- Linux
tags:
- Hacking/Tweaking
- Software
---

I recently acquired a TI [eZ430-Chronos](http://www.ti.com/tool/ez430-chronos)
watch/development platform. It's a pretty fancy piece of kit just running the
stock firmware, but I got it with hacking in mind, so of course that's what I
set out to do. Little did I know that TI's packaging of some of the related
tools is a good lesson in what not to do when packaging software for users of
any system that isn't Windows..

The first thing to do when working with a new platform is usually to try out the
sample applications, and indeed in this case I did exactly that. TI helpfully
provide a distribution of the PC-side software for communicating with the
Chronos that runs on Linux, but things cannot be that easy. What follows is a
loose transcript of my session to get
[slac388a](http://www.ti.com/litv/zip/slac388a) unpacked so I could look at the
provided code.

```sh
$ unzip slac388a.zip
$ ls
Chronos-Setup
$ chmod +x Chronos-Setup
$ ./Chronos-Setup
$
```

Oh, it did nothing. Maybe it segfaulted silently because it's poorly written?

```sh
$ dmesg | tail
[snip]
[2591.111811] [drm] force priority to high
[2591.111811] [drm] force priority to high
$ file Chronos-Setup
Chronos-Setup: ELF 32-bit LSB executable, Intel 80386, version 1 (GNU/Linux), statically linked, stripped
$ gdb Chronos-Setup
GNU gdb (GDB) 7.3
Copyright (C) 2011 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "x86_64-unknown-linux-gnu".
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>...
Reading symbols from /home/tari/workspace/chronos-tests/Chronos-Setup...
warning: no loadable sections found in added symbol-file /home/tari/workspace/chronos-tests/Chronos-Setup
(no debugging symbols found)...done.
(gdb) r
Starting program: /home/tari/workspace/chronos-tests/Chronos-Setup
[Inferior 1 (process 9214) exited with code 0177]
```
Great. It runs and exits with code 127. How useful.

I moved the program over to a 32-bit system, and of course it worked fine,
although that revealed a stunningly brain-dead design decision. The following
image says everything.

<figure>
    <img src="/images/2011/braindeath.png"
    alt="A Windows-style installer, 'InstallJammer Wizard'. On Linux."/>
    <figcaption>This is stupid.</figcaption>
</figure>

To recap, this was a Windows-style self-extracting installer packed in a zip
archive upon initial download, designed to run on a 32-bit Linux system, which
failed silently when run on a 64-bit system. I am simply stunned by the bad
design.

Bonus tidbit: it unpacked an uninstaller in the directory of source code and
compiled demo applications, as if whoever packaged it decided the users
(remember, this is an embedded development demo board so it's logical to assume
the users are fairly tech-savvy) were too clueless to delete a single directory
when the contents were no longer wanted. I think the only possible reaction is a
hearty :facepalm:.
