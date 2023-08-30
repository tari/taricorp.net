---
title: Improved timelapse video processing
slug: overlay-framedrop-tricks
date: 2023-08-30T05:58:37.811Z
---
Using the `ffmpeg`'s overlay filter is a handy trick.

The important thing is that the `overlay` filter attempts to align its inputs to the same presentation timestamp (PTS); that is, the instant from the start of the video at which a given frame is to be displayed. Although this behavior is not obvious, the documentation provides a few hints:

> It takes two inputs and has one output. The first input is the "main" video on which the second input is overlaid.
>
> This filter also supports the framesync options.
>
> Be aware that frames are taken from each input video in timestamp order, hence, if their initial timestamps differ, it is a good idea to pass the two inputs through a setpts=PTS-STARTPTS filter to have them begin in the same zero timestamp, as the example for the *movie* filter does.

This wording seems to imply that the PTS of each frame from the "main" input to the `overlay` filter is will be the PTS of the output frame as well, and the other input will attempt to match that PTS from the other stream in order to select an appropriate frame.

Taking that logic to the meaninful conclusion, if the "main" input to an `overlay` drops frames without modifying their PTS and the other input to the filter has the same frame timing, then the overlaid image (from the second input) will skip the same frames as the main input.

What this means is that `overlay` allows processing of frames to split, with one branch doing some filtering to determine which frame should be kept and which should be retained, while the final output can be a copy of the input by passing through the original input as the second input to the `overlay`. This may be easier to understand with a diagrammed example:

{% figure src="overlay-sample.drawio.svg" caption="Input frames are split (copied) to:

1. A filter sequence that converts to monochrome then discards some of the frames based on the monochrome result
2. Do nothing (no-op)

The first branch is the used as the main input to an overlay in order to set the desired output PTS, but because the second branch (as a copy of the input) is fully opaque the result is to only select the input frames that were not dropped by the filters on the first branch.
" %}

The result of this has the same duration as the original input video, but fewer frames because the PTS of each output frame is retained. The `setpts` filter can fix this.

It also has a problem with being longer than intended, because `overlay` by default repeats the last frame in the shorter of its inputs until both end: if any frames at the end of the input are dropped on the first branch, they'll still be taken from the second. Setting `shortest=1` makes it stop when either stream ends, which is correct for this application.

TODO: make some short examples with testsrc and simple filtering. Captioned with the filter chain used.