---
title: "tihle: a unique TI calculator emulator"
slug: tihle
draft: true
date: 2020-07-16T09:49:18.448Z
categories:
  - Software
tags:
  - ticalc
  - emulation
  - z80
  - calculators
  - archiving
---
Today I'm publishing [tihle](https://gitlab.com/taricorp/tihle), a new emulator targeting TI graphing calculators (currently only the 83+, but maybe others later). There's rather a lot to say about it, but here I will discuss the \[motivation for a new emulator]({{< relref "#motivation" >}}) and \[the state of the art]({{< relref "#the-state-of-the-art" >}}) followed by \[technical notes notes on the initial development process and design]({{< relref "#implementation" >}}).

Read on for that discussion, or jump straight to the **[project homepage](https://gitlab.com/taricorp/tihle)** on GitLab which has a **live demo** that runs in your web browser and other downloads.

<!--more-->

## Motivation

I've long been involved in the community of people who program for the [TI-83+ series of graphing calculators](https://en.wikipedia.org/wiki/TI-83_series); it was on that platform that I got started programming in the first place. These days I play more of an advisory than active role in writing programs, by running much of [Cemetech](https://www.cemetech.net/) behind the scenes and providing the occasional input to others. I think calculators are an excellent way to introduce people to programming, since they are readily available devices and not too complex to get started on, while still having enough capability to support experienced developers in doing interesting things (because they are readily accessible embedded systems). I fully credit getting started with programming calculators for having ended up programming embedded systems profesionally.

(some representative images here?)

Unfortunately, the future of programming for TI calculators seems to be in peril. About a month ago, the news came out that new versions of the OS for the TI-84+ CE (the most recent variant of the 83+ with a color screen and improved eZ80 processor) [will remove support for running native code](https://www.cemetech.net/news/2020/5/949/_/ti-removes-asmc-programming-from-ti-83-premium-ce).

### Death of a platform

While this doesn't necessarily affect older calculators or programs, in the long term it seems to spell doom for calculators as an inroad to developing embedded software in particular. Programs written in the calculators' dialect of BASIC continue to be accessible and a new Python implementation fill the void somewhat, but they lack in depth- where a user could spend time and effort developing native programs limited only by the hardware they run on before, in the future users will be limited to only those capabilities provided by TI's software.

In much the same way that I believe [Scratch](https://en.wikipedia.org/wiki/Scratch_(programming_language)) is a decent introduction to programming but completely hides interesting details and is not seriously used by anybody but those using it a learning tool, I also believe removal of support for running native code will ultimately mean people will no longer have calculators (which are often required school equipment!) as a useful entrypoint to serious programming.

### Historical interest

In addition to the loss of a way to introduce people to programming, removing support for native code also effectively throws away a large existing library of programs that stretches back more than 20 years (nicely embodied in [ticalc.org](https://www.ticalc.org/), which first came online in 1996). While the 84+ CE is a young platform relative to the TI-83+ series as a whole (and is incompatible with earlier software), it already has a rich library of programs created by users that will effectively be lost when it can no longer be run.

(grab some CE game screenshots here)

The precedent of effectively destroying the work of community members is troubling, and I am motivated to look for ways to preserve it. In much the same way that there still exist thriving communities around long-obsolete home computers like the [Apple II](https://apple2online.com/) and [Commodore 64](https://thec64community.online/) today, I think it's worthwhile to try to provide a similar opportunity by preserving the platform into a hostile future by working to give the systems and software ongoing life beyond what their creators envisioned (or perhaps more pointedly, beyond what they decided they could make money from).

As a newer platform than those early home computers that still have active communities, information and resources may be rather easier to come by for these calculators because much of the information was born digital and has always been online. However this is also hazardous to preservation, because if items are readily available online there may not be any replacements available if the original goes away. For instance, TI used to [freely provide an SDK for the 83+](https://www.ticalc.org/archives/news/articles/1/19/19421.html), but have more recently made it [much more difficult to access](https://education.ti.com/en/customer-support/sdk-request). Perhaps even more concerningly, TI's web site no longer seems to provide *any* information about the [TI-84+ CSE](https://www.ticalc.org/basics/calculators/ti-84plus-cse.html), seeming to deny that it ever existed (though manuals and software are still available if you know where to look).

### A calling

Recognizing these concerns about the loss of a valuable resource for beginning programmers and loss of interesting history to the grind of the free market, what are we to do?

There exist a number of web sites that document the calculators and offer resources related to them- I'm already involved in that, which is valuable and [generally well-preserved](https://archive.org/details/ticalc-2014-08) on [the Internet Archive](https://web.archive.org/). But if the existing resources are useless on current hardware as they largely become when large classes of programs are not runnable, new tools become required: I believe this situation calls for emulation of the calculators, to make the platform accessible to everybody.

## The state of the art

## Implementation