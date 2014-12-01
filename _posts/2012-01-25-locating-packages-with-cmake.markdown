---
author: tari
comments: true
date: 2012-01-25 17:26:44+00:00
layout: post
slug: locating-packages-with-cmake
title: Locating packages with cmake
wordpress_id: 510
categories:
- Software
tags:
- cmake
- libpng
- mkg3a
- windows
- zlib
---

When building programs with cmake on non-UNIX systems, it can be a pain to
specify the location of external libraries.  I've been upgrading
[mkg3a](https://www.taricorp.net/projects/mkg3a) to support using libpng to load
icons in addition to the old bmp loader, but that means I need to link against
libpng, and also zlib (since libpng depends on zlib to handle the image
compression).  Compiling it all on Windows, however, is not an easy task, since
there's no standard search path for libraries like there is on UNIX systems (eg
/usr/include for libraries, /usr/lib for libraries..).  I didn't find any good
resources on how to make it work in my own searches, so here's a quick write-up
of the process in the hopes that it'll be useful to somebody else.

I grabbed the zlib and libpng static libraries from
[gnuwin32](http://gnuwin32.sourceforge.net/packages/zlib.htm) and extracted them
near my mkg3a source tree, in the same directory.  Setting up to build, then, my
directory tree looks something like the following (some files omitted for
brevity):

```
build\
    - libs\
     - include\
      + libpng12\
      | png.h
      | pngconf.h
      | zconf.h
      | zlib.h
     - lib\
      | libpng.lib
      | zlib.lib
     + manifest\
    - mkg3a\
     | CMakeLists.txt
     | config.h.in
     | README
```

So I have a libs directory containing the headers and library files to link
against, build is my build tree, and mkg3a is the source tree.

In order to tell cmake where to find zlib and libpng now, we can use the
`CMAKE_PREFIX_PATH` variable, which is a path relative to the source directory.
In this case, the following command will pick up the libraries in libs and
generate project files for Visual Studio 2010 (note we're executing from within
the build tree):

    H:\Desktop\build> cmake -G "Visual Studio 10" -D CMAKE_PREFIX_PATH=../libs ../mkg3a

If the build tree were instead under the source tree (mkg3a/build/ instead of
just build/), the value for `CMAKE_PREFIX_PATH` would **not** need to change,
since it is specified relative to the source directory.

In short: set `CMAKE_PREFIX_PATH` to help it find packages when they're not in
the usual system locations.  It's much easier to combine all your external
libraries into one directory (libs in my example), but you could also specify a
list of paths and keep them separate.
