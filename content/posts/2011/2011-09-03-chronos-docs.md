---
author: tari
comments: true
date: 2011-09-03 02:41:49+00:00
slug: chronos-docs
title: Some Chronos Documentation
wordpress_id: 253
categories:
- Embedded Systems
tags:
- documentation
- Hacking/Tweaking
- Software
---

Moving on from my previous post (in which I muttered sullenly about brain-dead
packaging of software for Linux), I began hacking on my Chronos proper tonight.
Read on for some juicy tidbits.

<!-- more -->

## Initial build

The first order of business was to set up a toolchain targeting MSP430. Since
I'm running [Arch](https://www.archlinux.org/) on my primary development system,
it was a simple matter to build
[gcc-msp430](https://aur.archlinux.org/packages.php?ID=30132) from the AUR.

With that, I was ready to try compiling things. I assumed (correctly) that the
provided firmware would not build on GCC without modification, but a little
googling pointed me to [OpenChronos](https://github.com/poelzi/OpenChronos/),
which effectively takes the stock firmware, makes it build with any of several
compilers (TI's compiler included with [CCS](http://www.ti.com/tool/ccstudio),
[IAR's](http://web.archive.org/web/20110806113542/http://www.iar.com:80/website1/1.0.1.0/220/1/),
and [GCC](http://sourceforge.net/projects/mspgcc/)). Come to think of it, LLVM
has an experimental MSP430 backend that might be interesting to try out.

One git checkout and an invocation of make later, and I was staring at a
screenful of errors. "How auspicious," I thought. The first part of the fix was
easy-- I simply needed msp430-libc for some of the more specialized functions
that don't map well into straight C- things like interrupt handling (which is in
msp430-libc's signal.h for some reason) or machine-specific delays.

The remaining compilation errors after grabbing libc were rather more
troublesome, however. There were two main classes of problem.

  * Uses of types at some specific bit-width (such as `uint16_t`). These were
    easily resolved by strategic inclusion of stdint.h, but I'm not very happy
with how I had to do it. Spraying header inclusions all over the source code is
a poor way to fix things.
  * Large delay constants. There were two cases in the radio control code which
    adjusted the microcontroller's voltage regulator, which then requires a
rather long delay before the system can be considered stable again. The solution
in code is simply to delay for as many as ~800000 clock cycles. Normally that
wouldn't be a problem, but some of the delay constants were larger than the
input type to the `__delay_cycles` function could hold. My hacky solution was to
split those into two calls of half the length, which seemed to work out OK.

After a while to figure out the compilation problems, I was able to build a
firmware image. After the struggles I had with unpacking TI's sample code and
demo applications, it was fortunately painless to actually run them. I just
ensured I had Tcl/Tk installed and ran the Chronos Control Center application.
Putting the Chronos itself into WBSL (Wireless BootStrap Loader) mode and
clicking a few times was easy, and I quickly got my new firmware image flashed
onto the CC430.

## Preparing for mods

Now that I had a known-working toolchain, it was time to get to work actually
implementing some of the toy features I wanted to add. Since the single most
interesting feature of the hardware is the radio (although the low-power
capabilities of the MSP430 are quite shiny as well), I set out to see how I
could communicate with the watch from my PC.

One of the USB dongles that comes packaged with the Chronos is a USB wireless
access point, basically just a CC1111 (6801 core with USB and RF transciever). I
understand that earlier revisions of the demo applications didn't include source
code for the software running on the CC1111, but the current release includes
it. Some people had taken a bit of trouble to [reverse-engineer the
communications](http://e2e.ti.com:80/support/microcontrollers/msp430/f/166/t/32714.aspx),
but that alone isn't very useful documentation. With that in mind, I set out to
document for myself how to communicate with the RF access point and go through
that to talk to the Chronos.

Setting up communications is easy, fortunately. The CC1111 is programmed to
enumerate as a USB CDC, so one must only open the virtual serial port it creates
with a 115200 bps baud rate with 8 data bits and 1 stop bit. (If that's not
terse enough for you: 115200 baud, 8n1.)

With virtual serial communications up, the upper-level protocol is rather easy-
it consists of packets of at least 3 bytes each, where the first one is always
0xFF. Byte 2 provides a command ID, and byte 3 specifies the total packet size,
including the overhead (so the minimum valid size is 3). Anything more in the
message is interpreted based on the command ID.

### Command IDs

There are a number of command IDs defined, but only a few that are of particular
interest. In the hopes that somebody else will find it useful, I include my raw
notes on the command bytes below.

As a little bit of context, the system can run on either of two different radio
protocols. TI's SimpliciTI is a protocol designed mainly for communication
between low-power nodes in a network, while BlueRobin is a radio protocol
developed by IAR Systems, notable with the Chronos because it allows
communication with a [heart rate
monitor](http://www.bm-innovations.com/index.php/ez430-chronos) developed by BMi
GmbH.

```
Command bytes:
    BM_GET_PRODUCT_ID
        Dumps 32-bit product ID into the usb buffer
    BM_GET_STATUS
        returns system_status (some file-scope var?)
== bluerobin
    BM_RESET
        Turns off bluerobin
    BM_START_BLUEROBIN
        Start bluerobin (set a flag, actually), stop simpliciti if that's going
    BM_SET_BLUEROBIN_ID
    BM_GET_BLUEROBIN_ID
    BM_SET_HEARTRATE
    BM_SET_SPEED
== simpliciti RX
    BM_START_SIMPLICITI
        Start simpliciti, stop bluerobin if that's going
    BM_GET_SIMPLICITIDATA
        Dump the 4 bytes from the simpliciti_data buffer to USB
        also mark simpliciti data as read
        If no pending data, usb_buffer[PACKET_BYTE_FIRST_DATA] = 0xFF
    BM_SYNC_START
        nop
    BM_SYNC_SEND_COMMAND
        copy packet from USB to simpliciti buffer and flag for tx ready
    BM_SYNC_GET_BUFFER_STATUS
        1-byte payload packet out, = var simpliciti_sync_buffer_status
    BM_SYNC_READ_BUFFER
        copy simpliciti_data buffer out to USB
    BM_STOP_SIMPLICITI
        Flag to turn off simpliciti

== WBSL
    BM_START_WBSL
        flag to start WBSL, turn off bluerobin/simpliciti if active
    BM_STOP_WBSL
        stop wbsl, turn off LED
    BM_GET_WBSL_STATUS
        copy back var wbsl_status
    BM_GET_PACKET_STATUS_WBSL
        copy back var wbsl_packet_flag or WBSL_ERROR if wbsl is off
    BM_GET_MAX_PAYLOAD_WBSL
        copy back max number of bytes allowed in wbsl payload
    BM_SEND_DATA_WBSL
        set wbsl_packet_flag to WBSL_PROCESSING_PACKET
        deocode packet and spew it to the 430
== self-test
    BM_INIT_TEST
    BM_NEXT_TEST
    BM_GET_TEST_RESULT
    BM_WRITE_BYTE
        write a byte to the access point's Flash memory
        first data byte is the value to write
        second and third are address, little-endian (2 is lsb, 3 => msb)
        must be in test mode (precede this with BM_INIT_TEST)
```

(Command and system status constants are defined in `BM_API.h`, FWIW.)

Knowing all the commands, it's pretty easy to pull out the useful ones.
BM_START_SIMPLICITI makes the access point switch into SimpliciTI mode, and
sending BM_SYNC_START allows direct communication through the radio link with
BM_SYNC_{SEND,READ}_BUFFER functions.

## More.. later

This is as far as I'm going to go with this adventure for today, but there's
more to come in the coming days (hopefully, assuming my motivation holds out).
This is just preliminary documentation-- I'm hoping to create a more formal set
of documents providing a whirlwind overview of how to get hacking on the
Chronos, but I feel this is an excellent start.
