---
title: Cross-compiling CMake projects for Windows
slug: cmake-windows-cross
draft: false
date: 2021-01-20T22:17:00.442Z
categories:
  - Software
tags:
  - cmake
  - libpng
  - windows
  - cross-compiler
  - mingw
---
I sometimes find myself wanting to cross-compile programs with CMake on a Linux machine such that I get a standalong .exe that can be given to mostly non-technical Windows users to run. This isn't hard, but finding the right options is a little bit of a challenge every time, so now I'm recording the procedure here; both as a reminder to myself, and to provide a quick recipe that future searchers can use.

Cross-compiling for Windows will of course need an appropriate toolchain, which these days tends to be [mingw-w64](http://mingw-w64.org/). Many Linux distributions provide packages for it: [`mingw-w64`](https://packages.debian.org/sid/mingw-w64) on Debian (including Ubuntu and variants), [`mingw-w64-gcc`](https://archlinux.org/packages/community/x86_64/mingw-w64-gcc/) on Arch and similar for other distributions.

---

CMake [documents how to specify cross-compilation options](https://cmake.org/cmake/help/latest/manual/cmake-toolchains.7.html#cross-compiling), but it's not terribly clear which settings are mandatory. For simple needs, only three variables must be set:

 * `CMAKE_SYSTEM_NAME` being set implies that you're cross-compiling, which will prevent cmake from trying to do things like run the binaries it builds (unless they're tool binaries being built for the host, rather than the target).
 * `CMAKE_C_COMPILER` is the name of the compiler to use
 * `CMAKE_CXX_COMPILER` is the name of the compiler to use for C++ sources

Targeting mingw-64 then, the cmake invocation looks like this:

```
cmake -DCMAKE_SYSTEM_NAME=Windows \
      -DCMAKE_C_COMPILER=i686-w64-mingw32-gcc \
      -DCMAKE_CXX_COMPILER=i686-w64-mingw32-g++ \
      path_to_sources
```

The `i686-` prefixed compiler builds 32-bit binaries, which I usually prefer to build because they'll work both on 32- and 64-bit Windows. If no support for 32-bit Windows is required, the `x86_64-`-prefixed tools will build 64-bit binaries instead (eg, `x86_64-w64-mingw32-gcc`).

When building binaries to share it's probably helpful to do a non-debug build by also setting `CMAKE_BUILD_TYPE`, perhaps to `MinSizeRel` or `RelWithDebInfo`.

## Libraries

Libraries that you might depend on can be built in the same way, and installed to a chosen directory by setting `CMAKE_INSTALL_PREFIX` and building the install target. For instance building a libpng static library
(which itself provides options to enable a shared library and tests which we turn off):

```
cmake -DCMAKE_SYSTEM_NAME=Windows \
      -DCMAKE_C_COMPILER=i686-w64-mingw32-gcc \
      -DCMAKE_CXX_COMPILER=i686-w64-mingw32-g++ \
      -DCMAKE_INSTALL_PREFIX=$HOME/windows_binaries \
      -DPNG_SHARED=OFF -DPNG_TESTS=OFF \
      path_to_sources
cmake --build . --target install
```

[As I've observed previously](https://www.taricorp.net/2012/locating-packages-with-cmake/), you can then link against these libraries by setting `CMAKE_PREFIX_PATH`. So if we want to build against the libpng that was just built and generate a "release" binary:

```
cmake -DCMAKE_SYSTEM_NAME=Windows \
      -DCMAKE_C_COMPILER=i686-w64-mingw32-gcc \
      -DCMAKE_CXX_COMPILER=i686-w64-mingw32-g++ \
      -DCMAKE_BUILD_TYPE=RelWithDebInfo \
      -DCMAKE_PREFIX_PATH=$HOME/windows_binaries \
      path_to_sources
```