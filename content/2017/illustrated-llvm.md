+++
date = "2017-05-16T10:20:43+10:00"
title = "An illustrated guide to LLVM"
categories:
 - Software
tags:
 - llvm
 - rust
 - compilers
 - presentation
 - meetup
+++

At the most recent [Rust Sydney][meetup] meetup (yesterday, "celebrating" Rust's
[second birthday][birthday]) I gave a talk intended to provide an introduction
to using LLVM to build compilers, using Rust as the implementing language. The
presentations were not recorded which might have been neat, but I'm publishing
the slides and notes here for anybody who might find it interesting or useful.
It is however not as illustrated as the title may seem to suggest.

[meetup]: https://github.com/rustsydney
[birthday]: https://blog.rust-lang.org/2015/05/15/Rust-1.0.html

It's embedded below, or you can view standalone [in your browser][preso] or as
a PDF, available [with][with-notes] or [without][without-notes] presenter
notes. Navigate with the
arrow keys on your keyboard or by swiping. Press <kbd>?</kbd> to show additional
keys for controls; in particular, <kbd>s</kbd> will open a presenter view that
includes the plentiful notes I've included.

[preso]: /2017/illustrated-llvm-presentation/index.html
[with-notes]: /2017/illustrated-llvm-notes.pdf
[without-notes]: /2017/illustrated-llvm.pdf

<iframe style="max-width: 100%; width: 800px; max-height: 100%; height: 600px"
        src="/2017/illustrated-llvm-presentation/index.html">
</iframe>

In case of curiousity, I built the presentation with
[reveal.js](https://github.com/hakimel/reveal.js) and its preparation consumed a
lot more time than I initially expected (though that's not the fault of reveal).
