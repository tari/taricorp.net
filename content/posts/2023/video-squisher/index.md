---
title: "Video Squisher: minimal command-line processing on the web"
slug: video-squisher
date: 2023-12-23T09:47:06.970Z
---
I've recently been asked to reduce the size of video files with some regularity, taking in a video file and generating something with reduced file size. This is an easy task to accomplish with [Handbrake](https://handbrake.fr/), and since the transcodes I was asked to do were consistent in their needs, I was able to set up a preset in Handbrake to make these conversions very simple.

Unfortunately, there were a few steps that weren't as easy to automate: namely, grabbing the original video and sharing the transcoded version later. Rather than need to do anything myself for each video, I sought to make my process available for "self-service", probably as some kind of web-based tool instead. Since the imposition of receiving a file, running it through Handbrake, and sharing the result is fairly small though, I wanted to make this tool as simple as possible. I believe I succeeded, and that the results are interesting enough to share because I discovered a few new tricks that made it easier.

<!--more-->

## Requirements

Since manually processing a few videos is fairly easy, whatever I might build to automate video conversion would also need to be a simple tool requiring little effort to build and run. However, it also needs to be comprehensible to an unsophisticated user so I arrived at these requirements:

 * There must be a single server component with no external dependencies such as a database server.
 * All input and output must occur through a web browser.
 * Video transcoding progress should be reported to the user in real time.

Given I had been using Handbrake to manually transcode videos, I expected that automation of the process would involve running Handbrake's CLI in a subprocess and streaming its console output back to the client.

## Client prototyping: enter SSE

Of the requirements I had set, the goal of reporting real-time progress seemed most challenging so I investigated that first. I fairly quickly stumbled upon a web API that I wasn't familiar with which seemed to meet my needs [Server-sent events](https://en.wikipedia.org/wiki/Server-sent_events) (SSE). This API involves a client making a single HTTP request to a server, which then responds with a stream of events in a structured data format (using content type `text/event-stream`). At a high level, the flow of [using an `EventSource`](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) in a browser is to:

1. Send an HTTP request to a server
2. Handle messages as they are sent from the server. Each message has up to four fields that the client can interpret:
   * `data`: UTF-8 text of arbitrary length.
   * `event`: optional application-defined string identifying what kind of event this is.
   * `id`: optional application-defined ID for a message, allowing the client to resume from the last message it received if the connection is lost by sending a request containing this ID.
   * `retry`: a number indicating how long the server wishes the client to wait before attempting to reconnect, if the connection is lost.
3. When satisfied with the received data, the client may close the connection.

Overall, SSE is similar to older technologies like [HTTP long polling](https://javascript.info/long-polling) or the newer [websockets](https://javascript.info/websocket). Notably however, SSE operates over regular HTTP connections unlike websockets (which require that the server understand the websocket protocol and how to "upgrade" an HTTP request to a websocket), and SSE inherently presents a potentially-unbounded sequence of events to the client whereas long-polling may require the client to make a new request for each message to be received.[^streaming]

In the interest of making the server implementation simple, SSE seemed like a good choice because I would only need to ensure that the server returned a valid stream of events. SSE communication is unidirectional, excepting the initial request (messages are only streamed from the server back to the client) whereas websocket messages can be sent both ways (also from the client to the server) which introduces a small challenge because it needs to be possible to send data back to the server. For the application I'm interested in of receiving a file and sending back progress then a result, sending the file contents in an initial request ought to be sufficient.

[^streaming]: Today it should be possible to implement SSE in terms of other APIs available in web browsers, particularly streaming responses with the [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API): this blurs the lines between long-polling and SSE significantly, and makes clearer that SSE is essentially a form of long-polling using a particular data format. When server-sent events were introduced as an API around 2004 however, techniques for streaming responses in web browsers in the same way were still young and uncommon in practice.

### Sending file data

There's one problem with the idea of using server-sent events: the [`EventSource`](https://developer.mozilla.org/en-US/docs/Web/API/EventSource/EventSource) constructor provided by web browsers for the client to open a connection doesn't offer any way to send data alongside the original request, which I need in order to upload a file to be processed. Conveniently, others have noticed the same limitation and worked around it in the form of the [`fetch-event-source`](https://www.npmjs.com/package/@microsoft/fetch-event-source) package which clearly describes the limitations of the standard `EventSource`, saving me some explanation:

> * You cannot pass in a request body: you have to encode all the
>   information necessary to execute the request inside the URL, which is
>   limited to 2000 characters in most browsers.
> * You cannot pass in custom request headers
> * You can only make GET requests - there is no way to specify another method.
> * If the connection is cut, you don't have any control over the retry
>   strategy: the browser will silently retry for you a few times and
>   then stop, which is not good enough for any sort of robust application.

With this, I prototyped a basic client allowing a user to select a file, which would then be uploaded to the server and events handled as sent back. The HTML is simple, substantially just an input field and some javascript to be run when the user confirms the selected file:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>SSE prototype</title>
  </head>
  <body>
    <form id="inputForm">
      <label>
        Select a file to process:
        <input type="file" id="fileSelect" required>
      </label>
      <input type="submit" value="Go!">
    </form>
    <script type="module" src="client.mjs"></script>
  </body>
</html>
```

Since I don't care much about compatibility with old browsers that don't support javascript modules, I was able to write "modern" javascript in client.mjs:

```javascript
// Use fetch-event-source, pulling from a CDN so I don't need to bother
// with serving a copy alongside my application.
import { fetchEventSource } from 'https://cdn.jsdelivr.net/npm/@microsoft/fetch-event-source@2.0.1/+esm';

async function handleFile(evt) {
  // Don't do normal form submission; this function does something else.
  evt.preventDefault();

  // Get the File selected by the user.
  const file = document.getElementById('fileSelect').files[0];

  // Open an event source, POSTing the file data to /process as a blob
  // of bytes and interpreting the response as an event stream.
  await fetchEventSource('/process', {
    method: 'POST',
    header: {
      'Content-Type': 'application/octet-stream',
    },
    body: file,
    // For this prototype, just log every message that's received
    onmessage(ev) {
      console.log(ev);
    }
  });
}

// Do the EventSource thing when the form is submitted.
document.getElementById('inputForm').onsubmit = handleFile;
```