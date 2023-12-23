---
title: "Video Squisher: minimal command-line processing on the web"
slug: video-squisher
date: 2023-12-23T09:47:06.970Z
---
I've recently been asked to reduce the size of video files with some regularity, taking in a video file and generating something with reduced file size. This is an easy task to accomplish with [Handbrake](https://handbrake.fr/), and since the transcodes I was asked to do were consistent in their needs, I was able to set up a preset in Handbrake to make these conversions very simple.

Unfortunately, there were a few steps that weren't as easy to automate: namely, grabbing the original video and sharing the transcoded version later. Rather than need to do anything myself for each video, I sought to make my process available for "self-service", probably as some kind of web-based tool instead. Since the imposition of receiving a file, running it through Handbrake, and sharing the result is fairly small though, I wanted to make this tool as simple as possible. I believe I succeeded, and that the results are interesting enough to share because I discovered a few new tricks that made it easier.

<!--more-->