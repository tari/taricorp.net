---
title: "Video Squisher: minimal command-line processing on the web"
slug: video-squisher
date: 2023-12-23T09:47:06.970Z
categories:
  - software
tags:
  - python
  - handbrake
  - javascript
  - web
  - hacks
---
I've recently been asked to reduce the size of video files with some regularity, taking in a video file and generating something with reduced file size ("squishing" the video; hence "video squisher"). This is an easy task to accomplish with [Handbrake](https://handbrake.fr/), and since the transcodes I was asked to do were consistent in their needs, I was able to set up a preset in Handbrake to make these conversions very simple.

Unfortunately, there were a few steps that weren't as easy to automate: namely, grabbing the original video and sharing the transcoded version later. Rather than need to do anything myself for each video, I sought to make my process available for "self-service", probably as some kind of web-based tool instead. Since the imposition of receiving a file, running it through Handbrake, and sharing the result is fairly small though, I wanted to make this tool as simple as possible.

I believe I succeeded and that the results are interesting enough to share because I discovered a few new tricks that made it easier, so in this post I will describe what I built to meet this need and how it was made.

<!--more-->

## Requirements

Since manually processing a few videos is fairly easy, whatever I might build to automate video conversion would also need to be a simple tool requiring little effort to build and run. However, it also needs to be comprehensible to an unsophisticated user so I arrived at these requirements:

 * There must be a single server component with no external dependencies such as a database server.
 * All input and output must occur through a web browser.
 * Video transcoding progress should be reported to the user in real time.

Given I had been using Handbrake to manually transcode videos, I expected that automation of the process would involve running Handbrake's CLI in a subprocess and streaming its console output back to the client.

## Client prototyping: enter SSE

Of the requirements I had set, the goal of reporting real-time progress seemed most challenging so I investigated that first. I fairly quickly stumbled upon a web API that I wasn't familiar with which seemed to meet my needs: [Server-sent events](https://en.wikipedia.org/wiki/Server-sent_events) (SSE). This API involves a client making a single HTTP request to a server, which then responds with a stream of events in a structured data format (using content type `text/event-stream`). At a high level, the flow of [using an `EventSource`](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) in a browser is to:

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

There's one problem with the idea of using server-sent events: the [`EventSource`](https://developer.mozilla.org/en-US/docs/Web/API/EventSource/EventSource) constructor provided by web browsers for the client to open a connection doesn't offer any way to send data alongside the original request, which I need in order to upload a file to be processed. Conveniently, others have noticed the same limitation and worked around it in the form of the [`fetch-event-source`](https://www.npmjs.com/package/@microsoft/fetch-event-source) package which also describes the limitations of the standard `EventSource`, saving me some explanation:

> * You cannot pass in a request body: you have to encode all the
>   information necessary to execute the request inside the URL, which is
>   limited to 2000 characters in most browsers.
> * You cannot pass in custom request headers
> * You can only make GET requests - there is no way to specify another method.
> * If the connection is cut, you don't have any control over the retry
>   strategy: the browser will silently retry for you a few times and
>   then stop, which is not good enough for any sort of robust application.

With `fetch-event-source` in hand, I prototyped a basic client allowing a user to select a file, which would then be uploaded to the server and events handled as sent back. The HTML is simple, substantially just an input field and some javascript to be run when the user confirms the selected file:

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

Since I don't care much about compatibility with old browsers that don't support javascript modules, I was able to write "modern" javascript in `client.mjs` to plumb data through:

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

## Server implementation

Without a server the above client prototype is useless, so I next had to write a server application that can accept the uploaded file and send back events. Since I'm familiar with the tools available in Python's standard library, I opted to implement it in terms of [`http.server`](https://docs.python.org/3.12/library/http.server.html).

```python
import http.server

BUF_COPY_SZ = 1 << 20

class Handler(http.server.SimpleHTTPRequestHandler):
    def send_event(self, data: str = None, ty: str = None):
        """
        Send an event in a stream, with specified type (unset if None)
        and data (no data if None).
        """
        if data is not None:
            # Send the event type if specified.
            if ty is not None:
                self.wfile.write(f'event: {ty}\n'.encode('utf-8'))
            # Line breaks are field separators in an event stream, so multiline
            # data must be split into multiple data: lines.
            for line in data.splitlines():
                self.wfile.write(f'data: {line}\n'.encode('utf-8'))
            # Messages are separated by blank lines
            self.wfile.write(b'\n')
        else:
            # No data sends a line with no meaning, useful to keep the
            # connection alive by sending some data.
            self.wfile.write(b':\n')
        # Ensure the whole message gets sent immediately.
        self.wfile.flush()

    def do_POST(self):
        # SimpleHTTPRequestHandler will call this to handle POST
        # requests.

        # To receive the uploaded file, we need to know how large it is.
        upload_size = self.headers.get('Content-Length')
        if upload_size is None:
            self.send_error(400, 'Missing length', 'Content-Length must be set for POSTs')
            return
        upload_size = int(upload_size)

        # Input seems okay, so start sending an event stream.
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()

        # Save the uploaded data into a temporary file that can be
        # processed later, copying it in 1MB chunks. Send back
        # 'uploadprogress' events as we go, to demonstrate sending
        # events.
        with tempfile.NamedTemporaryFile(mode='wb', dir='/var/tmp') as infile:
            for o in range(0, upload_size, BUF_COPY_SZ):
                buf = self.rfile.read(min(BUF_COPY_SZ, upload_size - o))
                infile.write(buf)
                self.send_event(f'{o / upload_size:.02}', 'uploadprogress')
            self.send_event('1', 'uploadprogress')

# When run as a script, serve HTTP on an arbitrary port.
if __name__ == '__main__':
    PORT = 9428

    httpd = http.server.HTTPServer(('', PORT), Handler)
    print("serving on port", PORT)
    httpd.serve_forever()
```

This server will respond to `GET` requests by returning the contents of a file that exists (behavior provided by `SimpleHTTPRequestHandler`), allowing it to serve my HTML and javascript files. Any `POST` request expects to receive some uploaded file data and returns an event stream by calling `send_event` from inside `do_POST` for each request.

Notably, no per-request information is saved anywhere: if the connection is interrupted there is no mechanism to resume, because managing the state of each active stream and reaping the ones that have completed would be more complex. Associating a stream directly with a connection by keeping only local state ensures resources will always be cleaned up when a connection closes.

### Testing the principle

Running the server (`python server.py`) and loading it in a web browser, I was able to upload a file and see events come back as expected. However, when the server closed the connection after completing its work I found that the client would attempt to reconnect (as if the connection had been interrupted). This makes sense because in general it's not possible to determine whether a given connection closure was intentional, but it is a little bit annoying.

After spending some time studying the implementation of `fetch-event-source` (not actually very complex!), I decided that the best way to cleanly close a stream in the browser was to throw an exception:

```javascript
class Done extends Exception {}

try {
  await fetchEventSource('foo', {
    onmessage(ev) {
      // Decide if done..
      throw new Done();
    }
    onerror(err) {
      throw err;
    },
  });
} catch (e) {
  if (e instanceof Done) {
    // Finished successfully
  } else {
    // Unexpected error
    throw e;
  }
}
```

There might be a slightly better way to handle this, but I wasn't able to quickly discern it. The `Promise` returned by `fetchEventSource()` resolves successfully in some cases, so there's probably a detail that wasn't obvious to me.[^http1] In any case, depending on exceptions to close a connection works okay.

[^http1]: `http.server` speaks HTTP 1.0 and closes the connection when it's
done responding to a request by default, which might confuse event source clients and
cause this awkwardness. Using a chunked transfer encoding and speaking
HTTP 1.1 might prevent that (by making it clear when the stream ends),
but is somewhat more complex to handle on the server.

It's worth realizing here that my implementation of this application is completely unable to reconnect in case of connection loss because the server is entirely stateless: it is impossible to resume a stream because
any information about the transcode process will be lost when the connection to the server for a given request is closed. For personal use and limited applications I don't mind, but a public tool might want to be more robust and pay the associated complexity costs.

## Actual transcoding

Having proven the concept of streaming events, the remaining piece of the server is to run something that transcodes the received video then returns the new file and streams progress output while it's running. Given the input file is a `NamedTemporaryFile` called `infile`, running Handbrake's CLI and getting access to the output isn't hard:

```python
with tempfile.NamedTemporaryFile(mode='rb', dir='/var/tmp') as outfile:
    args = [
        # Output mp4 with leading MOOV
        '--format', 'av_mp4', '--optimize',
        # 5 megabits per second video, two-pass encoding
        '--multi-pass', '--vb', '5000',
        '--crop-mode', 'none',
        '--encoder', 'x264', '--encoder-preset', 'slow', '--turbo',
        # Don't process audio, just copy
        '--aencoder', 'copy',
        '--input', infile.name,
        '--output', outfile.name,
    ]
    with subprocess.Popen(['HandBrakeCLI'] + args,
                          stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          text=True) as proc:
        self.handle_subprocess(proc)
        assert proc.poll() is not None, "Subprocess should have exited"
        self.send_event(str(proc.returncode), 'returncode')
```

Here I've simply created a second temporary file for Handbrake to write its output to, then run it in a subprocess. A `handle_subprocess` method on the request handler (not yet implemented!) will be responsible for relaying output back to the client by calling `send_event`, and once the subprocess exits it sends back a `returncode` event to indicate whether the transcode process completed successfully.

### Real-time output streaming

Normally to capture the output from a subprocess using Python's `subprocess` module, you'd want to call `communicate` on the process to wait for completion and return its output as a string. This application wants to return output immediately as it arrives rather than all at once after the subprocess exits, so that's clearly not sufficient: we instead need to send a message whenever any new output appears, and ideally send empty messages rather than waiting for a long time without printing anything to ensure the stream's connection doesn't time out due to inactivity.

I know that `communicate` must do something similar to what I want to do by collecting output as it arrives, because that method ensures processes which take input on standard input won't get stuck by doing the same thing: waiting for output while a subprocess is waiting for input would deadlock the entire thing, so it must be able to opportunistically grab output from a subprocess and pass input in. Looking at how the Python standard library implements `communicate`, I found it worked similarly to how I expected it would (using something like the `select()` system call) and implemented something similar myself in `handle_subprocess`:

```python
def handle_subprocess(self, proc: subprocess.Popen):
    with selectors.DefaultSelector() as sel:
        # If not set to nonblocking, the read() of stdout can block
        # when we try to read more data than is present. When nonblocking,
        # it only returns whatever data is available.
        os.set_blocking(proc.stdout.fileno(), False)
        sel.register(proc.stdout, selectors.EVENT_READ)

        while True:
            # Wait up to 1 second for some data
            ready = sel.select(timeout=1)
            if ready:
                for key, events in ready:
                    # If there's data available, read it.
                    if key.fileobj == proc.stdout:
                        data = proc.stdout.read(16384)
                        # We were told there's data ready, but if we read
                        # nothing that means the output has been closed
                        # (the subprocess exited) and we reached the end.
                        if not data:
                            return
                        self.send_event(data, ty='stdout')
            else:
                # select() timed out; send an empty event
                self.send_event()
```

This assumes the subprocess' standard output is opened in text mode (we passed `text=True` to `subprocess.Popen()`), and thus sends chunks of text from its standard output out as messages by calling `send_event`.

The main tricks here are:
 * Setting `proc.stdout` to non-blocking mode so we won't ever wait for new data to arrive.
 * Using `read(n)` to read only up to `n` bytes of data, rather than reading to the end of the stream.
 * Polling with `selectors` to respond immediately when data becomes available to read, or give up after a timeout.

To test this, I used [curl](https://curl.se/) to manually send requests to the server because that was somewhat easier than clicking several things in a web browser for every test and it directly prints out the results:

```
$ curl -X POST \
  --data-binary @myvideo.mp4 \
  --header "Content-Type: application/octet-stream" \
  http://localhost:9429/squish
event: uploadprogress              
data: 0.0

event: uploadprogress                                                 
data: 0.99                                                            
                                                                      
event: uploadprogress                                                 
data: 1                                                               
                                   
event: stdout                                                                                                                               
data: [13:23:57] Compile-time hardening features are enabled          
                                                                      
event: stdout                                                         
data: Cannot load libnvidia-encode.so.1                                                                                                     
                                                                      
event: stdout                  
data: [13:23:57] hb_display_init: attempting VA driver 'iHD'
...
```

Somewhat interestingly, I had originally expected that calling `read` with a parameter (to limit the number of bytes read) should prevent it from blocking, but I found that my server was emitting large chunks of data much less frequently than expected, and wasn't generating empty (keepalive) messages at all. It turned out that the chunks were 16384 bytes (the length which was being passed to `read`) and the `read`s were actually blocking, which I fixed by calling `os.set_blocking`. It might be possible to make this logic a little bit simpler after that discovery, but I've found it to work okay.

This implementation ended up working nicely, so the remaining piece is to return the output file to the client and save it in the web browser.

### Sending files back

The output from Handbrake is created as a `NamedTemporaryFile`, which can be read like a normal file once the Handbrake subprocess exits. In order to let the client do some progress reporting for the download, I first send a `resultsize` message indicating how many bytes of output there are:

```python
outfile.seek(0, os.SEEK_END)
output_len = outfile.tell()
outfile.seek(0, os.SEEK_SET)
self.send_event(f'{output_len}', 'resultsize')

# Read chunks of the output file and send back to the client
while chunk := outfile.read(BUF_COPY_SZ):
    self.send_event(base64.b64encode(chunk).decode('ascii'), 'result')
```

The data in each `result` message is encoded with base64 because event streams only accept text, not binary data. To ensure the video data being returned is valid in an event stream, I've chosen to base64-encode it because that's easy to decode in the browser.

---

With all the server parts implemented, I had to extend the javascript running on the client to handle all of the event types in the `onmessage` function. I added an element to the HTML with ID `outputBox` to contain the encoder's output, which will be streamed, and added code to handle each event kind as they arrive on the stream (inside the event source's `onmessage` function):

```javascript
const outputBox = document.getElementById('outputBox');
let resultData = null;
let resultDataOffset = null;

switch (ev.event) {
  case 'uploadprogress':
    // Report progress of initial upload
    break;
  case 'stdout':
    // Add the new line of data to the output box
    outputBox.append(ev.data, '\n');
    // Scroll it to the bottom so the new output is visible
    outputBox.scrollTo(0, outputBox.scrollHeight);
    break;
  case 'returncode':
    // Interpret the return code as a number
    const code = Number(ev.data);
    // Abort if it wasn't successful
    if (code !== 0) {
      throw new Error('Encode failed');
    }
    break;
  case 'resultsize':
    // Interpret data as a number, allocating storage to contain
    // all the data that will be returned. These values will be
    // build up in following 'result' messages.
    resultData = new Uint8Array(Number(ev.data));
    resultDataOffset = 0;
    break;
  case 'result':
    // base64-decode the data
    const chunk = atob(ev.data);
    // Append bytes of the data chunk to resultData (using codePointAt()
    // because the "binary" string returned by atob() is a weird kind of
    // string).
    for (let i = 0; i < chunk.length; i++) {
      resultData[resultDataOffset++] = chunk[i].codePointAt(0);
    }

    // If all the expected data arrived, save the data as if it
    // were a regular downloaded file.
    if (resultDataOffset === resultData.length) {
      // Put the bytes (resultData) into a File
      const f = new File([resultData], file.name + '.mp4', {
        type: 'video/mp4'
      });

      // Create an HTML anchor which downloads the created file when
      // clicked.
      const link = document.createElement('a')
      link.download = f.name;
      link.href = URL.createObjectURL(f);
      // Free the resultData, since the created object URL
      // now contains all the data that matters.
      resultData = null;
      resultDataOffset = null;

      // Click the generated link to trigger download, and free the
      // object URL of data after that. This needs to use setTimeout()
      // because the download won't actually start until no scripts are
      // executing, so we delay calling revokeObjectURL() until after
      // the download has actually begun so the data is still present
      // to save.
      const clickHandler = () => {
        setTimeout(() => {
          URL.revokeObjectURL(link.href);
          link.removeEventListener('click', clickHandler);
        }, 150);
      };
      link.addEventListener('click', clickHandler);
      link.click();

      // All done; close the event stream by throwing an exception
      // which we know means everything is done.
      throw new Done();
    }
}
```

The handling of binary data and base64-decoding here is somewhat awkward, but works well enough. For very large videos it could be rather inefficient, but at least for videos with size around 100 megabytes I found the performance to be acceptable.

In the actual code I also added a `<progress>` element to the HTML, which gets updated for each `uploadprogress` event (indicating how much data has been uploaded) and each `result` event (indicating what fraction of the total result has been received). I haven't included that code here, just because it's not important to the more interesting concepts of how the system works.

## Results

The result in a browser looks like this, featuring the same file input field to choose a file, a progress bar that shows upload progress and later download progress, with all of the status output from the encoder appearing in real time beneath:

<video controls src="squish.webm" playsinline width="649" height="356" preload="metadata"></video>

As already noted, I added a progress bar for both upload and download progress which wasn't included in the code samples above. This could probably also be hooked up to the progress reporting that Handbrake does itself (especially in its JSON output mode), but that would require more than zero parsing of its output so I didn't bother; it's okay to "manually" read the status from text rather than only look at a progress bar.

The other particularly useful-seeming improvement that I've considered but not been interested in implementing could be to load the input video in a `<video>` element on the client before uploading it. The information from the browser could be used to determine its length, which could be used as an input to a simple algorithm that computes a required bitrate for the video output given a target file size. Being able to estimate the input bitrate in that way would solve the current problems where a low-bitrate input could be uselessly transcoded to a higher bitrate!

---

I've published the complete source code to this tool at **<https://gitlab.com/taricorp/videosquisher>**, which might be useful to others. Beyond that, I don't anticipate doing any further work on this because it meets my needs. The options passed to the video encoder might be changed at some point in the future if I decide they're worth changing, and there's some possibility I might later add the features noted in the previous paragraph; however right now I have no plans to make further improvements.

I chose to write about this tool simply because I thought its implementation used some interesting techniques that seem worth thinking about: certainly it could be adapted to other applications where a user might run a command-line tool with a fairly fixed set of options to consume one file and generate another, so this could be a convenient base on which to build similar tools!