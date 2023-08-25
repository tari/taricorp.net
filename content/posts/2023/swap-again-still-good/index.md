---
title: "Linux swap: handling database servers"
slug: database-swapspace
draft: false
date: 2023-08-23T08:44:49.620Z
---
I've written previously about how [received wisdom regarding swap on Linux systems]({% ref /posts/2014/swap.md /%}) (and [Chris Down has done it better than I did](https://chrisdown.name/2018/01/02/in-defence-of-swap.html)) to the effect that using swap at all indicates an underprovisioned or oversubscribed system, while in reality swap is usually good to have and can help a machine achieve better performance. This came to mind again recently while I was tweaking the configuration of some small services (handling small numbers of concurrent users) that run on the same system as a MariaDB database, and led to me to a few interesting realizations.

## Revisiting arguments for swap

Many programmers are aware of the generalities of swap (or called a page file on Windows): the OS tracks memory in units of one *page*, allocating pages of physical RAM when needed by a process. If a page of memory is needed but there are none free to allocate, then it either needs to reject the request (not always possible) or take a page from somewhere else (usually meaning it needs to kill the process that owned that page).

Swap space is a place on disk (or in other storage that is not main memory) where the OS can opt to place memory pages instead of freeing them through other means: if memory is needed but unavailable, it can "swap out" a page and arrange to swap it back in when its owner attempts to use it again. Swapping a page out or back in can take a long time (multiple milliseconds, or longer), but for pages which are rarely accessed it can be worthwhile to pay that cost so some other process can use the RAM that would otherwise be allocated to unused data.

Linux offers a parameter called *swappiness* which controls the system's bias toward swapping pages out or dropping pages from the *page cache*, which is a transparent cache for file accesses. When things are working well, "unused" memory will usually be used to store page cache data in order to accelerate file accesses and in typical configurations it will prefer to shrink the page cache rather than swap pages out.

### Memory compression

The idea behind swap ("*demand paging*", more generally) is very old. More recent is the idea of memory compression, where instead of writing pages out to storage when they're no longer desired in RAM the data is instead compressed and stored elsewhere in RAM. This is useful because memory pages usually compress pretty well (often compressing to less than half their original size), and memory is so much quicker to access than external storage that it's often at least as fast to decompress a compressed page than it is to read it back from disk.

Memory compression is now common in operating systems that expect to be used interactively (by a user sitting in front of the computer): MacOS has memory compression (but I'm unable to determine what that feature was added), Windows implements it since 2015 ([added in Windows 10](https://learn.microsoft.com/en-us/shows/seth-juarez/memory-compression-in-windows-10-rtm)), and Linux's `zram` was added in 2014 with some distributions (Fedora, [Pop!_OS](https://github.com/pop-os/default-settings/pull/163) and ChromeOS for instance) now enabling it by default.

When using zram on Linux, it seems like configuring swappiness is usually useful: the kernel's default value of 60 is biased toward shrinking the page cache, but paging data out by writing to zram (even after the CPU cost of doing compression) is usually faster than traditional swap, even if the traditional swap is on fast solid-state storage rather than a traditional hard drive. A swappiness value greater than 100 (up to 200, the maximum) tends to be a good idea in that case, reflecting that it tends to be less costly to swap to compressed memory than it would be to reload file data from disk when needed. This assumes that the choice of pages to swap out accurately reflects which data will actually be used next, which is a difficult problem to solve but today's operating systems tend to do that fairly well.

---

Either server-targeted OS distributions are more conservative with adopting this new technology however, or their creators believe that memory compression is not desirable in server workloads: Windows Server [disables memory compression by default](https://social.technet.microsoft.com/Forums/en-US/b2bf9771-9a6b-427f-ae66-94378e2305b8/memory-compression), and (from my experience) few Linux distributions enable any kind of zram by default though they do often default to at least a small amount of disk-backed swap.

It's difficult to find any justification for not enabling memory compression on servers because (at least in the Linux world) that's the default behavior so there are no changes to point to where there might be discussion of the question, but it seems like servers may tend to have memory compression disabled because they're expected to have sufficient memory to absorb all application demand. That is, it is assumed that the system owners ensure there is always "enough" physical memory, however much that is for their needs.

### What of small systems?

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

For memory-constrained systems however, their recommendation seems bad. As we've seen, setting swappiness to a very small number can have negative performance implications and especially so when memory is not plentiful. For large services with meaningful budgets (and perhaps paid database administrators), I imagine setting swappiness is no problem but for the small sorts of services I usually work on (with budget along the lines of "as cheap as possible"), setting swappiness globally is a bitter pill to swallow because it will probably limit (re)use of memory in useful ways. Is there a better way?

### Being cleverer

systemd MemoryswapMax=0 looks like it prevents a given service (or cgroup, if a slice) from swapping. That's much better!

## Possible alternatives

the buffer pool in mariadb behaves a lot like a chunk of page cache that's dedicated to the database. Reducing its size (or not making it larger) is also probably a fine option, though write-heavy workloads might want a fairly large one because the database also uses the buffer pool to buffer writes as well as reads.

Vettabase note that the official guidance of basically "give it as much memory as you can" is not very good: https://vettabase.com/is-innodb-buffer-pool-big-enough/

It's not obvious what methods the database uses to read from disk. If it were memory-mapping the files then using data in the OS page cache would be nearly free, but it probably doesn't do that because then reads could block unpredictably when the data isn't currently loaded.