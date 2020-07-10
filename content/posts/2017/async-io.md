---
title: Evaluating async I/O
slug: async-io
draft: true
date: 2017-02-28
categories:
 - Software
tags:
 - optimization
 - concurrency
 - threading
 - async
 - tokio
---

A common belief among software engineers of a certain temperament seems to be
that asynchronous I/O is the only way to achieve good performance in a server
application.

...

[HHVM docs][hhvm] for async observe that always blocking isn't necessarily a good
solution, because you want to do two operations in parallel and combine the
results. You could always spawn a thread for parallel operations though..

[hhvm]: https://docs.hhvm.com/hack/async/introduction

A thread pool can avoid some of the cost of creating a thread for each operation
you want. But if it has a fixed size and you're blocking on each thread, you'll
be likely to saturate the pool with threads that are blocking on other
operations when there's still CPU time available.

So use a thread pool without a fixed size, spawning threads when there are no
idle ones available.

---

Even better: spawn more threads when utilization is low. You need to be able
to measure utilization though.

On Linux, /proc/n/task enumerates threads, task/n/stat gives CPU statistics,
including run state (Running, Sleeping, D for uninterruptible, Zombie). You
could sample this for workers and look at whether they're runnable but not running
(need to know how many CPUs you have an compare to the number of runnable threads
I guess). If too many threads are runnable at any given time, stop spawning threads
and instead queue requests (or shed load!). See kernel Documentation/filesystesm/proc.txt
(Table 1-2).

It may also be possible to use cgroups for this, creating a cgroup might be useful
so the kernel does CPU accounting for you. Have a look at cgroups(7), kernel
Documentation/cgroup-v1/cpuacct.txt

This is of course not portable. Would need some work there.

---

This has a cost in stacks, since reusing a thread that has used a larger amount
of stack will have memory committed to those stacks which is not in use.
Periodically stop threads to free memory, or madvise to free it or something.

```c
pthread_attr_t attr;
pthread_getattr_np(pthread_self(), &attr);

void *stackaddr;
size_t stacksize;
pthread_attr_getstack(&attr, &stackaddr, &stacksize);
pthread_attr_destroy(&attr);

void *rsp;
__asm__("mov %rsp, %0" : "=r"(rsp));
assert(rsp >= stackaddr);
rsp -= 128; /* x86_64 redzone */

rsp &= ~(getpagesize() - 1); /* round down to page */
madvise(stackaddr, rsp - stackaddr, MADV_FREE);
```

`MADV_FREE` and `MADV_DONTNEED` have similar userspace semantics, but FREE is a
somewhat cheaper operation because DONTNEED actually removes the PTE for that
memory block whereas FREE will only do so if necessary. See https://lwn.net/Articles/590693/

Other resources..

 * https://www.mailinator.com/tymaPaulMultithreaded.pdf
 * http://blog.paralleluniverse.co/2014/02/04/littles-law/
 * http://blog.paralleluniverse.co/2014/05/29/cascading-failures/

Some quick investigation into rationales at work:

 * Straight async in java because threads are very expensive in java and fibers
   are not well supported.
 * Native threads or fibers in C++. Fibers feel just like native threads, just a
   little cheaper.
 * Go is goroutines, of course - fibers again.

Async seems more common in less.. efficient languages? PEP 492 for example
(async/await syntax) cites other languages as having support as just about the
only reason to add it, which feels kind of cargo-culty. The first example of
dedicated syntax chronologically appears to be in
[C#](https://msdn.microsoft.com/en-us/library/mt674882.aspx).

MSDN cites responsiveness in GUIs as the main motivation, enabled specifically
by dedicated syntax. Can be easier than threads as a result, since things look
like they block but don't because the compiler does magic under the hood.

fibers are generally defined as cooperative threads rather than preemptive
ones. You can avoid unnecessary context switch costs when IO-bound processing
might be preempted, but should not run CPU-bound operations on a fiber because
you can starve other fibers from doing their IO-bound processing.
