---
date: 2016-01-17
title: Web history archival and WARC management
slug: web-history-warc
subtitle: I should sleep more
categories:
 - Software
 - Linux
tags:
 - warc
 - wget
 - firefox
 - cookies
 - archiving
---

I've been a sort of 'rogue archivist' along the lines of the [Archive
Team](http://archiveteam.org/) for some time, but generally lack the combination
of motivation and free time to directly take part in their activities.

That said, I do sometimes go on bursts of archival since these things do concern
me; it's just a question of when I'll get manic enough to be useful and latch
onto an archival task as the one to do. An earlier public example is when I
[mirrored ticalc.org](https://archive.org/details/ticalc-2014-08).

---

The historical record contains plenty of instances where people maintained
copies of their communications or other documentation which has proven useful to
study, and in the digital world the same is likely to be true. With the ability
to cheaply store large amounts of data, it is also relatively easy to generate
collections in the hope of their future utility.

Something I first played with back in 2014 was extracting lists of web pages to
archive from web browser history. From a public perspective this may not be
particularly interesting, but if maintained over a period of time this data
could be interesting as a snapshot of a typical-in-some-fashion individual's
daily life, or for purposes I can't foresee.

Today I'm going to write a little about how I collect this data and reduce the
space requirements. The products of this work that are source code can be found
[on Bitbucket][optiwarc-bb].

<!-- more -->

## Collecting History

I use [Firefox](https://en.wikipedia.org/wiki/Firefox) as my everyday web
browser, which combined with [Firefox
Sync](https://www.mozilla.org/en-US/firefox/sync/) provides ready access to a
reasonably complete record of my web browsing activity. The first step is
extracting the actual browser history, which is a relatively straightforward
process since Firefox maintains all of this data in
[SQLite](https://www.sqlite.org/) databases. I use `cookies.sqlite` and
`places.sqlite` from my Firefox profile.

Extracting history from `places.sqlite` is as simple as running a query that
emits timestamps and corresponding URLs. For example:

```sh
sqlite3 places.sqlite \
    "SELECT visit_date, url FROM moz_places, moz_historyvisits \
     WHERE moz_places.id = moz_historyvisits.place_id \
       AND visit_date > $LASTRUN \
     ORDER BY visit_date"
```

This will print the timestamp and URL for every page in history newer than
`LASTRUN` (which can easily be omitted to get everything), with the fields
separated by pipes (`|`). The timestamp (`visit_date`) is a [UNIX
timestamp][unix] expressed in microseconds.

[unix]: https://en.wikipedia.org/wiki/Unix_time

---

While there's some utility in just grabbing web pages, the real advantage I've
found in using data directly from a web browser is that it can gain a personal
touch, with access to private data granted in many cases by cookies. This does
imply that the data should not be shared, but as with personal letters in
history this formerly-private information may become useful in the future at a
point when the privacy of that data is no longer a concern for those involved.

Again using sqlite and the `cookies.sqlite` file we got from Firefox, it's
relatively easy to extract a [cookies.txt][cookiestxt] file that can be read by
many tools:

```sh
sqlite3 -separator ' ' cookies.sqlite << EOF
.mode tabs
.header off
SELECT host,
       CASE substr(host,1,1)='.' WHEN 0 THEN 'FALSE' ELSE 'TRUE' END,
       path,
       CASE isSecure WHEN 0 THEN 'FALSE' ELSE 'TRUE' END,
       expiry,
       name,
       value
FROM moz_cookies;
EOF
```

The output of that `sqlite` invocation can be redirected directly into a
`cookies.txt` file without any further work.

[cookiestxt]: http://kb.mozillazine.org/Cookies.txt

---

With the list of URLs and cookies, it's again not difficult to capture a
[WARC][warc] containing every web page listed. I've used [`wget`][wget], largely
out of convenience. Taking advantage of a UNIX shell, I usually do the
following, piping the URL list into wget:

```sh
cut -d '|' -f 2- urls.txt | \
    wget --warc-file=`date` --warc-cdx --warc-max-size=1G \
         -e robots=off -U "Inconspicuous Browser" \
         --timeout 30 --tries 2 --page-requisites \
         --load-cookies cookies.txt \
         --delete-after -i -
```

[warc]: https://en.wikipedia.org/wiki/Web_ARChive
[wget]: https://www.gnu.org/software/wget/

This will download every URL given to it with the cookies extracted earlier, and
will also download external resources (like images) when they are referenced in
downloaded pages. The process will be logged to a WARC file named with the time
the process was started, limiting to approximately 1-gigabyte chunks.

This takes a while, and the best benefits are to be had from running this at
fairly short intervals which will tend to provide more unexpired cookies and
catch changes over short periods of time, thus presenting a more accurate view
of what the browser's user is actually doing.

## Deduplication

{{< figure src="/images/2016/lottawarcs.png"
           alt="A directory listing showing many WARC files, each larger than a gigabyte."
           caption="Mostly nondescript files, but there's a lot here." >}}

On completion, I'm presented with a directory containing some number of
compressed WARC files. That's a reasonable place to leave it, but this weekend
after doing an archival run that yielded about 90 gigabytes of data I decided to
look into making it smaller, especially considering I know my archive runs end
up grabbing many copies of the same resources on web sites which I visit
frequently (for example, icons on [DuckDuckGo](https://duckduckgo.com)).

The easy approach would be to use a compression scheme which tends to work
better than gzip (the typical compression scheme for WARCs). However, doing so
would destroy a useful property in that the files do not need to be completely
decompressed for viewing. These are built such that with an index showing where
a particular record exists in the archive, a user does not need to decompress
the entire file up to that point (as would be the case with most compression
schemes)- it is possible to seek to that point in the compressed file and
decompress just the desired record.

I had hope that the professionals in this field had already considered ways to
make their archives smaller, and that ended up being true but the documentation
is very sparse: the only truly useful material was [a recent
presentation][dedup-slides] by Youssef Eldakar from the [Bibliotheca
Alexandrina][alexandrina] cursorily describing tools to deduplicate entries in
WARC files using `revisit` records which point to a previous date-URL
combination that has the same contents[^discomfort].

[dedup-slides]: http://netpreserve.org/sites/default/files/attachments/2015_IIPC-GA_Slides_16b_Eldakar.pdf
[alexandrina]: https://en.wikipedia.org/wiki/Bibliotheca_Alexandrina
[^discomfort]: I'm not entirely comfortable with that approach, since there is
               no particular guarantee that any record exists with the specified "coordinates"
               (time of retrieval and network location) in web-space. However, this approach
               does maintain sanity even if a WARC is split into its individual records which
               is another important consideration.

I don't see any strong reason to keep my archives split into 1-gigabyte pieces
and it's slightly easier to perform deduplication on a single large archive, so
I used [`megawarc`][megawarc] to join the a number of smaller archives into one
big one.

[megawarc]: https://github.com/alard/megawarc

It was easy enough to find the published code for the [tools][warcrefs-code]
[described][warcsum-code] in the presentation, so all I had to do was figure out
how to run them.. right?

[warcrefs-code]: https://github.com/arcalex/warcrefs
[warcsum-code]: https://github.com/arcalex/warcsum

## The Process

The logical procedure for deduplication is as follows:

1. Run `warcsum` to compute hashes of every record of interest in the specified
   archive(s), writing them to a file.
2. Run `warccollres` to examine the records and their hashes, determining which
   ones are actually the same and which are just hash collisions.
3. Run `wardrefs` to rewrite the archives with references when duplicates are
   found.

I had a hard time actually getting that to happen, though.

### `warcsum`

Running `warcsum` was relatively easy; it happily chewed on my test archive for
a while and eventually spat out a long list of files. I later discovered that it
wasn't processing the whole archive, though- it stopped after about two
gigabytes of data. I eventually found that the program (written in C) was using
`int` as a type to represent file offsets, so the apparent offset in a file
becomes negative after reading two gigabytes of data which causes the program to
end, thinking it's done everything. I patched the relevant bits to use 64-bit
types (like `off_t`) where working with file offsets, and eventually got it to
emit 1.7 million records rather than the few tens of thousands I was getting
before.

---

While investigating the premature termination, I found (using
[`warcat`][warcat]) that `wget` sometimes writes record length fields that are
one byte longer than the actual record. I spent a while trying to investigate
that and repair the length fields in hopes of fixing `warcsum`'s premature
termination, but it ended up being unnecessary. In practice this off-by-one
doesn't seem to be harmful, but I do find it somewhat concerning.

I also discovered that `warcsum` assumes wrapping arithmetic for determining
how large some buffers should be, which is [undefined behavior][ub] in C and
could cause Bad Things to happen. I fixed the instance where I saw it, but that
didn't seem to be causing any issues on my dataset.

[ub]: https://stackoverflow.com/questions/3679047/integer-overflow-in-c-standards-and-compilers#3679149
[warcat]: https://github.com/chfoo/warcat/

### `warccollres`

Moving on to `warccollres`, I found that it assumes a lot of infrastructure
which I lack. Given the name of a WARC file, it expects to have access to a
MySQL server which can indicate a URL where records from the WARC can be
downloaded- a reasonable assumption if you're a professional working within an
organization like the Bibliotheca Alexandrina or Internet Archive, but excessive
for my purposes and difficult to set up.

I ended up rewriting all of `warccollres` in Python, using a self-contained
database and assuming direct access to the files. There's nothing particularly
novel in there (see `warccollres.py` in [the repository][optiwarc-bb]). WARC
records are read from the archive and compared where they have the same hash to
determine actual equality, and duplicates are marked as such.

I originally imported everything into a sqlite database and did all the work in
there (not importing file contents though-- that would be very inefficient), but 
this was rather slow because sqlite tends to be slow on workloads that involve
more than a little bit of writing to the database. With some changes I made it
use a "real" database ([MariaDB][mariadb]) which helped. After tuning some
parameters on the database server to allow it to use much larger amounts of
memory (`innodb_buffer_pool_size`..) and creating some indexes on the imported
data, everything moved along at a nice clip.

[mariadb]: https://mariadb.org/

As the process went on, it seemed to slow down- early on everything was
I/O-bound and status messages were scrolling by too fast for me to see, but
after a few hundred thousand records had been processed I could see a
significant slowdown. Looking at resource usage, the database was the limiting
factor.

It turned out that though I had created indexes in the database on the rows that
get queried frequently, it was still performing a full table scan to satisfy the
requirement that records be processed in the order which they appear in the WARC
file. (I determined this by manually running some queries and having mariadb
`ANALYZE` them for information on how it processed the query.) After creating a
composite index of the `copy_number` and `warc_offset` columns (which I wasn't
even aware was possible until I read the grammar for `CREATE INDEX` carefully,
and had to experiment to discover that the order in which they are specified
matters), the process again became I/O-bound. Where the first 1.2 million
records or so were processed in about 16 hours, the last 500 thousand were
completed in only about an hour after I created that index.

### `warcrefs`

Compared to the earlier parts, `warcrefs` is a quite docile tool, perhaps in
part because it's implemented in Java. I made a few changes to the file
describing how [Maven][maven] should build it so I could get a jar file
containing the program and all its required libraries which would be easy to
run.  With the file-offset issues in `warcsum` fresh in my mind, I proactively
checked for similar issues in `warcrefs` and found it used `int` for file
offsets throughout (which in Java is always a 32-bit value). I changed the
relevant parts to use `long` instead, avoiding further problems with large
files.

[maven]: https://maven.apache.org/

As I write this `warccollres` is still running on a large amount of data, so I
can't truly evaluate the capabilities of `warcrefs`. I did test it on a small
archive which had some duplication and it was successful (verified by manual
inspection[^zless]).

[^zless]: WARC files are mostly plain text with possibly-binary network traffic
          in between, so it's relatively easy to browse them with tools like
          [zless][zless-man] and verify everything looks correct. It's quite convenient,
          really.

[zless-man]: http://man.he.net/man1/zless

### `warcrefs` revisited

I'm writing this section after the above-mentioned run of `warccollres`
finished and I got to run `warcrefs` over about 30 gigabytes of data. It turned
out a few additional changes were required.

1. I forgot to recompile the jar after changing its use of file offsets to use
   `long`s, at which point I found the error reporting was awful in that the
   program only printed the error message and nothing else. It bailed out on
   reaching a file offset not representable as an int, but I couldn't tell that
   until I made it print a proper stack trace.
2. Portions of `revisit` records were processed as strings but have lengths in
   bytes. Where multibyte characters are used this yields a wrong size.
   Fortunately, the WARC library used to write output checks these so I just had to
   fix it to use byte lengths everywhere.
3. Reading records to deduplicate reopened the input file for every record and
   never closed them, causing the program to eventually reach the system open
   file limit and fail. I had to make it close those.

## Results

I got surprisingly good savings out of deduplication on my initial large
dataset. Turns out web browser history has a lot more duplication than a typical
archive: about 50% on my data, where Eldakar cited a number closer to 15% for
general archives.

```
$ ls -lh
total 47G
-rw-r--r-- 1 tari users  14G Jan 18 15:07 mega_dedup.warc.gz
-rw-r--r-- 1 tari users  33G Jan 17 10:45 mega.warc.gz
-rw-r--r-- 1 tari users 275M Jan 17 11:39 mega.warcsum
-rw-r--r-- 1 tari users 415M Jan 18 13:50 warccollres.txt
```

The input file was 33 gigabytes, reduced to only 14 after deduplication. I've
manually checked that all the records appear to be there, so that appears to be
true deduplication only. There are 1709118 response records in the archive
(that's the number of lines in the warcsum file), with only 210467 unique
responses[^copynum], making an average of about 8 copies per response. Perhaps
predictably, this implies that the duplicated records tend to be small since
the overall savings was much less than 8 times.

[^copynum]: `SELECT count(id) FROM warcsums WHERE copy_num = 1`

## Improvements

At this point deduplication is not a very automated process, since there are
three different programs involved and a database must be set up. This would be
relatively easy to script, but it hasn't yet seen enough use for me to be
confident in its ability to run unattended.

There are some inefficiencies, especially in `warccollres.py` which decompresses
records in their entirety into memory (where it could stream them or back them
with real files to reduce memory requirements for large records). It also
requires that there be only one WARC file under consideration, which was a
concession to simplicity of implementation.

---

In the downloading process, I found that it will sometimes get hung up on
streams, particularly streaming audio like [Hutton Orbital Radio][hutton] where
the actual stream URL appears in browser history. The result of that kind of
thing is downloading a "file" of unbounded size at a rather low speed (since
it's delivered only as fast as the audio will be played back).

[wpull][wpull] is a useful tool to replace wget with (that is also mostly
compatible, for convenience) which can help address these issues. It supports
custom scripts to control its operation in a more fine-grained way, which would
probably permit detection of streams so they don't get downloaded.  Also
attractive is wpull's support for running Javascript in downloaded pages, which
allows it to capture data that is not served "baked in" to a web page as is
often the case on modern web sites, especially "social" ones.

[hutton]: http://huttonorbital.com/HuttonOrbitalRadio.aspx
[wpull]: https://github.com/chfoo/wpull

## Concluding

I ended up spending the majority of a weekend hammering out most of this code,
from about 11:00 on Saturday through about 18:00 on Sunday with only about an
hour total for food-breaks and a too-much-yet-not-enough 6-hour pause to sleep.
I might not call it pleasant, but it's a good feeling to build something like
this successfully and before losing interest in it for an indeterminate amount
of time.

I have long-term plans regarding software to automate archiving tasks like this
one, and that was where my work here started early on Saturday. I'd hope that
future manic chunks of time like this one will lead to further progress on that
concept, but personal history says this kind of incredibly-productive block of
time occurs at most a few times a year, and the target of my concentration is
unpredictable[^manic].
Call it a goal to work toward, maybe: the ability to work on archiving as an
occupation, rather than a sadly neglected hobby.

In any case, if you missed it, the collection of code I put together for
deduplication is available on [Bitbucket][optiwarc-bb]. The history-gathering
portions I use are basically exactly as described in the relevant sections,
leaving a lot of room for future improvement. Thanks for reading if you've come
this far, and I hope you find my work useful!

[optiwarc-bb]: https://bitbucket.org/tari/optiwarc

[^manic]: In fact, the last time I did something like this I (re)wrote a large
          amount of chat infrastructure which I still have yet to finish writing up for
          this blog.
