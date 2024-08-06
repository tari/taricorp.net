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

I *did* spend some significant effort writing the documentation for the
program, but I didn't intentionally design the README with retro style; it
mostly just uses the default HTML structure provided by
[Pandoc](https://pandoc.org/)!

> It looks great. The posterization and dithering really gives the feel of the
> 90s, and the use of an even more limited palette is a clever way to work
> within the bounds. Capturing the nostalgia of having just way too many
> popups.

As described further in the following sections, not only did I have a lot of
fun using historical inspiration and realistic limitations to restrict myself,
but there were also a few interesting aspects to the implementation that I'll
describe! Continue reading for [design notes](#design-notes) and
[implementation notes](#implementation-notes).

## Design notes

I included many of my design notes in the documentation that comes along with
the program, but in the interest of easy reading I'll reproduce much of that
here alongside images that are much easier to study than they are when the
program is in motion.

### Window styles and color

With an idea in mind to build a "kill the pop-ups"-style screensaver, the first code I had to write was something that could display a window which I could then add interesting things to. Since I had retro PCs in mind, the window decorations and background color are based on the default styles of Windows 95, 98, and Me; grey borders with an outset/inset shading effect, and a blue titlebar (changing to grey when a window is inactive).

{{< figure src="testwindow.png" alt="A blank window titled 'Large Test window'" caption="The general concept for displaying windows." >}}

I also limited myself to approximately the [web-safe color palette](https://en.wikipedia.org/wiki/Web_colors#Web-safe_colors) with only 216 colors available, although the conscious choice to limit the color palette to that one came a bit later in the process. The CE calculators have displays capable of doing 16-bit color (5-6-5 RGB), but programmers usually run it in an 8-bit palettized mode instead (where each byte refers to one of 256 colors) because it's considerably faster on the calculator's relatively slow Z80 without any display acceleration to speak of.

As I was developing graphics to display in the program, I had some difficulty dealing with the limited 256-color palette and ensuring that my graphics looked like I intended. Once I realized I could lean into the theme with a web-safe palette and use existing tools (the [GNU Image Manipulation Program](https://www.gimp.org/)) to make my images look the same on my computer and a calculator, it was an easy choice! GIMP offers a web-safe palette as an option "out of the box" alongside a choice of several dithering methods, so it was rather fun and easy to develop graphics once I committed to that approach.

### Malware and malvertising

{{< figure src="malvertising.png" alt="Three windows, each containing something that seems untrustworthy. The leftmost is titled 'Limewire' and has a 'Download' link for a 3MB exe file seemingly claiming to be a copy of 'Crawling' by Linkin Park. The middle one advertises 'HOT SINGLES waiting to meet today!' where some of the text is stylized to look like flames and a large portion of the window is taken up by the frame for an image that is not displayed. The window on the right claims 'You are visitor #1,000,000!' with a button to claim a prize. An image of a yellow sports car is between them." caption="Malvertising lives in 2024, much as it did in 1999." >}}

These windows are inspired by malware and malvertising (advertisements designed
to take advantage of people who interact them, often by roping them into scams)
that feel to me like they were common around 1999. It turns out that LimeWire
as appears on the left is a little bit anachronistic because LimeWire didn't
reach its peak until 2001, but malware on peer-to-peer networks is a perennial
concern for their users. The other two advertisements here are much more
generic and would be at home on a web page today with some style adjustments.

Pornographic (or nearly-so) advertisements are not uncommon on web sites
peddling illegal (or questionably-legal) goods, so the "Hot singles" window
alludes to that concept without compromising the all-ages friendliness of my
program. As a bonus, using the "broken image" icon as appeared in Netscape
Navigator (in place of an image that would not be appropriate for all viewers)
nicely captures the feeling of personal computing prior to the year 2000. I was
also quite pleased with the idea of text that looks like it's on fire, which
feels strongly reminiscent of
[WordArt](https://en.wikipedia.org/wiki/Microsoft_Office_shared_tools#WordArt)
(which I feel has become much less used since the 90s).

Finally, the image of a sports car combined with a dubious claim of being the millionth visitor to a web page is an easy way for baddies to collect information from gullible targets. Dangling an apparent prize in front of a user raises plenty of questions to somebody who takes a moment to think about it (Why is a prize being given to the millionth visitor specifically?), but those who get excited and only think carefully later could find their personal information in the hands of n'er-do-wells before they realize!

### Memes

{{< figure src="memes.png" alt="Three windows, left to right: an image of a man with half his face covered in machinery, captioned 'CATS: ALL YOUR BASE ARE BELONG TO US'; a cartoon luchador in front of a sunset, with text 'STRONG BAD SINGS!', crossed out '$99.99?' followed by '$193.75', and a phone number 1-800-555-SBSINGS; the bow of a sunken ship sticking out above water with the legend 'Mistakes: Your purpose may only be to act as a warning to others'." caption="Internet users still enjoy memes today, though these may not be immediately recognized by younger viewers." >}}

Meme culture remains strong today, and while brainstorming ideas for things to include in WEB1999 I recalled several "classic" memes that worked out nicely. "All your base are belong to us" seems comfortably classified as a classic that many people will still recognize today, and in browsing a very old collection of memes I had stored I was reminded of the "demotivator" genre inspired by [Despair](https://despair.com/)'s parodies of motivational posters; "Mistakes" pictured above was one of the earliest examples of their work I found in old versions of their web site on [the Internet Archive's Wayback Machine](https://web.archive.org/web/19981212024329/http://www.despair.com/) that I thought would still look okay when reduced to 256 colors and greatly reduced in resolution.

Although I might not classify "Strong Bad Sings" as a meme, it comes from [Homestar Runner](https://homestarrunner.com/) which I get the impression became popular with many of the same people who would have been plugged into meme culture around the turn of the millennium.

### Mass media

{{< figure src="culture.png" alt="To the left, a window titled 'Dragonball Oasis' proclaiming 'Welcome to my DRAGONBALL Z fan page!' in rainbow text, featuring chibi-style drawings of two anime characters with dark, spiky hair. On the right, a window titled 'What droid?' asks 'What kind of droid are you?' featuring a photo of Star Wars' R2-D2 astromech droid and referring to a 'Free personality test!' that now includes Episode I." caption="The Star Wars prequels were just getting started at the end of the 90s, and young people watching cartoons were very into Dragonball Z." >}}

In developing ideas for windows, an early one I hit upon was the unprofessional
style of pages that might be found on
[GeoCities](https://en.wikipedia.org/wiki/GeoCities). Thanks to the [efforts of
the Archive Team](https://blog.archive.org/2009/08/25/geocities-preserved/), I
was able to easily browse semi-random pages from GeoCities, and one that I
found had exactly the title I used here: "Dragonball Oasis." To capture the
feeling of a web page designed by a young fan of anime an excess of enthusiasm
but little concern for easy readability, I thought it would be fun to make some
of the text be rainbow-colored with the color changing for every letter. This
page is also part of a webring, which is a concept that has all but completely
died since the early 2000s.

Later on, I realized that Star Wars Episode I was released in 1999, so was
perfectly contemporary with the intended timeframe this program represents. By
browsing old versions of the official Star Wars web page, I was inspired to ask
viewers what kind of droid they are best represented by, and took some liberty
to combine that idea with the sketchy concept of a "free personality test"
which I feel has a proud and dubious history on the Web.

{{< figure src="commercialism.png" alt="Two advertisements, one of them for America Online advertising 540 hours free and blazing 56k speeds and the other simply saying 'Got Milk?' and picturing a tall glass of milk." caption="Advertisements just like these were a common sight in the late 90s." >}}

Taking a step back from the malicious and scammy elements I took inspiration
from, I also borrowed ideas from a few of the most well-known 90s advertising
campaigns. AOL [became notorious for sending out enormous quantities of
CDs](https://web.archive.org/web/20030423062842/http://www.cbc.ca/consumers/market/files/home/aol_discs/)
to a public who grew increasingly hostile (or perhaps indifferent) to AOL, so
an advertisement like this that advertises many hours of free service would
have been a common sight. ["Got
Milk"](https://en.wikipedia.org/wiki/Got_Milk%3F) was another campaign that
appeared across many forms of media; there were few people in the United States
who were never exposed to those ads, so this ought to be familiar to anybody of
at least a certain age.

## Implementation notes

WEB1999 has two major tasks that it needs to handle while running:

1. Periodically open a new window.
2. Move the cursor to an open window and close it.

Opening windows is fairly easy, but how that interacts with moving the cursor
and interacting with windows is rather more complex. When there are multiple
windows onscreen, some UI elements might be obscured because the windows are
stacked. This presents a challenge to the cursor, because it should not
"interact" with UI elements that are not visible (not that it actually
interacts, it just needs to close a window when that's plausibly possible)
and consequently needs to choose a window and an element of that window to
move to and interact with.

### Cursor behavior

{{< figure src="testwindow.png" alt="A blank window titled 'Large Test window'" caption="The Large Test Window illustrates the important UI elements." >}}

Starting with the goal of closing a window by pressing the 'X' button in its
upper-right corner, it's simple to close a window when it's alone onscreen.
Simply by moving the cursor to the 'X' button, we can plausibly interact with
it and then remove the window.

If the 'X' button is offscreen however, it's impossible to interact with. It
would be reasonable to ensure that the button is never placed offscreen when
creating a new window, but that would be less visually interesting. So to
handle such a situation, the cursor must move to the window's titlebar and
"drag" the entire window to the left until its close button is visible. In the
video below, the program only ever has one window to consider, but it moves the
cursor to that window and closes it, moving the window if needed.

<figure>
<video controls muted width="320" height="240"
       src="{{< resource "testwindows.webm" >}}">
</figure>

When there are multiple windows onscreen, they can be modelled as a simple
list where the first window in the list is on top. By drawing them on the
screen from the bottom up, it's easy to ensure windows higher in the stack
obscure the lower ones.

### Window occlusion

Somewhat more difficult is determining which window the cursor should interact
with. Although the topmost one should always be interactable, I didn't think
always going to the topmost window would be interesting behavior, and it
doesn't seem to match what a human would do in this situation: a human would
probably choose a window located near the cursor and close it, unless it became
obscured before it could be closed. As it turns out, that human behavior is
fairly straightforward to express as long as it's clear which windows are not
obscured.

This was one of the situations where I took a shortcut, since although a
window's close button or titlebar should be interactable if any part of it is
visible, it was much simpler to treat a UI element as visible only if none of
it was obscured. While looping over all windows stacked on top of a candidate
window, the ones that cannot be closed or moved can be ignored.

```c++
Window& candidate = getAWindow();
Rect closeTarget = candidate->getCloseTarget();
bool closeOccluded = false;
Rect moveTarget = candidate->getMoveTarget();
bool moveOccluded = false;

while (occluderIdx-- > 0) {
    // Occlusion is simply based on having any overlap, because partial overlap
    // involves much more complicated geometry.
    auto occBounds = wm[occluderIdx]->getBounds();
    closeOccluded |= occBounds.overlapsWith(closeTarget);
    moveOccluded |= occBounds.overlapsWith(moveTarget);
}

// If both targets are occluded, this window is not interactable.
if (closeOccluded && moveOccluded) {
    dbg_printf("Window %p is fully occluded, will not "
               "interact.\n",
               &*candidate);
    continue;
}
```

### Distance metrics

Knowing what is interactable, choose the one nearest to the cursor.

The trick here (for a machine that doesn't have good division performance)
is that the precise distance between points doesn't matter, so L1 distance
is good enough.

---

With that logic in mind, here's a prototype in action where new windows were
periodically being spawned and an appropriate one was being closed, with
movement of the window as required.

<figure>
<video controls muted width="320" height="240"
       src="{{< resource "morewindows.webm" >}}">
</figure>

The cursor's speed seems inconsistent here because this particular prototype
restarted moving the cursor every time it considered whether a new window
should be targeted (when a window was created), and (as described in the
following sections) at the time I recorded this cursor movement over short
distances moved much more slowly than a human would.

### Cursor movement

Bresenham's line algorithm, but ended up being fixed-point math.

### Cursor pacing

Initially had constant time movements, but that didn't feel natural.

### Window placement

Approximate a normal distribution


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
