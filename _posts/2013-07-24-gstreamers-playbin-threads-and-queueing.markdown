---
author: tari
comments: true
date: 2013-07-24 02:54:09+00:00
layout: post
slug: gstreamers-playbin-threads-and-queueing
title: GStreamer's playbin, threads and queueing
wordpress_id: 988
categories:
- Linux
- Software
post_format:
- Aside
tags:
- gstreamer
- playbin
- playbin2
- python
- queue
- uri
---

I've been working on a project that uses GStreamer to play back audio files in
an automatically-determined order. My implementation uses a
[playbin](http://gstreamer.freedesktop.org/data/doc/gstreamer/0.10.36/gst-plugins-base-plugins/html/gst-plugins-base-plugins-playbin2.html),
which is nice and easy to use. I had some issues getting it to continue playback
on reaching the end of a file, though.

According to the documentation for the about-to-finish signal,

> This signal is emitted when the current uri is about to finish. You can set
> the uri and suburi to make sure that playback continues.
> 
> This signal is emitted from the context of a GStreamer streaming
> thread.

Because I wanted to avoid blocking a streaming thread under the theory that
doing so might interrupt playback (the logic in determining what to play next
hits external resources so may take some time), my program simply forwarded that
message out to be handled in the application's main thread by posting a message
to the pipeline's bus.

Now, this approach appeared to work, except it didn't start playing the next
URI, and the pipeline never changed state- it was simply wedged. Turns out that
you **must assign to the uri property from the same thread**, otherwise it
doesn't do anything.

Fortunately, it turns out that blocking that streaming thread while waiting for
data isn't an issue (determined by experiment by simply blocking the thread for
a while before setting the uri).
