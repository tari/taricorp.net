---
layout: page
title: feed-accelerator
date: 2012-01-01 19:01:24.000000000 -07:00
categories: []
tags: []
status: publish
type: page
published: true
---

feed-accelerator is an RSS/Atom feed reader following the UNIX philosophy ("do
one thing, and do it well").  It offers text-based configuration and a handful
of output formats which are designed to be fed into other programs.  It is built
on Python and the [Universal Feed Parser][ufp] library.

[ufp]: http://code.google.com/p/feedparser/

# Download

The code is hosted on [Bitbucket][bitbucket].

[bitbucket]: https://bitbucket.org/tari/feed-accelerator/

There are no official releases mainly because I started this project for my own
use, but I'm happy to add features and general improvements if there's
interest.

# Usage/Configuration

The program is configured by the file `feed.py.ini`, of which there is an
example in the source repository.  The config file is found in the same
directory as the main program, but future plans include searching other paths
for options.  A more in-depth discussion of the options follows, sorted by ini
section.  For discussion of the ini format used here, see the Python
documentation for the `configparser` module (`ConfigParser` for
Python before version 3.0).

```ini
[DEFAULT]
last_update = 0

[feed-accelerator]
output_mode = uzbl
output_file = 'accelerated.html'
buffer = 0
prefetch = 0

[boingboing.net]
uri = http://feeds.boingboing.net/boingboing/iBag
interval = 5
```

## DEFAULT

The DEFAULT section contains some housekeeping information for the reader.  The
only recognized option in this section is `last_update`, which stores a
timestamp (floating-point number of seconds since the epoch) of when feeds were
last fetched.  The value is used to determine which feed entries should be
ignored (treated as already-read), by cross-referencing with the timestamps
provided in feeds.

## feed-accelerator

This section specifies the main options controlling the program's output.  If
any of these options are not specified, they will be set to reasonable defaults.

 * `output_mode`: selects the output format to use.  See the `output_formatters`
   section for details.
 * `output_file`: file to write output to, for the formats that write to files. 
   Ignored for other formats.
 * `buffer`: Controls temporal buffering of output.  0 or 'False' turns it off,
   1 or 'True' is on.
 * `prefetch`: Turning this option on can makes the program save feeds to a
   temporary file before parsing.  It's useful if a feed always seems to return
nothing (known to occur for feeds on nyaa.eu, for example), but there's actually
content (a problem that seems to stem from a bug in the feed parser library).

### Output formatters

 * The `raw` output mode writes the markup of each entry to stdout, one line per
   entry.
 * `uzbl` output pipes entries to an internal instance of [uzbl-core][uzbl] for
   display.  This works the same as using raw mode and redirecting the output of
feed-accelerator to the input of uzbl with inclusion of some uzbl commands, but
this mode improves on that by linking the lifetimes of the two processes.
 * `html` mode writes entries to a file, one at a time (the file only ever
   contains one entry).  The path to the file to write is given by the
`output_file` option.
 * `torrent` mode is designed to automated bittorrent downloads. Every entry
   that appears to describe a torrent file will be saved to a new file in a
location given by the `directory` option for that feed.

[uzbl]: http://www.uzbl.org/

### Temporal buffering

This feature isn't yet implemented. The idea is that when enabled, this will
buffer received entries in order in order to spread them out, rather than have
entries appear all at once. The main purpose for such a feature is the case
where the output is connected to something which displays a single entry at a
time, allowing each to be shown for some nonzero amount of time.  A class stub
exists in the code, so the buffering logic is all that must be implemented.

# Bugs/TODO

 * Temporal buffering needs to be implemented.
 * The config file is currently only searched for in the same directory as the
   program itself.  Future expansion should add other options, such as
~/.feed-accelerator.ini and the current working directory.
 * Time of last update should be stored outside the main config file in order to
   avoid rewriting it every time the program exits and wiping out any comments
that may exist in there.
 * Torrent output mode should use the `output_file` option to get its directory
   rather than a per-feed option.

There are probably bugs lurking in the code.  I'd appreciate if you notify me of them, either through the issue tracker on bitbucket or some other means.  Patches are welcome.
