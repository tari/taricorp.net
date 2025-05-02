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
