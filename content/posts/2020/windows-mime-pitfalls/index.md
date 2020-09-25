---
title: Windows MIME type detection pitfalls
slug: windows-mime-pitfalls
draft: false
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

Static files (including the Javascript files causing me problems) are served by Django when using the development server, using the `django.view.static.serve` view. Of particular note here, it uses the `mimetypes` module to guess the MIME type of files based on their name:

```python
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or 'application/octet-stream'
```

Digging into what `mimetypes` does, it's documented to read mappings from the registry on Windows, and from a set of known paths on all other operating systems. The relevant code for loading mappings from the registry looks like this:

```python
with _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, '') as hkcr:
    for subkeyname in enum_types(hkcr):
        try:
            with _winreg.OpenKey(hkcr, subkeyname) as subkey:
                # Only check file extensions
                if not subkeyname.startswith("."):
                    continue
                mimetype, datatype = _winreg.QueryValueEx(subkey, 'Content Type')
                if datatype != _winreg.REG_SZ:
                    continue
                self.add_type(mimetype, subkeyname, strict)
```

In short: it enumerates keys in `HKEY_CLASSES_ROOT`, ignoring any that don't have a name starting with "." and uses the value of a "Content Type" subkey (if present) as the MIME type for files with that extension.

As far as this goes, it seems quite reasonable. Microsoft document `HKEY_CLASSES_ROOT` as a [combined view of system-wide and per-user filetype associations](https://support.microsoft.com/en-us/help/256986/windows-registry-information-for-advanced-users), and [the "Content Type" subkey may be set to a file type's MIME type](https://docs.microsoft.com/en-us/windows/win32/shell/fa-file-types).

Opening up the registry editor on my system, I do see that the value of `HKEY_CLASSES_ROOT\.js\Content Type` is `text/plain`. So this is where Python got the incorrect MIME type from, and I can fix it by changing the value of `Content Type`. For instance, this snippet in a .reg file (maybe `js.reg`) can be imported to set a correct MIME time for .js files, changing a per-user setting if set or the global one otherwise:

```
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\.js]
"Content Type"="text/javascript"
```

## Problems with this system

While it seems abstractly reasonable for programs to use the registry-based mechanism for getting file MIME types, the other ways it is used in practice seems inappropriate for these purposes.

As a Django-based example, I found [a Stack Overflow question with similar incorrect MIME type](https://stackoverflow.com/q/16303098/2658436) while investigating my initial problem. While the original question asker arrived at a workaround of manually configuring a correct MIME type in Python, after investigation it seems clear that the problem is better considered a system misconfiguration and I feel correcting the data in the registry is more appropriate.[^django-bug]

[^django-bug]: I [filed a bug against Django](https://code.djangoproject.com/ticket/32041) after doing this investigation myself, and found a proposal from 2008 that Django ship default MIME types for these purposes. It remains to be seen what the Django developers think of the situation.

Python isn't even the only platform that suffers from certain prevalence of incorrect MIME types in the Windows registry. A [fairly recent bug for the Go language](https://github.com/golang/go/issues/32350) indicates that the standard library for Go uses the same approach for guessing MIME types, with the same tendency to get wrong data.

On a fresh install of Windows, it even seems that many MIME types are unconfigured. When I checked what content type was set in the registry for .js files on a pristine copy of Windows (using a Windows Sandbox to have a quick and easy look), I found that there was none set. Being unset by default, it seems that in many cases (if nothing has set a mapping in the registry) Django will serve javascript as `application/octet-stream` because Python won't find any configuration, which seems incorrect.

### Fixing the problem once and for all

While it would be relatively easy to ship a reasonable MIME type mapping with Python or Django (indeed, Go seems to do this and use values from the registry instead if available), doing so would only fix the default case where no value is set.

The root problem with MIME type guessing on Windows seems to be that incorrect types often get written to the registry. It's not obvious where these incorrect values come from, but I suppose the bad data tends to be written by some programs when they are configured to open those files. It seems like these programs might be badly-behaved when they do this since associating a file type with a program doesn't necessarily say anything about the file's MIME type, but it seems widespread enough that fixing that is intractable.

While it is possible to provide "correct" MIME type mappings with software (and this will often work around the problem with Windows), doing so is not correct in all cases because users may sometimes *want* non-standard mappings and it's not possible to tell the difference between a mapping that has intentionally been set to an unusual value and one that was accidentally set that way.

Aspirationally, changes to the `mimetypes` API in Python (or similar ones in Go, I suppose) might improve the situation for many users. An option could be added that would tell the system to either ignore or prefer user-configured mappings, allowing applications to choose their preferred mode. However, doing so pushes complexity onto application authors in ways that probably cannot be predicted in all situations, which would mean the option would need to be exposed to application users to be set as required.

---

As best I can tell, the least-wrong solution to the situation of users often ending up with incorrect MIME type mappings on Windows is to make the problem more widely known so new software doesn't misbehave in the same ways around writing bad mappings, and users have an easier time of correcting the problem if it does occur.[^api-changes]

[^api-changes]: If APIs were changed to allow specifying the preferred source of mappings then better documentation would be needed anyway, so end users could be aware of the option if it were needed.

<span style="font-size: 200%">**Now you know!**</span>