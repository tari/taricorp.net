---
title: Migrating MediaWiki wikis to plain-text repositories
slug: mediawiki-migration
draft: false
date: 2022-11-29T22:21:08.566Z
tags:
  - mediawiki
  - software
  - python
  - markdown
  - hacking
---
I don't like MediaWiki. Sure, it powers arguably the most valuable repository of human knowledge that currently exists ([Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:About)), but that may be in spite of MediaWiki: not because of MediaWiki. My main complaints boil down to these:

* Running a small MediaWiki instance is not a trivial task:

  * It's not easy to keep the application up to date, because it's distributed as a collection of files usually meant to be extracted over an old version. Customizations are often made by directly editing the application files, so upgrading is often difficult.
  * It depends on a separate database, which also needs to be maintained.
  * Spam can be difficult to manage: there seems to be no shortage of wiki spam bots that can pass typical CAPTCHA solutions.
* Content is largely structured in a flat namespace, where every page is identified only by its name.

  * I find administration tasks to be cumbersome as a result, because special pages for performing administration of the system look a lot like regular pages that are "special" in some way.
  * Sometimes things are namespaced by placing colons (`:`) in page titles, but this doesn't seem to actually do anything aside from provide a visual indication.
  * There is a mechanism for categorizing pages (and doing so generates an automatic listing of pages for each category), but that is done by simply adding a link to the category in the page text which is difficult to discover when writing.
* Wiki markup is strange: it's very unlike any other markup language and in general doesn't feel designed so much as accreted. I don't like writing it.

Unfortunately, I've somewhat inherited maintainership of three different MediaWiki instances that I don't want to have to think about. They don't require much thought as they are now (for instance because account creation has been configured to require manual approval to combat spam), but simply running the application on a server is still more effort than I want to put into managing those.

### The problem with servers

While working on this project, I came across Quinn Dombrowski's article [*Sorry for all the Drupal*](https://quinndombrowski.com/blog/2019/11/08/sorry-all-drupal-reflections-3rd-anniversary-drupal-humanists/) which resonated with me regarding the problems with running full-blown web applications (Mediawiki for me, Drupal for them) in use cases that don't get resources allocated for ongoing maintenance. I think their commentary is worth reading in full, but there are a few particularly relevant items that relate to my goals here:

> When you’re building a Drupal site, it can feel like Legos. But in the medium term and beyond, it’s a misleading analogy. Barring the interference of careless pets or children with their hearts set on destruction, the Legos you assemble stay assembled until you choose to take them apart. Instead, building a Drupal site is like buying a pony. It seems like a fun and exciting undertaking, but you quickly discover that ponies require constant feeding and cleaning-up-after. You don’t ever get a break — you can’t shrug and figure the pony will sort out its own food-and-feces situation while you turn your attention to a new project.

Although Quinn is talking about Drupal-based web sites specifically, I find this is true of all web applications. They can often run with minimal supervision for quite some time, but eventually something needs to be updated or it gets vandalized and you need to figure out how to clean things up.

> If you don’t take care of it, and don’t find (and probably pay) someone else to take care of it, you can try to give it away — but wise technical staff will balk at the offer of having to take on someone else’s Drupal site, particularly if it’s been neglected for some time. Once your project is done, if you’re not realistically going to devote the ongoing resources required for maintaining it indefinitely, it’s time to consider what it will take to “archive” it, shut it down in some orderly manner. In essence, the responsible decision is to euthanize the pony.

This is exactly what I sought to do with this project: I no longer wish to expend effort on maintaining a whole server, and it is often difficult to find somebody willing to take over maintenance. In the case of these I want to avoid euthanizing the pony completely because I believe people still find the information useful, but by taking the wiki application out of the loop it's easier to keep everything online. It might become slightly more difficult to update the site content if not using MediaWiki but the problem of keeping everything online becomes much simpler and I'm quite happy to make that tradeoff, especially if the alternative would be letting the site slowly "starve to death" for want of maintenance.

## Alternatives

All of the wikis in question here are used for what amounts mostly to technical documentation, so it's useful to look at what some other major projects use and related tools:

* [Read the Docs](<* https://readthedocs.org/>) is a widely-used free hosted service for generating software reference documentation. It appears to be based on [Sphinx](https://www.sphinx-doc.org/) and can generate API documentation from code as well as serve textual documentation written in ReStructured Text.
* [Gitbook](https://www.gitbook.com/) is a commercial service mainly targeting human-written documentation sites (with similar use cases to most wikis) that builds web pages from Markdown files stored in Git.
* [mdBook](https://github.com/rust-lang/mdBook) seems to target a similar niche to Gitbook, but is completely open-source and probably somewhat less feature-rich. It doesn't seem to automatically generate an index of pages (requiring each new page to be manually added to the index as desired).
* Static site generators like [Hugo](https://gohugo.io/) (which I used for this web site!) take text from files (usually written in Markdown) and generate web pages, usually supporting taxonomies of pages (either via file organization or tagging individual files), though lacking good support for generating global indexes.
* [MkDocs](https://www.mkdocs.org/) is another static site generator geared to technical documentation that seems to fit between tools like Hugo and Read The Docs: it builds web pages from Markdown by auto-discovering documents and provides a browsable index, as well as supporting search.

For wiki-like documentation, I think it's particularly important that pages be easy to discover and browse. This usually means that a global index should exist, because otherwise finding documentation for something requires either guessing where it is (navigating categories to find it), searching for it (guessing some key words that relate to the topic and exist in the documentation) or relying on documentation authors to have provided a link.