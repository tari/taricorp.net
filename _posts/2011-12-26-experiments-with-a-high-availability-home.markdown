---
author: tari
comments: true
date: 2011-12-26 19:48:16+00:00
layout: post
slug: experiments-with-a-high-availability-home
title: Experiments with a high-availability /home
wordpress_id: 392
categories:
- Linux
tags:
- clustering
- drbd
- linux
- storage
- virtualization
---

I was recently experimenting with ways to configure my computing setup for high
availability of my personal data, which is stored in a Btrfs-formatted partition
on my SSD. When my workstation is booted into Windows, however, I want to be
able to access my data with minimal effort. Since there's no way to access a
Btrfs volume natively from within Windows, I had to find another approach. It
seemed like automatically syncing files out to my NAS was the best solution,
since that's always available and independent of most other things I would be
doing at any time.

# Candidates

The obvious first option for syncing files to the NAS is the ever-common rsync.
It's great at periodic file transfers, but real-time syncing of modifications is
rather beyond the ken of rsync. 
[lsync](https://blogs.oracle.com/timc/entry/lsync_keeping_your_sanity_by)
provides a reasonable way to keep things reasonably in-sync, but it's far from
an elegant solution.  Were I so motivated, it would be reasonable to devise a
similar rsync wrapper using inotify (or similar mechanisms) to only handle
modified files and possibly even postpone syncing changes until some change
threshold is exceeded.  With existing software, however, rsync is a rather
suboptimal solution.

From a cursory scan, cluster filesystems such as [ceph](http://ceph.com/) or
[lustre](http://wiki.lustre.org/index.php/Main_Page) seem like good options for
tackling this problem.  The main disadvantage of the cluster filesystem
approach, however, is rather high complexity. Most cluster filesystem
implementations require a few layers of software, generally both a metadata
server and storage server. In large deployments that software stack makes sense,
but it's needless complexity for me.  In addition, ensuring that data is
correctly duplicated across both systems at any given time may be a challenge. 
I didn't end up trying this route so ensuring data duplication may be easier
than it seems, but a cluster filesystem ultimately seemed like needless
complexity for what I wanted to do.

While researching cluster filesystems, I discovered
[xtreemfs](http://www.xtreemfs.org/), which has a number of unique features,
such as good support for wide-area storage networks, and is capable of operating
securely even over the internet.  Downsides of xtreemfs are mostly related to
the technology it's built on, since the filesystem itself is implemented with
Linux's FUSE (Filesystem in USErspace) layer and is implemented in Java.  Both
those properties make it rather clunky to work with and configure, so I ended up
looking for another solution after a little time spent attempting to build and
configure xtreemfs.

The solution I ultimately settled upon was [DRBD](http://www.drbd.org/), which
is a block-level replication tool.  Unlike the other approaches, DRBD sits at
the block level (rather than the filesystem level), so any desired filesystem
can be run on top of it.  This was a major advantage to me, because Btrfs
provides a few features that I find important (checksums for data, and
copy-on-write snapshotting). Handling block-level syncing is necessarily
somewhat more network-intensive than running at the file level, but since I was
targeting use over a gigabit LAN, network usage was a peripheral concern.

# Implementation

From the perspective of normal operation, a DRBD volume looks like RAID 1
running over a network.  One host is marked as the primary, and any changes to
the volume on that host are propagated to the secondary host.  If the primary
goes offline for whatever reason, the secondary system can be promoted to the
new primary, and the resource stays available. In the situation of my designs
for use of DRBD, my workstation machine would be the primary in order to achieve
normal I/O performance while still replicating changes to the NAS. Upon taking
the workstation down for whatever reason (usually booting it into another OS),
all changes should be on the NAS, which remains active as a lone secondary.

DRBD doesn't allow secondary volumes to be used at all (mainly since that would
introduce additional concerns to ensure data integrity), so in order to mount
the secondary and make it accessible (such as via a Samba share) the first step
is to mark the volume as primary. I was initially cautious about how bringing
the original primary back online would affect synchronization, but it turned out
to handle such a situation gracefully. When the initial primary (workstation)
comes back online following promotion of the secondary (NAS), the former primary
is demoted back to secondary status, which also ensures that any changes while
the workstation was offline are correctly mirrored back. While the two stores
are resyncing, it is possible to mark the workstation as primary once more and
continue normal operation while the NAS' modifications sync back.

Given that both my NAS and workstation machines run Arch Linux, setup of DRBD
for this scheme was fairly simple. First order of business was to create a
volume to base DRBD on. The actual DRBD driver is part of mainline Linux since
version 2.6.33, so having the requisite kernel module loaded was easy. The
userspace utilities are available in [the
AUR](https://aur.archlinux.org/packages.php?ID=36645), so it was easy to get
those configured and installed. Finally, I created a resource configuration file
as follows:

```
resource home {
  device /dev/drbd0;
  meta-disk internal;

  protocol A;
  startup {
    become-primary-on Nakamura;
  }

  on Nakamura {
    disk /dev/Nakamura/home;
    address ipv4 192.168.1.10:7789;
  }
  on Nero {
    disk /dev/loop0;
    address ipv4 192.168.1.8:7789;
  }

}
```

The device option specifies what name the DRBD block device should be created
with, and meta-disk internal specifies that the DRBD metadata (which contains
such things as the dirty bitmap for syncing modified blocks) should be stored
within the backing device, rather than in some external file. The protocol line
specifies asynchronous operation (don't wait for a response from the secondary
before returning saying a write is complete), which helps performance but makes
the system less robust in the case of a sudden failure. Since my use case is
less concerned with robustness and more with simple availability and maintaining
performance as much as possible, I opted for the asynchronous protocol. The
startup block specifies that Nakamura (the workstation) should be promoted to
primary when it comes online.

The two on blocks specify the two hosts of the cluster. Nakamura's volume is
backed by a Linux logical volume (in the volume group 'Nakamura'), while Nero's
is hosted on a [loop device](https://en.wikipedia.org/wiki/Loop_device). I chose
to use a loop device on Nero simply because the machine has a large amount of
storage (6TB in RAID5), but no unallocated space, so I had to use a loop device.
In using a loop device I ended up ignoring a warning in the DRBD manual about
running it over loop block devices causing deadlocks-- this ended up being a
poor choice, as described later.

It was a fairly simple matter of bringing the volumes online once I had written
the configuration. Load the relevant kernel module, and use the userland
utilities to set up the backing device. Finally, bring the volume up. Repeat
this series of steps again on the other host.

```sh
# modprobe drbd
# drbdadm create-md home
# drbdadm up home
```

With the module loaded and a volume online, status information is visible in
/proc/drbd, looking something like the following (shamelessly taken from the
[DRBD manual](http://www.drbd.org/users-guide/ch-admin.html#s-proc-drbd)):

```sh
$ cat /proc/drbd
version: 8.3.0 (api:88/proto:86-89)
GIT-hash: 9ba8b93e24d842f0dd3fb1f9b90e8348ddb95829 build by buildsystem@linbit, 2008-12-18 16:02:26
 0: cs:Connected ro:Secondary/Secondary ds:UpToDate/UpToDate C r---
    ns:0 nr:8 dw:8 dr:0 al:0 bm:2 lo:0 pe:0 ua:0 ap:0 ep:1 wo:b oos:0
```

The first few lines provide version information, and the two lines beginning
with '0:' describe the state of a DRBD volume. Of the rest of the information,
we can see that both hosts are online and communicating (Connected), both are
currently marked as secondaries (Secondary/Secondary), and both have the latest
version of all data (UpToDate/UpToDate). The last step in creating the volume is
to mark one host as primary. Since this is a newly-created volume, marking one
host as primary requires invalidation of the other, prompting resynchronization
of the entire device. I execute drbdadm primary --force home on Nakamura to mark
that host as having the canonical version of the data, and the devices begin to
synchronize.

Once everything is set, it becomes possible to use the DRBD block device
(/dev/drbd0 in my configuration) like any other block device- create
filesystems, mount it, or write random data to it. With a little work to invoke
the DRBD initscripts at boot time, I was able to get everything working as
expected. There were a few small issues with the setup, though:

  * Nero (the NAS) required manual intervention to be promoted to the primary
    role. This could be improved by adding some sort of hooks on access to
promote it to primary and mount the volume. This could probably be implemented
with [autofs](http://autofs.org/) for a truly transparent function, or even a
simple web page hosted by the NAS which prompts promotion when it is visited.
  * Deadlocks! I mentioned earlier that I chose to ignore the warning in the
    manual about deadlocks when running DRBD on top of loop devices, and I did
start seeing some on Nero. All I/O on the volume hosting the loop device on Nero
would stall, and the only way out was by rebooting the machine.

# Conclusion

DRBD works for keeping data in sync between two machines in a transparent
fashion, at the cost of a few more software requirements and a slight
performance hit. The kernelspace tools are in mainline Linux so should be
available in any reasonably recent kernel, but availability of the userspace
utilities is questionable. Fortunately, building them for oneself is fairly
easy. Provided the drbd module is loaded, it is not necessary to use the
userspace utilities to bring the volume online- the backing block device can be
mounted without DRBD, but the secondary device will need to be manually
invalidated upon reconnect. That's useful for ensuring that it's difficult for
data to be rendered inaccessible, since the userspace utilities are not strictly
needed to get at the data.

I ultimately didn't continue running this scheme for long, mainly due to the
deadlock issues I had on the NAS, which could have been resolved with some time
spent reorganizing the storage on that host. I decided that wasn't worth the
effort, however. To achieve a similar effect, I ended up configuring a virtual
machine on my Windows installation that has direct access to the disks which
have Linux-hosted data, so I can boot the physical Linux installation in a
virtual machine. By modifying the initscripts a little, I configured it to start
Samba at boot time when running virtualized in order to give access to the data.
The virtualized solution is a bit more of a hack than DRBD and is somewhat less
robust (in case of unexpected shutdown, this makes two operating systems coming
down hard), but I think the relative simplicity and absence of a network tether
are a reasonable compromise.

Were I to go back to a DRBD-backed solution at some time, I might want to look
into using DRBD in dual-primary mode. In most applications only a single primary
can be used since most filesystems are designed without the locking required to
allow multiple drivers to operate on them at the same time (this is why NFS and
similar network filesystems require lock managers). Using a shared-disk
filesystem such as [OCFS](https://en.wikipedia.org/wiki/OCFS) (or OCFS2), DRBD
is capable of having both hosts in primary mode, so the filesystem can be
mounted and modified on both hosts at once. Using dual primaries would simplify
the promotion scheme (each host must simply be promoted to primary when it comes
online), but would also require care to avoid split-brain situations (in which
communications are lost but both hosts are still online and processing I/O
requests, so they desync and require manual intervention to resolve conflicts).
I didn't try OCFS2 at all during this experiment mainly because I didn't want to
stop using btrfs as my primary filesystem.

To conclude, DRBD works for what I wanted to do, but deadlocks while running it
on a loop device kept me from using it for long. The virtual machine-based
version of this scheme performs well enough for my needs, despite being rather
clunky to work with. I will keep DRBD in mind for similar uses in the future,
though, and may revisit the issue at a later date when my network layout
changes.

**Update 26.1.2012:** I've [revisited](../2012/high-availability-home-revisited)
this concept in a simpler (and less automatic) fashion.
