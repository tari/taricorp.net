---
author: tari
comments: true
date: 2012-04-30 22:08:32+00:00
layout: post
slug: chainloading-truecrypt
title: Chainloading Truecrypt
wordpress_id: 664
categories:
- Linux
- Software
tags:
- bootloader
- linux
- mbr
- syslinux
---

I recently purchased a new laptop computer (a Lenovo Thinkpad T520), and wanted
to configure it to dual-boot between Windows and Linux.  Since this machine is
to be used "on the go", I also wanted to have full encryption of any operating
systems on the device. My choices of tools for this are
[Truecrypt](http://truecrypt.sourceforge.net/) on the Windows side, and dm\_crypt
with [LUKS](https://code.google.com/p/cryptsetup/) on Linux. Mainly due to
rather troublesome design on the Windows side of this setup, it was not as easy
as I might have hoped. I did eventually get it working, however.

# Windows

Installing Windows on the machine was easy enough, following the usual
installation procedure. I created a new partition to install Windows to filling
half of the disk, and let it do its thing. Downloading and installing Truecrypt
is similarly easy. From there, I simply chose the relevant menu entry to turn on
system encryption.

The first snag appeared when the system encryption wizard refused to continue
until I had burned an optical disk containing the recovery information (in case
the volume headers were to get corrupted). I opted to copy the iso file to
another location, with the ability to boot it via
[grub4dos](https://gna.org/projects/grub4dos/) if necessary in the future (or
merely burn a disc as necessary). The solution to this was to re-invoke the
volume creation wizard with the noisocheck option:

    C:\Program Files\TrueCrypt>TrueCrypt Format.exe /noisocheck

One reboot followed, and I was able to let TrueCrypt go through and encrypt the
system. It was then time to set up Linux.

# Linux

Basic setup of my Linux system was straightforward. Arch (my distribution of
choice) offers [good
support](https://wiki.archlinux.org/index.php/System_Encryption_with_LUKS) for
LUKS encryption of the full system, so most of the installation went smoothly.

On reaching the bootloader installation phase, I let it install and configure
syslinux (my loader of choice simply because it is easier to configure than
GRUB), but did not install it to the MBR. With the installation complete, I had
to do some work to manually back up the MBR installed by Truecrypt, then install
a non-default MBR for Syslinux.

First up was backing up the Truecrypt MBR to a file:

```
# dd if=/dev/sda of=/mnt/boot/tc.bs count=1
```

That copies the first sector of the disk (512 bytes, containing the MBR and
partition table) to a file (tc.bs) on my new /boot partition.

Before installing a Syslinux MBR, I wanted to ensure that chainloading the MBR
from a file would work. To that end, I used the installer to chainload to my new
installation, and used that to attempt loading Windows. The following
incantation (entered manually from the syslinux prompt) eventually worked:

    .com32 chain.c32 hd0 1 file=/tc.bs

Pulling that line apart, I use the chainloader to boot the file tc.bs in the
base of my /boot partition, and load the first partition on my first hard drive
(that is, where Windows is installed). This worked, so I booted once more into
the installer to install the Syslinux MBR:

    # dd if=/usr/lib/syslinux/mbr.bin of=/dev/sda bs=1 count=440 conv=notrunc

This copies 440 bytes from the given file to my hard drive, where 440 bytes is
the size of the MBR. The input file is already that size so the count parameter
should not be necessary, but one cannot be too careful when doing such
modification to the MBR.

Rebooting that, sadly, did not work. It turns out that the Syslinux MBR merely
scans the current hard drive for partitions that are marked bootable, and boots
the first one. The Truecrypt MBR does the same thing, which is troublesome-- in
order for Truecrypt to work the Windows partition must be marked bootable, but
Syslinux is unable to find its configuration when this is the case.

Enter albmbr.bin. Syslinux ships [several different
MBRs](http://www.syslinux.org/wiki/index.php/Mbr), and the alternate does not
scan for bootable partitions. Instead, the last byte of the MBR is set to a
value indicating which partition to boot from. Following the example from the
Syslinux wiki (linked above), then, I booted once more from my installer and
copied the altmbr into position:

    # printf '\x5' | cat /usr/lib/syslinux/altmbr.bin - | dd bs=1 count=440 conv=notrunc of=/dev/sda

This shell pipeline echoes a single byte of value 5, appends it to the contents
of altmbr.bin, and writes the resulting 440 bytes to the MBR on sda. The 5 comes
from the partition Syslinux was installed on, in this case the first logical
partition on the disk (/dev/sda5).

With that, I was able to boot Syslinux properly and it was a simple matter to
modify the configuration to boot either Windows or Linux on demand. Selected
parts of my syslinux.cfg file follow:

    UI menu.c32
    
    LABEL arch
        MENU LABEL Arch Linux
        LINUX /vmlinuz-linux
        APPEND root=/dev/mapper/Homura-root cryptdevice=/dev/sda6:HomuHomu ro
        INITRD /initramfs-linux.img
    
    LABEL windows
        MENU LABEL Windows 7
        COM32 chain.c32
        APPEND hd0 1 file=/tc.bs

# Further resources

For all things Syslinux, the [documentation
wiki](http://www.syslinux.org/wiki/index.php/The_Syslinux_Project) offers
documentation sufficient for most purposes, although it can be somewhat
difficult to navigate. A message from the [Syslinux mailing
list](http://zytor.com/pipermail/syslinux/2009-May/012557.html) gave me the key
to making Syslinux work from the MBR. The [Truecrypt
documentation](http://www.truecrypt.org/docs/) offered some interesting
information, but was surprisingly useless in the quest for a successful
chainload (indeed, the volume creation wizard very clearly states that using a
non-truecrypt MBR is not supported).
