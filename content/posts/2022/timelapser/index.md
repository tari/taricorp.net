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

VP9 and H.265 are attractive choices because they are very good at efficiently compressing video, but I found performance to be too bad to be usable for this application (achieving less than 0.1 frames per second at the target resolution). Both x264 and VP8 perform acceptably and achieve similar compression, so I opted to use VP8 since it's not legally encumbered by any patent licensing requirements (unlike H.264).

I somewhat arbitrarily chose a maximum bitrate of 20 megabits per second and [CRF](https://trac.ffmpeg.org/wiki/Encode/VP8) of 4 to achieve a high-quality encode, and ended up with this `ffmpeg` invocation:

```
ffmpeg -i v4l2 -video_size 2304x1536 -i /dev/video0 \
    -an -c:v libvpx -b:v 20M -crf 4 \
    -vf fps=0.1 -t 60 timelapse.mp4
```

---

With a way to use ffmpeg to capture time-lapse video directly (no intermediate image files!), we can move to thinking about where video will be stored.

## Storage considerations

As mentioned earlier, I only have a 32GB SD card at hand for this Raspberry Pi, and I don't trust it not to corrupt data without warning (both the Pi itself and the card; I don't really trust either with my data) so it seemed important to ensure that the Pi's local storage would not fill up with video and prevent further recording, as well as to copy data off the Pi shortly after its creation. I chose to address this by having the system upload video to Google Cloud Storage (GCS). There's nothing particularly special about GCS over one of the many other object storage systems available from many different service providers; it was just convenient for me to use GCS.

I didn't want to completely clean up video periodically (by deleting old files) in case of an upload failure, and it's useful to get more frequent feedback on how video capture is going in the form of segments that can be viewed immediately so I also wanted to have the system incrementally upload video as it is captured rather than uploading larger chunks at long intervals (say, every day). Incremental upload also helps reduce the bandwidth needs of the system, since the total data transfer is spread over a longer interval.

As discussed [above](#video-capture), by capturing video at a low frame rate rather than individual images at the same rate we can save storage space, improve picture quality, or possibly both. Incrementally uploading video files is somewhat more challenging than handling a similar collection of still images however, since still images have a convenient 1:1 relation to the captured frames (so it's easy to assume that a file's existence implies a complete frame) whereas video files become larger over time as frames are added.

### Incremental upload

To incrementally upload video, we need to choose a container that remains valid when more data is appended to it, then design a method to efficiently append new data to what's already present in remote storage.

#### Container choice

ISO MPEG-4 containers (`.mp4` files) are a common choice for video files and are supported by most software. However this container is not very well-suited to this application because by default some metadata (the `MOOV` atom) gets placed at the end of the file. ffmpeg can put that at the beginning of a file to make a file "streamable" by using the `-movflags faststart` option, but that doesn't really solve the live capture problem because the metadata stored in the `MOOV` atom that the `faststart` option moves around needs to be derived from the entire encoded file: ffmpeg implements `faststart` simply by outputting a file, then moving the `MOOV` block to the beginning and copying the rest of the file to follow it. Since this requires the entire input be available first, it is not appropriate for a pseudo-live stream.

The [Matroska](https://www.matroska.org/index.html) container (`.mkv`, and also conventionally used for `webm`) on the other hand turns out to work well for this application: I found that ffmpeg does update some headers at the beginning of a Matroska file when it stops encoding (similar to what it does for mp4 fast start), but the fields that get populated are not required to decode the video: they appear to only contain things like the total video length, which decoders do not require. In some experiments, I found that other programs were happy to play back a Matroska video that I had copied while ffmpeg was encoding it, even when capturing live video without a defined duration; they simply stopped playback on reaching the end of the data. In some situations players failed to report the overall video length or showed a wrong duration when asked to decode such a truncated file, but they were still able to play back everything that was present.

#### gcs-incremental

Recalling that I chose to use Google Cloud Storage to store captured video, [`gsutil`](https://cloud.google.com/storage/docs/gsutil) is a convenient way to interface with the object storage system from shell scripts. Since `ffmpeg` is also easily driven from a shell script, the default choice for implementing the entire system was also shell, rather than some other (perhaps less quirky) programming language.

To implement incremental upload of files, the general algorithm for copying a 'source' file on the local system to a 'destination' file on remote storage can be expressed as follows (assuming, as we established in the previous section, that files are only appended to):

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
 * Getting the size of a file on GCS is slightly tricky because `gsutil stat` prints file properties in a format similar to HTTP headers. It's not too hard to extract a number with `awk`.
 * `gsutil` doesn't provide a way to select only part of a file to upload, so we use `dd` to read part of the file and pipe the data to `gsutil`. Use of a pipe prevents [parallelization of the upload](https://cloud.google.com/storage/docs/parallel-composite-uploads) so performance is limited somewhat.
 * In order to compose the old and new file parts, we need to write a temporary file. This script assumes that a suffix of `.part` and an integer is sufficiently unique to avoid potential conflicts, but it would probably misbehave if multiple uploaders were trying to update the same file.
 * After a chunk of a file is uploaded, that data is **erased from the local disk** by using `fallocate` to punch a hole in the file, replacing all of the data that's been uploaded with zeroes and freeing any space on disk that it used.

The hole-punching in the source file is what allows the overall time-lapse capture system to assume that the amount of storage available is not a concern. Files that have been uploaded will remain on disk but consume essentially no space while retaining their original size, making it easy to tell whether a file has been uploaded in its entirety even after the fact. Failed uploads may cause increased disk usage (because holes will not be punched), but no loss of data so they can be retried later.

Having implemented mechanisms to capture video (easily done with `ffmpeg`) and to incrementally upload those videos to GCS (`gcs-incremental`), what remains is to combine them into something that will capture video and incrementally upload it.

## `timelapser`

Putting everything together into one script, the intended function can be summarized as follows:

 * Capture video with ffmpeg for a chosen duration
   * In a loop, run `ffmpeg` and emit to a file with a chosen name with capture duration set to `total duration` - `elapsed duration`
   * After the specified time is elapsed, ensure videos are uploaded and exit
 * Periodically do an incremental upload of captured video files, stopping once video capture ends

### Capture task

The video capture itself is fairly easy to write. Assuming a few variables specifying things like how long to capture for, what video device to use as input, and what framerate to output, I ended up with these shell functions:

```sh
now() {
  date +%s
}

run_capture() {
  local framerate=$(echo "scale=4;1/${SECONDS_PER_FRAME}" | bc)
  local i=0
  local current_time=$(now)
  local end_time=$((${current_time} + (${RUNTIME_MINUTES} * 60)))

  # Run ffmpeg in a loop in case of premature exit/failure, targeting
  # one segment that goes until the end time.
  echo "Starting capture for ${RUNTIME_MINUTES} minutes, until timestamp ${end_time}"
  while [ ${current_time} -lt ${end_time} ]
  do
    ffmpeg -n -loglevel error \
      -f v4l2 -video_size "${VIDEO_RESOLUTION}" -i "${VIDEO_DEVICE}" \
      -t $((${end_time} - ${current_time})) \
      -vf fps="${framerate}" -an -c:v libvpx -b:v 20M -crf 4 "${i}.mkv"
    # Increment file serial number to avoid overwriting old data
    let i=i+1
    current_time=$(now)
  done
}

echo "Running for $RUNTIME_MINUTES minutes"

run_capture & capture_pid=$!
```

`now` provides the current UNIX time, which is convenient for computing the total amount of time capture has been running. `run_capture` assumes its working directory is appropriate for storing video and captures a sequence of files `0.mkv`, `1.mkv` and so forth. Capturing a sequence of files ensures that if some transient error occurs (perhaps if the camera is accidentally unplugged) capture will resume without overwriting any older data.

Because the script needs to also run periodic uploads, `run_capture` is started in the background and its PID is saved so its status can be polled later, in particular for checking whether it has completed and exited.

### Upload task

Periodically doing an incremental upload is slightly more interesting, because I wanted to upload video parts at a regular cadence without any particular dependence on how long the upload takes. A naive version might implement a simple algorithm:

1. Wait for `interval`
2. Do incremental upload
3. If capture is still running, goto 1

If it takes any meaningful amount of time to perform the upload however, the uploads will be separated by the chosen interval and occur less frequently than intended. This is probably actually fine, but I chose to get clever with it to achieve a regular cadence.

### Queueing

If uploads should occur at intervals without regard for how long they take to complete, this implies there must be two concurrent processes: one that waits for intervals to expire (the "timer" task) and another that actually does the upload (the "uploader" task). This becomes difficult when we recall that `gcs-incremental` cannot be expected to work correctly if invoked in parallel, since this implies there must be some mechanism to synchronize uploads both between incremental uploads and the final upload that runs once capture completes.

A reasonably simple approach to this problem in more capable (than shell scripting) programming languages is to use a multi-producer queue: the uploader task can pull upload jobs out of a queue and execute them serially, while the timer and capture tasks place new jobs into the queue as appropriate (at intervals and once capture completes, respectively).

In a shell script, I realized it's possible to implement a queue with a pipe: if the receiver reads lines from a pipe in a loop until closed, other tasks can write lines to the pipe which will be processed in sequence. I ended up with this code for the receiver:

```sh
segment_uploader() {
  while read n; do
    echo Segment trigger "$n"
    for f in *.mkv; do
      info "Do incremental upload of file $f"
      gcs-incremental "$f" "${GS_PATH}"
    done
    info "Segment upload completed (for now)"
  done
}

# Run another task to scan and upload segments, which we signal by sending
# a message through a named pipe.
msgpipe=$(mktemp -u)
mkfifo -m 600 "${msgpipe}"
# Run a task that does nothing but holds the pipe open; killing this
# pipe holder will terminate the uploader when it reaches EOF (having processed
# anything that was already put into the FIFO).
sleep infinity >"${msgpipe}" & pipe_holder_pid=$!
segment_uploader <"${msgpipe}" & uploader_pid=$!

trigger_upload() {
  now > "${msgpipe}"
}
```

We create a named pipe `msgpipe` and direct data from that pipe to the input of `segment_uploader`. The `while read n` loop will read lines from the input and stop once the input is closed, running `gcs-incremental` over all of the video files in its working directory.[^pipe-filenames] Invoking the `trigger_upload` function will queue uploads of all current files.

[^pipe-filenames]: I notice while writing this that the uploader task could be made more efficient by receiving the name of a file to upload rather than a string that is otherwise ignored, which would allow it to inspect only the relevant file rather than all those that exist.

The `pipe_holder` is an unusual component that is required only as a result of POSIX named pipe semantics: the read end of a pipe is closed once all writers disconnect, which in this application would be after the first segment upload is triggered because `trigger_upload` opens the pipe, writes to it and closes it again. The presence of the `pipe_holder` prevents the uploader task from exiting until the `pipe_holder` itself exits.

---

Because it may be possible for concurrent writes to the pipe to be accidentally interleaved, I forced invocations of `trigger_upload` to be serialized through use of signals:

```sh
interruptible_sleep() {
  # Sleep in the background to make the sleep interruptible; waiting on a
  # foreground process isn't interruptible, but the wait builtin is.
  sleep $@ &
  wait $!
}

trap trigger_upload USR1
{
  while :; do
    interruptible_sleep ${SEGMENTS_INTERVAL}
    kill -USR1 $$ >/dev/null
  done
} & waker_pid=$!
```

The loop represented by `waker_pid` simply waits at intervals and sends `SIGUSR1` to the main script. We `trap` that signal and in response execute `trigger_upload` that writes to the pipe. Reception of this signal can interrupt a `wait` as embodied in the `interruptible_sleep` function and asynchronously trigger an upload, but it is guaranteed by the system (through the general semantics of signals) that only one handler will execute at a time.

### Capture completion

The final piece is to wait for capture to complete and trigger one final upload. Since the PID of the capture task was stored, this is as simple as `wait`ing on it in a loop:

```sh
# Wait for capture to finish
while true; do
  wait ${capture_pid}
  wait_status=$?
  if [ $wait_status -lt 128 ]; then
    echo "capture task exited with status $wait_status"
    break
  fi
done
```

The dance with `wait_status` here is required because `wait` can be interrupted by a signal, and in fact we expect it to be periodically interrupted by a `SIGUSR1` when we want to trigger an upload. In this situation the return code of `wait` is documented to be 128 or greater, so only when the return code is less than 128 is the capture task known to have exited.

Once the capture task exits, all that remains is to clean up and ensure all data has been uploaded:

```sh
# Terminate the waker
kill $waker_pid

# Run a final segment upload
trigger_upload

# Terminate the pipe holder to close the write end of msgpipe; wait for the
# uploader to complete then exit.
kill $pipe_holder_pid
wait $pipe_holder_pid
echo "Waiting up to 1 hour for uploader to finish processing.."
(sleep 1h; kill -HUP $$) & wait $uploader_pid
echo "Done!"
```

We first terminate the waker task to prevent any more uploads from being triggered, and trigger a final upload. Since the capture task has exited by this point, this upload is guaranteed to see all the data that will ever exist.

After triggering the upload we kill the `pipe_holder`, closing the `msgpipe` which will make the uploader exit once it processes everything remaining in the pipe. To avoid waiting forever if there's a problem while uploading, I chose to wait only up to an hour for it to complete before exiting.

## Automation

it's a systemd service + timer, wrapped in a debian package