---
title: "Revisiting swap: making database servers play nice"
slug: swap-again-still-good
draft: false
date: 2023-08-23T08:44:49.620Z
---
I've written previously about how [received wisdom regarding swap on Linux systems]({% ref /posts/2014/swap.md /%}) (and [Chris Down has done it better than I did](https://chrisdown.name/2018/01/02/in-defence-of-swap.html)) to the effect that using swap at all indicates an underprovisioned or oversubscribed system, while in reality swap is usually good to have and can help a machine achieve better performance. This came to mind again recently while I was tweaking the configuration of some small services (handling small numbers of concurrent users) that run on the same system as a MariaDB database, and led to me to a few interesting realizations.

## Summarizing arguments for swap

skim over how demand paging works, to remind the reader

---

zram is pretty cool. It allows a linux system to do the same kind of memory compression as [Windows since Windows 10](https://learn.microsoft.com/en-us/shows/seth-juarez/memory-compression-in-windows-10-rtm) and MacOS since sometime.

arch wiki writers suggest using high swappiness with zram:
https://wiki.archlinux.org/title/Zram#Optimizing_swap_on_zram

however memory compression at least on Windows Server is disabled by default. https://social.technet.microsoft.com/Forums/en-US/b2bf9771-9a6b-427f-ae66-94378e2305b8/memory-compression suggests that it might be tuned that way because servers are assumed to have plenty of memory (perhaps because typical users of Windows Server are less budget conscious). Memory compression may still be useful on servers if reducing memory use appears to be a good way to keep costs down.

In my case the limiting factor for system requirements probably is memory, since handling a small number of concurrent users for a web service doesn't require much CPU time.

## Databases 

Database servers usually seem to recommend only treating swap as emergency memory. For instance, the [MariaDB documentation recommends](https://mariadb.com/kb/en/configuring-swappiness/) setting `vm.swappiness` to either 0 or 1, which (as noted at the beginning of this post) is usually not a very good way to treat swap. However, given the design of the MariaDB server, this is a fairly reasonable approach because the database effectively maintains its own page cache (the [buffer pool](https://mariadb.com/kb/en/innodb-buffer-pool/)) separate from the OS's page cache for disk reads.

Compared to MariaDB, Postgres seems more willing to rely on OS page caching for data stored on disk: its documentation does not mention swappiness (though Percona suggest that [lowering swappiness is likely improve performance](https://www.percona.com/blog/tune-linux-kernel-parameters-for-postgresql-optimization/)), and it recommends [smaller values of `shared_buffers`](https://www.postgresql.org/docs/15/runtime-config-resource.html#GUC-SHARED-BUFFERS), suggesting that more than 40% of system RAM is unlikely to be useful. By comparison, MariaDB suggests that [allocating up to 80% of system memory](https://mariadb.com/kb/en/innodb-system-variables/#innodb_buffer_pool_size) to database-managed buffers may be worthwhile.

While researching this, I found [a user's comment from 2006 regarding postgres and swappiness](https://postgrespro.com/list/id/49298.209.244.4.106.1161290341.squirrel@www.drule.org):

> [Increasing swappiness] is very useful on smaller systems where memory is a scarce commodity.
 I have a Xen virtual server with 128MB ram.  I noticed a big improvement
in query performance when I upped swappiness to 80.  It gave just enough
more memory to fs buffers so my common queries ran in memory.
>
> Yes, throwing more ram at it is usually the better solution, but it's nice
linux gives you that knob to turn when adding ram isn't an option, at
least for me.

This comment alludes to the same characteristics that I'm considering here, namely that allowing the kernel to swap some things out of main memory during normal operation can in fact be good for performance, especially when you wish to run in an environment with limited memory.

---

So although we find here that databases *can* be memory-hungry as they attempt to manage what data is retained in memory, this is not standard among implementations. MariaDB (and its MySQL ancestor) seem to believe they can manage which data is kept in memory better than the OS can, and for that design it seems reasonable to encourage low swappiness values to ensure that whatever data the database believes is in memory will actually be in memory when it's wanted: if the kernel were to swap out a page that the database has cached, it would always be more efficient to simply reduce the size of the database's buffers to reclaim that memory than it is to store and reload it from swap.

## Making MariaDB nicer

With that diversion through history and looking at other databases, we've learned that at least some databases (postgres) have no strong opinion on swappiness. Certainly one could expect performance to suffer if the database's actual working set does not remain in memory, but it seems the MySQL developers (and MariaDB, which has inherited the overall design of MySQL) don't believe the OS can be trusted to do that. Without studying this in great detail (I'm not interested in spending enough effort to actually measure performance under various conditions), it seems best to accept the database's recommendations.

They suggest setting swappiness globally, which is bad for everything else on the system. If it's a single-purpose server (backing a large service, perhaps) that's not an issue, but for small servers that run more than just the database it's a bitter pill.

systemd MemoryswapMax=0 looks like it prevents a given service (or cgroup, if a slice) from swapping. That's much better!
