---
author: tari
comments: true
date: 2012-05-15 18:32:12+00:00
slug: divergence-meter-high-voltage-supply-and-fet-drivers
title: 'Divergence meter: high-voltage supply and FET drivers'
wordpress_id: 627
categories:
- Embedded Systems
- Hacking/Tweaking
tags:
- anime
- divergence-meter
- hardware
- msp430
- soldering
---

I got some time to work on the divergence meter project more, now that the new
board revision is in.  I assembled the boost converter portion of the circuit
and plugged in a signal generator to see what sort of performance I can get out
of it.  The bad news: I was rather dumb in choosing a FET, so the one I have is
fast, but can't be driven fully on with my 3.3V MSP430.  Good news is that with
5V PWM input to the FET, I was able to handily get 190V on the Nixie supply
rail.

Looking at possible FET replacements, I discovered that my choice of part, the
IRFD220, appears to be the only MOSFET that Mouser sell that's available in a
4-pin DIP package.  Since it seems incredibly wasteful to create another board
revision at this point, I went ahead with designing a daughterboard to plug in
where the FET currently does.

I got some ICL7667 FET driver samples from Maxim and have assembled this unit
onto some perfboard, but have not yet tested it.  Given I was driving the FET
with a 9V square wave while testing, it's possible that I blew out the timer
output to the FET on my microcontroller while testing.  Next time I get to work
on this, I'll be exercising that output to see if I blew it with high voltages,
and connecting up the perfboard driver to try the high voltage supply all driven
on-board.

<figure>
    <img src="/images/2012/DSC_2917.jpg" />
    <figcaption>Board with assembled power supplies</figcaption>
</figure>

<figure>
    <img src="/images/2012/DSC_3005.jpg" />
    <figcaption>FET driver bodge assembled on perfboard. Connections are
    annotated.</figcaption>
</figure>

