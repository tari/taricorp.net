---
date: 2017-11-07
title: Considering my backup systems
slug: considering-backup-systems
categories:
 - Software
tags:
  - cloud
  - archiving
  - paranoia
  - btrfs
  - linux
  - windows
---

With the recent news that [Crashplan were doing away with their "Home"
offering](https://www.crashplan.com/en-us/consumer/nextsteps/), I had reason to
reconsider my choice of online backup backup provider. Since I haven't written
anything here lately and the results of my exploration (plus description of
everything else I do to ensure data longevity) might be of interest to others
looking to set up backup systems for their own data, a version of my notes from
that process follows.

## The status quo

I run a Linux-based home server for all of my long-term storage, currently 15
terabytes of raw storage with btrfs RAID on top.  The choice of btrfs and RAID
allows me some degree of robustness against local disk failures and accidental
damage to data.

If a disk fails I can replace it without losing data, and using btrfs' RAID
support it's possible to use heterogenous disks, meaning when I need more
capacity it's possible to remove one disk (putting the volume into a degraded
state) and add a new (larger) one and rebalance onto the new disk.

btrfs' ability to take copy-on-write snapshots of subvolumes at any time makes it reasonable
to take regular snapshots of everything, providing a first line of defense against accidental
damage to data. I use [Snapper][snapper] to automatically create rolling snapshots of each
of the major subvolumes:

[snapper]: http://snapper.io/

 * *Synchronized files* (mounted to other machines over the network) have 8 hourly,
   7 daily, 4 weekly and 3 monthly snapshots available at any time.
 * *Staging* items (for sorting into other locations) have a snapshot for each of the
   last two hours only, because those items change frequently and are of low value until
   considered further.
 * Everything else keeps one snapshot from the last hour and each of the last 3 days.

This configuration strikes a balance according to my needs for accident
recovery and storage demands plus performance. The frequently-changed items
(synchronized with other machines and containing active projects) have a lot of
snapshots because most individual files are small but may change frequently, so
a large number of snapshots will tend to have modest storage needs. In
addition, the chances of accidental data destruction are highest there. The
other subvolumes are either more static or lower-value, so I feel little need
to keep many snapshots of them.

I use Crashplan to back up the entire system to their "cloud"[^1] service for
$5 per month. The rate at which I add data to the system is usually lower than
the rate at which it can be uploaded back to Crashplan as a backup, so in most
cases new data is backed up remotely within hours of being created.

[^1]: [There is no cloud, it's just someone else's computer.](http://www.chriswatterston.com/blog/my-there-is-no-cloud-sticker)

Finally, I have a large USB-connected external hard drive as a local offline
backup. Also formatted with btrfs like the server (but with the entire disk
encrypted), I can use `btrfs send` to send incremental backups to this external
disk, even without the ability to send information from the external disk back.
In practice, this means I can store the external disk somewhere else completely
(possibly without an Internet connection) and occasionally shuttle diffs to it
to update to a more recent version. I always unplug this disk from power and
its host computer when not being updated, so it should only be vulnerable to
physical damage and not accidental modification of its contents.

### Synchronization and remotes

For synchronizing current projects between my home server (which I treat as the
canonical repository for everything), the tools vary according to the
constraints of the remote system. I mount volumes over NFS or SMB from systems
that rarely or never leave my network. For portable devices (laptop computers),
[Syncthing][syncthing] (running on the server and portable device) makes
bidirectional synchronization easy without requiring that both machines always
be on the same network.

[syncthing]: https://syncthing.net/

I keep very little data on portable devices that is not synchronized back to the
server, but because it is (or, was) easy to set up, I used Crashplan's
peer-to-peer backup feature to back up my portable computers to the server.
Because the Crashplan application is rather heavyweight (it's implemented in
Java!) and it refuses to include peer-to-peer backups in uploads to their storage
service (reasonably so; I can't really complain about that policy), my remote
servers back up to my home server with [Borg][borg].

[borg]: https://www.borgbackup.org/

I also have several Android devices that aren't always on my home network-
these aren't covered very well by backups, unfortunately. I use
[FolderSync][foldersync] to automatically upload things like photos to my
server which covers the extent of most data I create on those devices, but it
seems difficult to make a backup of an Android device that includes things like
preferences and per-app data without rooting the device (which I don't wish to
do for various reasons).

[foldersync]: https://play.google.com/store/apps/details?id=dk.tacit.android.foldersync.full

### Summarizing the status quo

 * btrfs snapshots offer quick access to recent versions of files.
 * btrfs RAID provides resilience against single-disk failures and easy growth
   of total storage in my server.
 * Remote systems synchronize or back up most of their state to the server.
 * Everything on the server is continuously backed up to Crashplan's remote
   servers.
 * A local offline backup can be easily moved and is rarely even connected to a
   computer so it should be robust against even catastrophic failures.

## Evaluating alternatives

Now that we know how things were, we can consider alternative approaches to
solve the problem of Crashplan's $5-per-month service no longer being
available. The primary factors for me are cost and storage capacity. Because
most of my data changes rarely but none of it is strictly immutable, I want a
system that makes it possible to do incremental backups. This will of course
also depend on software support, but it means that I will tend to prefer
services with straightforward pricing because it is difficult to estimate how
many operations (read or write) are necessary to complete an incremental
backup.

Some services like Dropbox or Google Drive as commonly-known examples might be
appropriate for some users, but I won't consider them. As consumer-oriented
services positioned for the use case of "make these files available whenever
I have Internet access," they're optimized for applications very different
from the needs of my backups and tend to be significantly more expensive at
the volumes I need.

So, the contenders:

 * **[Crashplan for Small Business](https://www.crashplan.com/en-us/business/)**:
   just like Crashplan Home (which was going
   away), but costs $10/mo for unlimited storage and doesn't support
   peer-to-peer backup. Can migrate existing Crashplan Home backup archives to
   Small Business as long as they are smaller than 5 terabytes.
 * **[Backblaze](https://www.backblaze.com/cloud-backup.html)**: $50 per year for
   unlimited storage, but their client only runs on Mac and Windows.
 * **[Google Cloud Storage](https://cloud.google.com/storage/)**: four flavors
   available, where the interesting ones for backups are Nearline and Coldline.
   Low cost per gigabyte stored, but costs are incurred for each operation and
   transfer of data out.
 * **[Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html)**: very low
   cost per gigabyte, but incurs costs for download.
 * **[Online.net C14](https://www.online.net/en/c14)**: very low cost per gigabyte,
   no cost for operations or data transfer in the "intensive" flavor.
 * **[AWS Glacier](https://aws.amazon.com/glacier/)**: lowest cost for storage,
   but very high latency and cost for data retrieval.

The pricing is difficult to consume in this form, so I'll make some estimates
with an 8 terabyte backup archive. This somewhat exceeds my current needs, so
should be a useful if not strictly accurate guide. The following table
summarizes expected monthly costs for storage, addition of new data and the
hypothetical cost of recovering everything from a backup stored with that
service.

<table>
    <tr>
        <th>Service</th>
        <th>Storage cost</th>
        <th>Recovery cost</th>
        <th>Notes</th>
    </tr>
    <tr>
        <th>Crashplan</th>
        <td>$10</td>
        <td>0</td>
        <td>"Unlimited" storage, flat fee.</td>
    </tr>
    <tr>
        <th>Backblaze</th>
        <td>$4.17</td>
        <td>0</td>
        <td>"Unlimited" storage, flat fee.</td>
    </tr>
    <tr>
        <th>GCS Nearline</th>
        <td>$80</td>
        <td>~$80</td>
        <td>Negligible but nonzero cost per operation.
            Download $0.08 to $0.23 per gigabyte depending on total monthly
            volume and destination.</td>
    </tr>
    <tr>
        <th>GCS Coldline</th>
        <td>$56</td>
        <td>~$80</td>
        <td>Higher but still negligible cost per operation.
            All items must be stored for at least 90 days (kind of).</td>
    </tr>
    <tr>
        <th>B2</th>
        <td>$40</td>
        <td>$80</td>
        <td>Flat fee for storage and transfer per-gigabyte.</td>
    </tr>
    <tr>
        <th>C14</th>
        <td>€40</td>
        <td>0</td>
        <td>"Intensive" flavor. Other flavors incur per-operation costs.</td>
    </tr>
    <tr>
        <th>Glacier</th>
        <td>$32</td>
        <td>$740</td>
        <td>Per-gigabyte retrieval fees plus Internet egress. Reads may take up
            to 12 hours for data to become available. Negligible cost per operation.
            Minimum storage 90 days (like Coldline).</td>
    </tr>
</table>

Note that for Google Cloud and AWS I've used the pricing quoted for the
cheapest regions; Iowa on GCP and US East on AWS.

### Analysis

Backblaze is easily the most attractive option, but the availability restriction
for their client (which is required to use the service) to Windows and Mac makes
it difficult to use. It may be possible to run a Windows virtual machine on my
Linux server to make it work, but that sounds like a lot of work for something
that may not be reliable. **Backblaze is out.**

AWS Glacier is inexpensive for storage, but extremely expensive and slow when retrieving
data. The pricing structure is complex enough that I'm not comfortable depending
on this rough estimate for the costs, since actual costs for incremental backups
would depend strongly on the details of how they were implemented (since the
service incurs charges for reads and writes). The extremely high latency on bulk
retrievals (up to 12 hours) and higher cost for lower-latency reads makes it
questionable that it's even reasonable to do incremental backups on Glacier.
**Not Glacier.**

C14 is attractively priced, but because they are not widely known I expect backup
packages will not (yet?) support it as a destination for data. Unfortunately, that
means **C14 won't do.**

Google Cloud is fairly reasonably-priced, but Coldline's storage pricing is confusing
in the same ways that Glacier is. Either flavor is better pricing-wise than
Glacier simply because the recovery cost is so much lower, but **there are still better
choices than GCS.**

B2's pricing for storage is competitive and download rates are reasonable
(unlike Glacier!). It's worth considering, but **Crashplan still wins in
cost.** Plus I'm already familiar with software for doing incremental backups
on their service (their client!) and wouldn't need to re-upload everything to a
new service.

## Fallout

I conclude that the removal of Crashplan's "Home" service effectively means a doubling
of the monthly cost to me, but little else. There are a few extra things to consider,
however.

First, my backup archive at Crashplan was larger than 5 terabytes so could not
be migrated to their "Business" version. I worked around that by removing some
data from my backup set and waiting a while for those changes to translate to
"data is actually gone from the server including old versions," then migrating
to the new service and adding the removed data back to the backup set. This
means I probably lost a few old versions of the items I removed and re-added,
but I don't expect to ever need any of them.

Second and more concerning in general is the newfound inability to do
peer-to-peer backups from portable (and otherwise) computers to my own server.
For Linux machines that are always Internet-connected Borg continues to do the
job, but I needed a new package that works on Windows. I've eventually chosen
[Duplicati](https://www.duplicati.com/), which can connect to my server the
same way Borg does (over SSH/SFTP) and will in general work over
arbitrarily-restricted internet connections in the same way that Crashplan did.

## Concluding

I'm still using Crashplan, but converting to their more-expensive service
was not quite trivial. It's still much more inexpensive to back up to
their service compared to others, which means they still have some
significant freedom to raise the cost until I consider some other way
to back up my data remotely.

As something of a corollary, it's pretty clear that my high storage use on
Crashplan is subsidized by other customers who store much less on the service;
this is just something they must recognize when deciding how to price the
service!

