---
author: tari
comments: true
date: 2012-12-01 03:57:15+00:00
slug: better-ssl
title: Better SSL
wordpress_id: 835
categories:
- Miscellanea
post_format:
- Aside
tags:
- crypto
- https
- paranoia
- ssl
---

I updated the site's SSL certificate to no longer be self-signed. This means
that if you use the site over HTTPS, you won't need to manually accept the
certificate, since it is now signed by [StartSSL](https://www.startssl.com/). If
you're interested in doing similar, [Ars
Technica](http://arstechnica.com/information-technology/2012/11/securing-your-web-server-with-ssltls/)
have a decent walk through the process (though they target nginx for
configuration, which may not be useful to those running other web servers).

