---
title: "WEB1999: the web of 1999 in math class"
slug: web1999
date: 2025-01-22T16:00:00+11:00
---

I often find that imposed limitations make it easier to create things: it's
easy to aim for perfection if you can expend as much effort as you like on
something and thus end up with nothing that you'll ever call good enough to
share. Over on Cemetech in the final months of 2023,[^delayed] we [held a programming
contest](https://www.cemetech.net/forum/viewtopic.php?t=19320): write a
screensaver, any kind of screensaver. I'm not often one to do any kind of
competitive programming, but as a prompt for a constrained project this was a
good one for me. As a result, [I wrote a program I called
WEB1999](https://www.cemetech.net/forum/viewtopic.php?t=19329), that won second
place.

[^delayed]: Oops, it took me more than a year to write this post.

<!-- more -->

A screensaver is a nice project because there's a lot of room in which to play and many of the hard aspects of programming (interacting with humans) can be completely ignored! I wasn't originally planning to write anything to enter, but after thinking to myself what I might expect other people to enter, I came up with an idea that piqued my interest and didn't seem too hard to build. 

<details style="padding: 0 1em; margin: 0.5em; background-color: #eee;">
<summary>In this post you will find...</summary>
{{< toc >}}
</details>

## Get the program

If you want to play with the program instead of or in addition to simply
reading about it, a copy of WEB1999 suitable for loading onto a TI-84+ CE or
TI-83 Premium CE calculator can be obtained from the releases section of my
Gitlab project: \
**<https://gitlab.com/taricorp/web1999/-/releases>**

The source code can also be found on Gitlab, or a copy can also be obtained
from the [Cemetech archives](https://www.cemetech.net/downloads/files/2402) or
[ticalc.org](https://www.ticalc.org/archives/files/fileinfo/479/47909.html).
All of the release packages include the full source code and documentation, so
you shouldn't miss anything regardless of where you choose to get a copy from.

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
describe!

Continue reading for notes on [the program's design](#design-notes) and
[interesting aspects of its implementation](#implementation-notes), plus
[additional improvements I'd like to
make](#bytecoded-graphics-and-future-work).

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

As it turns out, it's much easier as a software author to assume an intelligent
user than it is to automate behavior that looks intelligent. On the upside
however, automating everything means none of the interaction actually needs to
work, and shortcuts can be taken there.

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

When there are multiple windows onscreen, some of them might be obscuring 
important parts of others like the close button or even hiding the lower
one completely.

Although the topmost window should always be interactable, I didn't think
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

This code sample (adapted from the real program's `getNewTarget` function)
illustrates generally how the logic to select a window
works, assuming one that we want to interact with is returned by
`getAWindow`. `wm` is the list of windows sorted with the topmost first:

```c++
extern Window wm[MAX_WINDOWS];

Window& candidate = getAWindow();
Rect closeTarget = candidate.getCloseTarget();
bool closeOccluded = false;
Rect moveTarget = candidate.getMoveTarget();
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
    dbg_printf("Window %p is fully occluded, will not interact.\n",
               &candidate);
    continue;
}
```

In the real program, this runs in a loop until an interactable window
is found with candidates chosen by their distance from the cursor: the
program will choose to interact with the window that is closest to the
cursor, as long as the region that the cursor needs to be in to either
move or close the window is not occluded by another window.

This code sample also illustrates a few of the abstractions I wrote to
hide some of the details of the math. A `Window`'s location is described
by a `Rect` which has a position onscreen, width and height; there are also
shortcut functions to get the `Rect`s corresponding to where the window's
titlebar is (which can be interacted with to bring the window to the top and
move it), as well as its close button. The `overlapsWith` method on `Rect`s
checks whether any part of a rectangle overlaps with some other rectangle.

### Distance metrics

The next moderately interesting question to answer was how to determine
which window is closest to the cursor, since it's now understood how to
determine if a given window is actually an acceptable candidate to interact
with.

The obvious approach is to use basic geometry and get the length of a vector
between the cursor and the closest point of a window to the cursor. If
`cx` and `cy` are the cursor's X and Y coordinates while `wx` and `wy` are
the coordinates of a point on a window, the distance is clearly
`sqrt((cx-wx)*(cx-wx) + (cy - wy)*(cy - wy))`: simply apply the Pythagorean
theorem.

On an eZ80 processsor where I could be doing this computation with fairly high
frequency, I didn't think getting a true hypotenuse length would be acceptably
performant. There's no hardware support for computing the square root of
numbers, and I wasn't very interested in trying to implement a fast square
root.

Instead, I noticed that the actual distance between two points doesn't actually
matter, as long as I can know which of multiple points (points on windows that
we might want to interact with) is closest to a chosen point (the cursor's
current location). Since the relationship between any two distances (which is
longer) before computing the square root and even before squaring the
coordinate offsets is the same as after doing those operations, I simplified
distance computations to work in terms of the [rectilinear
distance](https://en.wikipedia.org/wiki/Taxicab_geometry) instead:

```c++
static int distance_NonLinear(gfx_point_t a, gfx_point_t b) {
    return abs(a.x - b.x) + abs(a.y - b.y);
}
```

With a distance metric, the `getNewTarget` function can iterate over all
windows onscreen and find the one nearest to the cursor. The actual distance
is not known, but we do know the nearest window is found. As discussed in the
previous section, windows where none of the interaction targets are visible
(abstracted out as the `isFullyOccluded` function) are ignored.

```c++
Window* nearest = nullptr;
int nearestMetric = INT_MAX;

for (auto candidateIdx = 0; candidateIdx < wm.size(); candidateIdx++) {
   Window* candidate = wm[candidateIdx];
   if (isFullyOccluded(candidate)) {
       continue;
   }

   auto candidateDest = closeTarget.getNearestPoint(cursor.getLocation());
   auto candidateDist = distance_NonLinear(cursor.getLocation(), candidateDest);
   if (candidateDist < nearestMetric) {
       nearest = candidate;
       nearestMetric = candidateDist;
   }
}

return nearest;
```

---

With that logic in mind, here's a prototype in action where new windows were
periodically being spawned and an appropriate one was being closed, with
movement of the window as required.

<figure>
<video controls muted width="320" height="240"
       id="video-morewindows"
       src="{{< resource "morewindows.webm" >}}">
</figure>

The cursor's speed seems inconsistent here because this particular prototype
restarted moving the cursor every time it considered whether a new window
should be targeted (when a window was created), and (as described in the
following sections) at the time I recorded this video the cursor moved over
short distances moved much more slowly than a human would.

### Cursor movement

In the previous video, the cursor is already moving along a line between
its original location and its destination. This is very easy for a human
to do when using a mouse, but took some effort to implement in software
in a way that was reasonably performant on a (e)Z80 processor.

The first algorithm I thought of when considering how to determine where
to move the cursor was to use [Bresenhams' line
algorithm](https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm),
which I have previously heard of used for fast line-drawing functions on
TI calculators.
After spending some time familiarizing myself with Bresenham's algorithm,
I realized there was an issue with simply applying that algorithm: I need
the cursor to move over time, not merely draw the line between two points.

At this point I decided it made sense to take advantage of the eZ80 being
more capable than most 8-bit processors, in that it is able to do arithmetic
on integers that are up to 24 bits wide and can multiply (but not divide)
16-bit integers in hardware. So I reached for fixed-point math.

What I ended up with was a `Mover` class encapsulating the details of
computing how the cursor should move, which is constructed with two points to
move between and can be advanced over time to sweep between the start
and end points.

```c++
class Mover {
public:
    Mover(gfx_point_t start, gfx_point_t end);

    // Return the new position after moving at the given speed,
    // setting *done to true if the new position is the endpoint.
    gfx_point_t advance(uint8_t speed, bool *done);
};
```

Because it seemed reasonable to move the cursor in up to 128 steps, I chose to
express the progress from start to end point as an 8-bit unsigned value, with 1
bit before the decimal point and 7 after: the 8-bit integer `0` is 0.0, and
`0x80` is 1.0. In this way, moving the cursor at minimum nonzero speed involves
adding 1/128 (integer value `1`) to the progress along the line at each step.

Inspired by Bresenham's line algorithm, for each of the x and y coordinates
I multiplied the required distance to be moved by the fraction of the distance
to be moved (that fixed-point number) to get the distance to move the cursor
in one step. To prevent drift, the fractional part is saved and accumulates
between calls, adding to the distance moved when it exceeds 1 pixel.
The code looks like this, where `speed` is a fixed-point fraction of the
total distance to cover, `progress` is the fraction of the distance covered
already, `dx` and `dy` are the total distance to move on the X and Y axes,
and `errx` and `erry` are the accumulated error for each axis:

```c++
gfx_point_t Mover::advance(uint8_t speed) {
    // If speed would cause overshoot, clamp progress to 1.0.
    if (speed + progress > 0x80) {
        speed = 0x80 - progress;
    }
    gfx_point_t out;

    // Fixed-point multiplication, taking the integer part.
    out.x = (dx * speed) / 0x80;
    // Take the fractional part and add to accumulated error.
    errx += abs(dx * speed) & 0x7f;
    // If error is greater than 1.0, advance towards the destination
    // and subtract 1.0 from the error.
    if (errx >= 0x80) {
        out.x += signum(dx);
        errx -= 0x80;
    }

    // Do the same for the y axis...

    return out;
}
```

Notably, this implementation shouldn't require any actual division because
the divisions are always by 128, which can be expressed as an arithmetic
right shift by 7 bits instead. Multiplication is still needed, but eZ80's
hardware multiplier should be sufficient to make that fast.

### Cursor pacing

As I noted in relation to the [last video](#video-morewindows), the initial 
approach I chose to selecting the speed at which the cursor should move yielded
awkward results where it tended to move much slower than a human would if
it only needed to move a short distance. This had two reasons:

 * The amount of time required to move between two points was constant: the
   speed used to advance the `Mover` was always 1/128, so the cursor would
   always take 128 ticks to move between two positions.
 * When a new window was created, cursor movement was reset. If the new
   destination was close to the cursor's current position, it would always
   take 128 ticks to reach the new position which could make it seem to
   suddenly change speed to move very slowly when a new window appeared.

Clearly, constant-time cursor movement doesn't look like what a human would do.
I expect that a human attempting to move a mouse cursor to a given location
onscreen would tend to move faster (cover more pixels each second) for longer
moves, and might slow down as they near the target. In general, the time taken
to move a given distance onscreen would be roughly constant whereas what I had
implemented was that the fraction of the distance covered would be roughly
constant.

Because the `Mover` still works in fractions of the distance to cover however,
there needs to be a conversion between speed in pixels and the fraction of the
total distance to cover in each tick. The obvious approach is to compute the
distance to cover, then divide that distance by the desired speed in pixels per
tick and multiply by 1.0 (as a fixed-point value; 128): `speed_px * 128 /
distance_px`. For example, if the cursor moves at a constant speed of 4 pixels
per tick and it needs to move 64 pixels total, then it's obvious that it should
move one sixteenth of the total distance per tick (because 64 divided by 4 is
16): 4 * 128 / 64 = 8, which is equal to 1/16 when interpreted as a fixed-point
value with 7 fractional bits.

That obvious approach bumps into both of the issues that we've
already used tricks to improve the performance of, though: it both needs to
accurately compute the distance to traverse (which was previously replaced
with the rectilinear distance in `distance_NonLinear`) and divide by that
number (whereas we chose to do fixed-point arithmetic so the only required
division can be expressed as a bitshift).

Noticing that accurately expressing the fraction of the desired distance to
move would always require an accurate computation of the Euclidean distance
between two points on the screen (which I didn't want to do, because computing
the square root of a number would probably be slow), I instead chose to manually
write a piecewise function that looked about right:

```c++
// d is the rectilinear distance to travel
if (d == 0) {
       return 128;
} else if (d < 3) {
       return 64;
} else if (d < 9) {
       return 32;
} else if (d < 16) {
       return 16;
} else if (d < 48) {
       return 8;
} else if (d < 96) {
       return 4;
} else if (d < 152) {
       return 2;
} else {
       return 1;
}
```

In practice, this means that moves of 0 distance will take one tick to complete,
2 or less take 2 ticks, 8 or less take 4 ticks and so forth. I initially
wrote that function to work in powers of two exclusively (branches for values
of `d` less than 1, 2, 4, 8, ... taking 1, 2, 4, 8, 16, ... ticks to complete)
and then manually adjusted the points where the speed would change by just 
watching the program run while printing debug output (how far the cursor was
going to move next and the chosen speed), so when I thought a cursor movement
looked bad I could make a note and eventually converge on good-looking speeds.

This speed computation function is clearly not very accurate, but because
it's meant to behave like a hypothetical human operating a computer mouse it's
possibly even better this way than if it were accurate: a human's speed won't
always be exactly the same, and it builds in some bias toward moving slightly
slower for very short moves where a human might be more careful to move
accurately.

### Window placement

The last somewhat awkward thing in the [previous video](#video-morewindows)
is that the placement of windows on the screen doesn't seem as random as it
should be: they tend to be toward the right side of the screen, whereas it seems
more likely that pop-up windows would attempt to place themselves near the
center of the screen for maximum ~~annoyance~~ visibility.

To choose the position of a window when it was created, I was simply generating
uniform (or near enough to uniform) random screen coordinates for it to be
displayed at (0-319 on the X axis and 0-239 on the Y), then clamping values to
ensure there would always be something interactable visible (the titlebar to
drag the window, or its close button).

However, the coordinates of a window were the position of its `Rect`, which is
defined to be the top left corner. That meant that windows would never hang off
the left side of the screen, and could hang almost all the way off the right
which would tend to look like a bias toward the right side of the screen.

The obvious first thing to change was to make the randomly-selected X coordinate
represent the center of a window, rather than the left edge. While I did make that
change, I also considered how to make windows prefer to be placed toward the
center of the screen while still appearing to be random. (I left the Y coordinate
as it was, because a window with its top edge offscreen cannot be interacted
with at all.)

I assumed that a standard normal distribution tends to look random in a way
that is satisfactory to the eye, so after doing some research I decided to
approximate a normal distribution with an [Irwin-Hall
distribution](https://en.wikipedia.org/wiki/Irwin%E2%80%93Hall_distribution) of
degree twelve. With some tweaking of the values output from the distribution
with random numbers in the range 0-255 as input (generated as three 32-bit
integers and split into twelve bytes), I generated an approximation of a normal
distribution centered at 208:

```c++
static int genXCoord() {
    // This uses an Irwin-Hall distribution approximating a normal distribution in
    // range 0-512 to generate coordinates with approximate normal distribution
    // between -96 and 416 which is a pretty good range for window X coordinates.
    int sum = 0;

    for (auto i = 0; i < 3; i++) {
        uint32_t x = random();
        sum += x & 0xff;
        sum += (x >> 8) & 0xff;
        sum += (x >> 16) & 0xff;
        sum += (x >> 24) & 0xff;
    }
    return (sum / 6) - 96;
}
```

A division operation snuck in here, which at a glance seems like an odd choice
given the effort I went through earlier to avoid any division. In this case I
decided it was okay, because:

1. This function is called only when a new window is created, where it's
   plausible that a computer might "lag" a little bit because it's busy
   rendering the window.
2. Because the division is by a constant integer, it's [possible
   (and easy) to convert that to a multiplication and
   bit-shift](https://doi.org/10.1145/178243.178249) instead. I don't recall
   checking if the compiler I used to build WEB1999 actually did such a
   transformation (though [Clang does support doing
   so](https://lemire.me/blog/2019/02/08/faster-remainders-when-the-divisor-is-a-constant-beating-compilers-and-libdivide/)),
   but recognizing that it could is good enough for me.

### Selecting window kinds

A final interesting piece of WEB1999's implementation is how it selects which
kind of window to display when a new one is to be created. I wanted there to be
as many different pop-ups as I had time and memory available to make, but also
never wanted the same pop-up to be displayed more than once on the screen at any
given time: every visible window should be unique.

I achieved this by indirection in the window manager and dynamic dispatch. The
`WindowManager` owns an array of `Window*` which are the windows being displayed
onscreen, or `nullptr` if the window that goes in a slot is not open.  Each slot
in this array is assigned to a particular kind of window, which is a subclass of
`Window`. Those slots are assigned manually in the source code, something like
this (where in the actual implementation, use of a macro avoids repeating most
of the code for each case):

```c++
static Window *instances[10];
int x; // Random number representing a valid index in instances

int created_type;
switch(x) {
createWrap:
    case 0:
        if (instances[0] == nullptr) {
            instances[0] = new HotSingles();
            created_type = 0;
            break;
        }
        // Fall through to try the next kind if there's already a
        // HotSingles instance.
    case 1:
        // Try to create a DragonballFanpage in the same way,
        // in instances[1].
    case 2:
        // ...

        // After 10 window kinds, wrap back around
        goto createWrap;
}
```

Note that if a window of the randomly-chosen type already exists, this function
will attempt each of the others in sequence until one that doesn't yet exist is
created. That requires a check beforehand to ensure that there is at least one
available slot in `instances` to avoid an infinite loop, which I've omitted from
the above sample code. The use of a `goto` statement at all is also rather
unconventional, but I found it to be a useful shortcut that allowed me to
guarantee that this function would always complete in a reasonable amount of
time. It would be more random to continuously generate random numbers until an
empty `instances` slot were found, but then in an unluckly case the computer
could spend a long time searching for a free slot.

---

The `created_type` value, not yet discussed, is important to how the window
manager tracks the order of windows (which one is topmost). Because the order
of `instances` is determined by the type of each of its members, a level of
indirection is required to refer to each instance in the on-screen order.
This is where `created_type` comes in, as well as a second array of the same
size as `instances`:

```c++
static uint8_t order[10];

// Move all entries in order down
memmove(order + 1, order, sizeof(*order) * 9);
// Place the newly-created window on top
order[0] = created_type;
```

Then in order to iterate over windows in their onscreen order, code
walks though `order` and uses those values to index into `instances`:

```c++
// Iterate through windows, topmost first
for (int i = 0; i < slots_in_use; i++) {
    Window *w = instances[order[i]];
    // Do something with w
}
```

Although somewhat unusual in structure (similar to [Duff's
device](https://en.wikipedia.org/wiki/Duff's_device) but less syntatically
confusing), I think this approach nicely avoids creating multiples of any given
window type while also avoiding any need for more complex data structures,
depending on randomness to bound execution time, or wasting extra memory on
pointers.

---

One mildly annoying limitation to this solution is that because instances
of each window type are downcast to `Window` pointers and get freed
(with the `delete` operator) when closed, `Window` must have a virtual
destructor in order to avoid undefined behavior when the instances are
deleted even though no further action is required in the destructor:

```c++
class Window {
public:
    /*
     * Window instances are meant to be POD, but delete on a superclass pointer for an
     * instance of a subclass is undefined behavior even for POD types unless there is
     * a virtual destructor.
     */
    virtual ~Window() = default;
}
```

How I wrote the code isn't the only thing I find worthy of comment in WEB1999,
though. I also have thoughts to share on how I designed the windows that it can
display and why they look the way they do!

## Design notes

I included many of my design notes in the documentation that comes along with
the program, but in the interest of easy reading I'll reproduce much of that
here alongside images that are much easier to study than they are when the
program is in motion.

### Window styles and color

With an idea in mind to build a "kill the pop-ups"-style screensaver, the first
code I had to write was something that could display a window which I could
then add interesting things to. Since I had retro PCs in mind, the window
decorations and background color are based on the default styles of Windows 95,
98, and Me; grey borders with an outset/inset shading effect, and a blue
titlebar (changing to grey when a window is inactive).

{{< figure src="testwindow.png" alt="A blank window titled 'Large Test window'" caption="The general concept for displaying windows." >}}

I also limited myself to approximately the [web-safe color
palette](https://en.wikipedia.org/wiki/Web_colors#Web-safe_colors) with only
216 colors available, although the conscious choice to limit the color palette
to that one came a bit later in the process. The CE calculators have displays
capable of doing 16-bit color (5-6-5 RGB), but programmers usually run it in an
8-bit palettized mode instead (where each byte refers to one of 256 colors)
because it's considerably faster on the calculator's relatively slow
Z80-derived processor that also lacks any purpose-built hardware to make it
more efficient to display images.

As I was developing graphics to display in the program, I had some difficulty
dealing with the limited 256-color palette and ensuring that my graphics looked
like I intended. Once I realized I could lean into the theme with a web-safe
palette and use existing tools (the [GNU Image Manipulation
Program](https://www.gimp.org/)) to make my images look the same on my computer
and a calculator, it was an easy choice! GIMP offers a web-safe palette as an
option "out of the box" alongside a choice of several dithering methods, so it
was rather fun and easy to develop graphics once I committed to that approach.

Once I nailed down the general look and feel, the ideas I had for what to put
in each kind of window fell into several categories.

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

Finally, the image of a sports car combined with a dubious claim of being the
millionth visitor to a web page is an easy way for baddies to collect
information from gullible targets. Dangling an apparent prize in front of a
user raises plenty of questions to somebody who takes a moment to think about
it (Why is a prize being given to the millionth visitor specifically?), but
those who get excited and only think carefully later could find their personal
information in the hands of n'er-do-wells before they realize!

### Memes

{{< figure src="memes.png" alt="Three windows, left to right: an image of a man with half his face covered in machinery, captioned 'CATS: ALL YOUR BASE ARE BELONG TO US'; a cartoon luchador in front of a sunset, with text 'STRONG BAD SINGS!', crossed out '$99.99?' followed by '$193.75', and a phone number 1-800-555-SBSINGS; the bow of a sunken ship sticking out above water with the legend 'Mistakes: Your purpose may only be to act as a warning to others'." caption="Internet users still enjoy memes today, though these may not be immediately recognized by younger viewers." >}}

Meme culture remains strong today, and while brainstorming ideas for things to
include in WEB1999 I recalled several "classic" memes that worked out nicely.
"All your base are belong to us" seems comfortably classified as a classic that
many people will still recognize today, and in browsing a very old collection
of memes I had stored I was reminded of the "demotivator" genre inspired by
[Despair](https://despair.com/)'s parodies of motivational posters; "Mistakes"
pictured above was one of the earliest examples of their work I found in old
versions of their web site on [the Internet Archive's Wayback
Machine](https://web.archive.org/web/19981212024329/http://www.despair.com/)
that I thought would still look okay when reduced to 256 colors and greatly
reduced in resolution.

Finally, although I might not classify "Strong Bad Sings" as a meme, it comes
from [Homestar Runner](https://homestarrunner.com/) which I get the impression
became popular with many of the same people who would have been plugged into
meme culture around the turn of the millennium.

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

## Bytecoded graphics and future work

At this point, discussion has reached the limit of what I implemented in time
to submit WEB1999 to the contest I wrote it for. After that however, I had more
ideas that seemed interesting to play with even if they weren't going to be
included in my contest submission. This section discusses those ideas, which
involve a variety of technical decisions that I think are worthy of discussion.

---

In the version of WEB1999 I submitted to the contest, there were 11 different
windows. I might have added more, but the program was nearing the limit for
reasonable size. On CE calculators the tooling supports compressing programs so
they can be larger than 64 kilobytes, but even a compressed program is limited
by the available user RAM once decompressed (up to 154 KB) and I found the
program was nearing that limit.

Having designed those 11 window kinds, I had a pretty good idea of what
sorts of graphical operations are useful for this application. Since it
seemed interesting to try to allow windows to be provided separately from
the program itself, I set out to define windows as a simple domain-specific
language rather than as C++ classes that must be compiled in to the program.

That approach could allow window definitions to be stored independently from
the main program and act more like plug-ins than an integral part of WEB1999,
so it would be easy for users to pick and choose which windows they want
to see as well as create their own.

### Bytecodes

Knowing what operations are useful, I came up with the following bytecode
instructions that the program should be able to interpret. A window
would be described by its size, text to be shown in the titlebar,
and a series of bytecode instructions. Each instruction includes up to
four operands that specify things like a position in the window's
content area or colors to use:

 * `Fill(c)`: fills the entire window content area with a specified color.
 * `Color(c)`: sets the color used by all following shape drawing commands,
   until a new color is set.
 * `Rect(x, y, w, h)`: draw an unfilled rectangle with the top left corner
   at the specified x and y coordinates, with specified width and height.
 * `FillRect(x, y, w, h)`: same as `Rect()` but fills the rectangle with the
   same color as its outline.
 * `Horiz(x, y, w)`: draw a horizontal line start at specified (x,y)
   coordinates, with width w.
 * `Vert(x, y, h)`: same as `Horiz()` but draws a vertical line with height
   h.
 * `Circle(x, y, r)`: draw an unfilled circle centered at (x,y) with 
   radius r.
 * `TextFG(c)`: set the text foreground color to c.
 * `TextColors(f, b)`: set the test foreground color to f and background
   color to b.
 * `StrXY(x, y, s)`: display the string s at (x,y).
 * `Str(s)`: display the string s immediately to the right of the last
   displayed text.
 * `Sprite(x, y, i)`: display the image i at (x,y)
 * `SpriteRLET(x, y, i)`: display the image i (with transparency and
   RLE compression) at (x,y)

Clearly some of these commands partially duplicate the functionality
of others, but I found it useful to have simplified versions of some
commands like setting the text color (where I often wanted to change
the foreground color but not the background color), or encode data
differently (RLET sprites are faster to display and require less
memory to store, provided a sprite has moderately large areas of
contiguous transparency).

---

The encoding of bytecode that the program consumes is as a stream of
single-byte opcodes (basically the names of each of the supported functions),
each followed by its parameters encoded in a way defined by the opcode. The
`Fill` and `Color` operations for example are followed by a single byte
specifying the palette index to use, whereas `Sprite` is followed by a 16-bit X
coordinate, 8-bit Y coordinate, 8-bit image width and height, then width×height
bytes of image data.

Each of these bytecode functions translates pretty directly to graphics
functions as they exist in the calculator libraries, so that aspect of the
implementation is mostly uninteresting. But to simplify writing windows in
terms of the bytecode I spent some effort building tools, and those are also
worth discussing.

### Compilation and preview

I quickly found while translating some of the window types to bytecode that
it was difficult to manually write the bytecodes. Even with the assistance
of some macros, my initial approach of writing the bytecode as byte arrays
in the program's C++ source clearly wouldn't scale to creating more windows
with ease. The "Hot Singles" window was the first one I converted, and
it looked like this:

```c++
extern const uint8_t HotSingles_descriptor[] = WINDOW_BYTECODE(
        180, 126, "Singles near you!",
        FILL(C_WHITE),
        RECT(C_BORDER_TOP, 0, 0, 96, 64),
        SPRITE(broken_image, (96 / 2) - (broken_image_width / 2),
               (64 / 2) - (broken_image_height / 2)),
        SPRITE_RLET(hotsingles_left, 5, 66),
        SPRITE_RLET(hotsingles_right, 63, 66),
        STR_XY("Waiting to meet today!", 10, 94),
        TEXT_COLOR(C_GREEN),
        STR_XY("CHAT", 118, 22),
        STR_XY("NOW!", 120, 30)
);
```

Although not too difficult to read, I needed to edit other project files to
import image files in a format suitable for embedding in a program (variables
like `broken_image` and `hotsingles_left` refer to image data) and although it's
not difficult to understand how the window is meant to look from reading this
code, making changes while developing it is tedious because that required
rebuilding and relaunching the program.[^plugins]

[^plugins]: Referring to sprites by name as in `broken_image` also wouldn't
work for images that weren't built into the program, because in this example
they're actually expressed as pointers to data compiled into the program.

To improve on those things, I chose to define a domain-specific language that
expresses the bytecode operations nicely and integrate that with a way to
generate a live preview of the window definition code so I could get a
WYSIWYG experience.

My first approach to a domain-specific language was building a small Python
library that allowed me to write a window definition as a sequence of
Python function calls. Something like this:

```python
from w9bcc import *

FillWindow(C_WHITE)
Rectangle(C_BORDER_TOP, 0, 0, 96, 64)
```

That was a little easier to write, but I wasn't satisfied by the options I had
to load images or conveniently specify colors while still selecting a color
that actually exists in the palette used by the program. In particular,
although I could choose existing libraries to load images and quantize them to
the same palette as used by WEB1999 I thought it would be difficult to build a
Python interpreter and those libraries into a format that would be easy to
distribute so anybody could write window bytecode. In particular, my ideal was
that it should be possible for anybody to write window definitions just by
loading an editor in their web browser and save the resulting bytecode in a
format suitable for sending to a calculator. So, instead of continuing further
down the Python path I decided to make it so bytecode would be written in Lua
using some WEB1999-specific libraries.

Although I had never worked with Lua before, it seemed like a good choice for
this application because it's easy to embed in larger programs and it's not
too complex as a language so it should be fairly accessible to other people.
The result looks like this:

```lua
require 'w9bcc'

local WW = 168
WindowTitle("Singles near you!")
WindowSize{width = 168, height = 105}

FillWindow('white')

SetDrawColor('silver')
DrawRectangle{x = 0, y = 0, width = 96, height = 64}
local broken_image = Sprite:load('broken_image.png')
broken_image:draw_at{x = (96 / 2) - (broken_image.width / 2),
                     y = (64 / 2) - (broken_image.height / 2)}
```

It's not difficult to see a similarity between this Lua and the Python sample
above, but it has solutions to the difficulties I already discussed:

 * Colors are specified as strings, which are interpreted according to the [rules
   of CSS](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value). That
   means that where it's convenient basic names (like `white` or `green`)
   can be used, or colors can be specified with their RGB components (`#fdcb12`)
   or even by hue, saturation and lightness (HSL; `hsl(50 80% 40%)`).
 * Images can be loaded as `Sprite` objects, which are converted to the appropriate
   palette when loaded. Their dimensions are exposed as properties of the `Sprite`
   object, which is useful to compute the position to draw at when an image is
   meant to be centered at some position.

The Lua interpreter that runs this code is embedded in a Rust program,
because I needed to write code to handle image loading and color conversion.
It was reasonably easy to do those tasks in Rust and expose the relevant
functions to Lua as a library, with a few magic functions to emit data
into the final bytecode stream (hidden behind functions like `FillWindow`
in the above example).

---


In order to get WYSIWYG editing (and to satisfy the goal that everything should
be usable by anybody with access to a web browser), I embedded the Rust program
in a web application (which I knew would be feasible when I started using Rust
for this application). It has a text editor and a canvas to display a window in
(both things that are easy to do in a web page but moderately difficult to do
in programs generally), and when the text changes it attempts to run the
bytecode compiler. If successful, it then interprets the bytecode to display
the results. Since this is a web application, you can [go try it out for
yourself!](
{{< globalresource.inline >}}
{{ (resources.Get "2025/web1999/w9bcc-web/index.html").Permalink }}
{{< /globalresource.inline >}}
)

{{< figure src="w9bcc-snapshot.png" alt="A screenshot of a web browser, with a text box containing syntax-highlighted Lua code on the left side and an image of a WEB1999 window containing several colored boxes, text and sprites. A text box below the preview reads 'Generated: 608 bytes of bytecode.'" caption="The bytecode editor is a simple split view between code and a preview of the result, with status and error information also shown." >}}

One annoyance with this simple web application is in how images need to be
loaded. Because the app does not have access to files in general, they need
to be manually loaded via a file picker before they can be loaded with
`Sprite:load`. I think this could be improved with the [web file system
API](https://developer.mozilla.org/en-US/docs/Web/API/File_System_API), but
because my bytecode compiler can also be built as a regular program and run on
the command line it's not annoying enough for me to have investigated: it's
reasonably easy to load images into the webapp for testing, then save a copy
of the images and final bytecode source as the "final" version which can
be recompiled at any time without using the web app.

---

Interpreting the bytecode here reuses the C++ decoder that I built for the
actual program (here called `w99bci`), which is compiled separately from the
Rust bytecode compiler (`w99bcc`). A small Javascript driver program takes
bytecode from the compiler and passes it to the renderer which is exposed to
Javascript using Emscripten's binding generation tools.  I had to write
versions of the calculator graphics functions that worked in terms of a [2d
canvas rendering
context](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D),
but that wasn't terribly difficult. Displaying text in the same way it would
appear on a calculator was most complex, because I needed to embed a copy of
the calculator's bitmap font and decode text into a series of images to
display. The Javascript driver looks something like this:

```javascript
// interpreter is the bytecode compiler (Rust with embedded Lua interpreter)
const interpreter = new Interpreter()
// renderer takes bytecode and displays to a canvas (C++)
const renderer = Renderer.create(document.getElementById('rendererCanvas'))

// editor refers to the text input widget
const script = editor.getValue()
const result = await interpreter.evaluate(script)
renderer.render(result.bytecode)
```

The C++ renderer has a small amount of code that's emscripten-specific,
but most of the class implementation is the same between the web and
calculator. When constructing a renderer to be embedded in a web page,
the caller is expected to pass in a handle to the DOM canvas element,
palette data, and data representing the bitmaps corresponding to how
characters are displayed in the calculator's font. The palette and font
data are loaded from image files in the caller in my application.

```c++
#ifdef __EMSCRIPTEN__
Renderer::Renderer(emscripten::val canvasElement, emscripten::val paletteValues,
                   emscripten::val fontBitmaps)
    : x(0),
      y(0),
      w(canvasElement["width"].as<uint16_t>()),
      h(canvasElement["height"].as<uint8_t>()) {
    using namespace std::string_literals;
    auto ctx = canvasElement.call<emscripten::val>("getContext", "2d"s);

    gfx_Begin(ctx, paletteValues, fontBitmaps);
}

void Renderer::renderJS(const emscripten::val &bytecode) {
    std::vector<uint8_t> bytes =
            emscripten::convertJSArrayToNumberVector<uint8_t>(bytecode);
    if (bytes.size() == 0 || bytes.back() != OP_EOF) {
        EM_ASM({throw new Error('Bytecode must end with OP_EOF, but did not')});
    }

    render(bytes.data());
}

EMSCRIPTEN_BINDINGS(Renderer) {
    emscripten::class_<Renderer>("Renderer")
            .constructor<emscripten::val, emscripten::val, emscripten::val>()
            .function("render", &Renderer::renderJS);
}

#else /* !__EMSCRIPTEN__ */
Renderer::Renderer(Rect contentArea)
    : x(contentArea.x),
      y(contentArea.y),
      w(contentArea.width),
      h(contentArea.height) {}
#endif
```

To implement graphics in terms of the library functions used on a calculator,
I added more C++ code that maintains the same kind of global state that the
calculator has, and depends on the application passing in handles to the
requisite Javascript objects (the canvas rendering context notably):

```c++
static std::vector<RGB> palette;
static emscripten::val ctx = emscripten::val::undefined();
static emscripten::val fontBitmaps = emscripten::val::undefined();
static RGBA textFGColor = {.opaque = true, .rgb = {0, 0, 0}};
static RGBA textBGColor = {.opaque = false, .rgb = {}};
static int textX;
static int textY;

void gfx_Begin(emscripten::val canvasContext, emscripten::val paletteRGB,
               emscripten::val fontBitmapsIn) {
    ctx = canvasContext;
    fontBitmaps = fontBitmapsIn;

    for (size_t i = 0; i < paletteRGB["length"].as<size_t>(); i++) {
        uint8_t r = paletteRGB[i][0].as<uint8_t>();
        uint8_t g = paletteRGB[i][1].as<uint8_t>();
        uint8_t b = paletteRGB[i][2].as<uint8_t>();
        palette.push_back({.r = r, .g = g, .b = b});
    }
}

void gfx_FillRectangle(int x, int y, int w, int h) {
    ctx.call<void>("fillRect", x, y, w, h);
}
```

Since when running on a calculator a program needs to call `gfx_Begin` to
switch display modes anyway, it's easy to do canvas initialization in the same
function for `w99bci`. Functions like `gfx_FillRectangle` implement the actual
drawing commands, using the global state set up in `gfx_Begin`.

### Limitations

Currently the web-based editor can generate bytecode from an easy-to-write
Lua program, but can't be saved as a program that can be loaded by WEB1999
running on a calculator. The main reason for this is that I'm not very satisfied
with the amount of memory they would require: when window definitions are built
into the main program, they automatically get compressed with the rest of the
code and data and decompressed when the program is run. When loading external bytecode
however, the program would either need to:

1. Decompress bytecode on the fly whenever a window needs to be displayed,
   which could be slow.
2. Require that external bytecode not be compressed, potentially requiring
   a lot of memory.
3. Decompress all bytecode that will be used into RAM at startup.

None of those are very satisfactory to me. I don't think on-the-fly
decompression will be fast enough, not allowing compression of external
bytecode seems like it would be too large, and decompressing bytecode at
startup wouldn't solve the issue of the program currently being limited by the
amount of available RAM. Possibly a hybrid solution such as allowing a window
definition to be either compressed or uncompressed and decompressing them at
startup if needed would be acceptable, but I haven't spent the time to explore
those ideas much.

---

At the time of this writing, the latest revisions to WEB1999 have converted
all of the windows I created to be expressed in terms of bytecode. This is
integrated into the procedure for compiling the program, where `w99bcc` is run
as needed to translate Lua source into data that gets compiled into the program
and interpreted using the `w99bci` component. This represents useful steps toward
being able to load external bytecode as well, but since I haven't developed a
satisfactory solution to the bytecode size-related concerns it's unable to load
external bytecode at this time.

## Conclusions

I had fun writing WEB1999, and it was nice to have a calculator programming
challenge that caught my interest. It had been some years since I wrote any
software intended to run on a calculator, and I enjoyed working within those
limitations.

If you own or have access to a TI-84 Plus CE calculator, I'd encourage you to
load a copy of WEB1999 onto it for on-demand entertainment. For everybody else,
I hope there were some interesting aspects to its implementation that I've
described or that the historical discussion around the windows I designed was
some combination of entertaining and informative!
