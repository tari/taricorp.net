+++
title = "Fomu: a beginner's guide"
description = ""
date = "2019-03-06"
tags = ['fpga', 'fomu', 'tomu', 'icestorm', 'hacking', '3d printing', 'raspberry pi', 'debugging']
categories = ['Embedded Systems', 'Hacking']
+++

FPGAs are pretty cool pieces of hardware for tinkering with, and have become
remarkably easy to approach as a hobbyist in recent years. Boards like the
[TinyFPGA BX](https://www.crowdsupply.com/tinyfpga/tinyfpga-bx) don't require
any special hardware to use and can provide a simple platform for
modestly-scoped projects or just for learning.

While historically the software tools for programming FPGAs are proprietary and
provided by the hardware manufacturer, [Symbiflow](https://symbiflow.github.io/)
(enabled and probably inspired by earlier work like [Project
IceStorm](http://www.clifford.at/icestorm/)) provides [completely free and
open-source tooling](https://www.youtube.com/watch?v=-xyAauPa__s) and
documentation for programming some FPGAs, significantly lowering the cost of
entry (most vendors provide some free version of their design software but
limited to lower-end devices; a license for the non-free version of the software
is well into the realm of "if you have to ask, you can't afford it") and
appearing to yield better results in many cases.[^hardware-support]

[^hardware-support]: FPGA vendors don't publish all the information required to
                     build configuration bitstreams for their hardware, possibly because they wish
                     to support their side business in selling design tool licenses- this despite the
                     fact that (anecdotally, since I can't recall where I saw it) many FPGA
                     developers say that vendor tooling is one of the biggest annoyances in their
                     work. The open-source tools require a fair amount of painstaking
                     reverse-engineering of chips to create!

---

As somebody who finds it fun to learn new things and experiment with new kinds
of creations, FPGAs are quite interesting to me- they're quite complex devices
that enable very powerful creations, with excellent depth for mastery. While I
did some course lab work with Altera FPGAs in university (and a little bit of
chip design/layout later), I'd call those mostly canned tasks with
easily-understood requirements and problem-solving approaches; it was sufficient
to familiarize myself with the systems, but not enough to be particularly
useful.

The announcement of [Fomu](https://www.crowdsupply.com/sutajio-kosagi/fomu)
caught my interest because I was aware of the earlier [Tomu](https://tomu.im/)
but wasn't sufficiently interested to try to acquire any hardware. With Fomu
however, I'm rather more interested because it enables interesting capabilities
for playing with hardware- others have already demonstrated small
[RISC-V](https://en.wikipedia.org/wiki/RISC-V) CPUs running in that FPGA
(despite its modest logic capacity), for instance.

Even more conveniently for being able to play with Fomu, I've been in contact
with [Mithro](https://twitter.com/mithro) who is approximately half of the team
behind Fomu and gotten access to a stockpile of "hacker edition" boards that
have been hand-assembled but not programmed at all. With slightly early access
to hardware, I've been able to do some exploration and re-familiarize myself
with the world of digital logic design and figure out the hardware.

<!--more-->

## Hardware

In summary, Fomu is a small (9.4 by 13 by 0.6 millimeters) circuit board with a
[Lattice
ICE40UP5K-UWG30](https://www.latticesemi.com/Products/FPGAandCPLD/iCE40UltraPlus)
FPGA, a 16-megabit SPI Flash for configuration (and other data) storage, a
single RGB LED for blinkiness and a 48 MHz MEMS oscillator to provide a clock.

{{< figure src="/2019/fomu-0.0-front.jpg"
    caption="Board component side. The other side is mostly just the USB pads."
    alt="A photo of the board component side. There are seven integrated circuits and bare copper pads labelled clockwise from the top left 4, 3, 2, 1, G, R, O, I, C, S and V." >}}

The whole thing is built so it can fit inside a standard USB port. Production
boards are meant to ship with a [USB
bootloader](https://github.com/im-tomu/foboot) that allows new configurations to
be uploaded to the board only via that USB connection, but hacker boards are
provided completely unprogrammed (and untested).

### Schematic

Before we can make the hardware do something, we'll need to understand how
everything is put together:

<a href="/2019/fomu-schematic.png">
{{< figure src="/2019/fomu-schematic.png"
    alt="A schematic for 'TomuUltraPlus' created in Kicad. The schematic is separated into 7 logical blocks: power regulation and decoupling, SPI flash, MEMS clock, RGB LED, ICE40 power, ICE40 PLL power filter and ICE40 IO." >}}
</a>

Unfortunately, this schematic leaves some things to be desired. While it does
allow us to see what parts are actually on the board and generally how they're
connected, it fails to clearly mark the external connections- power and data
lines on the USB connector, test points and utility I/O pads.

The USB connections are easy to figure out, however; it's a standard pinout so
we can easily identify which physical pads on the board correspond to VUSB (5V
supply), ground and the two data lines (USBP, USBN). Rather trickier to work out
is the function of each of the test points on the board, though there is a
[provided template for laser-cutting a programming
jig](https://github.com/im-tomu/fomu-hardware/tree/master/hacker) which provides
some hints:

{{< figure src="/2019/fomu-laser-jig.svg"
    width="320px"
    caption="Here red and green lines are cuts, while black is raster engraving for marking."
    alt="Four rounded squares with lines and shapes marking where laser cuts or engraving should be done. There are seven holes that align on two of the squares to permit pins to pass through, and one of them has text denoting the purpose of each pin." >}}

This jig is meant to be built up by stacking four layers of material, engraving
a small pocket in the bottom to hold the board to program and inserting pogo
pins in the small holes to contact with the test points on the board. This
template helps us in that it has labels for the test points, though! All of the
test points are clearly identified, except it's unclear what voltage is expected
on the power supply.

By inspecting the board myself, I eventually determined that the test point for
supplying power (marked VCC on the programming jig template) is downstream of
the 3.3V regulator (not connected to the USB power supply pad) so it expects
3.3 Volts for programming.

### Convenient pinout diagram

By way of improving the schematic, here's that same photo of the board with the
signal names from the schematic pointed out on each of the pads, and the
individual chips pointed out.

{{< figure src="/2019/fomu-0.0-annotated.jpg" >}}

And the same in tabular form for easy searching:

Silkscreen | Schematic | Description
-----------|-----------|-----------------------------
         V | +3V3      | 3.3V rail
         S | CS        | SPI chip select (active low)
         C | SCK       | SPI clock
         I | MISO      | SPI MISO
         O | MOSI      | SPI MOSI
         R | CRESET_B  | FPGA reset (active low)
         G | GND       | Ground
         1 | PIN1      | User I/O 1
         2 | PIN2      | User I/O 2
         3 | PIN3      | User I/O 3
         4 | PIN4      | User I/O 4

## Bootstrapping

My first task in attempting to
bootstrap a board and load some configuration on it was building a programming
jig. Given there was already a template for a laser-cut acrylic one and I have
access to a benchtop laser cutter, this was easy:

<a href="/2019/fomu-laser-jig-assembled.jpg">
{{< figure src="/2019/fomu-laser-jig-assembled-small.jpg" >}}
</a>

It's a little bit ugly because the pogo pins I had ready access too are too
small to nicely fit in the laser-cut holes so I had to carefully glue them in
place.

---

Actually programming a board can be done with the
[fomu-flash](https://github.com/im-tomu/fomu-flash) utility running on a
Raspberry Pi. I conveniently had a Raspberry Pi 2 to hand, so a little wiring to
the Pi's GPIO header had a jig that should work. Unfortunately, it didn't- all I
got out when trying to make it identify the on-board flash chip was 1s:

```text
$ fomu-flash -i
Manufacturer ID: unknown (ff)
Memory model: unknown (ff)
Memory size: unknown (ff)
Device ID: ff
Serial number: ff ff ff ff
Status 1: ff
Status 2: ff
Status 3: ff
```

I gave up on that hardware after spending a while experimenting with it, and
decided to design a custom programming jig that might be a little easier to
ensure pin alignment is good. This is a little bit tricky because the minimum
pitch of the test points is just 1.8 mm, which is not large enough for the
0.1-inch (2.54 mm) DuPont connectors commonly used for prototyping and desirable
in this case because they're very easy to connect to the Raspberry Pi's GPIO
header.

### A better jig

Fortunately, I also have access to rather sophisticated prototyping tools and
had some nice parts handy from other projects. In particular, a [Form 2
stereolithographic 3D printer](https://formlabs.com/3d-printers/form-2/) and
some good pogo pins, [Preci-dip
90155-AS](https://www.digikey.com.au/product-detail/en/90155-AS/1212-1871-ND/5451894).
I computer-modeled a jig to be 3d-printed that should be both compact and
robust, pictured below (see the end of this post for downloadable resources):

{{< figure src="/2019/fomu-jig-iso.png"
    caption="Isometric view with all edges visible" >}}

<div style="display: flex; align-items: baseline;">
{{< figure src="/2019/fomu-jig-top.png"
    caption="Top view" >}}

{{< figure src="/2019/fomu-jig-bottom.png"
    caption="Bottom view" >}}
</div>

### Features

The design takes great advantage of the flexibility of 3d printing for
fabrication: it is easy to install the pogo pins off-vertical by making the
(press-fit) holes at an arbitrary angle; this would be very difficult with
conventional fabrication, but it allows the spacing of the pins at the top of
the jig to be large enough that 2.54mm connectors can be used, despite the pad
spacing on the board being only 1.8mm.

On the bottom side, there are several narrow features that act as a shelf to
support the board (which is 0.6mm thick) so its outside surface is flush with
the bottom surface of the jig. A semicircular boss on one side mates with the
cutout on the PCB to key the jig so it is obvious when the board is correctly
oriented in the jig. A small cutout on one edge allows a tool to be inserted to
pull the board out if needed, because the fit is close enough that it might
stick sometimes (or a tool could be pushed through from the top).

As a manufacturability consideration, the top surface has a slant between
opposite corners. This improves the print quality on a Form 2- because
dimensions on that side are not critical the part is designed to be printed with
that side "down" (actually up, once in the printer) and supports attached to it
on that end. By allowing the printer to gradually build up a slope rather than
immediately build a plane, it can better produce the intended shape- an earlier
version of the design with a flat top had a very rough finish because large and
thin layers of material tend to warp until enough material is built up to be
self-supporting.

---

The choice of pogo pins in particular is key, since they're made with a small
shoulder and retaining barbs that allow them to be easily press-fit into a
connector shell:

{{< figure src="/2019/90155-as-drawing.png"
    alt="Mechanical drawing of a Preci-dip 90155-AS pogo pin. It is 10mm long, with 1.4mm stroke. The central area along its length has several barbs and a narrow shoulder with 10 micron tolerances." >}}

The one downside of these pins is the short tail, intended for mounting to a
circuit board. While the aforementioned DuPont connectors can be mated to the
tail, they are not very secure and come off at the slightest force. A revised
design choosing parts for their function and not just immediate availability
might prefer to use a part like
[90101-AS](https://www.digikey.com.au/product-detail/en/preci-dip/90101-AS/1212-1860-ND/5451883),
which is intended for wire termination rather than board mounting- then wires
can be securely attached to the pin rather than tenuously placed on it. My
workaround that didn't involve buying more parts was carefully gluing the wires
in place, which seems to work okay.


## Programming

Having built a jig that I could be confident would work correctly, we now return
to the problem of actually programming the board. Connecting the new jig to my
Raspberry Pi in the same way I did the first one, it failed in the same way-
reading all 1s.

At this point I was rather stumped, with a few possible explanations for the
problems:

1. Both jigs are unreliable
2. I'm wiring the jigs up incorrectly
3. Software on my Pi is configured incorrectly
4. All of the Fomus I tried were faulty

To discount the first two possibilities, I was able to borrow Mithro's
professionally-built jig that already had a Raspberry Pi 3 connected to it. I
didn't have any credentials to log in to that Pi and use it interactively
however, so I was limited to checking its wiring and carefully ensuring I
connected my Pi to the jig in the same way, then try programming again. This
also failed.

<a href="/2019/mithro-programmer.jpg">
{{< figure src="/2019/mithro-programmer-small.jpg"
           caption="Mithro's jig. It seems very cleverly built to me, clearly designed by somebody with a lot of experience designing these kinds of fixtures." >}}
</a>

Having tried that I had to assume my Pi was somehow misconfigured, since it
seemed increasingly unlikely that I was doing anything wrong and it seemed
implausible that all of my boards were faulty. I eventually took the SD card out
of the other jig's Pi and inspected the software it would run by connecting it
to another computer. This amounted to the same `fomu-flash` program I was using,
so I inspected the system configuration in `/boot/config.txt` and found a
variety of non-default options that seemed plausibly useful. Ultimately, I found
some magic words:

```text
dtparam=spi=on
```

This option makes the kernel on the Pi expose a hardware-assisted SPI
peripheral, which seems like an obvious missing option until you realize that
`fomu-flash` actually bit-bangs SPI because the hardware support is insufficient
for this application. In any case, I did find that turning that option on makes
everything work correctly:

```text
$ fomu-flash -i
Manufacturer ID: Adesto (1f)
Memory model: AT25SF161 (86)
Memory size: 16 Mbit (01)
Device ID: 14
Serial number: ff ff ff ff
Status 1: 02
Status 2: 00
Status 3: ff
```

I [reported the bug](https://github.com/im-tomu/fomu-flash/pull/3) and made a
note of this in the documentation so hopefully nobody else has to deal with that
problem in the future, even if the root cause is mystifying.

## Success!

With the ability to talk to the configuration flash, it's then possible to write
an actual bitstream. To avoid needing to write one myself, it's easy to take the
[LED blinker example](https://github.com/im-tomu/fomu-tests/tree/master/blink)
from the fomu-tests repository:

```text
fomu-tests/blink$ make FOMU_REV=hacker
...

Info: constrained 'rgb0' to bel 'X4/Y31/io0'
Info: constrained 'rgb1' to bel 'X5/Y31/io0'
Info: constrained 'rgb2' to bel 'X6/Y31/io0'
Info: constrained 'clki' to bel 'X6/Y0/io1'
Warning: unmatched constraint 'spi_mosi' (on line 5)
Warning: unmatched constraint 'spi_miso' (on line 6)
Warning: unmatched constraint 'spi_clk' (on line 7)
Warning: unmatched constraint 'spi_cs' (on line 8)
Info: constrained 'user_1' to bel 'X12/Y0/io1'
Info: constrained 'user_2' to bel 'X5/Y0/io0'
Info: constrained 'user_3' to bel 'X9/Y0/io1'
Info: constrained 'user_4' to bel 'X19/Y0/io1'
Warning: unmatched constraint 'usb_dn' (on line 13)
Warning: unmatched constraint 'usb_dp' (on line 14)

...

Info: Device utilisation:
Info:            ICESTORM_LC:    33/ 5280     0%
Info:           ICESTORM_RAM:     0/   30     0%
Info:                  SB_IO:     5/   96     5%
Info:                  SB_GB:     1/    8    12%
Info:           ICESTORM_PLL:     0/    1     0%
Info:            SB_WARMBOOT:     0/    1     0%
Info:           ICESTORM_DSP:     0/    8     0%
Info:         ICESTORM_HFOSC:     0/    1     0%
Info:         ICESTORM_LFOSC:     0/    1     0%
Info:                 SB_I2C:     0/    2     0%
Info:                 SB_SPI:     0/    2     0%
Info:                 IO_I3C:     0/    2     0%
Info:            SB_LEDDA_IP:     0/    1     0%
Info:            SB_RGBA_DRV:     1/    1   100%
Info:         ICESTORM_SPRAM:     0/    4     0%

...

Built 'blink' for Fomu hacker

$ fomu-flash -w blink.bin
Erasing @ 018000 / 01969a  Done
Programming @ 01959a / 01969a  Done
$ fomu-flash -v blink.bin
Reading @ 01969a / 01969a Done
```

Programming that to the board yields a blinking LED as expected, so I've
achieved success in the basic form of this project by getting the FPGA to do
something. Further exploration will involve writing gateware with
[Migen](https://github.com/m-labs/migen) rather than straight Verilog (because I
find Verilog to be rather tedious to write) and trying to build a system around
a [RISC-V](https://en.wikipedia.org/wiki/RISC-V) CPU (because that sounds
interesting).

## Resources

If you want to make your own copy of the programming jig or just explore it,
you've got several options:

 * [View the model at OnShape](https://cad.onshape.com/documents/9f74d5e65249e3a7ac623708/w/687eaa8007de0437f2750c90/e/d8f52334f441612d76b97de0).
   This will allow you to view and make changes to the parametric model, which is
   what you'll need to make most useful changes to it.
 * [View the STL online](/2019/fomu-stl-viewer/). A quick and dirty way to get
   an interactive view of the model.
 * [Download the STL](/2019/fomu-jig.stl). If you just want to try to 3D print
   your own, this is all you need. It may also be useful if you want to make
   changes using a 3d modeling program (rather than a CAD program).
 * [Download a Solidworks part file](/2019/fomu-jig.sldprt). This was just
   exported from OnShape, but you might prefer this if you want to use
   SolidWorks to edit the model.

All of the official documentation for Fomu is [available on
Github](https://github.com/im-tomu). For basic information (such as what I
referred to when writing up this project), that's a great starting point.

I designed the programming jig in [OnShape](https://www.onshape.com/) which is a
pretty good and very convenient CAD tool.
