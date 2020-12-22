---
title: Web video with alpha channels
slug: web-video-alpha
draft: true
date: 2020-12-22T06:00:38.000Z
---
Today I had a little puzzle to solve regarding support for transparent video (videos with an alpha channel) on the web. I wanted to replace a "snow" effect implemented as very CPU-intensive CSS animations (three background images with their location animated) with a video. The actual implementation looked something like this:

```html
<style>
.snow_overlay {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
}
</style>
<div>
    Stuff goes here.
    <div class="snow_overlay"></div>
</div>
```

The style for the `snow_overlay` element causes it to fill its entire parent element and sit on top; so as long as whatever goes in that element is transparent then it effectively applies an effect to the container. This is easy to do with background images, but they [can't be efficiently animated and tiled at the same time](https://www.html5rocks.com/en/tutorials/speed/high-performance-animations/) to create the illusion of a moving infinite field (like of falling snow).

Check ffmpeg codec support:

ffmpeg -h encoder=apng

 * webm with vp9 works well, supports yuva420p. Apple software doesn't support vp9
 * png can be put in mp4/mov and support rgba or ya8, but browsers don't support png-in-mp4
 * apng supports the same alpha channels as png and is well supported, but alpha seems weird?

ffmpeg -i foo.webm -pix_fmt rgba foo.apng

The output apng seems totally white, but that might be an issue with coming from webm. Should try to generate from the source images.