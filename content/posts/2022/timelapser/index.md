---
title: Efficiently Capturing Time-Lapse video with a Raspberry Pi
slug: timelapser
draft: true
date: 2022-07-25T00:41:48.799Z
---
Earlier this year, I had a desire to capture time-lapse video of some construction that would take an unknown amount of time and occurred mostly during short periods of activity separated by intervals of inactivity with varying time. Because the overall recording time was unknown, this represented an interesting set of challenges that I wrote some software to address, using a Raspberry Pi and a USB webcam.

## Needs and existing options

## Chosen configuration



### Capture properties

The camera I had available for this is a Logitech C925e that advertises support for 1080p video at 30 frames per second, which is a much higher framerate than I need for this application but a respectable resolution. Investigating the camera's actual capabilities shows it's actually capable of higher resolution than that:

```
$ ffmpeg -f v4l2 -list_formats all -i /dev/video0
[video4linux2,v4l2 @ 0x1083cd0] Raw       :     yuyv422 :           YUYV 4:2:2 : 640x480 160x90 160x120 176x144 320x180 320x240 352x288 432x240 640x360 800x448 800x600 864x480 960x720 1024x576 1280x720 1600x896 1920x1080 2304x1296 2304x1536
[video4linux2,v4l2 @ 0x1083cd0] Compressed:       mjpeg :          Motion-JPEG : 640x480 160x90 160x120 176x144 320x180 320x240 352x288 432x240 640x360 800x448 800x600 864x480 960x720 1024x576 1280x720 1600x896 1920x1080
```

This output indicates that the camera supports output as either raw video or Motion JPEG in a variety of resolutions up to 1920x1080 pixels. Raw video can also be output at higher resolutions up to 2304x1536, but at a lower framerate (around 12 fps). Since I didn't care about any framerate higher than about 1 fps, it was a logical choice to run a a higher resolution.

### Storage considerations

I only have a 32GB SD card handy for the machine, and I don't trust it not to corrupt data without warning so it seemed important to ensure that the Pi's local storage would not fill up with video and prevent further recording.

I chose to address this by having the system upload video to Google Cloud Storage (but many other systems could be integrated similarly).

I didn't want to completely clean up video periodically in case of an upload failure, and it's useful to get more frequent feedback on how video capture is going in the form of segments that can be viewed immediately so I also chose to have the system incrementally upload  video as it is captured rather than uploading larger chunks at long intervals (say, every day). Incremental upload also helps reduce the bandwidth needs of the system, since the total data transfer is spread over a longer interval.

Most descriptions of time lapse video capture that I've seen (such as https://www.tomshardware.com/how-to/raspberry-pi-time-lapse-video) take a still frame at intervals and later combine those frames into a video. Although this works, it's fairly costly in terms of storage because each frame tends to be mostly similar to the ones before it: this is exactly the sort of characteristic that video codecs are designed to take advantage of.

By capturing video at a low frame rate rather than individual images at the same rate we can save storage space, improve picture quality, or possibly both. Incrementally uploading video files is somewhat more challenging however, since still images have a convenient 1:1 relation to the captured frames whereas video files become larger over time as frames are added.

### Codec choice

Because I was using a Raspberry Pi 2 ... video encode performance was important: I didn't want to spend more storage on video than was necessary, but the relatively slow processor in the Pi implies that a sophisticated video codec may not be usable.

Some versions of the Raspberry Pi support hardware-accelerated H.264 encoding, but I didn't try to make that work.

The basic use of ffmpeg for this application uses a V4L2 device as input and outputs at a very low framerate:

```
ffmpeg -i v4l2 -video_size 2304x1536 -i /dev/video0 \
    -vf fps=0.1 -t 60
```

In this instance I've captured video at one frame per 10 seconds (`vf fps=0.1`) and chosen to capture one minute of video (`t 60`).

### Incremental upload

To incrementally upload video, we need to choose a container that remains valid when more data is appended to it.

ISO MPEG-4 containers (`.mp4` files) aren't as well-suited because by default some metadata gets placed at the end of the file. ffmpeg can put that at the beginning of a file to make a "streamable" by using the `-movflags faststart` option, but that doesn't really solve the live capture problem because the metadata stored in the `MOOV` atom that the `faststart` option moves around needs to be derived from the entire encoded file (and fmpeg implements `faststart` simply by outputting a file, then moving the metadata to the front while copying the rest of the file: not appropriate for a pseudo-live stream.

The Matroska container (`.mkv`) on the other hand turns out to work well for this application: I found that ffmpeg does update some headers at the beginning of a file when it stops encoding, but the fields that get populated are not required to decode the video. They appear to only contain things like the total video length, which decoders do not require. In some experiments, I found that other programs were happy to play back a Matroska video that I had copied while ffmpeg was encoding it, even when capturing live video without a defined duration.