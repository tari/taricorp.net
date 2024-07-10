---
title: "WEB1999: the web of 1999 in math class"
slug: web1999
date: 2024-01-28T06:40:50.987Z
---
I often find that imposed limitations make it easier to create things: it's easy to aim for perfection if you can expend as much effort as you like on something and thus end up with nothing that you'll ever call good enough to share.
Over on Cemetech in the final months of 2023, we [held a programming contest](https://www.cemetech.net/forum/viewtopic.php?t=19320): write a screensaver, any kind of screensaver. I'm not often one to do any kind of competitive programming, but as a prompt for a constrained project this was a good one for me. As a result, [I wrote a program I called WEB1999](https://www.cemetech.net/forum/viewtopic.php?t=19329), that won second place.

<!-- more -->

A screensaver is a nice project because there's a lot of room in which to play and many of the hard aspects of programming (interacting with humans) can be completely ignored! I wasn't originally planning to write anything to enter, but after thinking to myself what I might expect other people to enter, I came up with an idea that piqued my interest and didn't seem too hard to build. 

## Get WEB1999

If you want to play with the program instead of or in addition to simply reading about it, a copy of WEB1999 suitable for loading onto a TI-84+ CE or TI-83 Premium CE calculator can be obtained from the releases section of my gitlab project: \
**<https://gitlab.com/taricorp/web1999/-/releases>**

A copy can also be obtained from the [Cemetech archives](https://www.cemetech.net/downloads/files/2402) or [ticalc.org](https://www.ticalc.org/archives/files/fileinfo/479/47909.html). All of the release packages include the full source code and documentation, so you shouldn't miss anything regardless of where you choose to get a copy from.

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

I included many of my design notes in the documentation that comes along with the program, but in the interest of easy reading I'll reproduce much of that here alongside images that are much easier to study than they are when the program is in motion.

### Window styles and color

{{< figure src="testwindow.png" alt="A blank window titled 'Large Test window'" caption="The general concept for displaying windows." >}}

With an idea in mind to build a "kill the pop-ups"-style screensaver, the first code I had to write was something that could display a window which I could then add interesting things to. Since I had retro PCs in mind, the window decorations and background color are based on the default styles of Windows 95, 98, and Me; grey borders with an outset/inset shading effect, and a blue titlebar (changing to grey when a window is inactive).

I also limited myself to approximately the [web-safe color palette](https://en.wikipedia.org/wiki/Web_colors#Web-safe_colors) with only 216 colors available, although the conscious choice to limit the color palette to that one came a bit later in the process. The CE calculators have displays capable of doing 16-bit color (5-6-5 RGB), but programmers usually run it in an 8-bit palettized mode instead (where each byte refers to one of 256 colors) because it's considerably faster on the calculator's relatively slow Z80 without any display acceleration to speak of.

As I was developing graphics to display in the program, I had some difficulty dealing with the limited 256-color palette and ensuring that my graphics looked like I intended. Once I realized I could lean into the theme with a web-safe palette and use existing tools (the [GNU Image Manipulation Program](https://www.gimp.org/)) to make my images look the same on my computer and a calculator, it was an easy choice! GIMP offers a web-safe palette as an option "out of the box" alongside a choice of several dithering methods, so it was rather fun and easy to develop graphics once I committed to that approach.

### Malware and malvertising

{{< figure src="malvertising.png" alt="Three windows, each containing something that seems untrustworthy. The leftmost is titled 'Limewire' and has a 'Download' link for a 3MB exe file seemingly claiming to be a copy of 'Crawling' by Linkin Park. The middle one advertises 'HOT SINGLES waiting to meet today!' where some of the text is stylized to look like flames and a large portion of the window is taken up by the frame for an image that is not displayed. The window on the right claims 'You are visitor #1,000,000!' with a button to claim a prize. An image of a yellow sports car is between them." caption="Malvertising lives in 2024, much as it did in 1999." >}}

These windows are inspired by malware and malvertising (advertisements designed to take advantage of people who interact them, often by roping them into scams) that feel to me like they were common around 1999. It turns out that LimeWire as appears on the left is a little bit anachronistic because LimeWire didn't reach its peak until 2001, but malware on peer-to-peer networks is a perennial concern for users of those networks. The other two advertisements here are much more generic and would be at home on a web page today with some style adjustments.

Pornographic (or nearly-so) advertisements are not uncommon on web sites peddling illegal (or questionably-legal) goods, so the "Hot singles" window alludes to that concept without compromising the all-ages friendliness of my program. As a bonus, using the "broken image" icon as appeared in Netscape Navigator (in place of an image that would not be appropriate for all viewers)  nicely captures the feeling of personal computing prior to the year 2000. I was also quite pleased with the idea of text that looks like it's on fire, which feels strongly reminiscent of [WordArt](https://en.wikipedia.org/wiki/Microsoft_Office_shared_tools#WordArt) (which I feel has become much less used since the 90s).

Finally, the image of a sports car combined with a dubious claim of being the millionth visitor to a web page is an easy way for baddies to collect information from gullible targets. Dangling an apparent prize in front of a user raises plenty of questions to somebody who takes a moment to think about it (Why is a prize being given to the millionth visitor specifically?), but those who get excited and only think carefully later could find their personal information in the hands of n'er-do-wells before they realize!

### Memes

{{< figure src="memes.png" alt="Three windows, left to right: an image of a man with half his face covered in machinery, captioned 'CATS: ALL YOUR BASE ARE BELONG TO US'; a cartoon luchador in front of a sunset, with text 'STRONG BAD SINGS!', crossed out '$99.99?' followed by '$193.75', and a phone number 1-800-555-SBSINGS; the bow of a sunken ship sticking out above water with the legend 'Mistakes: Your purpose may only be to act as a warning to others'." caption="Internet users still enjoy memes today, though these may not be immediately recognized by younger viewers." >}}

Meme culture remains strong today, and while brainstorming ideas for things to include in WEB1999 I recalled several "classic" memes that worked out nicely. "All your base are belong to us" seems comfortably classified as a classic that many people will still recognize today, and in browsing a very old collection of memes I had stored I was reminded of the "demotivator" genre inspired by [Despair](https://despair.com/)'s parodies of motivational posters; "Mistakes" pictured above was one of the earliest examples of their work I found in old versions of their web site on [the Internet Archive's Wayback Machine](https://web.archive.org/web/19981212024329/http://www.despair.com/) that I thought would still look okay when reduced to 256 colors and greatly reduced in resolution.

Although I might not classify "Strong Bad Sings" as a meme, it comes from [Homestar Runner](https://homestarrunner.com/) which I get the impression became popular with many of the same people who would have been plugged into meme culture around the turn of the millennium.

### Plain old advertising

{{< figure src="commercialism.png" alt="Two advertisements, one of them for America Online advertising 540 hours free and blazing 56k speeds and the other simply saying 'Got Milk?' and picturing a tall glass of milk." caption="Advertisements just like these were a common sight in the late 90s." >}}

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
