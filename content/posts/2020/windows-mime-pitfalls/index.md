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

Investigating 

https://docs.microsoft.com/en-us/windows/win32/shell/fa-file-types
https://stackoverflow.com/questions/16303098/django-development-server-and-mime-types/64055514#64055514
https://github.com/golang/go/issues/32350
https://code.djangoproject.com/ticket/32041