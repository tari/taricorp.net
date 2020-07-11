---
layout: page
title: PuTTYJL
date: 2010-05-30 20:36:42.000000000 -06:00
categories: []
tags: []
status: publish
type: page
published: true
---

PuTTYJL is a wrapper and patch for [PuTTY][putty] written in C# for .NET 3.5 and
Windows 7, adding support for the new [jump lists][jl], allowing you to create
jump list entries for saved sessions in the registry and optionally just launch
the wrapper to start a default session in PuTTY.

PuTTY includes native jump list support since version 0.61.  I recommend using
that over this software, since I am no longer updating it, although it's still
useful if you want to define a default session for PuTTY to launch or have
finer-grained control over the jump list.

## Download

Latest version is 0.10: [binaries](/images/2010/puttyjl-0.10.zip),
[source](/images/2010/puttyjl-0.10-src.tar.gz) available. Consider this a public
beta, since it's not at all documented.

The included version of PuTTY is patched with my stacking fix (so it stacks on
PuTTYJL's taskbar icon; see `AppID.c`) and the [PuTTY Tray][putty-tray] patchet,
compiled with Visual Studio 2010.

## Todo/Bugs

 * Add an about box to the PuTTYJL config dialog.
 * Create a readme
 * Include licensing information
 * Crashes when PuTTY has no saved sessions (fixed in current beta)
 
## Version history

 * 0.10 - 30.05.2010: Initial public release

[putty]: http://www.chiark.greenend.org.uk/~sgtatham/putty/
[jl]: http://windows.microsoft.com/en-us/windows7/products/features/jump-lists
[putty-tray]: http://haanstra.eu/putty/
