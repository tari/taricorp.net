---
author: tari
comments: true
date: 2013-01-17 02:17:28+00:00
slug: of-cable-modems-and-the-dumb-solution
title: Of Cable Modems and the Dumb Solution
wordpress_id: 841
categories:
- Miscellanea
- Software
tags:
- BSD
- debugging
- pfSense
---

I was [studying in Japan](http://jcmu.isp.msu.edu/) last semester (which
explains somewhat why I haven't posted anything interesting here in a while).
That's a whole different set of things to blog about, which I'll get to at some
point with any luck (maybe I'll just force myself to write one post per day for
a bit, even though these things tend to take at least a few hours to write..).

## Background

At any rate, back in [Houghton](http://www.mtu.edu/) I live with a few roommates
in an apartment served by Charter internet service (which I believe is currently
DOCSIS2). The performance tends to be quite good (it seems that the numbers that
they quote for service speeds are guaranteed minimums, unlike most other ISPs),
but I like to have complete control over my firewall and routing.

In the past, such freedom has been achieved through my trusty
[WRT54GL](https://en.wikipedia.org/wiki/Linksys_WRT54G_series#WRT54GL), but the
4-megabyte Flash chip in that device makes it hard to fit in a configuration
that includes IPv6 support, which is
[increasingly](https://en.wikipedia.org/wiki/IPv4_address_exhaustion)
[important](https://en.wikipedia.org/wiki/IPv6_deployment) to me. As I had an
Intel [Atom-based
board](http://www.intel.com/content/www/us/en/motherboards/desktop-motherboards/desktop-board-di510mo.html)
sitting around some time ago, I decided to turn that into a full-time
router/firewall running [pfSense](https://www.pfsense.org/). The power available
with pfSense is probably overkill for my needs, but it ensures I'll be able to
stay up to date and potentially do fancy things with my network configuration at
some future date.

Returning to the matter at hand: the whole system was working just fine for a
while, but I got a report from my roommates that the internet connection had
stopped working, but came up okay with a bargain-basement consumer router (a
Linksys/Cisco E900). From what information I was able to get from my roommates,
it sounded like a hardware failure in the secondary network card, which is used
for the WAN uplink (not exactly surprising, since it's a 100-megabit PCI
Ethernet card I pulled out of something else some time ago).

## Debugging

On my recent return to the apartment, one of my priorities was getting the
pfSense system up and running again as the main router/firewall. While the E900
was performing fine, pfSense allows me to get a few additional things out of the
connection. Most notably, Charter provide a [6rd
relay](http://www.myaccount.charter.com/customers/Support.aspx?SupportArticleID=2665#ipv6prep)
for ISP-provided IPv6 (compared to something like the public IPv6 tunnel service
available from [Hurricane Electric](https://www.tunnelbroker.net/)), which is
quite desirable to me.

After performing a basic test, the pfSense box did indeed fail to get a public
IP address from Charter when put in place as the primary gateway. At that point,
I decided to break out a network analyzer
([Wireshark](https://www.wireshark.org/) in this case) and see how the DHCP
solicitations on the WAN interface differed between the E900 and my pfSense
configuration. What follows is Wireshark's dissection of a single DHCP Discover
message from each system.

Linksys E900:

```
Ethernet II, Src: Micro-St_60:86:0c (8c:89:a5:60:86:0c), Dst: Broadcast (ff:ff:ff:ff:ff:ff)
    Destination: Broadcast (ff:ff:ff:ff:ff:ff)
    Source: Micro-St_60:86:0c (8c:89:a5:60:86:0c)
    Type: IP (0x0800)
Internet Protocol Version 4, Src: 0.0.0.0 (0.0.0.0), Dst: 255.255.255.255 (255.255.255.255)
    Version: 4
    Header length: 20 bytes
    Differentiated Services Field: 0x10 (DSCP 0x04: Unknown DSCP; ECN: 0x00: Not-ECT (Not ECN-Capable Transport))
        0001 00.. = Differentiated Services Codepoint: Unknown (0x04)
        .... ..00 = Explicit Congestion Notification: Not-ECT (Not ECN-Capable Transport) (0x00)
    Total Length: 328
    Identification: 0x0000 (0)
    Flags: 0x00
    Fragment offset: 0
    Time to live: 128
    Protocol: UDP (17)
    Header checksum: 0x3996 [correct]
    Source: 0.0.0.0 (0.0.0.0)
    Destination: 255.255.255.255 (255.255.255.255)
User Datagram Protocol, Src Port: bootpc (68), Dst Port: bootps (67)
    Source port: bootpc (68)
    Destination port: bootps (67)
    Length: 308
    Checksum: 0x9918 [validation disabled]
Bootstrap Protocol
    Message type: Boot Request (1)
    Hardware type: Ethernet
    Hardware address length: 6
    Hops: 0
    Transaction ID: 0x1a5f4329
    Seconds elapsed: 0
    Bootp flags: 0x8000 (Broadcast)
        1... .... .... .... = Broadcast flag: Broadcast
        .000 0000 0000 0000 = Reserved flags: 0x0000
    Client IP address: 0.0.0.0 (0.0.0.0)
    Your (client) IP address: 0.0.0.0 (0.0.0.0)
    Next server IP address: 0.0.0.0 (0.0.0.0)
    Relay agent IP address: 0.0.0.0 (0.0.0.0)
    Client MAC address: Micro-St_60:86:0c (8c:89:a5:60:86:0c)
    Client hardware address padding: 00000000000000000000
    Server host name not given
    Boot file name not given
    Magic cookie: DHCP
    Option: (53) DHCP Message Type
        Length: 1
        DHCP: Discover (1)
    Option: (12) Host Name
        Length: 10
        Host Name: Needlecast
    Option: (55) Parameter Request List
        Length: 4
        Parameter Request List Item: (1) Subnet Mask
        Parameter Request List Item: (3) Router
        Parameter Request List Item: (15) Domain Name
        Parameter Request List Item: (6) Domain Name Server
    Option: (61) Client identifier
        Length: 7
        Hardware type: Ethernet
        Client MAC address: Micro-St_60:86:0c (8c:89:a5:60:86:0c)
    Option: (255) End
        Option End: 255
    Padding
```

pfSense 2.0.2:

```
Ethernet II, Src: 3com_8a:b9:6b (00:50:da:8a:b9:6b), Dst: Broadcast (ff:ff:ff:ff:ff:ff)
    Destination: Broadcast (ff:ff:ff:ff:ff:ff)
    Source: 3com_8a:b9:6b (00:50:da:8a:b9:6b)
    Type: IP (0x0800)
Internet Protocol Version 4, Src: 0.0.0.0 (0.0.0.0), Dst: 255.255.255.255 (255.255.255.255)
    Version: 4
    Header length: 20 bytes
    Differentiated Services Field: 0x10 (DSCP 0x04: Unknown DSCP; ECN: 0x00: Not-ECT (Not ECN-Capable Transport))
        0001 00.. = Differentiated Services Codepoint: Unknown (0x04)
        .... ..00 = Explicit Congestion Notification: Not-ECT (Not ECN-Capable Transport) (0x00)
    Total Length: 328
    Identification: 0x0000 (0)
    Flags: 0x00
    Fragment offset: 0
    Time to live: 16
    Protocol: UDP (17)
    Header checksum: 0xa996 [correct]
    Source: 0.0.0.0 (0.0.0.0)
    Destination: 255.255.255.255 (255.255.255.255)
User Datagram Protocol, Src Port: bootpc (68), Dst Port: bootps (67)
    Source port: bootpc (68)
    Destination port: bootps (67)
    Length: 308
    Checksum: 0x3a68 [validation disabled]
Bootstrap Protocol
    Message type: Boot Request (1)
    Hardware type: Ethernet
    Hardware address length: 6
    Hops: 0
    Transaction ID: 0x06303c2b
    Seconds elapsed: 0
    Bootp flags: 0x0000 (Unicast)
        0... .... .... .... = Broadcast flag: Unicast
        .000 0000 0000 0000 = Reserved flags: 0x0000
    Client IP address: 0.0.0.0 (0.0.0.0)
    Your (client) IP address: 0.0.0.0 (0.0.0.0)
    Next server IP address: 0.0.0.0 (0.0.0.0)
    Relay agent IP address: 0.0.0.0 (0.0.0.0)
    Client MAC address: 3com_8a:b9:6b (00:50:da:8a:b9:6b)
    Client hardware address padding: 00000000000000000000
    Server host name not given
    Boot file name not given
    Magic cookie: DHCP
    Option: (53) DHCP Message Type
        Length: 1
        DHCP: Discover (1)
    Option: (61) Client identifier
        Length: 7
        Hardware type: Ethernet
        Client MAC address: 3com_8a:b9:6b (00:50:da:8a:b9:6b)
    Option: (12) Host Name
        Length: 7
        Host Name: pfSense
    Option: (55) Parameter Request List
        Length: 8
        Parameter Request List Item: (1) Subnet Mask
        Parameter Request List Item: (28) Broadcast Address
        Parameter Request List Item: (2) Time Offset
        Parameter Request List Item: (121) Classless Static Route
        Parameter Request List Item: (3) Router
        Parameter Request List Item: (15) Domain Name
        Parameter Request List Item: (6) Domain Name Server
        Parameter Request List Item: (12) Host Name
    Option: (255) End
        Option End: 255
    Padding
```

(Apologies to anybody who finds the above ugly, but I only have so much patience
for CSS while blogging.)

There are a few differences there, none of which seem really harmful. Given it
was working without incident before, however, I guessed that maybe some upstream
configuration had changed and become buggy. In particular, I thought that either
the BOOTP broadcast flag (line 32 of both packet dissections) needed to be set
for some reason, or the upstream DHCP server was choking on some of the
parameters pfSense was requesting.

In an effort to pin down the problem, I manually made some DHCP requests with
[dhclient](https://www.isc.org/downloads/dhcp/) configured to match what I was
seeing from the E900. The configuration I used with dhclient looked like this
(where xl0 is the identifier BSD assigns to my WAN interface):

    interface "xl0" {
    	send host-name "Needlecast";
    	request subnet-mask, routers, domain-name, domain-name-server;
    	send dhcp-client-identifier 1:8c:89:a5:60:86:0c;
    }

This yielded packets that, when examined in Wireshark, only differed by some of
the hardware addresses and the BOOTP broadcast flag. At that point I was rather
stuck. Newer releases of dhclient support an option to force the broadcast flag
in requests, but FreeBSD (which pfSense is derived from) does not provide a new
enough version to have that option, and I didn't want to try building it myself.
In addition, I know that my ISP doesn't lock connections to MAC addresses, so I
shouldn't have to spoof the MAC address of the E900 (indeed, nothing needed to
be changed when switching from pfSense to the E900, so the other direction
shouldn't need anything special).

Since I was stuck, it was time to start doing things that seemed increasingly
unlikely. One comment on the pfSense forum related to a similar issue mentioned
that cable modems tend to be simple DOCSIS-to-Ethernet bridges, so there's some
sort of binding to the client MAC address in the upstream DOCSIS machinery,
which rebooting the modem should reset. So I hooked everything up normally,
cycled power to the modem and booted up pfSense, and...

**...it worked.**

I had spent a few evenings working on the problem, and the fix was that simple.
I was glad it was finally working so I could reconfigure internet-y goodness
(QoS, DDNS updating, 6rd tunneling, VPN) on it, but there was certainly also
frustration mixed in there.

## Lessons

So what's the lesson? I suppose we might say that "you're never too
knowledgeable to try rebooting it". It's common advice to less savvy users to
"try rebooting it", but I think that's an oft-neglected solution when more
technically-inclined individuals are working on a problem. On the other hand,
maybe I've just learned some details about DOCSIS systems and the solution in
this case happened to be rebooting.

\<witty and relevant image goes here\>
