---
title: A selection of CPU hardware bugs
slug: some-cpu-bugs
date: 2026-01-28T12:28:00.000+11:00
---
Catherine (Whitequark)'s recent [observations on poorly](https://crackhead.technology/)[-engineered firmware](https://social.treehouse.systems/@whitequark/115946915331426694) reminded me of a few mistakes I've seen in vendors' CPUs; some unimportant and others surprisingly bad. Since I've never seen these widely discussed, here's some discussion and links to supporting evidence to make the more widely known.

<!--more-->

## Intel's misspelled CPUIDs

I'm aware of two situations where Intel have sold CPUs that report misspelled names in some of the strings returned by the [`CPUID` instruction](https://en.wikipedia.org/wiki/CPUID). This seems embarrassing for an organization of Intel's size, but probably doesn't hurt anybody's ability to use the CPUs in question.

### GenuineIotel

A web search for "GenuineIotel" reveals some discussions regarding this apparent typo, where some processors such as the [Xeon E3-1231 v3](
https://instlatx64.github.io/InstLatx64/GenuineIotel/GenuineIotel00306C3_Haswell_CPUID5.txt) return the string "GenuineIotel" (instead of the usual "GenuineIntel") for the CPU manufacturer ID. This one is well-known enough to be mentioned in the list of manufacturer IDs on Wikipedia.

It's possible this misspelling is actually caused by some kind of random hardware error, since the characters 'n' and 'o' differ by only one bit; an unpredictable error that sets that bit would change `GenuineIntel` to `GenuineIotel`.

### ore i5

Another error that seems more likely to be human error in the CPU is in the i5-1245U CPU, which returns a processor brand string `Intel(R) ore(TM) i5-1245U` which is simply missing the 'C' in `Core(TM) i5`. Web searches for "Intel(R) ore(TM)" show a number of results which could be errors introduced by non-technical users attempting to copy down text from their screen when asking for tech support, but the [Ubuntu certified configuration of the Dell Latitude 5430 with this CPU](https://ubuntu.com/certified/platforms/12916) attests to this error actually being present in at least some machines using that CPU.

It's possible this misspelling is not part of the physical CPU design and is instead part of the system firmware because [at least on many AMD CPUs the CPU name is normally set by the system firmware](https://chipsandcheese.com/p/why-you-cant-trust-cpuid). It's possible that the CPU design or its microcode encode this misspelling, or that Intel's firmware package that vendors use is the source. In either case, it seems embarrassing for them that such an error made it out into machines purchased by members of the public.

## ITE's pipeline bug

https://github.com/zephyrproject-rtos/zephyr/pull/45881/files
