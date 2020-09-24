---
title: Windows MIME type detection pitfalls
slug: windows-mime-pitfalls
draft: true
date: 2020-09-24T23:12:12.586Z
categories:
  - Software
tags:
  - windows
  - python
  - django
  - mime
---
I've been doing some [Django](https://djangoproject.com) development lately, and was mystified why it seemed the [debug toolbar](https://github.com/jazzband/django-debug-toolbar) on my local development instance wasn't showing up, though it had been in the past. It turns out to have been a surprising interaction between browsers sometimes enforcing that resources be served with correct MIME types and the way Windows provides system-wide MIME type configuration!

<!--more-->

Investigating further, I found that the markup for the debug toolbar was in fact being generated and placed in the pages served by my development server, but not being shown. I guess that there may have been a recent update to `django-debug-toolbar` that may have broken it, and found that [version 3.0 (quickly followed by 3.1) had recently been released](https://pypi.org/project/django-debug-toolbar/#history). Downgrading to version 2.2 fixed the issue, so I was confident I hadn't somehow misconfigured the debug toolbar.

Looking more closely at the browser console, I noticed an important error message:

> Loading module from “http://localhost:8000/static/debug_toolbar/js/toolbar.js” was blocked because of a disallowed MIME type (“text/plain”).

It seems that `django-debug-toolbar` 3.0 started loading the scripts that make it work as Javascript modules rather than plain scripts, because in the past I've noticed (and learned to ignore) similar warnings when using the Django development server:

> The script from “http://localhost:8000/static/myscript.js” was loaded even though its MIME type (“text/plain”) is not a valid JavaScript MIME type.

This change has thus broken the debug toolbar because the scripts that make it work are no longer being executed since my local server is serving javascript files with the wrong [`Content-Type`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type). Why is that?

## MIME type guessing

https://docs.microsoft.com/en-us/windows/win32/shell/fa-file-types
https://support.microsoft.com/en-us/help/256986/windows-registry-information-for-advanced-users
https://stackoverflow.com/questions/16303098/django-development-server-and-mime-types/64055514#64055514
https://github.com/golang/go/issues/32350
https://code.djangoproject.com/ticket/32041