---
title: Notes on CORDIC in TI calculators
slug: ti-cordic
draft: false
date: 2022-11-06T22:22:30.043Z
---
I've been thinking about the details of how TI's Z80-based calculators implement trigonometric operations (sin, cos, tan, ...) and have concluded that the details may be interesting but don't seem well-documented.\
\
It's well-known that [TI use CORDIC](https://education.ti.com/en/customer-support/knowledge-base/ti-83-84-plus-family/product-usage/11693) to iteratively compute approximations for these functions, but the details of that algorithm matter. The "classical" CORDIC as [described by Volder](https://doi.org/10.1109/AFIPS.1959.57) is well suited to base-2 computers, but it's not directly applicable to a machine like a pocket calculator that "thinks" in base 10 (also well-documented, TI use a BCD floating-point numeric representation).\
\
Hermann Schmid's 1974 book [Decimal Computation](https://archive.org/details/decimalcomputati0000schm/) describes in Chapter 7 a straightforward adaptation for CORDIC to base 10, which certainly works but suffers somewhat in that it requires 9*(number of digits) iterations to converge to an answer rather than simply (number of bits) iterations.\
\
The most obvious reference for a pocket calculator's use of CORDIC is the HP-35, where the precise algorithms in use were described by William Egbert in the [June 1977 issue of the HP Journal](http://hparchive.com/Journals/HPJ-1977-06.pdf#page=17). Although this isn't obviously a CORDIC implementation, it borrows the terminology for pseudo-multiplication and pseudo-division from [Meggit's 1962 work](https://doi.org/10.1147/rd.62.0210) and the recurrence relation in use clearly matches the shift-and-add loop in CORDIC.\
Rather interestingly, there seems to be an important difference between this implementation and Schmid's in that HP's version computes the tangent of an input angle only, and the sine or cosine of the angle are expressed as a ratio of the tangent or cotangent (requiring exponentiation and division to get the final result) whereas classical CORDIC can apply pre-scaled gain to get those results directly.

- - -

\
I've found that a straightforward implementation of Schmid's version of CORDIC in software (with decimal floating point) achieves fairly good results, but of course requires many iterations to achieve 14 digits of precision as is used on TI-Z80 calculators. That approach is also most relevant to fixed-point computations: it simply does not handle very small values (smaller than 1e-14) well.\
While [there exist techniques for doing accurate CORDIC in floating-point](https://doi.org/10.1109/ARITH.1993.378100), those are both newer than I expect the TI-Z80 implementation to be, and seem very storage-intensive to implement (needing a lot of ROM). [According to Mike Sebastian](http://www.rskey.org/~mwsebastian/miscprj/models.htm), every TI-Z80 calculator (82 through 86, numerically) seems to use the same implementation for these functions, the earliest of which (the 85) was released in 1992.\
\
Although I haven't experimented with an implementation similar to the one described by Egbert, I think there's more to the story of TI's version than any single one of these sources. In particular, I found that TI's version appears to treat values smaller than 1e-6 specially: TI displays sin(1e-5) as 1e-5, but we can see the undisplayed guard digits by subtracting 1e-5 from that result, getting -1.666e-16. At sin(1e-6) however, the result is precisely equal to 1e-6.\
\
It seems suggestive to me that the result drops off after exactly 5 decimal digits, because that matches the 5-digit pseudo-quotient described by HP. It seems that TI's implementation may assume that the sine of any angle smaller than 1e-6 radians is simply the angle itself (which tends to be accurate to about the first 12 digits!), and might also be able to recognize common angles (multiples of π/4) to return exact answers.

- - -

\
Somebody asked [a question on Reddit](https://www.reddit.com/r/TI_Calculators/comments/w5fs8a/powers_of_i_imaginary_not_quite_correct/) about where error creeps in when taking exponents of i that seems relevant to this investigation as well.\
\
Small exponents like i² (1) and i³ (-1) are displayed exactly, but when you reach an exponent of 7 then the displayed value is off by a factor of about 1e-13. I suppose that exponentiation of complex numbers may be implemented by converting to polar form and back, taking advantage of the same CORDIC algorithm to do those conversions.\
\
When the input angle to CORDIC is large we know that it needs to be scaled to be in range (usually 0-π/2), so I suspect that large exponents end up like large angles where scaling them to be in range introduces a small error (on the order of 1 least-significant digit per turn) which becomes evident when the exponent of i becomes large enough.\
\
It's also a little bit interesting that powers that are a multiple of 10 (i10, i20) continue to yield exact results (-1). I suspect this is because the power of 10 simply causes the exponent of the value to change, which doesn't introduce any further error in the mantissa.