---
author: tari
comments: true
date: 2012-01-27 04:28:43+00:00
layout: post
slug: high-availability-home-revisited
title: High-availability /home revisited
wordpress_id: 530
categories:
- Linux
tags:
- btrfs
- drbd
- linux
- rsync
- storage
- unison
---

About a month ago, I wrote about my experiments in ways to [keep my home
directory consistently
available](../2011/experiments-with-a-high-availability-home.html). I ended up
concluding that DRBD is a neat solution for true high-availability systems, but
it's not really worth the trouble for what I want to do, which is keeping my
home directory available and in-sync across several systems.

Considering the problem more, I determined that I really value a simple setup.
Specifically, I want something that uses very common software, and is resistant
to network failures. My local network going down is an extremely rare occurence,
but it's possible that my primary workstation will become a portable machine at
some point in the future- if that happens, anything that depends on a constant
network connection becomes hard to work with.

If an always-online option is out of the question, I can also consider solutions
which can handle concurrent modification (which DRBD can do, but requires using
OCFS, making that solution a no-go).

## Rsync

rsync is many users' first choice for moving files between computers, and for
good reason: it's efficient and easy to use.  The downside in this case is that
rsync tends to be destructive, because the source of a copy operation is taken
to be the canonical version, any modifications made in the destination will be
wiped out.  I already have regular cron jobs running incremental backups of my
entire /home so the risk of rsync permanently destroying valuable data is low. 
However, being forced to recover from backup in case of accidental deletions is
a hassle, and increases the danger of actual data loss.

In that light, a dumb rsync from the NAS at boot-time and back to it at shutdown
could make sense, but carries undesirable risk.  It would be possible to
instruct rsync to never delete files, but the convenience factor is reduced,
since any file deletions would have to be done manually after boot-up.  What
else is there?

## Unison

I eventually decided to just use
[Unison](http://www.cis.upenn.edu/~bcpierce/unison/), another well-known file
synchronization utility.  Unison is able to handle non-conflicting changes
between destinations as well as intelligently detect which end of a transfer has
been modified.  Put simply, it solves the problems of rsync, although there are
still situations where it requires manual intervention.  Those are handled with
reasonable grace, however, with prompting for which copy to take, or the ability
to preserve both and manually resolve the conflict.

Knowing Unison can do what I want and with acceptable amounts of automation
(mostly only requiring intervention on conflicting changes), it became a simple
matter of configuration.  Observing that all the important files in my home
directory which are not already covered by some other synchronization scheme
(such as configuration files managed with Mercurial) are only in a few
subdirectories, I quickly arrived at the following profile:


    root = /home/tari
    root = /media/Caring/sync/tari
    
    path = incoming
    path = pictures
    path = projects
    path = wallpapers

Fairly obvious function here, the two sync roots are /home/tari (my home
directory) and /media/Caring/sync/tari (the NAS is mounted via NFS at
/media/Caring), and only the four listed directories will be synchronized. An
easy and robust solution.

I have yet to configure the system for automatic synchronization, but I'll
probably end up simply installing a few scripts to run unison at boot and when
shutting down, observing that other copies of the data are unlikely to change
while my workstation is active.  Some additional hooks may be desired, but I
don't expect configuration to be difficult.  If it ends up being more complex,
I'll just have to post another update on how I did it.

**Update Jan. 30:** I ended up adding a line to my rc.local and rc.shutdown
scripts that invokes unison:

    su tari -c "unison -auto home"

Note that the Unison profile above is stored as ~/.unison/home.prf, so this
handles syncing everything I listed above.
