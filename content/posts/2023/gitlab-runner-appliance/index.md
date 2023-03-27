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

1. Run a Docker-in-Docker container. This puts a copy of the Docker engine inside a container (itself running inside the Docker engine on the host machine), which is mostly isolated from the host but requires careful configuration to get good performance. It also requires that the outer container be run in **privileged mode** which makes it possible for software running inside the outer container (the CI build) to access the host system with relative ease.
2. Expose the Docker engine's control socket inside the container (mount `/var/lib/docker.sock`). This is easier to set up, giving the build unfettered access to the Docker engine running on the host, allowing it to send **arbitrary commands** such as "start a container that will mine Bitcoin in the background, then run the CI build".
3. Don't use `docker` for builds, instead using tools that don't need to be able to run containers in order to build them like [buildah](https://buildah.io/) or [kaniko](https://github.com/GoogleContainerTools/kaniko).

Although the third option is generally best (I particularly appreciate Kaniko, because its ability to consume a `Dockerfile` means it's easy to interactively develop the recipe for building a container, then use a different tool in CI), it's not always good enough- especially if you want to run a container that you've just built, perhaps to verify that it works as expected before publishing it. Unfortunately, the other two options both open up quite large security holes that could be abused by malicious builds.

On a dedicated CI host these risks are somewhat less important because there probably isn't any data present that relates to anything but CI builds (so there's a very limited amount of data that's interesting to steal), but if I want to use spare resources on systems that I use for other things then those risks seem problematic: unrelated system data should not be accessible to the builder, even though builds should be able to use `docker` themselves in order to build or test container images.

### Resource limits

Similarly, ensuring that a CI runner doesn't use excessive resources can be somewhat difficult. The risk of using all of the resources of a dedicated CI runner is small (at worst, it stops working and needs to be restarted), but compromising the functionality of other services by consuming all available resources on a shared machine would be problematic.

It's relatively simple to limit the amount of CPU time or memory that can be used by a given Docker container, and `gitlab-runner` allows that to be configured for each job that is run. Somewhat more difficult to manage is disk usage however, because Docker uses disk for a variety of uses:

 * Container images; the files making up the environment in which containers run.
 * Container data; the data that a container writes when it runs.
 * Volumes; additional storage that can be attached to containers.

Docker provides some limited tools for managing storage, but nothing that is very useful for limiting the amount of disk used beyond basic applications like "delete everything that isn't currently in use." [docuum](https://github.com/stepchowfun/docuum) is a convenient third-party tool to help limit the amount of disk space used by container images by cleaning up old ones that aren't in use, but needs to be set up manually.

## Virtualization to the rescue

Given all of these concerns and limitations around providing privileged access to a system that runs other tasks and limiting the resources that can be consumed, virtualization seems like the perfect solution.

## Running the appliance

TODO: Firewalling!