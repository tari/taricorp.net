---
layout: page
title: Projects
date: 2010-04-11 20:02:34.000000000 -06:00
categories: []
tags: []
status: publish
type: page
published: true
meta:
  _edit_last: '1'
  _wp_page_template: default
author:
  login: tari
  email: peter@taricorp.net
  display_name: tari
  first_name: Peter
  last_name: Marheine
in_global_nav: true
---

This section of the site contains a variety of things that I've created through
the pursuit of meaning in existence.

{% for page in site.pages %}{% if page.url contains "/projects" and page.url != "/projects/index.html" %}{{ page.title }}{% endif %}{% endfor %}

# License

Where not otherwise specified, I provide this information under the terms of
the zlib license (see below).  If you want to use these things in a way that is
not compatible with the license, contact me.  I'm likely to be willing to
provide it to you under some other license, as I believe that the primary value
of any product is in its use.

> Copyright (c) &lt;''year''&gt; Peter Marheine
> 
> This software is provided 'as-is', without any express or implied
> warranty. In no event will the authors be held liable for any damages
> arising from the use of this software.
> 
> Permission is granted to anyone to use this software for any purpose,
> including commercial applications, and to alter it and redistribute it
> freely, subject to the following restrictions:
> 
>    1. The origin of this software must not be misrepresented; you must not
>    claim that you wrote the original software. If you use this software
>    in a product, an acknowledgment in the product documentation would be
>    appreciated but is not required.
> 
>    2. Altered source versions must be plainly marked as such, and must not be
>    misrepresented as being the original software.
> 
>    3. This notice may not be removed or altered from any source
>    distribution.
