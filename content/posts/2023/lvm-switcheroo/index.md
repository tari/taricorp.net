---
title: "Switcheroo: moving a Linux system's root with LVM"
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
  ├─myhost-swap        254:0    0   512M  0 lvm  [SWAP]
  ├─myhost-root        254:1    0    40G  0 lvm  /
  ├─myhost-home        254:2    0    60G  0 lvm  /home
  └─myhost-var         254:3    0    60G  0 lvm  /var
```

The disk `sdf` is a NVMe drive in a USB enclosure, which I want to move the system to booting from. `nvme0n1` is the current boot disk, which has the root filesystem as well as `/home` and `/var` which need to be moved. Move of the data is backed by LVM, which enables this whole procedure.

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

`efibootmgr` tells us here that the firmware is configured to prefer to boot GRUB (entry `Boot0001`, which comes first in `BootOrder`), and it finds the GRUB image on `HD` number `1`, in a partition with UUID `abf0aa0a...`. The other boot entry contains a lot of text, which in this output is displayed as hexadecimal bytes but I know that it's actually meant to be text encoded with [UCS-2](https://en.wikipedia.org/wiki/Universal_Coded_Character_Set) (similar to UTF-16: two bytes per character, with the second zero for most Latin characters).

Seeing this slight mess of text summons memories from when I first configured EFI boot on this system: I remember being unable to make the firmware [directly boot the kernel](https://wiki.archlinux.org/title/EFISTUB), then giving up and using [GRUB](https://www.gnu.org/software/grub/) instead. While it seemed that the system's firmware was willing to boot a Linux kernel image directly, it would not pass the required kernel command line options so the kernel was unable to do anything useful like mount the root filesystem. Using GRUB instead means the configuration is loaded from a file rather than any parameters passed from the firmware, sidestepping that issue.

It looks like the disk number (1 for the GRUB entry that is of interest here) is chosen by the system and perhaps correlates to a physical port on the mainboard, so there should be no special considerations in making the firmware select the correct disk to boot from. To select the correct partition to load GRUB from however, either the new partition's UUID must be set to be the same as the old or the `Boot0001` entry must be updated with a new UUID.