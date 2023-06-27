---
title: Building a gitlab-runner virtual appliance
slug: gitlab-runner-appliance
draft: true
date: 2023-03-27T02:57:03.963Z
categories:
  - software
tags:
  - docker
  - gitlab-runner
  - gitlab
  - buildroot
  - virtualization
  - qemu
  - libvirt
  - virtual-appliance
---
I use [Gitlab CI](https://docs.gitlab.com/ee/ci/) to run continuous integration builds for some software that I'm responsible for. I'm generally happy with its functionality as well as the availability of free builders for public open-source projects (allowing those projects to run builds on machines managed by Gitlab.com).

I also run builds for some private projects that don't qualify for free builds however, and those projects use enough resources (more than 2000 machine-minutes per month) to exceed their free allotment of builder minutes. While I could buy additional build resources from Gitlab themselves, the monetary value of these builds to me isn't that large so I'd prefer to donate resources I already have by hosting runners myself, on machines that I already use for other tasks but which have resources to spare.

[Hosting a Gitlab runner](https://docs.gitlab.com/runner/) is pretty easy if you can dedicate a machine to it, because then security is an easy problem to solve (ensure it only runs builds for things that you trust) and resource management is similarly easy (only allocate the resources you're willing to give it). Doing the same thing on a system that is also used for other tasks however is somewhat more difficult.

## Isolating builds

Although the runner has other modes, the most convenient way to manage builds is by running them in Docker containers because then individual projects have a convenient way to describe the environment in which they are meant to run. Docker isn't really meant to be sandboxed however[^rootless], and in the typical configuration a single Docker engine runs as root on a single computer. If a project in CI wants to use docker itself (for example to build a container image of the project), there are two-and-a-bit options:

[^rootless]: "Rootless Docker" is a supported mode in which the Docker engine (the component that actually spawn containers) doesn't need to have root privileges, but it's rather fiddly to set up.

1. Run a Docker-in-Docker container. This puts a copy of the Docker engine inside a container (itself running inside the Docker engine on the host machine), which is mostly isolated from the host but requires careful configuration to get good performance. It also requires that the outer container be run in **privileged mode** which makes it possible for software running inside the outer container (the CI build) to access the host system with relative ease.
2. Expose the Docker engine's control socket inside the container (mount `/var/lib/docker.sock`). This is easier to set up, giving the build unfettered access to the Docker engine running on the host, allowing it to send **arbitrary commands** such as "start a container that will mine Bitcoin in the background, then run the CI build".
3. Don't use `docker` for builds, instead using tools that don't need to be able to run containers in order to build them like [buildah](https://buildah.io/) or [kaniko](https://github.com/GoogleContainerTools/kaniko).

Although the third option is generally best (I particularly appreciate Kaniko, because its ability to consume a `Dockerfile` means it's easy to interactively develop the recipe for building a container, then use a different tool in CI), it's not always good enough- especially if you want to run a container that you've just built, perhaps to verify that it works as expected before publishing it. Unfortunately, the other two options both open up quite large security holes that could be abused by malicious builds.

On a dedicated CI host these risks are somewhat less important because there probably isn't any data present that relates to anything but CI builds (so there's a very limited amount of data that's interesting to steal), but if I want to use spare resources on systems that I use for other things then those risks seem problematic: unrelated system data should not be accessible to the builder, even though builds should be able to use `docker` themselves in order to build or test container images.

### Resource limits

Similarly, ensuring that a CI runner doesn't use excessive resources can be somewhat difficult. The risk of using all of the resources of a dedicated CI runner is small (at worst, it stops working and needs to be restarted or have some unneeded files deleted), but compromising the functionality of other services by consuming all available resources on a shared machine would be problematic.

It's relatively simple to limit the amount of CPU time or memory that can be used by a given Docker container, and `gitlab-runner` allows that to be configured for each job that is run. Somewhat more difficult to manage is disk usage however, because Docker uses disk for a variety of uses:

 * Container images; the files making up the environment in which containers run.
 * Container data; the data that a container writes when it runs.
 * Volumes; additional storage that can be attached to containers.

Docker provides some limited tools for managing storage, but nothing that is very useful for limiting the amount of disk used beyond basic applications like "delete everything that isn't currently in use." [docuum](https://github.com/stepchowfun/docuum) is a convenient third-party tool to help limit the amount of disk space used by container images by cleaning up old ones that aren't in use, but needs to be set up manually. Many filesystems allow administrators to specify disk quotas for individual users or groups which provides very robust disk utilization limits, but those can be tricky to configure and are not very familiar to most users.

### Virtualization to the rescue

Given all of these concerns and limitations around providing privileged access to a system that runs other tasks and limiting the resources that can be consumed, virtualization seems like the perfect solution. It's quite easy to create a virtual machine running a Linux distribution of your choice and install a Gitlab Runner on it, and I'm sure many people do exactly that. I'm not very pleased with the idea of creating a virtual machine that requires maintenance like any other system (ensuring installed packages get updated and the like), so I investigated creating a "virtual appliance" for the application instead.

The general idea of a virtual appliance is to build a virtual machine image that can be booted and be used nearly immediately with minimal configuration, and requiring near-zero maintenance effort as well. How hard could that be?

## Creating an appliance

There are two major recent inspirations for what I wanted to do:
 * [Wesley Moore's garage door monitor](https://www.wezm.net/v2/posts/2022/garage-door-monitor/) runs a custom application and little else on a Raspberry Pi to provide a garage door-related network service.
 * [Home Assistant OS](https://www.home-assistant.io/installation/linux) packages Home Assistant (a fairly complex piece of Python software) into a virtual machine that's easy to update and suitable even for (somewhat) non-technical users.

Both of these are based on [Buildroot](https://buildroot.org/), a tool designed for building Linux-based embedded systems. Noting that a virtual appliance is really just a form of embedded system packaged in a format that can be consumed by a hypervisor, experimenting with Buildroot seems like an excellent starting point for building the appliance I want.

### "External" trees

Never having used buildroot before, I was pleased with the quality of its documentation, though I found some aspects of the build system rather clunky to use. A somewhat "traditional" way to build embedded systems is to simply make a copy of the base framework (buildroot itself in this case, or perhaps a vendor's SDK in others) and modify it for the desired application, but this approach suffers from being tightly coupled to a single version of the framework so it can often be very difficult to update to newer tools and frameworks.[^coupling-issues]

[^coupling-issues]: I assume this is a reason that many vendor tools or SDKs for embedded use are often based on old versions of open-source software and rarely if ever receive updates: the developers did not take care to make it easy to decouple from their own dependencies so it's difficult for them to update and consequently those updates occur rarely if ever. That many vendors ship very old Linux kernels on Android devices is a good example of what happens, since Android tends to carry a fairly large number of patches on top of the upstream Linux kernel.

Fortunately, Buildroot documents several approaches to segregate customizations from Buildroot's core, described in [Chapter 9 of the user manual](https://buildroot.org/downloads/manual/manual.html#customize). I opted to use the `br2-external` approach, where a configuration variable can be set at build-time to specify the location of customizations using a well-defined layout that allows the build system to integrate the external items nicely.

Since I wanted to keep the entire project in a single directory, I ended up with a layout containing two checked-in directories:

 * `external`: directory for my `br2-external` customization tree
 * `buildroot`: a copy of Buildroot

In order to build everything, I run the following command from the project's root directory:

```sh
make -C buildroot \
     BR2_EXTERNAL=$(pwd)/external \
     O=$(pwd)/output \
     gitlab_runner_appliance_defconfig
```

This uses the default configuration that I wrote in `external/configs/gitlab_runner_appliance_defconfig` and sets things up to built in a new `output` directory nest to the `external` and `buildroot` source trees. Once set up, things can be interactively customized or built with `make -C output`.

This configuration keeps built artifacts out of directories containing the sources (so it's easy to keep track of what is important and what's the result of a build) as well as keeping customizations separate from buildroot itself (so it's easier to update buildroot and keep track of what I've modified).

### Storage setup

At an abstract level, I wanted to make the appliance read-only wherever possible to it would be nearly impossible to break, and very simple to rebuild from scratch: the system image should contain all configuration and any persistent read-write storage should be treated as unimportant. With buildroot this is fairly easy; I found that making the root filesystem unwritable was okay provided no other part of the system configuration wanted to write to that filesystem, which as described in a moment required some extra configuration.

To avoid wasting storage space for the root filesystem, I opted to build a [squashfs](https://www.kernel.org/doc/html/latest/filesystems/squashfs.html) image to boot from. This is convenient because it's designed to minimize space on persistent storage and does not support being written to, so no special configuration is required to ensure it is not modified unexpectedly.

Because a squashfs isn't really a whole disk image, I needed to take advantage of capabilities of typical hypervisors which are less common in non-virtualized systems: the kernel for the OS needs to be loaded from a file by the hypervisor and started directly, then the squashfs image provided as a disk image that can be read. This is slightly cumbersome in that it means two read-only files need to be stored for the appliance, but I wasn't very interested in figuring out how to pack both pieces into one disk image that could be booted.

### Applications

This appliance is meant to run two services that work together: Gitlab Runner to talk to a Gitlab server and receive jobs to run, and Docker to execute jobs under the direction of the Gitlab Runner. Buildroot includes packages for both of these, so getting them in my system image was as easy as enabling `BR2_PACKAGE_GITLAB_RUNNER` and `BR2_PACKAGE_DOCKER_ENGINE`.

Docker tends to make certian assumptions about the system on which it's running, and for that reason (as well as because I prefer to use it over traditional sysvinit), I chose to set `BR2_INIT_SYSTEMD` to enable [systemd](https://systemd.io/) as the component responsible for booting up the system once the kernel is running. Buildroot defaults to use a simpler collection of scripts and smaller tools for similar purposes (derived from the old UNIX System V), but I prefer the convenience of systemd's tight integration for this application and don't mind its larger resource footprint.

By experiment (attempting to boot an image with Docker running and seeing if it successfully started), I found that Docker by default will fail to run on a read-only root filesystem even when booted with systemd. Fortunately its logs were detailed enough to tell me that it was attempting to write to `/var/lib/containerd` which appears to be a place that it stores small amounts of runtime information. As I'm familiar with configuring systemd, I created a mount unit to install in the root filesystem that tells systemd to create a tmpfs at that path so it's writable but won't be retained across reboots.

By setting the Buildroot variable `BR2_ROOTFS_OVERLAY` to `$(BR2_EXTERNAL_GITLAB_RUNNER_APPLIANCE_PATH)/rootfs/`, Buildroot will be instructed to copy the contents of `external/rootfs/` in the project source directory into the generated root filesystem. Then I could simply write some systemd unit files that would be automatically loaded; for this specific example, `external/rootfs/etc/systemd/system/var-lib-containerd.mount` that gets installed to `/etc/systemd/system/var-lib-containerd.mount` in the final OS image:

```ini
[Unit]
Description=containerd temporary data

[Mount]
What=none
Where=/var/lib/containerd
Type=tmpfs

[Install]
RequiredBy=containerd.service
```

Setting `RequiredBy` makes systemd ensure that this tmpfs mount will be set up before Docker's `containerd` is started, because it will fail if that directory is not writable.

#### Mutable storage

The only data for the appliance that I reasonable want to be backed by actual persistent storage is where Docker stores container images and the data created by containers while they are running (that ends up containing data like a copy of the source code that a given CI job is running for). I opted to make the system assume that the hypervisor will provide a writable disk device with a particular name, expressed by `etc/systemd/var-lib-docker.mount`:

```ini
[Unit]
Description=docker data volume

[Mount]
What=/dev/disk/by-label/docker-data
Where=/var/lib/docker
Type=ext4

[Install]
RequiredBy=docker.service
```

This is very similar to the earlier tmpfs mount, but expects to find a ext4 filesystem at `/dev/disk/by-label/docker-data`. This `by-label` directory is automatically populated at runtime with links to storage devices based on the names declared by their contents, so one way to create an image that will be successfully mounted is to create a filesystem in a file that has the correct label, then attach that file to the virtual machine as a disk:

```
qemu-img create docker.img 20G
mkfs.ext4 -L docker-data docker.img
```

The above example uses the `qemu-img` tool to create a 20GB file with no particular structure, then `mkfs.ext4` to create an ext4 filesystem in that file. `-L docker-data` sets the filesystem label, which here needs to match the one specified in the systemd unit. How to hook that up to a virtual machine at runtime will be discussed later.

### docuum

Though it was fairly easy to build an OS image that runs Docker and a Gitlab Runner, these alone will probably tend to run out of space on the docker data volume because container images will not be automatically deleted when they are unused. Fortunately, this is a common problem for users of Docker which is solved in one way by Stephan Boyer's [Docuum](https://github.com/stepchowfun/docuum). This tool runs as a service and automatically deleted unused container images from disk to keep their total size under a chosen number of bytes.

Docuum is written in Rust so it has no particular runtime dependencies, but is somewhat unusual to build. Fortunately, the Buildroot documentation was sufficient for me to discover how to:

1. Add a custom package to my buildroot external tree
2. Write a package definition describing how to compile a Rust program

The result lives in `external/package/docuum` of the source repository and is fairly simple. To make Docuum run automatically on boot, I wrote a systemd service definition in `external/rootfs/etc/systemd/system/docuum.service`:

```ini
[Unit]
Description=LRU eviction of Docker images
After=docker.service
Wants=docker.service

[Service]
Environment="THRESHOLD=10 GB"
# Docuum logs seen containers to a file in XDG_DATA_HOME and complains
# continuously if it's not writable (/$HOME/.local/share by default).
Environment="XDG_DATA_HOME=/var/lib/docker/docuum/"
ExecStart=/bin/docuum --threshold ${THRESHOLD}
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Of note, the comment in this file observes that docuum wants to keep a small amount of data in persistent storage. Because the root filesystem is not meant to be writable and `/var/lib/docker` is already meant to contain persistent data, I instruct docuum to store its state in a directory under `/var/lib/docker`.

Although I probably could have worked out how to make this package install the service definition rather than putting it in my rootfs overlay directory, learning how to do that seemed unnecessary because I don't intend to use the package definition outside of this project.

### Kernel configuration

Since I'm targeting a virtual machine, Buildroot's `qemu_x86_64_defconfig` provided a useful starting point for configuration, especially in providing a kernel configuration suitable for running as a virtual machine guest (enabling things like VirtIO device drivers, and omitting irrelevant hardware drivers).

My desired application requires some additional kernel features that aren't enabled by default in Linux, so with some experimentation I arrived at the following kernel configuration items in my `gitlab_runner_appliance_defconfig` file:

```
BR2_LINUX_KERNEL=y
BR2_LINUX_KERNEL_USE_CUSTOM_CONFIG=y
BR2_LINUX_KERNEL_CUSTOM_CONFIG_FILE="board/qemu/x86_64/linux.config"
BR2_LINUX_KERNEL_CONFIG_FRAGMENT_FILES="$(BR2_EXTERNAL_GITLAB_RUNNER_APPLIANCE_PATH)/Kconfig"
```

`USE_CUSTOM_CONFIG` makes the build system use configuration fragments provided by the following options: `CUSTOM_CONFIG_FILE` points at the default Qemu x86_64 configuration provided with Buildroot. My own additional options are specified in `KERNEL_CONFIG_FRAGMENT_FILES`, which lists a single file that lives in the project repository at `external/Kconfig` with the following options:

```
# rootfs is a zstd-compressed squashfs
CONFIG_SQUASHFS=y
CONFIG_SQUASHFS_ZSTD=y
CONFIG_SQUASHFS_FILE_DIRECT=y
CONFIG_SQUASHFS_DECOMP_MULTI_PERCPU=y
# runc wants to use BPF for something cgroup-related
CONFIG_BPF_SYSCALL=y
CONFIG_BPF_JIT=y
CONFIG_CGROUP_BPF=y
```

Since I wanted to use a squashfs image for the root filesystem I needed to ensure the kernel was able to understand it, and I found that some BPF features needed to be turned on in order for Docker in the container to work correctly.

### Networking

## Running the appliance

Nice trick: memory balloon autodeflate:
 * https://libvirt.org/formatdomain.html#memory-balloon-device
 * https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5a10b7dbf904bfe01bb9fcc6298f7df09eed77d5
 * https://gitlab.com/qemu-project/qemu/-/commit/e3816255bf4b6377bb405331e2ee0dc14d841b80

### Firewalling

This runs on my home network, but shouldn't be able to access devices on my LAN.
In general, it should only reach things via the public internet.

```
echo > no-host-lan.xml << EOF
<filter name="no-host-lan">
    <rule action="drop" direction="out" statematch="false">
        <ip dstipaddr="10.0.0.0" dstipmask="255.0.0.0"/>
    </rule>
    <rule action="drop" direction="out" statematch="false">
        <ip dstipaddr="172.16.0.0" dstipmask="255.240.0.0"/>
    </rule>
    <rule action="drop" direction="out" statematch="false">
        <ip dstipaddr="192.168.0.0" dstipmask="255.255.0.0"/>
    </rule>
    <!--
    <rule action="drop" direction="out" statematch="false">
        <ipv6 dstaddr="fd00::" dstipmask="8"/>
    </rule>
    -->
</filter>
EOF
virsh nwfilter-define no-host-lan.xml --validate
```

Then associate this rule with a VM:

```
<interface type="...">
  ...
  <filterref filter="no-host-lan"/>
</interface>
```