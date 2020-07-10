---
author: tari
comments: true
date: 2013-02-01 21:35:10+00:00
slug: fourier-transform
title: '"Four"ier transform'
wordpress_id: 924
categories:
- Miscellanea
- Software
tags:
- '4'
- comedy
- dsp
- fourier
- math
- python
- transform
---

Today's [Saturday Morning Breakfast Cereal](http://www.smbc-comics.com/):

<figure>
    <a href="http://www.smbc-comics.com/?id=2874">
        <img src="/images/2013/20130201.gif" alt="SMBC for February 1, 2013" />
    </a>
</figure>

I liked the joke and am familiar enough with the math of working in unusual
bases that I felt a need to implement a quick version of this in Python. Code
follows.

```python
#!/usr/bin/env python

def fourier(x, b):
    """Attempts to find a fourier version of x, working down from base b.

    Returns the fouriest base."""
    mostFours = 0
    bestBase = -1

    for base in range(b, 1, -1):
        fours = 0
        t = x
        while t != 0:
            if (t % base) == 4:
                fours += 1
            t //= base

        # Prefer lower bases
        if fours >= mostFours:
            print(baseconvert(x, base) + "_{0}".format(base))
            mostFours = fours
            bestBase = base

    return bestBase

BASE_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def baseconvert(x, base):
    s = ""
    while x != 0:
        s += BASE_CHARS[x % base]
        x //= base
    return ''.join(reversed(s))

if __name__ == '__main__':
    from sys import argv, exit
    if len(argv) < 2:
        print("""Usage: {0} <number>

Computes the "four"ier transform of <number>, printing the optimizations to
reach the "fouriest" form.""".format(argv[0]))
        exit(1)

    x = int(argv[1])
    # Base 36 is the largest sensible base to use
    base = fourier(x, 36)

    if base == -1:
        print("{0} is four-prime!".format(x))
```

This is Python 3.x code, using explicit integer division. It should work under
the 2.x series if you change line 34 to use "/=" rather than "//=". It can only
go up to base 36, because I didn't want to deal with bases that are hard to
represent in reasonable ways. Up to base 64 is an option, but in that case I
would have wanted to use [MIME base 64](https://en.wikipedia.org/wiki/MIME),
which puts digits at positions 52 through 61, which would be confusing to read.
Thus it only supports up to base 36, but could be adjusted with relative east to
do larger bases.

Running a few examples:

```sh
$ python fourier.py 624
HC_36
HT_35
IC_34
IU_33
JG_32
K4_31
143_23
1B4_20
440_12
4444_5

$ python fourier.py 65535
1EKF_36
1IHF_35
1MNH_34
1R5U_33
1VVV_32
2661_31
2COF_30
2JQO_29
2RGF_28
38O6_27
3IOF_26
44LA_25
B44F_18
14640_15
4044120_5

$ python fourier.py 3
3 is four-prime!
```

A few quirks: it prefers lower bases, so bases that match earlier attempts in
fouriness will be printed, despite having equal fouriness. I've decided to call
values that have no representations containing a '4' character "four-prime",
which is probably going to be a rare occurrence, but the program handles it
okay.

Generalization of the algorithm is certainly possible, and basically requires
changing the condition on line 14 to match different digit values. For example,
a hypothetical "Three"ier transform would replace the '4' on line 14 with a '3'.

# Further reading

There's a rather interesting discussion of the topic over on
[Reddit](http://www.reddit.com/r/math/comments/17oyhn/smbc_fourier/), as well as
[a](https://github.com/snowyote/fouriest)
[few](http://wigfield.org/fourier.html)
[other](http://codepen.io/anon/full/kcaFK) implementations. (Thanks to
[Merth](http://merthsoft.com/) for pointing those out to me.)
