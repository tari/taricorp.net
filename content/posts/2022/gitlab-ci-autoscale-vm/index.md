[Socket]
ListenStream=/run/gitlab-runner-vm/docker.sock
Service=gitlab-runner-vm.service
RemoveOnStop=yes

gitlab-runner-vm.service depends on a VM unit and runs systemd-socket-proxy to
connect back to the VM

how do we get a task? runner needs to run on the main machine
configure runner with docker executor that connects to the proxied socket
in /run/gitlab-runner-vm/

libvirt-vm@.service:
```
[Unit]
Description=libvirt domain %i
Requires=libvirt-guests.service
After=libvirt-guests.service
StopWhenUnneeded=true

[Service]
Type=forking
PIDFile=/run/libvirt/qemu/%i.pid
ExecStart=/usr/bin/virsh create /etc/libvirt/qemu/%i.xml
# Shutdown the domain gracefully by sending ACPI shutdown event.
ExecStop=/usr/bin/bash -c 'export LANG=C; COUNT=0; while [ $COUNT -le 60 ]; do STATE=$(virsh domstate %i 2>&1); if [ "$STATE" = "running" ]; then [ $(($COUNT % 15)) -eq 0 ] && virsh shutdown %i; ((COUNT++)); elif [ "$STATE" = "shut off" ] || [ "${STATE::27}" = "error: failed to get domain" ]; then exit 0; fi; sleep 1; done; exit 1'
```

the VM unit stops when unneeded, and proxy sets --exit-idle-time so the VM
shuts down when it's idle (the runner isn't connected to the docker service
inside the VM)

systemd-socket-proxyd(8)

VM can be light, runs alpine linux with gitlab-runner

can't use systemd-machined; that only runs namespace containers- want a full-blown VM

https://github.com/dehesselle/virtctl
available in AUR, manages libvirt VMs as systemd units

oh, machinectl understands libvirt somehow? apparently that's just a thing it knows
.. but that doesn't seem to expose it as a controllable service unit.

set up the VM with virt-manager
turns out boot.alpinelinux.org is a thing. Nice!
..I couldn't get it to work. Whatever.

autodeflate is a great trick with the balloon device
https://libvirt.org/formatdomain.html
especially if the VM often gets shut down, the balloon will get reset
to its default size adn we don't need to get clever with it

I don't want a large root disk for this VM. Seems easiest to create
another disk image (backed by ZFS?) for it, or perhaps even just allocate
a LVM volume to pass to the VM as a disk.

discard="unmap" on virtio block is good and nice (and the default at least
for new VMs it seems; my old Home Assistant one didn't have it)
[doing this to the hass VM makes `fstrim /mnt/data` work in it, which saves.. nothing
 fstrim -av shows modest savings of ~100MB]

perhaps even suspending and resuming the VM is a better approach than shutting down
and rebooting it. Snapshots of a running system arne't supported with UEFI firmware:
https://bugzilla.redhat.com/show_bug.cgi?id=1881850

fast boot is very important to this application, and alpine with a default configuration
does not boot fast.
using efistub instead of GRUB speeds it up a little

But maybe `virsh save` is faster than booting from scratch? seems quick.