---
layout: page
title: RX Bitrate Calculator
date: 2011-12-11 01:23:09.000000000 -07:00
categories: []
tags: []
status: publish
type: page
published: true
---

This is an extremely simple GUI for calculating ideal configuration register
values for serial communications (UART, SPI, I2C) on [Renesas RX
microcontrollers](http://www.renesas.com/products/mpumcu/rx/index.jsp) It's
based on the information in the RX62N/RX621 user's guide, but may apply to other
chips as well. Given the target bit rate and CPU clock, it generates the
configuration register values which yield the smallest error.

<figure>
    <img src="/images/2011/62nsci.png" />
</figure>

[Download source package](/images/2011/RXSCI_Calc.zip) for Visual Studio 2010.

Includes binaries for .NET 4 or better (see bin subdirectory), should work
correctly under [Mono](http://www.mono-project.com/Main_Page) without
modification.

## Web calculator

Considering how simple the above program is and how limited its utility is, I
ported it to Javascript so it can be run in a web browse. Embedded below, or
[standalone](brr-calc.html)

<iframe src="brr-calc.html"></iframe>

