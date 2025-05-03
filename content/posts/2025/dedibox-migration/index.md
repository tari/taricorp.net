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
