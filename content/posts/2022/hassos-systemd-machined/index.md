---
title: HassOS VM with systemd-machined
slug: hassos-systemd-machined
draft: true
date: 2022-01-07T23:06:56.168Z
---

I've been running [Home Assistant] on my home server in a Docker container for a while, using the 'Hass.io' configuration. However, while investigating some issues with the supervisor component (that provides the simple management features) where it seemed to be crashing I discovered that 'Hass.io' is no longer a supported configuration. The new equivalent is "Home Assistant Supervised" but the setup tool for that configuration only seems to officially support Debian-based systems and the documentation warns that other configuration should be preferred.

The other supported configurations are "Home Assistant Container" which appears to simply be a standalone OCI (Docker) container without the supervisor cmoponent, or a full-block virtual machine.

```
machinectl pull-raw --verify=no https://github.com/home-assistant/operating-system/releases/download/7.1/haos_ova-7.1.qcow2.xz HassOS-7.1
```

This fails because I don't have enough free disk space, I assume machinectl is being kind of dumb about unpacking the image and not making it sparse. I don't really want an opaque image anyway, so I'll unpack it to a tar and import that.

```
wget https://github.com/home-assistant/operating-system/releases/download/7.1/haos_ova-7.1.qcow2.xz
unxz haos_ova-7.1.qcow2.xz
sudo guestmount -a haos_ova-7.1.qcow2 -i /mnt
```

Guestmount seems to hang, so instead try to convert to a sparse raw image and import that.

```
$ qemu-img convert -S 1k haos_ova-7.1.qcow2 haos_ova-7.1.raw
$ machinectl import-raw haos_ova-7.1.raw HassOS-7.1
$ machinectl list-images
NAME       TYPE RO  USAGE CREATED                      MODIFIED
HassOS-7.1 raw  no 820.1M Sat 2022-01-08 10:26:51 AEDT Sat 2022-01-08 10:26:52 AEDT

1 images listed.
```

This seems to have worked, now machined has the image.