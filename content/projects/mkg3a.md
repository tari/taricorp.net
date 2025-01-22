---
layout: page
title: mkg3a
date: 2011-12-05 22:44:11.000000000 -07:00
categories: []
tags: []
status: publish
type: page
meta:
  _edit_last: '1'
  _wp_page_template: default
  _jd_tweet_this: 'yes'
  _jd_twitter: ''
  _wp_jd_clig: ''
  _wp_jd_bitly: ''
  _wp_jd_wp: ''
  _wp_jd_yourls: ''
  _wp_jd_url: ''
  _wp_jd_target: ''
  _jd_wp_twitter: ''
  _jd_post_meta_fixed: 'true'
author:
  login: tari
  email: peter@taricorp.net
  display_name: tari
  first_name: Peter
  last_name: Marheine
---

Mkg3a is my contribution to the community effort to build a free and
open-source toolchain targeting the Casio FX-CG line of calculators.  Here's
the [blog post introducing the project](/2011/mkg3a.html), and the 
[feedback/announcements thread](http://www.cemetech.net/forum/viewtopic.php?t=6153)
on Cemetech.

# Code

I don't usually make a point of packaging releases, since this is such a small project.  The code is always available in the repository at Bitbucket: https://bitbucket.org/tari/mkg3a/

Releases are tagged in the repository, and automatic snapshot packages are
available from Bitbucket's [downloads
page](https://bitbucket.org/tari/mkg3a/downloads).

# Building

mkg3a is configured with cmake.  For a basic build, the following should work:

```
$ hg clone https://bitbucket.org/tari/mkg3a
$ mkdir mkg3a/build
$ cd mkg3a/build
$ cmake ..
$ make
# make install
```

To clone a specific revision or tag (perhaps version 0.1e), use mercurial's -r option:

```
$ hg clone -r 0.1e https://bitbucket.org/tari/mkg3a
```

Specifying the install path at build-time is done via cmake (like `--prefix=` with autotools):

```
$ cmake .. -DCMAKE_INSTALL_PREFIX=/usr
```

For other tasks, have a look at the CMake documentation, and consider using a CMake GUI such as `ccmake` or `cmake-gui`.

You'll need libpng and zlib for default build.  You can avoid that dependency
(and disable the PNG icon loader as a consequence) by setting CMake's
`USE_PNG` variable to `OFF`.  It's useful to disable the PNG
support when building on Windows, since it's a bit of effort to get those
libraries configured (I've written up some notes on [building the
libraries](/2012/static-libpng-on-win32-with-cmake.html) and
[telling CMake where to look for them](/2012/locating-packages-with-cmake.html)).

# Usage

To do much of anything useful with mkg3a, you'll want to have some compiled code
for the Prizm.  GCC (built to target SH3) and
[libfxcg](https://github.com/Jonimoose/libfxcg) are the primary tools  you'll
need to do that.  [more notes on building programs to come, hopefully].

The mkg3a README file includes some usage examples.  Refer to those until I
get some written here.
