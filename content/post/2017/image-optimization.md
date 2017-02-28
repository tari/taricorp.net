---
date: 2017-02-23
title: Quick and dirty web image optimization
subtitle: An exercise in measurement
layout: post
tags:
  - web
  - png
  - jpeg
  - optipng
  - jpegtran
  - jupyter
  - python
  - science
  - csv
---

Given a large pile of images that nominally live on a [web server][cemetech], I
want to make them smaller and more friendly to serve to clients. This is hardly
novel: for example, Google offer [detailed advice on reducing the size of images
for the web][google-advice]. I have mostly JPEG and PNG images, so, `jpegtran`
and `optipng` are the tools of choice for bulk lossless compression.

[cemetech]: https://www.cemetech.net/
[google-advice]: https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/image-optimization

To locate and compress images, I'll use GNU [`find`][gnu-find] and
[`parallel`][gnu-parallel] to invoke those tools. For JPEGs I take a simple
approach, preserving comment tags and creating a progressive JPEG (which can be
displayed at a reduced resolution before the entire image has been downloaded).

[gnu-find]: https://www.gnu.org/software/findutils/
[gnu-parallel]: https://www.gnu.org/software/parallel/

    find -iname '*.jpg' -printf '%P,%s\n' \
        -exec jpegtran -o -progressive -copy comments -outfile {} {} \; \
        > delta.csv

Where things get a little more interesting is when I output the name and size of
each located file (`-printf ...`) and store those in a file (`>
delta.csv`).[^csv] This is so I can collect more information about the changes
that were made.

[^csv]: Assumption: none of the file names contain commas, since I'm calling
  this a CSV (comma-separated values) file. It's true in this instance, but may
  not be in others.

## Check the JPEGs

Loading up a [Jupyter][jupyter] notebook for quick computations driven with
Python, I load the file names and original sizes, adding the current size of
each listed file to my dataset.

[jupyter]: https://jupyter.org/

```python
import os
deltas = []

with open('delta.csv', 'r') as f:
    for line in f:
        name, _, size = line.partition(',')
        size = int(size)
        newsize = os.stat(name).st_size
        deltas.append((name, size, newsize))
```

From there, it's quick work to do some list comprehensions and generate some
overall statistics:

```python
original_sizes = [orig for (_, orig, _) in deltas]
final_sizes = [new for (_, _, new) in deltas]
shrinkage = [orig - new for (_, orig, new) in deltas]

pct_total_change = 100 * (sum(original_sizes) -
                          sum(final_sizes)) / sum(original_sizes)

pct_change = [shrinkage /
              orig for (shrinkage, orig) in zip(shrinkage, original_sizes)]
avg_pct_change = 100 * sum(pct_change) / len(pct_change)

print('Total size reduction:', sum(shrinkage),
      'bytes ({}%)'.format(round(pct_total_change, 2)))
avg = sum(shrinkage) / len(shrinkage)
print('Average reduction per file:', avg,
      'bytes ({}%)'.format(round(avg_pct_change, 2)))
```

This is by no means good code, but that's why this short write-up is "quick and
dirty". Over the JPEGs alone, I rewrote 2162 files, saving 8820474 bytes
overall; about 8.4 MiB, 8.02% of the original size of all of the files- a
respectable savings for exactly zero loss in quality.

## PNGs

I processed the PNGs in a similar fashion, having `optipng` emit interlaced
PNGs which can be displayed at reduced resolution without complete data and try
more combinations of compression parameters than it usually would, trading CPU
time for possible gains. There was no similar tradeoff with the JPEGs, since
apparently `jpegtran`'s optimization of encoding is entirely deterministic
whereas `optipng` relies on experimental compression of image data with varying
parameters to find a minimum size.

Since I observed that many of the PNGs were already optimally-sized and
interlacing made them significantly larger (by more than 10% in many cases), I
also considered only files that were more than 256 KiB in size. To speed up
processing overall, I used `parallel` to run multiple instances of `optipng` at
once (since it's a single-threaded program) to better utilize the multicore
processors at my disposal.

    find -iname '*.png' -size +256k -printf '%P,%s\n' \
        -exec parallel optipng -i 1 -o 9 ::: {} + \
        > delta.csv

Running the same analysis over this output, I found that interlacing had a
significant negative effect on image size. There were 68 inputs larger than 256
KiB, and the size of all of the files increased by 2316732 bytes; 2.2 MiB,
nearly 10% of the original size.

A few files had significant size reductions (about 300 KiB in the best case),
but the largest increase in size had similar magnitude. Given the overall size
increase, the distribution of changes must be skewed towards net increases.

### Try again

Assuming most of the original images were not interlaced (most programs that
write PNG don't interlace unless specifically told to) and recognizing that
interlaced PNGs tend to compress worse, I ran this again but without interlacing
(`-i 0`) and selecting all files regardless of size.

The results of this second run were much better: over 3102 files, save 12719421
bytes (12.1 MiB), 15.9% of the original combined size. One file saw a whopping
98% reduction in size, from 234 KB to only 2914 bytes- inspecting that one
myself, the original was inefficiently coded 32 bits per pixel (8-bit RGBA), and
it was reduced to two bits per pixel. I expect a number of other files had
similar but less dramatic transformations. Some were not shrunk at all, but
`optipng` is smart enough to skip rewriting those so it will never make a file
larger- the first run was an exception because I asked it to make interlaced
images.

## That's all

I saved about 20 MiB for around 5000 files- not bad. A [copy of the
notebook][notebook] I used to do measurements is available (check out
[nbviewer][nbviewer] for an online viewer), useful if you want to do something
similar with your own images. I would not recommend doing it to ones that are
not meant purely for web viewing, since the optimization process may strip
metadata that is useful to preserve.

[notebook]: /images/2017/image-optimization.ipynb
[nbviewer]: https://nbviewer.jupyter.org/
