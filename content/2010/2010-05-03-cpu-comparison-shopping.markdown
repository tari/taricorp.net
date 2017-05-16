---
author: No Content Found
comments: true
date: 2010-05-03 22:18:08+00:00
layout: post
slug: cpu-comparison-shopping
title: CPU Comparison Shopping
wordpress_id: 74
categories:
- Miscellanea
---

I've been slowly working towards putting together a new PC build to replace my
current one, a Core 2 Duo- based system I built about three years ago, which is
starting to show its age.  In the interest of comparison shopping, I put
together a spreadsheet and some charts looking at the newer Intel (i5/i7) and
AMD (Phenom X4/X6) processors.  Turns out that Intel's Core i5-750 seems to be
the best deal in processors for what I'm looking for in a system at the moment.

## Raw Data

Clock speeds are in MHz, TDP in Watts, and cost is price in USD at [newegg](http://www.newegg.com/) as of 5/3/2010.  Processors with SMT (hyperthreading) are noted in the Cores column.

<table >
<tbody >
<tr >
<td >Manufacturer </td>
<td >Model </td>
<td >Cores </td>
<td >Clock </td>
<td >TDP </td>
<td >Cost </td>
</tr>
<tr >
<td >AMD </td>
<td >Phenom II X4 955 BE </td>
<td >4 </td>
<td >3200 </td>
<td >125 </td>
<td >159.99 </td>
</tr>
<tr >
<td >AMD </td>
<td >Phenom II X4 940 BE </td>
<td >4 </td>
<td >3000 </td>
<td >125 </td>
<td >161.99 </td>
</tr>
<tr >

<td >AMD
</td>

<td >Phenom II X4 965 BE
</td>

<td >4
</td>

<td >3400
</td>

<td >125
</td>

<td >180.99
</td>
</tr>
<tr >

<td >AMD
</td>

<td >Phenom II X6 1090T
</td>

<td >6
</td>

<td >3200
</td>

<td >125
</td>

<td >309.99
</td>
</tr>
<tr >

<td >Intel
</td>

<td >Core i5-650
</td>

<td >2
</td>

<td >3200
</td>

<td >73
</td>

<td >184.99
</td>
</tr>
<tr >

<td >Intel
</td>

<td >Core i5-661
</td>

<td >2
</td>

<td >3330
</td>

<td >87
</td>

<td >199.99
</td>
</tr>
<tr >

<td >Intel
</td>

<td >Core i7-920
</td>

<td >4 (SMT)
</td>

<td >2660
</td>

<td >130
</td>

<td >279.99
</td>
</tr>
<tr >

<td >Intel
</td>

<td >Core i7-930
</td>

<td >4 (SMT)
</td>

<td >2800
</td>

<td >130
</td>

<td >294.99
</td>
</tr>
<tr >

<td >Intel
</td>

<td >Core i5-750
</td>

<td >4
</td>

<td >2660
</td>

<td >95
</td>

<td >199.99
</td>
</tr>
<tr >

<td >Intel
</td>

<td >Core i7-860
</td>

<td >4 (SMT)
</td>

<td >2800
</td>

<td >95
</td>

<td >279.99
</td>
</tr>
</tbody>
</table>

<!-- more -->

## Performance Charts

I started by charting the benchmark scores for each processor in the table in
Cinebench R10 and Crysis, using benchmark results from
[bit-tech](http://www.bit-tech.net/).  The Crysis results are very limited since
Bit-Tech's benchmark settings varied.  I used 1680x1050, all settings on High,
no AA or AF.

<figure>
[Note: images have been lost.
If anyone really wants them back up, I'll regenerate them, but otherwise I won't bother.]
</figure>

{% comment %}
## [![Cinebench score](http://www.taricorp.net/wp-content/uploads/2010/05/cinebench.png)](http://www.taricorp.net/wp/wp-content/uploads/2010/05/cinebench.png)[![Crysis score](http://www.taricorp.net/wp-content/uploads/2010/05/crysis.png)](http://www.taricorp.net/wp-content/uploads/2010/05/crysis.png)Cost Comparison
{% endcomment %}

Finally, I compared the benchmark results and cost, charting how each processor
scored when the cost was divided by benchmark scores.

<figure>
Figure missing. See above.
</figure>
{% comment %}
## [![Cost / Cinebench score](http://www.taricorp.net/wp-content/uploads/2010/05/cinebench-cost.png)](http://www.taricorp.net/wp-content/uploads/2010/05/cinebench-cost.png)[![Cost / Crysis score](http://www.taricorp.net/wp-content/uploads/2010/05/crysis-cost.png)](http://www.taricorp.net/wp-content/uploads/2010/05/crysis-cost.png)Analysis
{% endcomment %}

AMD's processors generally offer better price-to-performance ratios, but Intel
wins out in terms of raw performance (I didn't include Intel's 6-core processor
here, so the 1090T still tops the charts, though).

Intel's newer i5 and i7 cores performed noticeably better in Crysis, and perform
better per-core in general.  Given the low cost-performance ratio and good raw
performance numbers, the Core i5-750 seems to be the best choice for processors
in my price range at the moment.  Even better, the TDP of the i5-750 is a full
30 Watts below that of the comparable AMD processors, all of which weigh in at
125 W.

The one factor that remains to be seen in this cost analysis is motherboards,
but I think it's pretty safe to assume that costs for AM3 and LGA1156 boards are
similar.
