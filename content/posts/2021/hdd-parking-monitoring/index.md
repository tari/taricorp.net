---
title: Monitoring (and preventing) excessive hard drive head parking on Linux
slug: hdd-parking-monitoring
draft: true
date: 2021-08-09T00:34:31.020Z
categories:
  - software
tags:
  - smart
  - idle3
  - apm
  - seagate
  - westerndigital
  - seachest
  - prometheus
  - monitoring
  - linux
---
 It is [fairly well-known among techies](https://mobile.twitter.com/marcan42/status/1423974853955125250) that hard drives used in server-like workloads can suffer from poor configuration by default such that they [frequently load and unload their heads](https://superuser.com/questions/840851/how-much-load-cycle-count-can-my-hard-drive-hypotethically-sustain), which can cause disks to fail much faster than they otherwise would. While I have been aware of this in my home server as well, it is easy to forget to ensure that disks are not silently killing themselves by cycling the heads. Since I use [Prometheus](https://prometheus.io/) to capture information on the server's operation however, I can use that to monitor that my hard drives are doing well.

## Collecting SMART metrics

https://github.com/prometheus-community/node-exporter-textfile-collector-scripts

### Monitoring metrics

With the SMART metrics captured by Prometheus, it's fairly easy to write a query that will show how often a given disk is parking its heads. The `smartmon_load_cycle_count_value` metric seems like it would be the right one to query, but that actually expresses a percentage value (0-100) representing how many load cycles remain in the specified lifetime- on reaching 0 the disk has done a very large number of load cycles.

Somewhat more useful for monitoring is the `smartmon_load_cycle_count_raw_value`, which provides the actual number of load cycles that have been done. By taking the rate of those it becomes pretty easy to see which disks are loading and unloading most, so I choose to query with `sum(rate(smartmon_load_cycle_count_raw_value[6h])) by (disk)` to summarize by disk and get a 6-hour rolling average rate in load cycles per second, pictured here:

![A Prometheus console plotting load cycle rates per disk for five disks over a period of two weeks. Three of them have nonzero rates, with /dev/sde peaking at about 4 millicycles per second, /dev/sdc around 3 millicycles per second, and /dev/sdb at a much lower maximum rate of about 0.5 millicycles per second. The remaining two disks are at zero across the entire time range.](load-cycles-prometheus-fs8.png)

In this case, there are at least two disks that I probably need to configure, since `/dev/sde` seems to be parking as often as about every 4 minutes (0.004 Hz) and `/dev/sdc` is only parking slightly less often. `/dev/sdb` also seems worth inspecting.

## Preventing excessive parking

To prevent parking more often that is useful (for a server, usually that choice would be "very rarely"), there are a couple ways to do it and which apply will depend on what the hard drive vendor's firmware supports.

Of the three disks that I decided need some attention, I have one Western Digital disk and two Seagate ones. From the SMART data again, they are specifically these models:

 * `/dev/sdc`: Seagate Archive HDD (SMR) ST8000AS0002-1NA17Z, firmware version RT17
 * `/dev/sde`: Seagate IronWolf ST8000VN004-2M2101, firmware version SC60
 * `/dev/sdb`: Western Digital Red WDC WD40EFRX-68N32N0, firmware version 82.00A82

### APM

APM is standardized; `hdparm -B` set to 7F for maximum timeout. This isn't persistent, but could be auto-set on each boot with a udev rule. Alternately `smartctl -s apm,off`.

### Western Digital `idle3`

For drives made by Western Digital, the inactivity timer for parking the heads is called the `idle3` timer. Of particular note, WD Green drives ship configured to park the heads after only 8 seconds of inactivity which could notionally wear out the disk in a matter of *months* if the heads are cycling more-or-less continuously!

The `idle3-tools` package allows configuring the timer on Linux, though timer values are unintuitive- the tool sets a "raw" idle3 timer value, so a value like 232 (0xe8) actually means 3120 seconds according to `idle3ctl -g105`.

### Seagate EPC

Most Seagate disks have configurable Extended Power Conditions (EPC) settings that include timers for how long the disk needs to stay idle before entering various low-power modes. 

According to [at least one manual](https://www.seagate.com/www-content/product-content/skyhawk/en-us/docs/100855892b.pdf), the four low-power states are:

* `idle_a`: power down some electronics
* `idle_b`: park the heads (unloading them)
* `idle_c`: reduce spindle speed, heads unloaded
* `standby_z`: stop spindle completely

Seagate provide a "[Seachest](https://www.seagate.com/au/en/support/software/seachest/)" collection of tools for manipulating their drives, but rather more usefully to users of non-Windows operating systems like Linux they also offer an open-source [openSeaChest](https://github.com/Seagate/openSeaChest). The tool to use there is `openSeaChest_PowerControl` which allows each of the EPC timers to be configured.

`--idle_a ...` etc. View values with `--showEPCSettings`

My Seagate Archive SMR disk (which began life as an external hard drive and was retired from that role when it became too small to hold as much as I wanted to back up to it) doesn't support showing EPC settings, but does support setting timers after running `--EPCfeature enable`. I'll have to watch the park counts on that to ensure it actually worked.

## Monitoring SSDs

This same setup can be used to monitor wear on SSDs, which is nice. SSDs expose some different metrics though, particularly the `media_wearout_indicator`