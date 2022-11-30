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

## Alternatives

All of the wikis in question here are used for what amounts mostly to technical documentation, so it's useful to look at what some other major projects use and related tools:

* [Read the Docs](<* https://readthedocs.org/>) is a widely-used free hosted service for generating software reference documentation. It appears to be based on [Sphinx](https://www.sphinx-doc.org/) and can generate API documentation from code as well as serve textual documentation written in ReStructured Text.
* [Gitbook](https://www.gitbook.com/) is a commercial service mainly targeting human-written documentation sites (with similar use cases to most wikis) that builds web pages from Markdown files stored in Git.
* [mdBook](https://github.com/rust-lang/mdBook) seems to target a similar niche to Gitbook, but is completely open-source and probably somewhat less feature-rich. It doesn't seem to automatically generate an index of pages (requiring each new page to be manually added to the index as desired).
* Static site generators like [Hugo](https://gohugo.io/) (which I used for this web site!) take text from files (usually written in Markdown) and generate web pages, usually supporting taxonomies of pages (either via file organization or tagging individual files), though lacking good support for generating global indexes.
* [MkDocs](https://www.mkdocs.org/) is another static site generator geared to technical documentation that seems to fit between tools like Hugo and Read The Docs: it builds web pages from Markdown by auto-discovering documents and provides a browsable index, as well as supporting search.

For wiki-like documentation, I think it's particularly important that pages be easy to discover and browse. This usually means that a global index should exist, because otherwise finding documentation for something requires either guessing where it is (navigating categories to find it), searching for it (guessing some key words that relate to the topic and exist in the documentation) or relying on documentation authors to have provided a link.