---
layout: page
title: The TI-86
date: sometime in 2008
last_revised: 2011-07-29 22:23:20.000000000 -06:00
categories: []
tags: []
status: publish
type: page
published: true
meta:
  _edit_last: '1'
  _wp_page_template: default
author:
  login: tari
  email: peter@taricorp.net
  display_name: tari
  first_name: Peter
  last_name: Marheine
---

This page contains some of my notes on features of the TI-86, which first
appeared on my Freewebs site sometime around 2005. I've made an effort to
correct and clarify some things, but it may still be only partially accurate in
some places.

For all things TI-86, readers may find ["The Guide"](http://guide.ticalc.org/)
useful.

## Ports

### 0 - LCD memory map

Port 0 controls the memory address the display hardware will read from when
refreshing the screen. (Unlike the 83+ and similar, the 85 and 86 have
memory-mapped displays, which make drawing much faster in software.) To get the
address read, take the value in port 0, add 0xC0, and multiply by 0x100. For
example, the typical value of 0x3C puts the display buffer at 0xFC00. Put
another way, the value of the port is the high byte of the buffer address minus
0xC0. For that reason, the display buffer must always be in the uppermost 16k of
memory.

The block of memory at 0xCA00 is often used as a secondary display buffer
(either for greyscale via buffer-flipping or just double-buffered drawing). The
system's graph buffer is based at 0xCA06 and evidently whatever's immediately
below that isn't critical, but the 6 bytes at 0xCDFA *are* potentially
important, so you should back those up if using the buffer at 0xCA00.

Bit 1 of port 3 reads reset if the LCD is currently refreshing, which can be
useful for preventing tearing when flipping between buffers (vsync!).

### 1 - Keypad

This one behaves just like the other z80 calculators. Write a mask out and read
back a value with bits reset corresponding to the keys currently depressed
within the corresponding group. The following table gives the mask for each
group and the keys corresponding to each bit on a per-group basis (all values in
hex, unused values are blank):

<table>
<tbody>
<tr>
<th></th>
<th>3F</th>
<th>5F</th>
<th>6F</th>
<th>77</th>
<th>7B</th>
<th>7D</th>
<th>7E</th>
</tr>
<tr>
<th>7</th>
<td>More</td>
<td>Alpha</td>
<td>x-Var</td>
<td>Del</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<th>6</th>
<td>Exit</td>
<td>Graph</td>
<td>Table</td>
<td>Prgm</td>
<td>Custom</td>
<td>Clear</td>
<td>;</td>
</tr>
<tr>
<th>5</th>
<td>2nd</td>
<td>Log</td>
<td>Sin</td>
<td>Cos</td>
<td>Tan</td>
<td>^</td>
<td>;</td>
</tr>
<tr>
<th>4</th>
<td>F1</td>
<td>LN</td>
<td>EE</td>
<td>(</td>
<td>)</td>
<td>÷</td>
<td>;</td>
</tr>
<tr>
<th>3</th>
<td>F2</td>
<td>x<sup>2</sup></td>
<td>7</td>
<td>8</td>
<td>9</td>
<td>×</td>
<td>Up</td>
</tr>
<tr>
<th>2</th>
<td>F3</td>
<td>,</td>
<td>4</td>
<td>5</td>
<td>6</td>
<td>-</td>
<td>Right</td>
</tr>
<tr>
<th>1</th>
<td>F4</td>
<td>STO&gt;</td>
<td>1</td>
<td>2</td>
<td>3</td>
<td>+</td>
<td>Left</td>
</tr>
<tr>
<th>0</th>
<td>F5</td>
<td>;</td>
<td>0</td>
<td>.</td>
<td>(-)</td>
<td>Enter</td>
<td>Down</td>
</tr>
</tbody>
</table>

### 3 - ON key, power, interrupt mask

Bit 3 controls whether the LCD is on. Write it set to turn the display off, and
reset to turn it on. Read bit 3 to get the current state of the ON key (which is
conspicuously absent from the above table, since it's more closely tied to
system interrupts than the rest of the keypad). Reads reset when the key is
down, otherwise set.

My notes mention you should reset the system flag in bit 4 of (IY+9) when you
want to check the ON key's status, but not why you would want to do that.
Presumably the default ISR does something with the ON key when that bit is set.

The lower bits (I assume 0-2, but not sure) of this port control what interrupt
sources will actually fire an interrupt in the CPU. My notes are incomplete
here, but I know bit 0 is for the ON key. I assume the other two are timer
interrupts and link activity, but that's mostly just speculation.

### 4 - Power management

Write bit 0 set for normal power mode, or reset for low-power mode. Not sure
what all this does, but if you want to work like a "real" power-down write this
bit reset before halting the CPU (..and waiting for an interrupt). This port
reads back the last value written to it.

### 5, 6 - Memory paging

Port 5 controls memory paging in bank 1 (0x4000-0x7FFF), and port 6 does the
same on bank 2 (0x8000-0xBFFF). I'm not sure exactly what ranges are valid, but
one should only need to change these in rare occasions. Both read the last value
written, which is useful if you want to flip pages and restore them to the old
value when you're done.

### 7 - Link port

Like the other Z80 calculators made by TI, the link port is two lines with
pull-up resistors on both lines. Writing bit 0 or 1 set pulls the corresponding
line low, which can be read on the other end of the link.

## Interrupts

### Hooks

The default IM 1 ISR includes a hook you can insert to have your own code called
each time an interrupt fires. Place up to 200 bytes of code at 0xD2FE and
calculate a checksum, then set bit 2 of the flag at (IY+0x23) as follows:

```
    ld de,$28                       ; Initial value
    ld a,(_alt_interrupt_exec)
    ld hl,_alt_int_chksum + $28
    add a,(hl)
    add hl,de
    add a,(hl)
    add hl,de
    add a,(hl)
    add hl,de
    add a,(hl)
    add hl,de
    add a,(hl)
    ld (_alt_int_chksum),a
    set 2,(iy + $23)                ; Enable user routine
    ei                              ; Ensure interrupts are enabled</pre>
```

### Power-off

Between port 4 (above) and a few flags, making the machine look like it's
properly off (on these calculators, waiting for an interrupt is as close to off
they get without removing the batteries) is pretty easy:

```
    di
    ld      a,1
    out     ($03),a                      ; Wait for ON key int
    res     shift2nd,(iy+shiftflags)     ; Clear 2nd status
    res     onRunning,(iy+onflags)       ; Calc no longer running
    ei
    halt                                 ; Wait for on key interrupt
```

### 'Down-Left Bug'

Apparently something in the default ISR can crash the calculator if you hold the down and left arrow keys. Setting bit 2 at (IY+0x12) is one way to avoid it (which I assume also has some other effect, but my notes don't specify), or you can install your own interrupt handler in IM 2 which bypasses the flawed logic:

```
    ex af,af'
    exx
    in a,(3)
    rra
    push af         ; 
    call nc,$01A1   ; Call out to system ISR - not needed if you only
    pop af          ; read the keyboard via port 1 rather than the ROM calls
    ld a,9
    adc a,0
    out (3),a
    ld a,$0B
    out (3),a
    ex af,af'
    exx
    ei
    reti
```

### Speedy processing

The above interrupt to be installed in IM 2 is evidently somewhat faster than the system ISR. If you don't want to or are unable to install the vector table necessary for IM 2 setup, similar speed can be achieved by installing an interrupt hook as described earlier in this document, then popping the top value from the stack into oblivion and returning at your leisure:

```
    ; your interrupt code here
    inc sp
    inc sp
    reti    ; ISR done
```

## Error handlers

Some ROM calls will throw system errors, not nicely returning error status. You
can register an error handler routine by calling `_InstError` with HL pointing to
your handler code. If/when your handler is invoked (by an error), the error code
will be in A. Do not return from the handler (the invoker plays with the stack
before calling your routine), instead do whatever you like and tell the system
to put your program away by calling `_jforcecmdnochar` when done with reporting
the error or cleaning up or whatnot.
