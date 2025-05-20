---
title: online.net dedibox offline migration
slug: dedibox-migration
date: 2025-05-03T09:25:00.000Z
---
I've been paying for one of [Scaleway's Dedibox servers](https://www.scaleway.com/en/dedibox/) for years, because I find it to be a good value for applications that need modest amounts of compute capability and large amounts (~1TB) of hard-drive-based (slow) storage. I noticed recently while reviewing their price lists that I was being charged more than the current published rates for my server, though: I'm being charged nearly €13 per month for a system which is only €9 per month in the public price list!

I asked them about this price discrepancy via a support ticket, and was disappointed by their response: the service is billed at the same rate as it was created at, and to get the current rate I'd need to set up a new server. This rings hollow because I recall being notified of price increases in the past (which I was willing to accept), but they will apparently not give me the benefit of lower prices. It seems like they're counting on the relative difficulty of migrating services between physical servers to milk their long-time customers for nearly 40% more money!

As a hobbyist I don't use this server for anything critical (I don't mind some downtime) and I'm highly motivated by saving about €4 per month, so I planned out how I would do that migration between systems. Read on for what those plans looked like and how execution went.

<!-- more -->

## Current state

Hardware-wise, my current server is a `START-2S-SATA` model, with a slow [Silvermont](https://en.wikichip.org/wiki/intel/microarchitectures/silvermont) Intel Atom processor, 4GB of RAM and a 1TB hard drive. Systems with the same specs are about €4 per month cheaper than I currently pay and new services cost the same as one month's service to activate, so I would break even in monetary cost (having paid less overall than if I hadn't done any migration) in only about three months.

For the OS on this server, I use [NixOS](https://nixos.org/) specifically because the way the system is configured makes it easy to rebuild should something go wrong. Whereas with a traditional Linux distribution rebuilding a system from scratch would involve manually installing any packages that were installed and then restoring configuration from backup, with Nix the entire configuration is built from a small number of plain-text files that are easy to back up. Data still needs to be restored from backups, but restoring most of the system is as simple as installing Nix, copying `configuration.nix` and any other files back over, then running `nixos-rebuild switch`.

This machine is also backed up daily using [Borg](https://www.borgbackup.org/), so I know there are up-to-date backups that could be used to rebuild it if needed, as I did need to do once a few years ago when my server failed and needed to be replaced. In that case I was able to rebuild from backup, but it took most of an afternoon which is rather more faffing about than I'd like to do (although since then I've also moved some services to elsewhere). Given I plan to migrate from a working system to a new one, I think I can do it in a way that requires less effort.

### Hardware-dependent configuration

Despite how Nix should make rebuilding system configuration easier, I also believe some parts of the system configuration are based on the current machine's hardware and/or network addresses and will need to be changed. From reading through the configuration files, there only appear to be a few:

#### Networking

Most obviously, there are some DNS names pointing at this server, both with IPv4 and IPv6 addresses. Those will need to be updated for new addresses, and anything on the server that has been taught about what addresses to use may also need to be changed.

For IPv4, Scaleway simply provide a DHCP server that will assign the correct address to a server that requests one so there is no special configuration required. IPv6 is [slightly harder](https://www.scaleway.com/en/docs/dedibox-ipv6/quickstart/), where their infrastructure will delegate a /48 subnet but it needs to be requested using an assigned [DUID](https://en.wikipedia.org/wiki/DHCPv6#DHCP_unique_identifier). My Nix configuration to set this up looks like so (with addresses and IDs redacted):

```
  systemd.services.dhcpcd = {
    preStart = ''
      cp ${pkgs.writeText "duid" "00:03:00:01:xx:xx:xx:xx:xx:xx"} /var/db/dhcpcd/duid
    '';
    serviceConfig.ReadWritePaths = ["/var/db/dhcpcd"];
  };
  networking.dhcpcd = {
    persistent = true;
    extraConfig = ''
      clientid "00:03:00:01:xx:xx:xx:xx:xx:xx"
      noipv6rs
      interface enp0s20
        ia_pd 1/2001:xxxx:xxxx::1/48 enp0s20
        static ip6_address=2001:xxxx:xxxx::1/48
    '';
  };
```

`dhcpcd` is the default DHCP client for NixOS, and I configured it to request a /48 IPv6 prefix and send the specified DUID, as well as set a static address inside the delegated prefix. A different server will have different a DUID and /48 prefix which I will need to change. Since I don't actually use the /48 prefix at all though, it's also possible that a new server will allow SLAAC (which for some reason isn't available on all Dediboxes) and I can get rid of this configuration completely.

#### Disks and boot

This system has a single hard drive that it boots from using GRUB:

```
boot.loader.grub = {
  enable = true;
  device = "/dev/sda";
};
```

The disk is partitioned with only two partitions: one ext4 volume for `/boot` and a Linux LVM physical volume containing the root filesystem and another data storage :

```
fileSystems = {
  "/" = {
    device = "/dev/mapper/lvm-root";
    fsType = "xfs";
  };
  "/boot" = {
    device = "/dev/sda1";
    fsType = "ext4";
  };
  "/data" = {
    device = "/dev/mapper/lvm-data";
    fsType = "xfs";
    options = [ "uquota" ];
  };
};
```

This doesn't refer to any device UUIDs or anything, so recreating the same structure on another machine should be enough to get it working. I haven't done any special bootloader configuration, so I also think it's likely that setting up GRUB in the same way is enough to ensure the system can boot again.

## Planning

Having investigated the configuration and found only the networking options that look like they need to be modified for a new machine (and even those only need to be updated for IPv6), I think the easiest approach to migration will be to simply copy the disk, update the network configuration then reboot and hope everything works.

Actually doing that seems like it could be done easily just with [`dd` over the network](https://superuser.com/questions/1279671/clone-disk-over-network), or perhaps more cleverly using [Clonezilla](https://clonezilla.org/). Clonezilla seems like it could be faster because it knows how to avoid copying disk blocks that are unused, but doesn't trivially support copying directly between two disks over the network[^iscsi] and doesn't seem to know how to determine unused blocks on LVM volumes so it wouldn't actually offer me very much of an advantage.

[^iscsi]: I imagine I could set up the new machine as an iSCSI target and connect the old one to that as initiator so the new machine's disk appears as a local device (backed by the one over the network), though I've never had reason to try using iSCSI before so that would be an unfamiliar workflow.

## Execution

First I wanted to boot up the new machine with a live system. Confusingly, my only option for setting up the new machine was to install one of the provided OSes on it: there was no option to boot it from some image without doing an automated installation. So I used the Dedibox web console to install Debian, with the expectation that I would immediately throw away that install. This was moderately annoying, because it was contrary to [Scaleway's installation documentation](https://www.scaleway.com/en/docs/dedibox/how-to/install-a-server/) which says there is a "Install over KVM" (using remote access via a machine's BMC) option but that I didn't see. I believe that option didn't exist because this type of machine doesn't actually have a BMC suitable for remote administration, but I didn't find any suggestion in the documentation that only some machines have that feature.

TODO figure

!\[](/static/images/dedibox-console-install.png)

After I let it automatically install Debian, I hit the "Rescue" button on the control panel to reboot the system into a RAM-based Linux system so I could erase the entire disk. The most recent version of a distribution they offer for system rescue that I was willing to use was Ubuntu 20.04 which is dismayingly out of date (although it's still supported until 2028, so it's not obsolete!), but that didn't end up being an issue at all. After waiting a while I was able to SSH in to the machine running Ubuntu from a ramdisk, and work out exactly how I was going to copy the old machine's disk over.

Next, I had to bring the disk on the old system into a read-only state. A simple method to do that could have been to boot it into a rescue system same as the old one, but I was hesitant to do so because the rescue system is so awkward to use. I also considered [switching to rescue mode](https://www.freedesktop.org/software/systemd/man/latest/systemd.special.html#rescue.target) (`systemctl isolate rescue.target`) but didn't trust that I would still be able to managed the system via SSH while in rescue mode (it's unclear if the network would stay up and my SSH session would stay alive). Instead I took advantage of [`lsof` and `awk` to find files opened for writing](https://unix.stackexchange.com/a/115722), and manually determined what services or processes needed to be stopped to close those files through various `systemctl stop` incantations. I was surprised to find that this was fairly easy, and once all writable files were closed I was able to remount all of the filesystems read-only (`mount -o remount,ro /` and so forth) so they were guaranteed not to change while I was working on copying their contents.

echo password | ssh origin "sudo -S dd if=/dev/sda bs=1M | lzop -1" | lzop -d | pv --size=1000G | sudo dd of=/dev/sda1 bs=1

Overall, the transfer proceeded at around 50 megabytes per second and completed in around 6 hours. Having some downtime overnight wasn't a concern for me, so I let it run overnight and when I got up in the morning the transfer had completed.

xfs_repair detected errors! Retransferred the root filesystem (the bulk storage one was okay) and it checked out.

### Performance

Although I haven't yet discussed it here, I did put some effort into ensuring the data transfer would complete in a reasonable amount of time: with a 1 terabyte hard drive and mandatory downtime, performance that might otherwise be acceptable (say, 10 megabytes per second) could translate to unacceptably long downtime.

The visible result of that in the commands I ran (above) was that `lzop` is included in the shell pipeline to help ensure that network bandwidth wouldn't limit transfer speed. `ethtool` on both machines reported that I had 2.5-gigabit Ethernet connections, but I wasn't confident that I'd actually be able to sustain transfers at that speed given no visibility into the network topology between the systems (although I do know that they're physically located in the same datacenter). I figured compression could help ensure the transfer wouldn't become network-limited, and by experiment found that `gzip --fast` quickly became CPU-bound on these machines (that is, it couldn't compress data as fast as the data could be transmitted) due to their slow [Intel Atom C2000-family processors](https://www.intel.com/content/www/us/en/products/sku/77977/intel-atom-processor-c2350-1m-cache-1-70-ghz/specifications.html). `lzop` won't compress as well, but was not CPU-bound.

As it turned out I don't think compression really made a difference: while monitoring the transfer (using the output from `pv`), throughput was usually around 50 megabytes per second (about 500 megabits per second) and in a test transfer to test throughput (from `/dev/zero` on the source to `/dev/null` on the destination) I only achieved about 1 gigabit per second of throughput after compression. In monitoring CPU usage I found that `ssh` on the receiver was using all available CPU time on one core, so decrypting the data in transit was probably a bigger factor in overall performance. Compression probably helps reduce that cost some (because smaller data on the wire means less data to encrypt), but I *also* didn't put any special effort into ensuring the data on disk would be compressible!

Because these systems use traditional spinning-rust hard drives (they seem to be HGST 2.5" form-factor drives), typically when a disk sector is unused its old contents will be retained. In contrast, [proactively erasing unused blocks](https://en.wikipedia.org/wiki/Trim_(computing)) usually improves overall performance of solid-state storage systems (SSDs). I could have used [`zerofree`](https://frippery.org/uml/) to erase unused disk blocks and ensure they would compress well, but didn't want to spend the time to set that tool up and then wait for it to write what may have been a very large amount of data to the source drive before I could even begin the transfer. Since `zerofree` needs to operate on an unmounted (or read-only) filesystem, I thought doing so probably wouldn't reduce the amount of mandatory downtime where I needed everything to be read-only.

In retrospect, I think `zerofree` might still have been beneficial to use, but only just barely. An old review I found for similar models of hard drive quoted sustained read and write speeds around 100 megabytes per second, or about twice the actual read and write speeds I saw while the transfer was running. Supposing that most of the disk blocks had previously been written at least once and therefore may not have contained data that would compress to any appreciable degree during the transfer, the time spent writing zeroes to them (at about 100 megabytes per second) and then reading them (at the same speed again) would average out to about the same 50 megabytes per second but would reduce the amount of CPU time required for `ssh` to handle decryption of the compressed data. If I were to repeat this process, I might reconsider trying to run `zerofree` before starting the data transfer; but on systems with better CPUs or solid-state drives it probably wouldn't be worthwhile.
