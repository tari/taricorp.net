---
layout: page
title: Casio Prizm Binaries
date: 2012-08-09 14:29:45.000000000 -06:00
categories: []
tags: []
status: publish
type: page
---

This page documents details of the Casio Prizm graphic calculator's processor,
intended for developers seeking to create software for that platform. Much of
this information applies to any system with a SuperH processor, though.

# Basic facts

The calculator's processor is a Renesas SH4A family unit without an FPU. It is
believed to be a SH7724 variant, running at 58 MHz by default.

The processor runs in **big-endian** mode. Additional details of the system may
be found within Cemetech's
[WikiPrizm](http://prizm.cemetech.net/index.php?title=Technical_Info) project.

The closest target triple to build GCC for, given what we know above, is
`sh3eb-elf-unknown`. This is often shortened to simply
`sh3eb-elf`. The Prizm's operating system is built with the Renesas
compiler, so the Hitachi ABI[^hitachi] must be used. The SH3
target for GCC is not a perfect match to the target processor, so an additional
option is required to select the SH4A target without FPU.

Thus, the compiler options required to compile software for the Prizm are
`-m4a-nofpu -mhitachi`.

[^hitachi]: The Hitachi ABI is used by the official SH compiler, which was
    originally developed by Hitachi in conjunction with the processor before being
    transferred to Renesas Technology under a joint venture between Hitachi and
    Mitsubishi Electric.

# ABI

GCC for the SH processor supports two (mostly similar) ABIs (application binary
interface). It uses the GNU ABI by default, but may instead be instructed to use
the Hitachi ABI for compatibility with code built with the Renesas compiler by
specifying `-mhitachi` at compile time.

Within this document **aggregate** types are defined as C structs or unions.
Compare to **integral** types, which are all others (char, int, pointer..). A
procedure's stack frame is a region of memory allocated from the stack at the
beginning of the procedure.

*This section has been adapted from the <a href="http://www.kpitgnutools.com/manuals/SH-ABI-Specification.html">SH ABI specification</a> from <a href="http://kpitgnutools.com/">KPIT Cummings Infosystems</a>.*

## Byte Ordering

The SH architecture supports both big- and little-endian byte ordering.
Big-endian code and little-endian code may not be mixed in the same program.

## Floating Point Unit

Code may be created either to use the floating-point unit, or to perform all
floating-point operations in software. Code that uses the floating-point unit is
said to use the `fpu` model, code that performs all floating-point operations in
software is said to use the `nofpu` model. The choice of floating-point model
affects the way that function arguments and results are passed.

`fpu` and `nofpu` model code may not, in general, be mixed in the same program.

## Stack layout

* Each called function creates and deletes its own frame.
* The stack grows from high address to low address.
* The top of stack (i.e., the lowest address) is always referenced by the stack
  pointer register, SP.
* The stack pointer is always 4 byte aligned.
* The topmost frame is the frame of the currently executing function. When a
  function is called, it allocates its own frame by decreasing SP; on exit, it
deletes the frame by restoring SP to the value upon entry. Each function is
responsible for creating and deleting its own frame. Not all functions will
require a stack frame and a stack frame is allocated only if required.
* As well as the stack pointer, a frame may also have a frame pointer, FP, a
  register used to address parts of the frame. Only a subset of frames need
frame pointers.
* If a stack frame uses a frame pointer, the frame pointer is held in R14.

## Data Types

The following table shows the size and required alignment for all data types.

<table>
<tr>
<th>Type</th>
<th>Size (bytes)</th>
<th>Alignment (bytes)</th>
</tr>
<tr>
<td>char</td>
<td>1</td>
<td>1</td>
</tr>
<tr>
<td>short</td>
<td>2</td>
<td>2</td>
</tr>
<tr>
<td>int</td>
<td>4</td>
<td>4</td>
</tr>
<tr>
<td>long</td>
<td>4</td>
<td>4</td>
</tr>
<tr>
<td>long long</td>
<td>8</td>
<td>4</td>
</tr>
<tr>
<td>float</td>
<td>4</td>
<td>4</td>
</tr>
<tr>
<td>double</td>
<td>8 (4 on SH3e)</td>
<td>4</td>
</tr>
<tr>
<td>Pointer</td>
<td>4</td>
<td>4</td>
</tr>
</table>

## Register Usage

**Caller Save** registers are not guaranteed to be preserved, across function
calls, while **Callee Saved** registers are. That is, a function must save the
values in caller-saved registers when calling another (provided those values are
used after the procedure call), while a function that modifies callee-saved
registers must save and restore their values when done.

A register is Reserved if it has some special use required either by software
convention or by the hardware. They are not used by the compiler.

The registers and their usage are given below:

 * R0-R1: Function return value; caller saves
 * R2-R3: Scratch; caller saves
 * R2: Aggregate return address; caller save (GNU ABI only)
 * R4-R7: Parameter passing; caller saves
 * R8-R13: Callee Saves
 * R14: Frame Pointer (FP); callee saves
 * R15: Stack Pointer (SP); callee saves
 * MACH, MACL: Caller saves[^macregs]
 * PR: Linkage register (saves the subroutine return address); caller saves
 * SR: Status register
 * GBR: Reserved
 * VBR: Reserved

[^macregs]: MAC registers are callee-saved under the Hitachi ABI.

When compiling with a hardware FPU, floating-point registers are also available:

 * FR0-FR3: Return value; caller saves
 * FR4-FR11: Parameter passing; caller saves
 * FR12-FR15: Callee saves

### Frame Pointer

R14 is the frame pointer, but is not used as such when explicitly omitted with
the `-fomit-frame-pointer` option.

### Parameter passing

Registers R4-R7, FR4-FR11, and stack are used for parameter passing.

The first four arguments are passed in registers R4 through R7. Floating-point
arguments are passed in fr4 through fr11. All the remaining arguments are pushed
onto the stack, last to first, so that the lowest numbered argument not passed
in a register is at the lowest address in the stack.

The registers are always filled in SH3. For example, given the function `foo(
int a, int b, int c, long long d )` a, b, and c are passed in r4, r5, and r6
respectively, but d is passed partly in r7 and partly on the stack.

For SH3e and SH4, the entire argument is passed on the stack. That is, d will be
passed entirely on the stack.

Under the Hitachi ABI, aggregate types are passed on the stack. For e.g., in the
following code the members of structure `s` in the `foo(s)` function call are passed
on the stack. Under the GNU ABI, they would instead be passed in registers.

```c
typedef struct _S { int a; } S;
S s;

S foo (S s) {
       return s;
}
void bar() {
       s = foo(s);
}
```

Every stack push is rounded to a multiple 4 bytes. If the size of a value pushed
onto the stack is different from the size of an actual push, padding is added
downward. For example, if 2 bytes of data, 0x1234, are to be pushed onto the
stack, 4 bytes are pushed like so:

```
sp + 3 0x34
sp + 2 0x12
sp + 1 padding (unknown value)
sp + 0 padding (unknown value)
```

Values shorter than 4 bytes in function calls are never sign-extended- the
high-order bits have unspecified value.

### Function Return Values

If the return type of a function is no larger than 4 bytes it is returned in R0
or FR0 as applicable. Values 8 bytes and smaller are returned in the pair of R0
and R1.

If R0 and R1 are used to return the function value, R0 contains the most
significant part and R1 contains the least significant part for big-endian mode
and vice-versa for little-endian mode.

For all other types, the function value is always returned in memory.
Specifically, the caller allocates an instance of the aggregate type and passes
a pointer to the instance as an invisible argument. The caller stores the
function value into the memory location pointed to by the invisible pointer.

### Bit Fields

A bit-field is allocated within a storage unit whose alignment and size are the
same as the alignment and size of the underlying type of the bit-field. The
bit-field must reside entirely within this storage unit: a bit-field never
straddles the natural boundary of the underlying type.

In the little-endian ABI, bit-fields are allocated from right to left (least to
most significant) within a storage unit. In the big-endian ABI, bit-fields are
allocated from left to right (most to least significant) within a storage unit.

A bit-field shares a storage unit with the previous structure member if there is
sufficient space within the storage unit.

## Structure Alignment

All structure members are aligned to 4 byte boundaries unless `__attribute__
((packed))` is specified.

