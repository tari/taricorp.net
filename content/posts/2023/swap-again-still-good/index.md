---
title: "Revisiting swap: making database servers play nice"
slug: swap-again-still-good
draft: false
date: 2023-08-23T08:44:49.620Z
---
I've written previously about how [received wisdom regarding swap on Linux systems]({% ref /posts/2014/swap.md /%}) (and [Chris Down has done it better than I did](https://chrisdown.name/2018/01/02/in-defence-of-swap.html)) to the effect that using swap at all indicates an underprovisioned or oversubscribed system, while in reality swap is usually good to have and can help a machine achieve better performance. This came to mind again recently while I was tweaking the configuration of some small services (handling small numbers of concurrent users) that run on the same system as a MariaDB database, and led to me to a few interesting realizations.

---

zram is pretty cool. It allows a linux system to do the same kind of memory compression as [Windows since Windows 10](https://learn.microsoft.com/en-us/shows/seth-juarez/memory-compression-in-windows-10-rtm) and MacOS since sometime.

arch wiki writers suggest using high swappiness with zram:
https://wiki.archlinux.org/title/Zram#Optimizing_swap_on_zram

however memory compression at least on Windows Server is disabled by default. https://social.technet.microsoft.com/Forums/en-US/b2bf9771-9a6b-427f-ae66-94378e2305b8/memory-compression suggests that it might be tuned that way because servers are assumed to have plenty of memory (perhaps because typical users of Windows Server are less budget conscious). Memory compression may still be useful on servers if reducing memory use appears to be a good way to keep costs down.

In my case the limiting factor for system requirements probably is memory, since handling a small number of concurrent users for a web service doesn't require much CPU time.

---

Database servers usually recommend only treating swap as emergency memory, which we noted in the topmost links is not a very good way to look at it: https://mariadb.com/kb/en/configuring-swappiness/. However for what MariaDB does (keeping what is effectively its own private page cache), it makes sense to keep the database server from swapping.

postgres docs don't specifically mention swap, but at least Percona suggest doing the same: https://www.percona.com/blog/tune-linux-kernel-parameters-for-postgresql-optimization/

They suggest setting swappiness globally, which is bad for everything else on the system. If it's a single-purpose server (backing a large service, perhaps) that's not an issue, but for small servers that run more than just the database it's a bitter pill. A [postgres-related discussion from 2006](https://postgrespro.com/list/id/49298.209.244.4.106.1161290341.squirrel@www.drule.org) includes a similar comment to my though in the prior section:

> This is very useful on smaller systems where memory is a scarce commodity.
 I have a Xen virtual server with 128MB ram.  I noticed a big improvement
in query performance when I upped swappiness to 80.  It gave just enough
more memory to fs buffers so my common queries ran in memory.
>
> Yes, throwing more ram at it is usually the better solution, but it's nice
linux gives you that knob to turn when adding ram isn't an option, at
least for me.

That mailing list thread was discussing historical behavior of postgres in preferring to depend on the OS's page cache rather than the database's (compare to what the MariaDB recommendation is, which seems to want you to depend on the database's page cache rather than the OS), but this particular comment observed that it can be very useful to encourage swapping (and control what might get swapped) when running in a memory-constrained environment.

systemd MemoryswapMax=0 looks like it prevents a given service (or cgroup, if a slice) from swapping. That's much better!
