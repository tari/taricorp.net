---
author: tari
comments: true
date: 2012-02-05 19:35:55+00:00
layout: post
slug: static-libpng-on-win32-with-cmake
title: Static libpng on win32 with CMake
wordpress_id: 582
categories:
- Software
post_format:
- Aside
tags:
- cemetech
- cmake
- libpng
- mkg3a
- windows
- zlib
---

Working on mkg3a upgrades for libpng more, I was getting unusual crashes with
the gnuwin32 libpng binaries (access violations when calling `png_read_int()`). 
It turned out that the libpng dll was built against an incompatible C runtime,
so I had to build static libraries.  With the official libpng source
distribution (and zlib), building static libraries was reasonably easy.  Using
the MSVC make tool in the libpng source tree, I first had to build zlib.  The
default build (for some reason) doesn't build the module containing
`_inflate_fast`, so I had to add inffast.obj to the OBJS in
zlib/win32/Makefile.msc (this manifested as an unexported symbol error when
linking a program against zlib).  Building it then was easy, using nmake in the
Visual Studio toolkit:

    zlib-1.2.5> nmake -f win32/Makefile.msc

With zlib built, copy zlib.h and zlib.lib out of the source directory and into
wherever it will be used.

For libpng, we first have to modify the makefile, since the one included uses
unusual options.  Change CFLAGS to read CFLAGS=/nologo /MT /W3 -I..\zlib for
some sane options.  The include path also needs to be updated to point to your
zlib.h.  In my case, that makes it -I..\include\.  The rest of the procedure for
building libpng is very similar to that for zlib:

    lpng158> nmake -f scripts/Makefile.msc

Building against libpng then requires png.h, pngconf.h, pnglibconf.h and
png.lib.  To build against these libraries, I simply put the include files in an
'include' directory, the .lib files in a 'lib' directory, and [pointed cmake at
it](locating-packages-with-cmake).

Warnings about runtime libraries when linking a program against these static
libraries is an indication that you'll probably see random crashes, since it
means theses static libraries are using a different version of the runtime
libraries than the rest of your program.  I saw this problem manifested as
random heap corruption.  Changing CFLAGS (in the makefiles) to match your target
configuration as set in Visual Studio and rebuilding these libraries will handle
that problem.
