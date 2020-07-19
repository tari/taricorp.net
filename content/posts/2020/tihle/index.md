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
  - gpl
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

{{< toc >}}

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

In addition to the loss of a way to introduce people to programming, removing support for native code also effectively throws away a large existing library of programs that stretches back more than 20 years (nicely embodied in [ticalc.org](https://www.ticalc.org/), which first came online in 1996). While the 84+ CE is a young platform relative to the TI-83+ series as a whole (and is incompatible with earlier software), it already has a rich library of programs created by users that will effectively be lost when they can no longer be run on the hardware they are designed for.

<figure>
  <picture>
    <source type="image/webp" srcset="{{< resource "calcuzap.webp" >}}">
    <img src="{{< resource "calcuzap.gif" >}}" loading=lazy
         width=320
         alt="Calcuzap, a top-down space shooter game">
  </picture>
  <img src="{{< resource "cca.png" >}}" loading=lazy
       width=320
       alt="A port of Colossal Cave Adventure, a very early text adventure">
  <picture>
    <source type="image/webp" srcset="{{< resource "tetrica.webp" >}}">
    <img src="{{< resource "tetrica.gif" >}}" loading=lazy
         width=320
         alt="Tetric A, a Tetris clone">
  </picture>
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
  
<img src="{{< resource "tihle.svg" >}}" width=360 style="margin: auto; display: block;">

## Implementation, or: the development log {#implementation}

With a plan in mind, I had to start building something. I could have started
with the core of one of the existing existing emulators, but had a few reasons
to instead start from (mostly) scratch:

 * Code quality is highly variable, and I'm not familiar with their code.
   I have no idea what kinds of bugs and pitfalls may exist in them.
 * Support for high-level emulation would require an unknown amount of
   modification.
 * Portability is questionable, since they're mostly implemented in various
   flavors of C or C++ and typically have Windows as the primary target system.

I'm a big fan of **Rust** and know that portability of Rust programs is pretty good
because the language implementation's standard library does a pretty good job
of abstracting away platform details. In addition, I know the compiler has
good support for WebAssembly as a platform, which should make it reasonably
easy to make a port that **runs in a web browser**. Running in a web browser is
desirable because it is the most accessible way to allow people to emulate
games- see for instance [the
Emularity](http://ascii.textfiles.com/archives/4546), which powers emulation
of thousands of programs on the Internet Archive.

### Cores

Though I chose to start from scratch with an emulator written in Rust, I still
didn't want to spend the effort to implement CPU emulation from scratch. Since
the Z80 is such an old CPU and so widely used, there are a number of existing
emulators that I might be able to use the core from. Rust is easy to link against
C code, so there are many options to consider. Among the most notable:

 * [YAZE-AG](http://www.mathematik.uni-ulm.de/users/ag/yaze-ag/) is very mature
   and emulates a whole CP/M system.
 * [Fuse](https://en.wikipedia.org/wiki/Fuse_(emulator)) is also very mature
   and emulates the ZX Spectrum. It also has a reputation for high accuracy
   thanks in part to its comprehensive test suite.

<figure>
  <a href="http://visual6502.org/images/pages/Zilog_Z84C00_die_shots.html">
    <picture>
      <source type="image/webp" srcset="{{< resource "Z84C00_die_shot_20x_1b_640w.webp" >}}">
      <img src="{{< resource "Z84C00_die_shot_20x_1b_640w.jpg" >}}"
           alt="A photo of the die of a CMOS Z80. Large rectangular features surround
                a central rectangle of extremely fine detail.">
    </picture>
  </a>
  <figcaption>
    The Visual 6502 project has a
    <a href="http://www.visual6502.org/JSSim/expert-z80.html">gate-level Z80 simulator</a>
    that could yield ultimate accuracy at a "blistering" 5 Hz simulated clock speed!
    It's not feasible to use.
  </figcaption>
</figure>

I eventually settled on a core that's not part of any major emulator:
[Manuel Sainz de Baranda y Goñi's "redcode" core](https://github.com/redcode/Z80). It's
written in very portable C and designed to be used a library so it takes very little
setup or modification to use in my application. It does depend on a large external
header-only library as provided, but I was able to adapt it to be more standalone
with some work.

I tend to prefer to use permissive licenses on my software, but the redcode Z80 core
is **[GPL][gpl]**-licensed. Since linking it into my binaries would require my code to also be
GPL I would prefer to use a core with a more permissive license, but accepting
GPL in exchange for not needing to implement the core myself seems like a fair
and expedient trade on balance. In the future I might choose to implement my own core
and change the license for tihle, but for the time being it will be copyleft.

[gpl]: https://en.wikipedia.org/wiki/GNU_General_Public_License

### Taking emulation up a level

Building the CPU core and getting it to run some code wasn't terribly hard,
which left the core issue of how to implement high-level emulation. The emulator
needs to be able to recognize when the CPU needs to "trap" into operations
provided by the emulator.

I initially defined traps as simply taking some **action on instruction fetch**.
When the CPU would attempt to read memory at chosen addresses, the emulator
would execute a trap handler based on the memory address being read, then
return data equivalent to instructions appropriate to the trap- usually
just the value `C9` for a `ret` instruction.

This approach quickly turned out to be problematic as I was testing the emulator.
I chose **[Phoenix][phoenix]** as the target program for initial development because
it's a sort of classic calculator game and as a bonus shouldn't depend too tightly
on emulation accuracy- Phoenix has designed to be portable across a number of calculators,
so hopefully doesn't contain many assumptions about the system.

[phoenix]: https://www.ocf.berkeley.edu/~pad/game-ti83p-phoenixz.html

<figure>
  <img src="{{< resource "phx80459.png" >}}" width=192 height=128 style="image-rendering: pixelated;">
  <img src="{{< resource "phx80460.png" >}}" width=192 height=128 style="image-rendering: pixelated;">
  <img src="{{< resource "phx80461.png" >}}" width=192 height=128 style="image-rendering: pixelated;">
  <img src="{{< resource "phx80462.png" >}}" width=192 height=128 style="image-rendering: pixelated;">
  <figcaption>A few screenshots of Phoenix.</figcaption>
</figure>

Unfortunately, I quickly ran into problems with the way Phoenix generates random numbers.
Its `FAST_RANDOM` routine uses some self-modifying code to read values from semi-random
memory addresses, mixing the read values through a few shifts and `xor`s. The initial
address it reads is the CPU reset vector; `0x0000`, which I had also defined as the trap
that terminates emulation. To work around this I modified reset detection: instead of
simply trapping reads from that address, I made the "terminate" flag instead be controlled
by any **write to port 255**, which is unused on the calculator. By putting code at the
reset vector to write to port 255, we can avoid spurious termination.

It quickly becomes obvious that treating termination separately from other traps
doesn't work well. If the program decides to read a value from `0x0028` (where
control flow jumps to execute a system routine), it would cause incorrect actions
to be taken which would almost certainly cause the program to begin behaving
incorrectly. What's required is a way to ensure traps are only taken when executing
the target code, not if the system happens to read a given memory address as data.
It wasn't an immediate problem, but this will be revisited later.

### MirageOS

The initial implementation of the memory subsystem only emulated RAM, not the
Flash memory in the calculator that holds the OS. Regular programs only execute
out of RAM, so it was easy enough to trap on any access to Flash. This became
problematic once emulation of Phoenix reached a certain point, because it turns
out I had chosen to use the **MirageOS** version of Phoenix, meaning there was
another dependency on the contents of Flash that I had not expected.[^memory-map]

[^memory-map]: On the 83+, the Z80's 64 KiB memory space is split into 4 banks.
               Typically, page 0 of Flash (which contains OS code) is always mapped
               into the low 16 KiB,
               "bank A" from `0x4000`-`0x8000` can be swapped to contain different
               parts of Flash, and the top 32 KiB is RAM. Flash applications like
               Mirage execute of out bank A.

[MirageOS][mirage][^not-mirageio] is a shell implemented as a Flash application; it runs directly from Flash,
and provides useful support routines to programs designed to take advantage of it.

[mirage]: http://www.detachedsolutions.com/mirageos/

[^not-mirageio]: Not to be confused with [the library operating system of the same name](https://mirage.io/),
                 which I also have some experience with.

This version of Phoenix uses the `setupint` routine provided by Mirage to implement
its timer interrupt that controls game speed. Since Mirage isn't open-source, I would
have had to either reverse-engineer the details of how that works or simply map Mirage
into memory. I opted to do the latter, since Mirage is freely redistributable
and it will always be easier to emulate it than faithfully implement its
functionality in terms of emulator traps.

### Hoisted by my own bugs: a debugging adventure

After adding Mirage to the system, things still weren't working. I spend some time
reverse-engineering `setupint` and by painstakingly comparing that with execution
traces from the emulator, the flow that routine was taking seemed reasonable. It looked
like it was jumping somewhere incorrect on servicing the first interrupt after
setting it up! Checking the value of the `I` register that specifies the location of
the interrupt vector table to the core, it didn't seem correct- meaning there was
a problem with the core. Let's dive into that adventure (or skip ahead to
[the next section]({{< relref "#rethinking-traps" >}}) if you prefer not to learn
some about my debugging process):
                 
---

Mirage installs its interrupt vector table to the block of memory at `0x8B00`, filling
it with the value `0x8A`. Because custom interrupts on the 83+ must always use the
Z80's interrupt mode 2 but the calculator is not designed to use this mode,
this ensures that all interrupts will vector to `0x8A8A`. Breaking execution
at `0x71D2` where it loads the `I` register:

```z80
ROM:71CE                 ld      hl, 8B00h       ; Interrupt vectors go at 8B00
ROM:71D1                 ld      a, h
ROM:71D2                 ld      i, a
ROM:71D4                 dec     a               ; A = 8A
ROM:71D5                 ld      bc, 101h
ROM:71D8                 rst     28h             ; Fill 256 bytes of 8A at 8B00
ROM:71D8 ; ---------------------------------------------------------------------------
ROM:71D9                 dw 4C33h                ; MemSet
```

As expected, `HL` was `0x8B00` and `A` should have been `8B`, but instead it
had value `0x84` and after the `ld i, a` instruction the value of `I` hadn't
changed!

---

Digging deeper, I had to debug the emulator- not just inspect the emulated
CPU state. This was actually more difficult than expected, because I had been
developing with [CLion][clion] on Windows, using a Rust toolchain targeting the MSVC
tools. CLion only supports debugging with GNU tools however, so I couldn't use
the integrated debugger. I do have a copy of Visual Studio handy however, which
works just fine to debug MSVC binaries.

[clion]: https://www.jetbrains.com/clion/

I ended up adding a pause to the emulator
on startup so I could launch it through CLion, then switch to Visual Studio to
attach the debugger and set breakpoints before unpausing the emulator.
This worked quite tolerably, since Visual Studio was still able to make sense
of all the debug symbols in the binary so the only tedious part was in getting
the debugger attached.

With everything hooked up, I saw the following state in my debugger:

<img src="{{< resource "debug-8bit-broken.png" >}}"
     alt="A two-pane debugger, with disassembly above and local variables as defined
          in the source code below. The local variables object, state and af are
          expanded to show a value_uint16 of 0x8400 in af.">

By inspecting the assembly and comparing with the debugger's view of the locals,
I can tell that `rcx` points to the emulator `object`, and offset 0x40 from that
refers to the state of the CPU core. `PC` of the core has already been incremented
to the next instruction, and the intent seems to be that the value of the emulated
`A` register will be tansferred through `ecx` into `I`. However, the value
it's reading is 0, not `0x84` as it should be based on the debugger's view
of the `AF` register pair.

The redcode emulator uses some utility types that I reimplemented when I didn't
want to include the whole "Z" library that it wants to use, which include the
`Z16Bit` union used to represent the 16-bit register pairs. It looks like this:

```c
typedef union {
    zuint16 value_uint16;

#ifdef IS_BIG_ENDIAN
    // 0 is the low-order byte of these aggregates
    struct {
        zuint8 index1;
        zuint8 index0;
    } values_uint8;
#else
    struct {
        zuint8 index0;
        zuint8 index1;
    } values_uint8;
#endif
} Z16Bit;
```

The intent of this type appears to be in allowing easy access to each byte of a 16-bit
value; this could be done just with shifting and masking that presumably the compiler
could optimize, but I suppose it was designed to not depend on compilers being
efficient. In this case, it seems the program is actually reading the wrong byte
of the value; when it contains `0x8400` and we want to read the value of `A`, it should
take the high byte of the value but is instead taking the low. The macro `A` in the source
code for the core expands to an access to `object.state.af.values_uint8.index0` which
should be the high byte of the `AF` register pair.

So it turns out I made a mistake in adapting that definition to my needs, and `index0` is
meant to be the high-order byte of the aggregate value, not the low! Simply swapping
the locations of `index1` and `index0` then rebuilding, the state was then correct:

<img src="{{< resource "debug-8bit-fixed.png" >}}"
     alt="A two pane debugger configuration again, this time with the value 0x8b05 in af.">

Not only does `A` now have the value we expect from reading the Mirage disassembly,
`ecx` now does contains `0x8B` and the value is correctly written to `I`. Problem solved!

### Rethinking traps

With improved confidence in the core's correctness now, emulation can progress to the point
where it's relevant to resume thinking about how to correctly implement traps such
that non-instruction reads from memory won't spuriously trigger them. With the change
in reset handling to trap on writes to a particular port, it makes sense to explore
the ways in which traps could better be handled.

It's likely that there will need to be a number of different traps; certainly for
a handful of system routines. This means any trap method must be able to provide
a way to identify which trap to execute, but it must only be triggered when
executed by the CPU. Some ideas come to mind:

 * Write a value to a selected port that's not otherwise used on the calculator.
 * Provide a flag from the core to the emulator for handling memory reads to
   indicate an instruction fetch rather than any other data read.
 * Implement a custom instruction that causes a trap.

Modifying the core to handle memory reads differently has unknown complexity
so I didn't want to do that, and writing a value to a port didn't seem like a
very good choice because it can only accomodate 256 values per chosen port.
While I don't know how many traps will eventually be needed, 256 seems like
it may not be enough so I opted to look into creating a **custom instruction**.

---

Looking at what instructions are defined in both the Z80 and eZ80 documentation
(leaving the door open for eZ80 emulation later), there's a lot of unused
space in the ED-prefixed instructions that isn't used by either CPU and
isn't known to have useful undocumented effects.

[According to Jacco Bot](http://www.z80.info/z80undoc.htm), `ED00`-`ED3F`
and `EDC0`-`EDFF` all have no discernable effect so are good candidates
for custom instructions. Cross referencing with the eZ80 CPU manual (Zilog
UM0077, table 109), much of the first block is filled in while the second
remains sparsely used.

<figure>
  <img src="{{< resource "um0077-table109.png" >}}">
  <figcaption>The `ED`-prefixed instruction space for the eZ80 CPU.</figcaption>
</figure>

Choosing semi-arbitrarily, **`ED25` seems like a nice `TRAP` instruction**,
since `25` is an ASCII '%' which seems like it might "pop" out of a text
representation of memory a little bit.

To indicate which trap should be taken, I chose to have the instruction
include a 16-bit value which indicates to the emulator which trap is desired.
This provides a very large number of possible traps that ought to
be sufficient for any future needs.

---

Implementing this new instruction turned out to be very easy, and I learned
a little more about how the core is implemented. I simply needed to add a hook
for traps (to call from the C core into my Rust emulator) and add a new
function that calls that hook, then insert a pointer to that function
in the table of `ED`-prefixed instruction handlers.

```c
INSTRUCTION(ED_tihle_trap) {
  PC += 4;
  uint16_t trap_no = (READ_8(PC - 2) | (READ_8(PC - 1) << 8));
  CYCLES += object->trap(object->context, trap_no);
  return 0;
}
```

### The need for an OS

Now that traps are actually a special instruction, it turns out the system needs
some kind of OS image! Without one, there's no way to trigger traps on calls into
OS code. As a quick solution, I implemented a tiny OS image that traps on
the major OS entrypoints:

```asm
; Trap instruction: ED25 + 16 bit parameter
.addinstr TRAP * 25ED 4 NOP

#define TRAP_RESET 0
#define TRAP_BCALL 1
#define TRAP_OS_INTERRUPT 2

.seek $0000
    trap TRAP_RESET
    rst 00h

.seek $0028
    trap TRAP_BCALL
    ret

.seek $0038
    trap TRAP_OS_INTERRUPT
    reti
```

The important traps here are for calls to OS routines at `0x0028`, and the
default interrupt handler at `0x0038`. The handler for `TRAP_BCALL` inspects
the CPU state to choose what system routine to emulate, so it provides
most of the OS functionality that any program needs.

### Debugging in pictures

With this work, the general structure of the emulator seems sound. Although
I didn't want to implement an OS to begin with one is now present, though its
complexity is strictly controlled according to whether I find it easier to
implement routines in Z80 or as traps. It was then a matter of **implementing
and debugging the core functions** that Phoenix needs.

For some parts of debugging it was easier to write small programs that exercised
only the function(s) that needed debugging; these might be good to promote
to unit tests in the future.

<figure>
  <img src="{{< resource "helloworld-broken.png" >}}"
       alt="A line of nonsensical symbols is displayed on the emulated screen.">
  <img src="{{< resource "helloworld-fixed.png" >}}"
       alt="The emulated screen says Hello, world!">
  <figcaption>Text rendering seemed partially correct; it turned out I was computing
  an 8-bit index into the font bitmap rather than pointer-sized, so getting the character
  to display was wrong for most characters.</figcaption>
</figure>

Displaying text is not particularly hard, though getting a copy of the bitmap
font that the calculator uses was a bit of work. I ended up getting each
character as an image, then writing some Python scripts to combine them into
a binary blob that can be embedded in the emulator. It nearly worked with only a
little work, but I did have to debug some bad computations stemming from getting
an 8-bit character value and integer rollover.

<figure>
  <img src="{{< resource "too-many-titles.png" >}}"
       loading=lazy
       alt="The string 'Phoenix 4.3' is displayed all the way down the screen.">
  <img src="{{< resource "text-wonky-title.png" >}}"
       loading=lazy
       alt="Some menu entries appear under 'Phoenix 4.3', but slightly garbled and misaligned.">
  <img src="{{< resource "text-better-title.png" >}}"
       loading=lazy
       alt="The Phoenix menu appears, with some visual artifacts but legible text.">
  <figcaption>The title screen was a little too enthusiastic but tamed with some changes
    to correctly emulate undocumented behaviors.</figcaption>
</figure>

My initial traps for the `_PutS` system routine failed to emulate the **undocumented
behavior** that it updates `HL` to point past the string that is displayed. Text output
in the small font also had some problems with updating the screen coordinates to draw
at. The vertical lines in the small-font text were apparently an error in my font bitmap
data that was easily fixed, though the black line at the top of the screen was a
different problem.

<figure>
  <img src="{{< resource "warped-title.png" >}}"
       alt="The menu is now white text on black with a jagged left border, but the
            text is now slanted and wraps from the bottom to the top of the screen.">
  <figcaption>
    Fixing some of the LCD bugs shows Phoenix wants to display white on black, and
    shows there remain a few bugs to be solved.
  </figcaption>
</figure>

My LCD emulation[^lcd-driver] had some issues to fix around not being in the correct
mode initially and failing to update its addresses correctly in some situations. It turns
out Phoenix is somewhat unusual among games for the 83+ in that it directly accesses
the LCD for all its display operations, rather than delegating to a library function
provided by the OS (`_GrBufCopy`) or a shell (`fastcopy`) which makes it a good test
of basic LCD driver emulation. The display warping was a simple problem of having
the wrong display width parameter in the driver emulation.

[^lcd-driver]: On the 83+ the LCD driver is controlled through two ports from the CPU.
               Other calculators like the TI-85 have memory-mapped displays, but the 83+
               series requires the CPU to push data to and from the display and emulators
               must understand most of the LCD driver's command set in order to work
               correctly.
              
---

With the display looking largely correct, the final major hurdle to something that
looks like a game was in generating **timer interrupts**, which Phoenix uses to control
the game speed. This required implementing a few control ports which the CPU uses to
enable or disable interrupts and ensuring that interrupts would be triggered at
the correct times accurately, but wasn't too bad although I spent some time vexed by a bug
where IRQ flags never got reset so interrupts fired continuously.

<figure>
  <picture>
    <source type="image/webp" srcset="{{< resource "phoenix-title-mostlyworking.webp" >}}">
    <img src="{{< resource "phoenix-title-mostlyworking.gif" >}}"
         alt="The game title and author are shown at the top of the screen, with
              options to start the game, adjust settings or get more information.
              Jagged shapes scroll down both sides of the screen.">
  </picture>
  <figcaption>
    With working interrupts, the menu looks as it should!
  </figcaption>
</figure>

### Handling input

In order to make the game playable, the last piece of the puzzle is in allowing
it to receive input. On a physical calculator this is through a simple matrix keyboard,
interfaced directly to the CPU via I/O port 0. Where some complexity comes in
is in how the calculator OS provides its input abstractions, which turns
out to be important but not well documented.

TI-OS provides a routine for scanning the keyboard, called `_GetCSC`. It returns one
value, a scan code corresponding to the key (if any) that is currently pressed.
The documentation leaves it at that however, when the behavior around
multiple keys being pressed or keys being held is also important.

It turns out that `_GetCSC` is implemented largely via interrupts; while servicing
regular timer interrupts, the OS scans they keyboard for keys that are being pressed,
and if any are then stores that value in RAM. `_GetCSC` reads that value and clears
it. If everything were that simple it would be very easy, but the interrupt
handler also debounces some keys; the directional arrows and <kbd>del</kbd> key
can repeat if held, while others will not. The actual timing is that the first
repeat of a held key comes after about 48 interrupts, and every 10 thereafter
meaning the first repeat comes after about 250 milliseconds and subsequent ones
occur at 20 Hz.

While OS2 contains an implementation of this logic (which seemed overcompilicated
until I actually understood how this key repeat works), I opted to implement
keyboard scanning as a trap instead. While the keyboard hardware is fully
emulated because Phoenix only uses `_GetCSC` for a few things and directly
interfaces with the keyboard for the rest, the OS timer interrupt calls
into the emulator to do keyboard scanning because it's easier to implement
and probably more performant.

<figure>
  <picture>
    <source type="image/webp" srcset="{{< resource "phoenix-with-input.webp" >}}">
    <img src="{{< resource "phoenix-with-input.gif" >}}" loading=lazy
         alt="The Phoenix menu looks correct, but the menu pointer moves too fast to see.">
  </picture>
  <picture>
    <source type="image/webp" srcset="{{< resource "phoenix-playable.webp" >}}">
    <img src="{{< resource "phoenix-playable.gif" >}}" loading=lazy
         alt="Now the game menu is controllable, and gameplay is demonstrated.">
  </picture>
  <figcaption>
    Without correct key repeat control the menus work but are too fast to control;
    afterwards, the game is perfectly playable!
  </figcaption>
</figure>

With this, I'm rather surprised that Phoenix is playable! There's certainly more work
to be done to improve everything, but "Phoenix is playable" was the goal I set for
myself that must be reached before I published the project.

## Current state and future

Currently, I've really only tested Phoenix. It's possible that some other games will
work in tihle as it stands, and others might work with only minor changes. There
are notable holes that I'd like to fill:

 * Programs are loaded directly to the point in memory that they execute from.
   Programs and data should be loaded into memory as if they were managed normally
   by TI-OS, which will allow programs that want to be able to load external data
   (such as level packs) to do so, and also enable saving of high scores.
 * Actually run shells, not just programs
 * Improve LCD emulation to support grayscale games (which rapidly switch pixels
   between black and white).
 * Support an on-screen keyboard, useful for touchscreen devices and easier
   to navigate than pressing keys on a computer keyboard.

I'm quite happy with the ability to run the emulator in a web browser as it
is right now. While I can't claim much credit for it beyond choosing tools that
would support that target,[^browser-target] it's still very gratifying to see
everything come together to make emulation so accessible. In the longer term,
I'd like to try to get emulation via tihle **available on the Internet Archive**,
like [many DOS games are](https://blog.archive.org/2019/10/13/2500-more-ms-dos-games-playable-at-the-archive/).

Emscripten works; thanks SDL

might improve the OS a lot over time

{{< comments >}}
