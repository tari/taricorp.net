---
layout: page
title: Essays
date: 2011-12-05 22:18:51.000000000 -07:00
categories: []
tags: []
status: publish
type: page
published: true
in_global_nav: true
---

These are mostly things that are more well-reasoned or supported than content
in the main category of the site.  No promises, though.

{% for page in site.pages %}{% if page.url contains "/essays" and page.url != "/essays/index.html" and page.title %} * [{{ page.title }}]({{page.url}}){% if page.excerpt %}: {{ page.excerpt }}{% endif %}
{% endif %}{% endfor %}

