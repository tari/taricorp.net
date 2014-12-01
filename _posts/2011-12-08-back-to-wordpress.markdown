---
author: tari
comments: true
date: 2011-12-08 02:40:56+00:00
layout: post
slug: back-to-wordpress
title: Back to wordpress
wordpress_id: 283
categories:
- Software
tags:
- archiving
- futurism
- storage
---

After about a year of running a purely static site here, I finally decided it
would be worthwhile to move the site backend back to Wordpress.

I moved away from Wordpress early this year primarily because I was dissatisfied
with the theming situation.  While [lightword](http://www.lightword-theme.com/)
is certainly a well-designed piece of software and markup, I wanted a system
that would be easier to customize.  Being written and configured in PHP (a
language I don't know and have have little interest in learning), I decided
Wordpress didn't offer the easy customizeability that I wanted in a web
publishing platform, and made the switch to generating the site as a set of
static pages with [hyde](http://ringce.com/hyde).  I've now decided to make the
switch back to Wordpress, and the rest of this post outlines my thought process
in doing so.

# Archiving

One of the things that I am most concerned about in life is the preservation of
information.  To me, destruction of information, no matter the content, is a
deeply regrettable action.  Deliberate destruction of data is fortunately rare,
but too often it may still be lost, often through simple neglect.  For example,
[science fiction author] Charlie Stross, in a [recent
discussion](http://www.antipope.org/charlie/blog-static/2011/12/todays-chewy-reading.html#comment-224496),
noted that the web site belonging to [Robert
Bradbury](http://en.wikipedia.org/wiki/Matrioshka_brain) has become inaccessible
at some point since his death, and Mr. Stross was thus unable to find Bradbury's
original article on the subject of Matroishka brains.

That comment led me to realize quickly that this great distributed repository of
our age (the world wide web) is a frighteningly ethereal thing- what exists on a
server at one moment may disappear without warning for reasons ranging from
legal intervention (perhaps because some party asserts the information is
illegal to distribute) to the death of the author (in which one's web hosting
may be suspended due to unpaid bills).  Whatever the reason, it is impossible to
guarantee that some piece of data will not be lost forever if the author's copy
disappears.

How can we preserve information on the web?  Historically, libraries have filled
that role, and in that respect, things haven't changed that much in the Internet
age.  The [Internet Archive](https://archive.org) is a nonprofit organization
that works to be like a digital library, and they specifically note that huge
swaths of cultural (and other) data might be lost to the depths of time if we do
not take steps to preserve it now.  The Internet Archive's [wayback
machine](http://archive.org/web/web.php) (which will probably be familiar to
many readers who have needed to track down no-longer-online data) is a
continually-updated archive of snapshots of the web.

It's fairly slow to crawl, but most pages are eventually found by the wayback
machine crawlers, so the challenge of data preservation is greatly reduced for
site owners, to in most cases only requiring content to be online for a short
time (probably less than a year in most cases) before it is permanently
archived.  For non-textual content unfortunately, the wayback machine is
useless, since it will only mirror web pages, and not images or other
non-textual content.  To ensure preservation of non-textual content, however,
the solution is also rather easy: upload it to the Internet Archive.  It's not
automatic like the wayback machine, but the end result is the same.

# Back to Wordpress

This brings me back to my choice of using Wordpress to host this web site,
rather than a solution that I develop and maintain.  Quite simply, I decided
that it is more important to get information I produce out in public so it can
be disseminated and archived, rather than maintain fine-grained control over the
presentation of the information.

While with Hyde I was able to easily control every aspect of the site design and
layout, it also meant that I had to write much of the software to drive
any additional features that might improve searchability or structure of the
content.  When working with Wordpress (or any out-of-the-box CMS really),
however, I can concern myself with the things that are of real importance- the
data, and let the presentation mostly take care of itself.

While Hyde put up barriers to disseminating information (the source being
decoupled from presentation and requiring offline editing, for example), my
new-old out-of-the-box CMS solution in Wordpress makes it extremely easy to
publicize information without getting tied up in details which are ultimately
irrelevant.

## Filtering oneself

With ease of putting information out in public comes the challenge of searching
it.  I try to be selective about what I make public, partially because I tend to
be somewhat introverted, but also in order to ensure that the information I
generate and publicize is that which is of interest to people in the future
(although it seems I was only doing the latter subconsciously prior to now). 
There are platforms to fill with drivel and day-to-day artifacts of life, but a
site like this is not one of them- Twitter, Facebook, and numerous other
'social' web sites fill that niche admirably, but can never replace more
carefully curated collections

## Ephemera

Preservation of ephemera is at the core of some of the large privacy concerns in
today's world.  Companies such as Facebook host huge amounts of arguably
irrelevant content generated by their users, and mine the data to generate
profiles for their users.  On its surface, this is an amazing piece of work,
because these companies have effectively constructed automated systems to
document the lives of everybody currently alive.  Let that sink in for a moment:
Facebook is capable of generating a moderately detailed biography for each of
this planet's _7 billion_ people (provided they each were to provide Facebook
with some basic data).

What would you do with a biography of someone distilled from advertising data
(advertising data because that's what Facebook exists to do- sell information
about what you might like to buy to advertisers)?  I don't know, but the future
has a way of finding interesting ways to use existing data.  In some distant
future, maybe a project might seek to reconstruct (even resurrect, by a way of
thinking) everybody who ever lived.  There are innumerable possibilities for
what might be done with the data (this goes for anything, not just biographical
data like this), but it becomes impossible to use it if it gets destroyed.

The historical bane of all archives has been capacity.  With digital archives,
this is a significantly smaller problem.  With multi-terabyte hard disks costing
on the order of $0.10 per gigabyte and solid-state memory continuing to follow
the pace of Moore's law (although probably not for much longer), it is easier
than ever to store huge amounts of information, dwarfing the largest collections
of yesteryear.  As long as storage capacity continues to grow (we've only
recently scratched the surface of using quantum phenomena (holography) for data
storage, for example), the sheer amount of data generated by nearly any process
is not a concern.

# Back on topic

Returning from that digression, the point of switching this site back to a
Wordpress backend is to get data out to the public more reliably and faster, in
order to preserve the information more permanently.  What finally pushed me back
was a sudden realization that there's nothing stopping me from customizing
Wordpress in a similar fashion to what I did on the Hyde-based site- it simply
requires a bit of experience with the backend code.  While PHP is one language I
tend to loathe, the immediate utility of a working system is more valuable than
the potential utility of a system I need to program myself.

There's another lesson I can derive from this experience, too: building a
flexible system is good, but you should distribute it ready-to-go for a common
use case.  Reducing the barrier to entry for a tool can make or break it, and
tools that go unused are of no use- getting people using a new creation is the
primary barrier to its adoption.

