---
title: A Wayback Machine Bookmarklet
slug: wayback-bookmarklet
draft: false
date: 2020-03-21T09:37:39.883Z
categories:
  - Miscellanea
  - Software
tags:
  - archiving
  - bookmarklet
  - javascript
  - paranoia
  - snippets
  - software
  - warc
  - wayback machine
  - web
---
Sometimes I find it useful to be able to quickly save a page to the [Wayback Machine](https://en.wikipedia.org/wiki/Wayback_Machine), often to be able to provide a stable link to a page that I don’t control- for instance if I’m pointing somebody to a document that describes something they’re asking about, then it’s nice to ensure that there will still be an archived copy if the original goes away.

{{< figure src="/images/save-page-now.png" alt="The 'Save Page Now' field in the wayback machine. There is a 'Save Page' button associated with a URL entry field." >}}

While the landing page on web.archive.org has a “save now” form to quickly save a page given its URL, this is still more cumbersome than I’d like- it involves copying the desired URL, opening a new tab to web.archive.org, pasting the URL into the form and pressing the save button- in exactly that order.

The concept of [bookmarklets](https://en.wikipedia.org/wiki/Bookmarklet) comes to the rescue: little snippets of Javascript in a bookmark to do some function- it’s easy enough to open a new tab to a given URL with some javascript, so by inspecting how the “Save page” button works, I can automate it:

```
javascript:void(window.open('https://web.archive.org/save/'+location.href));
```

I’ve put that string into a bookmark that sits on my browser’s bookmarks bar, so I can just click on that to open a new tab which will save the currently-shown page to the Wayback Machine in a new tab. Much easier!

Of course this is still cumbersome to do with many URLs, such as if I want to archive all the links in a blog post. Fortunately [AMBER](http://amberlink.org/) automates that particular use case, and larger applications tend to be the realm of [fetching WARCs with wget](https://www.archiveteam.org/index.php?title=Wget_with_WARC_output).