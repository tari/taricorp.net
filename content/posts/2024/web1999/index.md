---
title: "WEB1999: the web of 1999 in math class"
slug: web1999
date: 2024-01-28T06:40:50.987Z
---
I often find that imposed limitations make it easier to create things: it's easy to aim for perfection if you can expend as much effort as you like on something and thus end up with nothing that you'll ever call good enough to share.
Over on Cemetech in the final months of 2023, we [held a programming contest](https://www.cemetech.net/forum/viewtopic.php?t=19320): write a screensaver, any kind of screensaver. I'm not often one to do any kind of competitive programming, but as a prompt for a constrained project this was a good one for me.

A screensaver is a nice project because there's a lot of room in which to play and many of the hard aspects of programming (interacting with humans) can be completely ignored! I wasn't originally planning to write anything to enter, but after thinking to myself what I might expect other people to enter, I came up with an idea that piqued my interest and didn't seem too hard to build. As a result, [I wrote a program I called WEB1999](https://www.cemetech.net/forum/viewtopic.php?t=19329), that won second place.

## WEB1999 in action

<figure>
<video controls autoplay muted
       width="320" height="240" src="{{< resource "full99.webm" >}}"
       poster="{{< resource "promo.png" >}}">
<figcaption>WEB1999 in action.</figcaption>
</figure>

Inspired heavily by the [Realistic Internet Simulator](https://web.archive.org/web/20021204203905/https://www2.b3ta.com/realistic-internet-simulator/) ("Kill the Pop-ups"), WEB1999 invokes the spirit of pop-up advertising and Internet culture around the turn of the millennium in the form of a program that runs on Texas Instruments' TI-84+ CE color-screen graphing calculators.

The contest judges had some very nice things to say:

> An excellent instance of a screensaver modeled after both the golden age of screensavers and the golden age of the internet. Callbacks to both classic internet culture and the calculator community of yore, with a few easter eggs to boot.

> An HTML readme that looks like it's from '99? Nice!

I *did* spend some significant effort writing the documentation for the program, but I didn't intentionally design the README with retro style; it mostly just uses the default HTML structure provided by [Pandoc](https://pandoc.org/)!

> It looks great. The posterization and dithering really gives the feel of the 90s,
and the use of an even more limited palette is a clever way to work within the
bounds. Capturing the nostalgia of having just way too many popups.

As described further in the following section, I had a lot of fun using realistic limitations to restrict myself!

## Design notes

I included many of my design notes in the documentation that comes along with the program, but in the interest of accessibility I'll reproduce much of that here.

- - -

Title: WEB1999 - Relive the 90s Internet on your Calculator!

Description:  Miss the chaotic, popup-filled internet of the late 90s? WEB1999 brings the classic web experience to your TI-83 Premium CE or TI-84 Plus CE calculator!

This program recreates those annoying (yet strangely nostalgic) popups, like "HOT SINGLES in your area!" and "YOU'VE WON!".  Hum "Ride of the Valkyries" as you watch WEB1999 do its thing - it plays itself!

Features

Faithful recreations of iconic 90s web popups

Web-safe 216-color palette for that authentic look

Relive web design trends of the era

Want to try it?

Visit the links below to download. If you're using an emulator, experience it as it was truly intended!

Download on Cemetech: https://www.cemetech.net/downloads/files/2402

Source Code on Gitlab: https://gitlab.com/taricorp/web1999/-/releases

Get Nostalgic

If you loved (or hated) the early internet, WEB1999 is a must-try.  Share it with friends and reminisce about the days before endless scrolling and targeted ads.

Hashtags: #web1999 #retro #calculators #programming #nostalgia #90s #webdesign

---

What critics (the contest judgest) are saying about WEB1999:

An excellent instance of a screensaver modeled after both the golden age of screensavers and the golden
age of the internet. Callbacks to both classic internet culture and the calculator community of yore,
with a few easter eggs to boot. No key input required, other than to exit the screensaver. Extremely thorough
readme, including a history/background on each of the "windows" that can appear.

It looks great. The posterization and dithering really gives the feel of the 90s,
and the use of an even more limited palette is a clever way to work within the
bounds. Capturing the nostalgia of having just way too many popups.

An HTML readme that looks like it's from '99? Nice!
