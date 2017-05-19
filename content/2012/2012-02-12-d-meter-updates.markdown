---
author: tari
comments: true
date: 2012-02-12 20:17:30+00:00
slug: d-meter-updates
title: D-meter updates
wordpress_id: 596
categories:
- Embedded Systems
tags:
- divergence-meter
- hardware
- jtag
- msp430
- soldering
- spy-bi-wire
---

I've been able to do some more work on the divergence meter now.  The
university's labs made short work of the surface-mount soldering, but there were
some hitches in the assembly and testing phase, in which I discovered some of
the part footprints were wrong, and it was a bit of trouble getting the
programmer working.

I was able to work around most of the bad footprints, but some of them were
barely salvageable, since the through-holes were too small.  I was able to drill
them out on the drill press in the lab, but that left me with very small contact
areas to solder to, so I had a few hideous solder joints.

After getting the power supply portions of the board soldered came getting the
MSP430 talking to my [MSP430
Launchpad](http://www.ti.com/ww/en/launchpad/launchpad.html?DCMP=mcu-launchpad&HQS=launchpad),
which I'm using as a programmer.  Initial attempts to program the micro were met
with silence (and mspdebug reporting no response from the target), but the
problem turned out to be due to using cables that were too long- I had simply
clipped test leads onto the relevant headers, yielding a programming cable that
was around 1 meter long, while the MSP430 Hardware Tools User's Guide
([SLAU278](http://www.ti.com/lit/ug/slau278h/slau278h.pdf)) indicates that a
programming cable should not exceed 20 cm in length.   I assembled a shorter
cable in response (by soldering a few wires onto the leads of a female 0.1"
socket) and all was well.

The most recent snag in assembly was the discovery that I had botched some of
the MSP430's outputs.  I had connected the boost converter's PWM input to Timer
A output 0 on the micro, but I discovered while writing the code to control the
boost converter that it's impossible to output PWM on output module 0, due to
the assignment of SFRs for timer control.  The user's manual for the chip even
mentions this, but I simply failed to appreciate it.

I _could_ have cut a few traces and performed a [blue wire
fix](http://catb.org/jargon/html/B/blue-wire.html), but it seemed like a very
poor solution, and I was still concerned about the poor contact on the other
vias I had to drill out, so I bit the bullet and created a new revision of the
board with correct footprints for all the parts, and a more comprehensive ground
plane (hopefully reducing inductive spiking on the optocoupler control lines).
I've now sent revision 1.1 out to be made, so improved boards will be here in a
few weeks.  Until then, I'll be working on the software a bit more, and
hopefully updating this post with photographs.
