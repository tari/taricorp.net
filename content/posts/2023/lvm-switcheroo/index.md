---
title: Moving a Linux system's root without rebooting
slug: lvm-switcheroo
date: 2023-08-29T05:13:24.389Z
---
## Discovering the current state

Although I know this sytem uses LVM, it's been a while since I configured it so many of the details are fuzzy. Before beginning, I needed to investigate what the current configuration was in order to understand what I should do to perform the switcheroo.

First, I used `lsblk` to understand what storage devices were connected and in use (with irrelevant ones omitted here):

```
# lsblk
NAME                   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sdf                      8:80   0 953.9G  0 disk
nvme0n1                259:1    0 238.5G  0 disk
├─nvme0n1p1            259:2    0   512M  0 part /boot
└─nvme0n1p2            259:3    0   238G  0 part
  ├─myhost-root        254:0    0    40G  0 lvm  /
  ├─myhost-home        254:1    0    60G  0 lvm  /home
  └─myhost-var         254:2    0    60G  0 lvm  /var
```

The disk `sdf` is a NVMe drive in a USB enclosure, which I want to move the system to booting from. `nvme0n1` is the current boot disk, which has the root filesystem as well as `/home` and `/var` which need to be moved. Most of the data is backed by LVM, which enables this whole procedure.

There's also a small (512MB) partition at `nvme0n1p1` mounted at /boot. This will be important to preserve. Looking at the disk's partition table in detail provides more useful information (with information that's not relevant to this discussion removed):

```
# gdisk -l /dev/nvme0n1
Found valid GPT with protective MBR; using GPT.
Disk /dev/nvme0n1: 500118192 sectors, 238.5 GiB
Sector size (logical/physical): 512/512 bytes

Number  Start (sector)    End (sector)  Size       Code  Name
   1            2048         1050623   512.0 MiB   EF00  EFI system partition
   2         1050624       500117503   238.0 GiB   8E00  Linux LVM
```

### EFI configuration

The small boot partition is in fact a EFI system partition (ESP), telling us a few things:

 * This machine uses [UEFI](https://en.wikipedia.org/wiki/UEFI) to boot, not legacy BIOS.
 * It's impossible to put this data on LVM, because the system firmware needs to be able to read the files stored therein. (It's actually formatted with a FAT32 filesystem, which is common for EFI systems.)
 * The [boot sector](https://en.wikipedia.org/wiki/Boot_sector) and any data stored outside a partition does not need to be preserved, because only the data on the ESP is needed to boot. Compare to legacy BIOS, where the boot sector always contains bootloader code that must be preserved and sometimes bootloader code is stored in unpartitioned areas of the disk which must also be preserved.
 * The firmware may have references to partition UUIDs that tell it what to boot from, which would need to either be preserved or updated later.

To understand what the firmware's boot configuration is, I can use `efibootmgr`:

```
# efibootmgr
BootCurrent: 0001
Timeout: 5 seconds
BootOrder: 0001,0000
Boot0000* Arch Linux    VenHw(99e275e7-75a0-4b37-a2e6-c5385e6c00cb)72006f006f0074003d002f006400650076002f006d00610070007000650072002f006b006900720069007300680069006d0061005f006e00650077002d0072006f006f007400200072007700200069006e0069007400720064003d002f0069006e00740065006c002d00750063006f00640065002e0069006d006700200069006e0069007400720064003d002f0069006e0069007400720061006d00660073002d006c0069006e00750078002e0069006d006700
Boot0001* GRUB  HD(1,GPT,abf0aa0a-b6ed-45a9-9c16-77727fef1538,0x800,0x100000)/File(\EFI\GRUB\grubx64.efi)
```

`efibootmgr` tells us here that the firmware is configured to prefer to boot GRUB (entry `Boot0001`, which comes first in `BootOrder`), and it finds the GRUB image on `HD` number `1`, in a partition with UUID `abf0aa0a…`. The other boot entry contains a lot of text, which in this output is displayed as hexadecimal bytes but I know that it's actually meant to be text encoded with [UCS-2](https://en.wikipedia.org/wiki/Universal_Coded_Character_Set) (similar to UTF-16: two bytes per character, with the second zero for most Latin characters).

Seeing this slight mess of text summons memories from when I first configured EFI boot on this system: I remember being unable to make the firmware [directly boot the kernel](https://wiki.archlinux.org/title/EFISTUB), then giving up and using [GRUB](https://www.gnu.org/software/grub/) instead. While it seemed that the system's firmware was willing to boot a Linux kernel image directly, it would not pass the required kernel command line options so the kernel was unable to do anything useful like mount the root filesystem. Using GRUB instead means the configuration is loaded from a file rather than any parameters passed from the firmware, sidestepping that issue.

It looks like the disk number (1 for the GRUB entry that is of interest here) is chosen by the system and perhaps correlates to a physical port on the mainboard, so there should be no special considerations in making the firmware select the correct disk to boot from. To select the correct partition to load GRUB from however, either the new partition's UUID must be set to be the same as the old or the `Boot0001` entry must be updated with a new UUID.

To confirm that this UUID refers to the UEFI system partition, I looked at `/dev/disk/by-partuuid` and verified that the file `abf0aa0a…` is a link to `nvme0n1p1`: the ESP. It seems plausible that there might be a way to tell the firmware to load something from the ESP directly without specifying the filesystem UUID, but I'm not sufficiently motivated to discover if that's true right now.

## Moving /boot

To move the ESP, I've chosen to reuse the original partition UUID so I don't need to change firmware configuration at all. This should make it easier to switch back to the old disk if I need to.

First I used `gdisk` to interactively create a partition on the new disk with the same size, partition type, and UUID as the original:

```
# gdisk /dev/sdf
GPT fdisk (gdisk) version 1.0.9.1

Partition table scan:
  MBR: protective
  BSD: not present
  APM: not present
  GPT: present

Found valid GPT with protective MBR; using GPT.

Command (? for help): p
Disk /dev/sdf: 2000409264 sectors, 953.9 GiB
Model: Generic
Sector size (logical/physical): 512/4096 bytes
Disk identifier (GUID): CE6A291B-12C9-4669-BF19-8696D81FBF4B
Partition table holds up to 128 entries
Main partition table begins at sector 2 and ends at sector 33
First usable sector is 34, last usable sector is 2000409230
Partitions will be aligned on 2048-sector boundaries
Total free space is 2000409197 sectors (953.9 GiB)

Number  Start (sector)    End (sector)  Size       Code  Name

Command (? for help): n
Partition number (1-128, default 1):
First sector (34-2000409230, default = 2048) or {+-}size{KMGTP}:
Last sector (2048-2000409230, default = 2000408575) or {+-}size{KMGTP}: +512M
Current type is 8300 (Linux filesystem)
Hex code or GUID (L to show codes, Enter = 8300): EF00
Changed type of partition to 'EFI system partition'

Command (? for help): x

Expert command (? for help): c
Using 1
Enter the partition's new unique GUID ('R' to randomize): abf0aa0a-b6ed-45a9-9c16-77727fef1538
New GUID is ABF0AA0A-B6ED-45A9-9C16-77727FEF1538 
```

After writing that and exiting `gdisk`, `gdisk -l /dev/sdf` verifies that the new partition has the same size (start and end sectors) as the old one, so I'm happy with this result.

### Copying the filesystem

To copy the filesystem, I'd like to take a bit-exact copy to ensure there won't be any unexpected differences between the original and copy. Since I don't need to write to this filesystem in most cases, I can remount it read-only then copy the block device directly:

```
# mount -o remount,ro /boot
# dd if=/dev/nvme0n1p1 of=/dev/sdf1 bs=1M
512+0 records in
512+0 records out
536870912 bytes (537 MB, 512 MiB) copied, 14.6401 s, 36.7 MB/s
```

To ensure consistency, this filesystem should remain read-only until I replace it with the new copy. Otherwise changes wouldn't be propagated to the copy, and I'd need to copy it again.

## LVM switcheroo

With the non-LVM data moved, it's on to the rest. To recall how LVM works (or provide a quick introduction to readers unfamiliat with it), the Linux Logical Volume Manager (LVM) offers a variety of features to abstract away the details of persistent storage devices.

 * Physical volumes (PVs) are created on physical storage (actual hard disks).
 * Multiple PVs can be combined into a volume group (VG), which acts like a storage pool made up of all of the PVs in the VG.
 * Logical volumes (LVs) are created on VGs and act like regular disk partitions, but given superpowers by the layers of VG and PV underneath.

By sitting between actual storage and the "partition" that typically has a filesystem on it (a LV), it's possible to configure the LV to behave entirely unlike a real disk. A few interesting capabitilies:

 * A "thin" LV can be larger than the underlying PV, which might be useful in a system that is actively managed and the administrator ensures there is always enough storage available: they can create a very large filesystem that doesn't need to be resized as storage is added, without having enough storage for the entire filesystem from the outset.
 * "Snapshot" LVs capture changes to another LV, exactly capturing its contents at the time the snapshot was created without blocking writes to the original. This works a lot like the snapshot features of [ZFS](https://klarasystems.com/articles/basics-of-zfs-snapshot-management/) and [btrfs](https://fedoramagazine.org/working-with-btrfs-snapshots/), but isn't tied to use of any particular filesystem.
 * Allocation policy of a LV with regard to the PVs in its VG can be controlled, often using the `raid` LV type to use any of the common [RAID](https://en.wikipedia.org/wiki/RAID) allocation policies to spread data across disks to improve performance, provide redundancy against disk failure, or both.

### Desired configuration

After doing some reading of the LVM-related documentation (in particular [lvmraid(7)](https://www.man7.org/linux/man-pages/man7/lvmraid.7.html), I concluded that temporarily configuring my LVs as RAID1 across the two devices is a sensible approach. By also setting the *activation mode* to *degraded*, the system will allow the relevant LVs to be used as long as either PV it's on (assuming RAID1 with two devices) is present. By doing this, I can reconfigure the LVs then wait for them to be synced, and reboot to swap in the new storage. If something goes wrong with the new one, I can connect the old one and they will still have the same contents so I can easily roll back and try again.

First, create a PV on the new disk in a new partition that fills the rest of the device (`sdf2`) and add it to the VG (which is named `myhost`):

```
# pvcreate /dev/sdf2
  Physical volume "/dev/sdf2" successfully created.
# vgextend myhost /dev/sdf2
```

At this point `vgdisplay` shows there are two active PVs in the VG, and its size is much larger than it was previously. Now convert each of the LVs I care about to RAID1, mirrored across both PVs:

```
# for lv in root var home; do
for> lvconvert --type raid1 --mirrors 1 myhost/$lv
for> done
Are you sure you want to convert linear LV myhost/root to raid1 with 2 images enhancing resilience? [y/n]: y
  Logical volume myhost/root successfully converted.
Are you sure you want to convert linear LV myhost/var to raid1 with 2 images enhancing resilience? [y/n]: y
  Logical volume myhost/var successfully converted.
Are you sure you want to convert linear LV myhost/home to raid1 with 2 images enhancing resilience? [y/n]: y
  Logical volume myhost/home successfully converted.
```

After conversion, the LVs need to sync: make a copy of all their data on the new PV. The `lvmraid` manpage says to use `lvs -a -o name,sync_percent` to monitor this process:

```
# lvs -a -o name,sync_percent
  LV              Cpy%Sync
  root            3.71
  [root_rimage_0]
  [root_rimage_1]
  [root_rmeta_0]
  [root_rmeta_1]
```

Before continuing, I waited until `Cpy%Sync` was 100% for each of the volumes. To ensure that the system will still try to boot with only one replica present, I verified that the current LVM configuration allowed degraded RAID LVs to be activated:

```
# lvmconfig --type current activation/activation_mode
activation_mode="degraded"
```

Since this was already set as I wanted, I didn't need to make any further changes, and could shut down to swap out the old disk and install the new one.

## Unexpected misbehavior

After swapping the two disks and disconnecting the one in the USB enclosure (leaving only the new one installed in the machine), the firmware booted the Linux kernel correctly, but the system didn't boot successfully, complaining that it couldn't find the root filesystem. Using the rescue shell I was able to determine that all my LVs were present, but inactive (unusable until activated) and in the `partial` state, seemingly indicating that some important metadata was stored only on the original PV and LVM refused to allow the LVs to activate because it didn't have all of the data needed to manage them correctly.

I suspect there may have been a way to repair this RAID issue, but I opted to fall back to the approach I had used previously rather than embark into the unknown

## Without redundancy

Since I had already managed to break the system more by attempting to use RAID than the old approach would have, I fell back at this point to the workflow I had used previously that still allows everything to be moved without downtime other than for physically moving hardware around but makes rollback to the original state more difficult. Unfortunately because I had already broken the system, I had to do this from a rescue shell after crawling around to connect the requisite cables so I could use the rescue shell.

1. Convert the VG back to `linear` allocation, rather than `raid1`
2. Move all data off the old PV
3. Remove the old PV from the VG
4. (optional) Wipe the old PV

```
# lvconvert --type linear myhost/root myhost/var myhost/home
# pvmove /dev/sdf2
# vgreduce myhost /dev/sdf2
# pvremove /dev/sdf2
```

`pvmove` takes a while to complete, because it moves all data on `sdf2` to other PVs in the VG. Then `vgreduce` removes the PV from the VG, and `pvremove` wipes the PV signature off the old disk.

After doing that, I rebooted normally and the system came up as expected this time, running entirely on the new disk. Meanwhile, the old disk has no data left on it and could be reused for other purposes.

## Useful tools, if you don't mess it up

Since this captures a workflow I've used before to minimize downtime when moving a Linux system's root between physical devices but never written it down, this writeup should be useful to me in the future and hopefully suggests the same or similar choices to future readers seeking to do something similar.

My failed experiment with LVM RAID also indicates that when doing low-level computer maintenance it's often best to go with a proven approach to avoid nasty surprises: this nasty surprise wasn't too bad, but it did delay my dinner while I sorted it out. Had it worked out then I would have added another tool to my arsenal, and because this system isn't very critical to anybody, on balance the learning experience seems to have been worthwhile. For the future however, I'd want to either do more experimentation before trying that approach again, or simply follow the well-trod path for safety.