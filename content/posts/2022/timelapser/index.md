---
title: Efficiently Capturing Time-Lapse video with a Raspberry Pi
slug: timelapser
draft: true
date: 2022-07-25T00:41:48.799Z
---
Earlier this year, I had a desire to capture time-lapse video of some construction that would take an unknown amount of time and occurred mostly during short periods of activity separated by intervals of inactivity with varying time. Because the overall recording time was unknown, this represented an interesting set of challenges that I wrote some software to address, using a Raspberry Pi and a USB webcam.

## Existing options

There is no shortage of articles around the web describing how to capture time lapse videos with a Raspberry Pi, such as [Caroline Dunn's article in Tom's Hardware](https://www.tomshardware.com/how-to/raspberry-pi-time-lapse-video). I find that most of these involve some kind of script to take still images at intervals, and another component (usually using ffmpeg) to combine those images into a video.

Although this approach works fine, it suffers from several obvious shortcomings:
 * Frames stored as individual image files tend to require much more space to store them than an equivalent video file, since each frame will usually be very similar to the preceding ones: video codecs are designed to take advantage of this redundancy.
 * Captured images and generated videos must be manually retrieved (or deleted) on capture completion. For long captures or when generating multiple sequences, this may require regular human intervention to ensure the system is still running and storage is still available.

Since the events I wished to capture would take an unknown amount of time (possibly months), it was important to me that the system should be reliable and not require regular (manual) maintenance as well as not use more storage space than necessary. To that end, I chose to write my own set of scripts that is described by the rest of this article.

### Available hardware

The hardware I had available amounted to a Raspberry Pi 2 (and a USB WiFi adapter) with 32GB microSD card as boot volume, a Logitech C925e USB webcam, and extension cords and power supply suitable to place the system wherever I needed. The Pi 2 is a rather dated and slow machine by now, but ought to be sufficient for this application.

## Video capture

The Logitech C925e advertises support for 1080p video at 30 frames per second, which is a much higher framerate than I need for time-lapse video capture (around one frame per second seems fine) but a respectable resolution. Investigating the camera's actual capabilities shows it's actually capable of higher resolution than that:

```
$ ffmpeg -f v4l2 -list_formats all -i /dev/video0
[video4linux2,v4l2 @ 0x1083cd0] Raw       :     yuyv422 :           YUYV 4:2:2 : 640x480 160x90 160x120 176x144 320x180 320x240 352x288 432x240 640x360 800x448 800x600 864x480 960x720 1024x576 1280x720 1600x896 1920x1080 2304x1296 2304x1536
[video4linux2,v4l2 @ 0x1083cd0] Compressed:       mjpeg :          Motion-JPEG : 640x480 160x90 160x120 176x144 320x180 320x240 352x288 432x240 640x360 800x448 800x600 864x480 960x720 1024x576 1280x720 1600x896 1920x1080
```

This output indicates that the camera supports output as either raw video or Motion JPEG in a variety of resolutions up to 1920x1080 pixels. Raw video can also be output at higher resolutions up to 2304x1536, but at a lower framerate (around 12 fps, it turns out). Since I didn't care about any framerate higher than about 1 fps, it was a logical choice to run at that higher resolution.

---

The basic use of ffmpeg for this application uses a V4L2 device as input (the webcam) and outputs at a very low framerate to `timelapse.mp4`:

```
ffmpeg -i v4l2 -video_size 2304x1536 -i /dev/video0 \
    -vf fps=0.1 -t 60 timelapse.mp4
```

In this instance I've captured video at one frame per 10 seconds (`vf fps=0.1`) and chosen to capture one minute of video (`-t 60`). In the final script these are configurable, but this illustrates the concept nicely.

Although the required framerate for video encoding is low in this application, video encode performance remains a concern because the Raspberry Pi 2 is not a very powerful computer. I wanted to use a video codec that achieves good compression, and it needed to do so with enough speed that frames can be encoded at least as frequently as they are captured.

Some versions of the Raspberry Pi support hardware-accelerated H.264 encoding (in a quick search, it's unclear if that includes the Pi 2), but I didn't try to make that work: there doesn't seem to be support for the relevant hardware in ffmpeg so I would have needed to use some other software to do the encoding, and it's unclear what the hardware encoder's limitations are (such as maximum resolution). I instead did some manual experimentation by doing a live video capture with assorted codecs:

 * [H.264](https://www.videolan.org/developers/x264.html) (`x264`)
 * [VP8](https://datatracker.ietf.org/doc/html/rfc6386) (`libvpx`)
 * [H.265](https://www.videolan.org/developers/x265.html) (`x265`)
 * [VP9](https://www.webmproject.org/vp9/) (`libvpx-vp9`)

VP9 and H.265 are attractive choices because they are very good at efficiently compressing video, but I found performance to be too bad to be usable for this application (achieving less than 1 frame per second at the target resolution). Both x264 and VP8 perform acceptably and achieve similar compression, so I opted to use VP8 since it's not legally encumbered by any patent licensing requirements (unlike H.264).

I somewhat arbitrarily chose a maximum bitrate of 20 megabits per second and [CRF](https://trac.ffmpeg.org/wiki/Encode/VP8) of 4 to achieve a high-quality encode, and ended up with this `ffmpeg` invocation:

```
ffmpeg -i v4l2 -video_size 2304x1536 -i /dev/video0 \
    -an -c:v libvpx -b:v 20M -crf 4 \
    -vf fps=0.1 -t 60 timelapse.mp4
```

---

With a way to use ffmpeg to capture video directly (no intermediate video files!), we can move to thinking about where video will be stored.

## Storage considerations

As mentioned earlier, I only have a 32GB SD card at hand for this Raspberry Pi, and I don't trust it not to corrupt data without warning (both the Pi itself and the card; I don't really trust either with my data) so it seemed important to ensure that the Pi's local storage would not fill up with video and prevent further recording, as well as to copy data off the Pi shortly after its creation. I chose to address this by having the system upload video to Google Cloud Storage (GCS). There's nothing particularly special about GCS over one of the many other online object storage systems available; it was just convenient for me to use.

I didn't want to completely clean up video periodically in case of an upload failure, and it's useful to get more frequent feedback on how video capture is going in the form of segments that can be viewed immediately so I also wanted to have the system incrementally upload video as it is captured rather than uploading larger chunks at long intervals (say, every day). Incremental upload also helps reduce the bandwidth needs of the system, since the total data transfer is spread over a longer interval.

As discussed [above](#video-capture), by capturing video at a low frame rate rather than individual images at the same rate we can save storage space, improve picture quality, or possibly both. Incrementally uploading video files is somewhat more challenging than handling a similar collection of still images however, since still images have a convenient 1:1 relation to the captured frames (so it's easy to assume that a file's existence implies a complete frame) whereas video files become larger over time as frames are added.

### Incremental upload

To incrementally upload video, we need to choose a container that remains valid when more data is appended to it, then design a method to efficiently append new data to what's already present in remote storage.

#### Container choice

ISO MPEG-4 containers (`.mp4` files) are a common choice for video files and are supported by most software. However this container is not very well-suited to this application because by default some metadata (the `MOOV` atom) gets placed at the end of the file. ffmpeg can put that at the beginning of a file to make a file "streamable" by using the `-movflags faststart` option, but that doesn't really solve the live capture problem because the metadata stored in the `MOOV` atom that the `faststart` option moves around needs to be derived from the entire encoded file: ffmpeg implements `faststart` simply by outputting a file, then moving the `MOOV` block to the front beginning while copying the rest of the file. Since this requires the entire input be available first, it is not appropriate for a pseudo-live stream.

The [Matroska](https://www.matroska.org/index.html) container (`.mkv`, and also conventionally used for `webm`) on the other hand turns out to work well for this application: I found that ffmpeg does update some headers at the beginning of a Matroska file when it stops encoding (similar to what it does for mp4 fast start), but the fields that get populated are not required to decode the video: they appear to only contain things like the total video length, which decoders do not require. In some experiments, I found that other programs were happy to play back a Matroska video that I had copied while ffmpeg was encoding it, even when capturing live video without a defined duration; they simply stopped playback on reaching the end of the data. In some situations players failed to report the overall video length or showed a wrong duration when asked to decode such a truncated file, but they were still able to play back everything that was present.

#### gcs-incremental

Recalling that I chose to use Google Cloud Storage to store captured video, [`gsutil`](https://cloud.google.com/storage/docs/gsutil) is a convenient way to interface with storage from shell scripts. Since `ffmpeg` is also easily driven from a shell script, the default choice for implementing the entire system was also shell, rather than some other (perhaps less quirky) programming language.

To implement incremental upload of files, the general algorithm for copying a 'source' file on the local system to a 'destination' file on remote storage can be expressed as (assuming as we established in the previous section that files are only appended to):

1. Check whether `destination file` exists
   * If no, copy entire `source file` to `destination file` and exit
2. Get size of `destination file`
   * If same size as `source file`, do nothing and exit
3. Append bytes from `source file` starting at offset `remote size` to `destination file`

Somewhat problematically, in most object storage systems like Google Cloud Storage, "objects" (files in our abstraction) are immutable: it is not possible to modify an object in place. Making changes to an existing object will then usually involve making a copy of the object with the changes applied, and doing so is most obviously implemented by downloading the original and making changes, then uploading the changed version (possibly replacing the original object).

It should be obvious that appending to a file stored on GCS by downloading it and re-uploading doesn't achieve the goal of incremental upload, since in that case we could simply upload the entire local file. Fortunately, it's possible to ["compose" an object from multiple pieces](https://cloud.google.com/storage/docs/composite-objects): given two objects, `gsutil compose` can be used to concatenate them into a single object without making a copy of either. With that operation, appending to a file for incremental upload is simply a matter of uploading the new data as a new object, then performing a `compose` operation to add it to the original object.

---

The following shell script implements this incremental upload; I call it `gcs-incremental`. When passed the path to a local file and a location on Cloud Storage, it implements the algorithm described above.

```sh
#!/bin/bash -e

SOURCE_FILE="$1"
GS_PATH="$2"
DEST_FILE="${GS_PATH}/$(basename "${SOURCE_FILE}")"

info() {
  echo "$@" >&2
}

if ! gsutil -q stat "${DEST_FILE}"; then
  info "${DEST_FILE} does not exist; uploading entire file"
  gsutil cp "${SOURCE_FILE}" "${DEST_FILE}"
else
  SOURCE_SIZE=$(stat --format=%s "$SOURCE_FILE")
  DEST_SIZE=$(gsutil stat "${DEST_FILE}" | awk '$1 == "Content-Length:" { print $2 }' || echo 0)
  TO_UPLOAD_SIZE=$(("${SOURCE_SIZE}" - "${DEST_SIZE}"))
  PART_FILE="${DEST_FILE}.part.${SOURCE_SIZE}"

  if [ "${TO_UPLOAD_SIZE}" = 0 ]; then
    info "Nothing to upload; stopping"
    exit 0
  fi
  info "Uploading ${TO_UPLOAD_SIZE} bytes.."

  dd if="${SOURCE_FILE}" skip="${DEST_SIZE}" count="${TO_UPLOAD_SIZE}" iflag=skip_bytes,count_bytes \
    | gsutil -q cp - "${PART_FILE}"
  gsutil compose "${DEST_FILE}" "${PART_FILE}" "${DEST_FILE}"
  gsutil rm "${PART_FILE}"
  fallocate --punch-hole --offset 0 --length "${SOURCE_SIZE}" "${SOURCE_FILE}"
fi
```

There are several aspects of this implementation worth noting:
 * Getting the size of a file on GCS is slightly tricky because `gsutil stat` prints file properties like HTTP headers. It's not too hard to extract a number with `awk`.
 * `gsutil` doesn't provide a way to select only part of a file to upload, so we use `dd` to read part of the file and pipe the data to `gsutil`. Use of a pipe prevents [parallelization of the upload](https://cloud.google.com/storage/docs/parallel-composite-uploads) so performance is limited somewhat.
 * In order to compose the old and new file parts, we need to write a temporary file. This script assumes that a suffix of `.part` and an integer is sufficiently unique to avoid potential conflicts, but it would probably misbehave if multiple uploaders were trying to update the same file.
 * After a chunk of a file is uploaded, that data is **erased from the local disk** by using `fallocate` to punch a hole in the file, replacing all of the data that's been uploaded with zeroes and freeing any space on disk that it used.

The hole-punching in the source file is what allows the overall time-lapse capture system to assume that the amount of storage available is not a concern. Files that have been uploaded will remain on disk but consume essentially no space while retaining their original size, making it easy to tell whether a file has been uploaded in its entirety even after the fact. Failed uploads may cause increased disk usage (because holes will not be punched), but no loss of data so they can be retried later.

Having implemented mechanisms to capture video (easily done with `ffmpeg`) and to incrementally upload those videos to GCS (`gcs-incremental`), what remains is to combine them into something that will capture video and incrementally upload it.

## `timelapser`