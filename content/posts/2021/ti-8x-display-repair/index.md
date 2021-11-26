---
title: Repairing TI-83 Plus Displays
slug: ti-8x-display-repair
draft: true
date: 2021-11-26T03:45:04.112Z
categories:
  - Hardware
tags:
  - calculators
---
Sometime last year I scored a cheap TI-83 Plus Silver Edition (SE) on Ebay, however the seller discovered before shipping that it had some display problems- there would sometimes be vertical blank lines on the display or it might not display anything at all. They were going to cancel the sale because it wasn't in complete working condition as originally claimed, but being familiar with the hardware for these calculators and their common issues, I was happy to buy it anyway under the assumption that I could fix it myself.

This turned out to be true, and in the interest of assisting others who have similar problems with calculators, I am herein  describing the process involved in making those repairs.

## Symptoms & background

The monochrome TI-8x calculators (most commonly the 83+ and 84+ variants, but also some less common ones like the non-plus TI-83 and -82) are a fairly old design by now (nearly 30 years old!), and some examples of those devices are consequently about that old as well. With age comes deterioration, especially in the display assemblies for which the design seems to have had some longevity issues.

These calculators use a 96 by 64-pixel monochrome LCD, driven by a Toshiba T4A06 LCD driver (or compatible drivers in later models such as the T6K04) which is in turn connected to the calculator's Z80 CPU. In some early versions the CPU is its own chip, but in most variants it is build into a TI-designed ASIC.

The connection between the CPU and LCD is a fairly low-speed parallel bus with 8 data signals and a few control signals. If one or more of those connections is intermittent or outright broken, the display will appear to misbehave at times. Visibly, this might look like:

 * Screen does not turn on
 * Vertical white or black lines across the entire height of the screen
 * "Static" patterns across parts of or the entire screen

(put in some illustrations here)

In most cases the culprit for these sorts of problems is the cable connecting the calculator's mainboard to the LCD having some bad connections. The cable seems to be attached to the boards with some kind of adhesive that has in many cases degraded, causing connections to fail. Fortunately, because the calculator's design is barely changed since the early 90s it's relatively easy to replace this cable with only basic tools and skills.

---

can check if it's a driver or display problem (or elsewhere) by taking a screenshot using a link cable. If screenshots look normal it's a problem with the actual LCD (which generally cannot be fixed) but if the same glitches appear in a screenshot then LCD driver connection seems bad.

## Performing repairs

Open the calculator by first removing all five batteries, including the backup coin cell. The screw on the backup battery compartment goes all the way through the case, so it must be removed to open the calculator. Then unscrew the six Torx screws holding the back of the case to the front (**TODO: what size Torx screws?**)

With the screws removed, the halves of the case can carefully be pried apart. It's difficult to damage the internal circuitry doing this, but using excessive force can leave marks in the case. However it probably will require more force than you expect to get it to come apart.

Inside, a paper and foil shield sits on top of the circuit boards and is held down by two screws near the bottom. Remove the screws and shield (which may be lightly glued onto the board as well). At this point all the important components are laid out nicely, and the cable that we want to replace is evident.

---

Continuing on to begin repairs, the LCD cable can be removed simply by pulling on it to break the adhesive. Take care to note that this is the **point of no return**: if you remove this cable it cannot be reattached and you need to complete the replacement.

In this calculator the cable left behind rather a lot of residue on the copper pads on both the LCD and mainboard. I cleaned it off using a razor blade to gently scrape the residue away, leaving shiny copper.

..then install some wires between each pair of pads on the mainboard and LCD. I used whatever solid-core wire was handy, choosing to run them down away from the LCD on the mainboard, and fold them back over.

I overheated one of the pads on the LCD and caused it to detach from the board, but fortunately I was able to carefully scrape the green soldermask off the track on the  board and attach my wire elsewhere on the same trace.

### Testing

To test my repairs, I used a bench power supply to apply 6V to the pads on the mainboard that the batteries normally connect to, and attempted to power the calculator on normally. This failed and I spent a while looking for faults but couldn't find any. It eventually started working for indiscernable reasons after I gave the LCD a good push back into the little retaining posts in the case- I'm somewhat concerned that one or more of my connections is poor, but it's working for now.