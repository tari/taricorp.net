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

Today I'm publishing [tihle](https://gitlab.com/taricorp/tihle), a new emulator
targeting TI graphing calculators (currently only the 83+, but maybe others
later). There's rather a lot to say about it, but here I will discuss the
[motivation for a new emulator]({{< relref "#motivation" >}}) and [the state of
the art]({{< relref "#the-state-of-the-art" >}}) followed by technical notes on
the [design]({{< relref "#design" >}}) and [initial development process]({{<
relref "#implementation" >}}).

Read on for that discussion, or jump straight to the **[project homepage](https://gitlab.com/taricorp/tihle)** on GitLab which has a **live demo** that runs in your web browser and other downloads.

<!--more-->

## Motivation

I've long been involved in the community of people who program for the [TI-83+ series of graphing calculators](https://en.wikipedia.org/wiki/TI-83_series); it was on that platform that I got started programming in the first place. These days I play more of an advisory than active role in writing programs, by running much of [Cemetech](https://www.cemetech.net/) behind the scenes and providing the occasional input to others. I think calculators are an excellent way to introduce people to programming, since they are readily available devices and not too complex to get started on, while still having enough capability to support experienced developers in doing interesting things (because they are readily accessible embedded systems). I fully credit getting started with programming calculators for having ended up programming embedded systems profesionally.

<figure>
  <img src="{{< resource "calcdcc.jpg" >}}" loading=lazy >
  <figcaption>Tim's workspace for
    <a href="https://www.cemetech.net/forum/viewtopic.php?p=262170#262170">CalcDCC</a>
    looks like it could contain any embedded engineer's prototype.
  </figcaption>
</figure>

Unfortunately, the future of programming for TI calculators seems to be in peril. About a month ago, the news came out that new versions of the OS for the TI-84+ CE (the most recent variant of the 83+ with a color screen and improved eZ80 processor) [will remove support for running native code](https://www.cemetech.net/news/2020/5/949/_/ti-removes-asmc-programming-from-ti-83-premium-ce).

### Death of a platform

While this doesn't necessarily affect older calculators or programs, in the long
term it seems to spell doom for calculators as an inroad to developing embedded
software in particular. Programs written in the calculators' dialect of BASIC
continue to be accessible and a new Python implementation fills the void
somewhat, but they lack in depth- where a user could spend time and effort
developing native programs limited only by the hardware they run on before, in
the future users will be **limited to only those capabilities provided by TI's
software**.

In much the same way that I believe [Scratch](https://en.wikipedia.org/wiki/Scratch_(programming_language)) is a decent introduction to programming but completely hides interesting details and is not seriously used by anybody but those using it a learning tool, I also believe removal of support for running native code will ultimately mean people will no longer have calculators (which are often required school equipment!) as a useful entrypoint to serious programming.

### Historical interest

In addition to the loss of a way to introduce people to programming, removing support for native code also effectively throws away a large existing library of programs that stretches back more than 20 years (nicely embodied in [ticalc.org](https://www.ticalc.org/), which first came online in 1996). While the 84+ CE is a young platform relative to the TI-83+ series as a whole (and is incompatible with earlier software), it already has a rich library of programs created by users that will effectively be lost when it can no longer be run.

<figure>
  <div style="display: flex; flex-wrap: wrap; justify-content: space-evenly;">
    <img src="{{< resource "calcuzap.gif" >}}" loading=lazy
         width=320
         alt="Calcuzap, a top-down space shooter game">
    <img src="{{< resource "cca.png" >}}" loading=lazy
         width=320
         alt="A port of Colossal Cave Adventure, a very early text adventure">
    <img src="{{< resource "tetrica.gif" >}}" loading=lazy
         width=320
         alt="Tetric A, a Tetris clone">
  </div>
  <figcaption>
    A small selection of the games that are available for the TI-84+ CE today:
    <a href="https://www.ocf.berkeley.edu/~pad/game-ti8c-calcuzap.html">Calcuzap</a>
    <a href="https://github.com/drdnar/open-adventure-ce">Colossal Cave Adventure</a> and
    <a href="https://www.cemetech.net/downloads/files/1347">Tetric A</a>.
  </figcaption>
</figure>

The precedent of effectively **destroying the work of community members** is
troubling, and I am motivated to look for ways to preserve it. In much the same
way that there still exist thriving communities around long-obsolete home
computers like the [Apple II](https://apple2online.com/) and [Commodore
64](https://thec64community.online/) today, I think it's worthwhile to try to
provide a similar opportunity by preserving the platform into a hostile future
by working to give the systems and software ongoing life beyond what their
creators envisioned (or perhaps more pointedly, beyond what they decided they
could make money from).

As a newer platform than those early home computers that still have active communities, information and resources may be rather easier to come by for these calculators because much of the information was born digital and has always been online. However this is also hazardous to preservation, because if items are readily available online there may not be any replacements available if the original goes away. For instance, TI used to [freely provide an SDK for the 83+](https://www.ticalc.org/archives/news/articles/1/19/19421.html), but have more recently made it [much more difficult to access](https://education.ti.com/en/customer-support/sdk-request). Perhaps even more concerningly, TI's web site no longer seems to provide *any* information about the [TI-84+ CSE](https://www.ticalc.org/basics/calculators/ti-84plus-cse.html), seeming to deny that it ever existed (though manuals and software are still available if you know where to look).

### A calling

Recognizing these concerns about the loss of a valuable resource for beginning programmers and loss of interesting history to the grind of the education-industrial complex,[^complex] what are we to do?

[^complex]: Most users of these calculators have them because their schools
            require them, and schools tend to require them because TI spend
            significant effort in selling the calculators to schools and
            positioning them as tools for standardized testing.

There exist a number of web sites that document the calculators and offer
resources related to them- I'm already involved in that, which is valuable and
[generally well-preserved](https://archive.org/details/ticalc-2014-08) on [the
Internet Archive](https://web.archive.org/). But if the existing resources are
useless on current hardware as they largely become when large classes of
programs are not runnable, new tools become required: I believe this situation
calls for emulation of the calculators, to **make the platform accessible to
everybody**.

## The state of the art

There already exist a number of emulators for TI calculators, including:

 * [WabbitEmu](http://wabbitemu.org/), which is open-source and generally good
   quality.
 * [jsTIfied](https://www.cemetech.net/projects/jstified/), an emulator
   available as a web application.
 * [Virtual TI](https://www.ticalc.org/archives/files/fileinfo/84/8442.html),
   one of the earliest calculator emulators to be created.
 * [PindurTI](https://wikiti.brandonw.net/index.php?title=Emulators:PindurTI),
   which is now defunct but offered some useful capabilities in its day.
 * ..and others

While most of these are accurate enough to run most programs, this is not the
whole story: all of them **require a ROM image to work**. The ROM includes the
calculator's operating system and boot code, which implement huge swaths of
functionality from keyboard and display handling through implementing
floating-point arithmetic and the TI-BASIC interpreter.

TI jealously protect their OS and boot code because from the point of view of
their business, the entire value of the calculator is in its software. If an
emulator can run the same software on a more general machine, what reason is
there for a user to purchase a $100 device from TI?[^lol-testing] But if we want
to preserve *community* software for emulation, we don't really care about the
same functions that TI are interested in protecting.

[^lol-testing]: Most users only need a physical calculator because more capable
                devices (phones and computers) are not permitted in standardized
                testing!

Though truly accurate emulation still requires all OS functions be available in
the same way, many applications only use a small subset of them. So what options
are available for emulating the system software?

### OS implementations

 * TI's EOS (TI-OS) is provided with the calculator, and can be downloaded
   from TI in order to update a calculator. However, they added a [clickwrap
   agreement to the OS in
   2013](https://www.cemetech.net/forum/viewtopic.php?t=8819) that attempts
   to forbid use of the OS for emulation. While that clause is questionably
   enforceable, nobody (myself included) is very interested in challenging it-
   mostly because TI has historically tended to turn a blind eye to the
   distribution of ROMs. Any such distribution in a larger, more public forum
   increases the risk of calling in the lawyers, so for these and the reasons
   discussed above, I do not believe it is tenable to use TI's OS for
   general-availability emulation.
 * Brandon Wilson's [OS2](https://www.brandonw.net/calculators/OS2/) seems most
   relevant, in that it wants to reimplement TI-OS "but better." However,
   it hasn't been updated in 11 years at this point and seems dead. It's also
   dependent on the assembler and tools provided by Zilog, which only run on
   Windows and are closed-source.
 * [GlassOS](https://www.cemetech.net/forum/viewtopic.php?t=5686)
   is implemented in C and actually seems useable, but lacks compatibility
   with any existing software.
 * [KnightOS](https://github.com/KnightOS/KnightOS) is UNIX-like and seems to
   have a selection of useful software, but again is not compatible with any
   existing software beyond a small library of ports targeting it.
 * Many other people (myself included) have attempted to write OSes, but they
   don't merit mention here because they're of even less practical use.

### Boot code

While the calculator OS implements most functionality, the boot code is also
relevant- TI's OS uses some support code from the boot code, and of course the
boot code is responsible for handling the system power-up sequence and allowing
recovery from a no-OS situation.

The boot code on these calculators is meant to be read-only,[^boot-ro] and is
programmed into the device at the factory. Thus, there is no official source for
boot code short of reading it from the memory of a physical calculator and the
community consensus tends to be that sharing copies of the boot code would
infringe on TI's copyright.

[^boot-ro]: I understand the write-protection of the boot code on many
            calculators is not as robust as expected from understanding the
            hardware's capabilities such that it can actually be modified from
            software only, but the fact remains that it's not *intended* to ever
            be updated.

[Ben "FloppusMaximus"
Moody](https://www.ticalc.org/archives/files/authors/72/7233.html) at one time
published a reimplementation of the calculator boot code called "BootFree,"
which seems to have disappeared from the Internet except for the version
integrated with WabbitEmu. While it seems BootFree disappeared for reasons
related to the addition of the clickwrap agreement to the EOS downloads provided
by TI,[^bootfree-clickwrap] [^educators-emulators] I don't think the same
reasons apply to emulation that doesn't use the EOS- thus, BootFree seems like a
fine resource in pursuit of making emulation available to all.

[^bootfree-clickwrap]: WabbitEmu added support for automatically downloading an
  EOS image from TI and combining it with a copy of BootFree to make a
  fully-functional ROM without ever touching a real calculator [sometime in
  2010](https://github.com/sputt/wabbitemu/commit/4a028a726a27d307fb25e5f607fd30118e9e765c).
  This seems to have flown under TI's radar for a few years, possibly until the
  release of jsTIfied in 2012 brought emulation more into the mainstream. Where
  previously emulation had a somewhat higher barrier to entry, the availability
  of an emulator running entirely in a web browser combined with the possibility
  of automatically making a complete software image from freely-available
  resources seems to have motivated TI both to begin more aggressively marketing
  their own emulator (TI-SmartView) and place barriers in front of community
  emulation in the form of clickwrap in order to extract licensing fees from
  educators who might otherwise use free emulators.

[^educators-emulators]: Anecdotally, Cemetech saw a number of new users
  following the release of jsTIfied who were clearly in education because for a
  time it required users to register accounts on the site to use it (a choice
  related to a technical limitation that some operations required data
  be sent to the server and bounced right back). I assume there were a number of
  teachers who might have instructed their students to use jsTIfied in order to
  avoid any extra costs in accessing the calculators required by their
  curriculum.

## Design

If the goal is to freely emulate calculator programs, we recognize that while
the boot code situation seems compatible with accurate emulation, the current
available
***<abbr title="Software allowing anybody to use or modify it for any reason; Open Source.">libre</abbr>*
OSes are insufficient**. While it is technically feasible to
emulate TI's EOS (the only reasonable choice for emulating the current software
library), legal forces make it untenable to use as a base for publicly-available
emulation with the goal of allowing anybody to run programs for the platform.

It's also worth noting that there are two major divisions in kinds of programs
that run on these calculators: they can be implemented in the provided BASIC
dialect (TI-BASIC), or distributed as machine code for the calculator. TI-OS
implements the interpreter for TI-BASIC so both of these can be run on the
existing emulators, but because using TI-OS is not an option for this project we
need to choose how to approach things. The possibility space of emulation
projects forks:

 * Build a TI-BASIC interpreter, not necessarily one that runs on an
   emulated calculator.
 * Create a whole-machine emulator that works without TI-OS.

While I've explored the feasibility of creating a from-scratch TI-BASIC
interpreter in the past, it's never made much progress and I got rather
bogged down in accurate emulation of the calculator's rather unique decimal
floating-point format.[^ti-floats] I have instead chosen to work on a
**whole-machine emulator that doesn't require TI-OS**.

[^ti-floats]: I now note that accurate emulation of that particular
  aspect is likely unnecessary, but haven't revisited that concept because I
  chose to think about the whole-machine emulation.

### Novelty

It is interesting to compare emulation of calculator programs to that of game
systems (which are also common targets for emulation). In game systems the
interest in emulation is almost entirely on the programs (games) that are
separate from the system. Similarly, I am currently interested in providing
emulation of third-party programs that happen to be run on a calculator.

Game systems tend to have small amounts of platform code that game software
might use, which emulators tend to hide the existence of: a tiny minority of
emulator users would have the capability to extract the firmware from a game
system they own, and though most users probably engage in copyright infringement
to obtain copies of game software to run on emulators, the emulators themselves
owe their existence to the fact that they **don't contain any
copyright-infringing code themselves**.

On calculators, emulation of interesting programs with existing emulators
requires a copy of the system software which notionally requires access to a physical
calculator to obtain. This means the emulators can reliably be considered not to fall afoul
of any laws, though the barrier to entry is raised. However, the programs themselves
are almost entirely made available freely by their authors- among the hobbyists who
write calculator software, the platform is largely open. If an emulator can do without
a ROM image of a calculator, it is feasible to freely provide the existing library of
software to all comers.

Game system emulators tend to solve their inability to distribute the system
firmware through high-level emulation: various operations that may be taken by
software can be recognized, and the emulator can implement those operations
itself. This approach both avoids any dependency on system firmware for its
implementation and can often achieve better performance because the emulator
need not faithfully emulate the underlying process- only its side effects are
in scope.
Though high-level emulation tends to sacrifice accuracy in ways that can cause
some emulated software to behave incorrectly, this is often because the emulator
must take shortcuts to achieve acceptable performance. When emulating a
calculator with a 40-year-old CPU architecture that runs at a few Megahertz,
acceptable performance should be much easier to achieve without noticeable
shortcuts.[^performance-ballpark]

[^performance-ballpark]: Concretely, the TI-83+ CPU runs at 6 MHz and a Z80
  cannot execute any instructions in less than 4 clock cycles (and most take
  more than 4, possibly as many as 23). A CPU in a general-purpose device today
  might run at 3 GHz and achieve average throughput of two instructions per
  cycle, meaning an emulating machine today is comfortably 1000 times faster
  than the Z80 it emulates (and maybe more like 5000 times faster depending on
  the workload!).

With the precedent of existing emulators that are very faithful to the known
hardware behavior and decision that no existing calculator OS is appropriate for
the application, **tihle** is born. The name indicates how important that
feature is to its existence: it is a **h**igh-**l**evel-**e**mulator for **TI**
calculators.[^why-not-os2]

[^why-not-os2]: Some readers might ask: "why not improve an existing *libre*
  OS like OS2?" My answer is that doing so is too hard: while the Z80 is a
  well-understood CPU to program for, its age means much of the tooling
  available to us today that makes programmers more productive is simply not
  available. While a truly free (*libre*) EOS replacement would be ideal, I do
  not consider it to be immediately feasible.

## Implementation, or: the development log {#implementation}

## Current state and future


