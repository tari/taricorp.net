---
title: Format-shifting MediaWiki for improved presentation
slug: mediawiki-format-shifting
draft: false
date: 2022-11-29T22:21:08.566Z
tags:
  - mediawiki
  - software
  - python
  - markdown
  - hacking
---
[Mediawiki](https://www.mediawiki.org/) is a pretty useful piece of software. It powers arguably the most valuable repository of human knowledge that currently exists ([Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:About)) and does a reasonable job of being accessible to casual authors for well-scoped subjects such as individual video games, exemplified by the [Minecraft Wiki](https://minecraft.fandom.com/wiki/Minecraft_Wiki) among others.

## Some complaints

Despite its near-ubiquity and obvious utility, I often find Mediawiki (and similar wiki software) deployed in applications that I don't think it's well-suited to. My complaints boil down to these items:

1. Running a small MediaWiki is not a trivial task, though it scales up well.
2. Content is primarily structured in a flat namespace.
3. Wiki markup is not very nice to write or work with.

### The problem with servers

Quinn Dombrowski's article [*Sorry for all the Drupal*](https://quinndombrowski.com/blog/2019/11/08/sorry-all-drupal-reflections-3rd-anniversary-drupal-humanists/) effectively captures many of the hazards in providing a web application In particular, that they always need maintenance:

> When you’re building a Drupal site, it can feel like Legos. But in the medium term and beyond, it’s a misleading analogy. Barring the interference of careless pets or children with their hearts set on destruction, the Legos you assemble stay assembled until you choose to take them apart.

> Instead, building a Drupal site is like buying a pony. It seems like a fun and exciting undertaking, but you quickly discover that ponies require constant feeding and cleaning-up-after. You don’t ever get a break — you can’t shrug and figure the pony will sort out its own food-and-feces situation while you turn your attention to a new project.

Although Quinn is talking about Drupal-based web sites specifically, this tends to be true of most software (and indeed infrastructure in general). They can often run with minimal supervision for quite some time, but eventually something needs to be updated or it gets vandalized and you need to figure out how to clean things up. If you haven't been spending effort on maintenance already, that cleanup can be remarkably difficult.

#### MediaWiki particulars

Having spent some time myself maintaining MediaWiki sites, there are some specific concerns that I've found annoying about MediaWiki.

To begin with, it's updated on a fairly regular cadence, with a new release about every six months. This is a good thing because it means the software itself is maintained to keep up with the world changing around it (as well as to fix issues that are discovered), but it also places the onus on a system operator to keep their copy up to date. As a system implemented in PHP, it can be pretty easy to update an unmodified copy of MediaWiki: just [unpack the new copy over the old one](https://www.mediawiki.org/wiki/Manual:Upgrading) and visit the special `upgrade` page.

For installations of the software that have been customized at all however, **upgrading can be difficult**. Because the software is distributed as a collection of files that are easy to modify, it's common for customizations to be made by simply editing the code making up the software because it's very easy to do. Of course, in that case the changes need to be made again after an upgrade because the new version's files will have replaced the (modified) old one.

Even when changes are made at the intended extension points (as [extensions](https://www.mediawiki.org/wiki/Manual:Extensions)), compatibility when upgrading is not guaranteed. In the most convenient case an extension is maintained by somebody else and gets updated in a timely fashion as needed for each version of MediaWiki, but custom-built extensions for niche requirements might demand that the system administrator take responsibility for maintaining them (because nobody else has exactly the same needs), which could be very time-consuming as the sysadmin is unlikely to be well-versed in the software's internals.

### Namespacing awkwardness

MediaWiki tends to assume that every page has a unique name. This seems reasonable if you're building an encyclopedia because it's not too bad to [disambiguate](https://en.wikipedia.org/wiki/Wikipedia:Disambiguation) by appending more detail to a page's title, but there are plenty of applications where you might prefer to be able to organize things hierarchically.

MediaWiki has ways to organize pages into categories of course, but they're somewhat cumbersome. Simply placing a link to a page titled `Category:Foo` in a page will place it into the "Foo" category and cause it to be listed on the "Foo" category page. This is convenient, but merely introduces a parallel way to organize pages: they still can't have the same name as any other page and categories mostly only provide a mechanism to automatically create lists of other pages.

A related item that I find weird is that because everything in MediaWiki is identified by a simple name, performing special actions like managing registered users occurs on pages with special names, such as `Special:UserLogin` to log in. The developers refer to `Special` here as a namespace which seems like a fair characterization (because colons are treated specially in page names), but [WWW](https://en.wikipedia.org/wiki/World_Wide_Web) technologies have successfully used slashes for the same purpose for over 30 years, so using colons seems like a strange choice.

### Markup annoyances

* Link to a category to place the page in it. Difficult to discover what pages are in a category if you're not MedaiWiki.
* It's generally pretty weird and no other system uses the same format.
* The templating system transcludes pages, so it's generally impossible to render a wiki without having the entire rest of the wiki as well so templates can be expanded.

## Doing something about it

Now that I've complained some about MediaWiki, what of it? Why do I care? Once again referring to Quinn Dombrowski for well-stated commentary:

> If you don’t take care of it, and don’t find (and probably pay) someone else to take care of it, you can try to give it away — but wise technical staff will balk at the offer of having to take on someone else’s Drupal site, particularly if it’s been neglected for some time. Once your project is done, if you’re not realistically going to devote the ongoing resources required for maintaining it indefinitely, it’s time to consider what it will take to “archive” it, shut it down in some orderly manner. In essence, the responsible decision is to euthanize the pony.

Unfortunately, I've somewhat inherited maintainership of three different MediaWiki instances that I don't want to have to think about. They don't require much thought as they are now (for instance because account creation has been configured to require manual approval to combat spam), but simply running the application on a server is still more effort than I want to put into managing those.

---

This is exactly what I sought to do with this project: I no longer wish to expend effort on maintaining a whole server, and it is often difficult to find somebody willing to take over maintenance. In the case of these wikis I want to avoid euthanizing the pony completely because I believe people still find the information useful, but by taking the wiki application out of the loop it's easier to keep everything online. It might become slightly more difficult to update the site content if not using MediaWiki but the problem of keeping everything online becomes much simpler and I'm quite happy to make that tradeoff, especially if the alternative would be letting the site slowly "starve to death" for want of maintenance.

## Alternatives

All of the wikis in question here are used for what amounts mostly to technical documentation, so it's useful to look at what some other major projects use and related tools:

* [Read the Docs](<* https://readthedocs.org/>) is a widely-used free hosted service for generating software reference documentation. It appears to be based on [Sphinx](https://www.sphinx-doc.org/) and can generate API documentation from code as well as serve textual documentation written in ReStructured Text.
* [Gitbook](https://www.gitbook.com/) is a commercial service mainly targeting human-written documentation sites (with similar use cases to most wikis) that builds web pages from Markdown files stored in Git.
* [mdBook](https://github.com/rust-lang/mdBook) seems to target a similar niche to Gitbook, but is completely open-source and probably somewhat less feature-rich. It doesn't seem to automatically generate an index of pages (requiring each new page to be manually added to the index as desired).
* Static site generators like [Hugo](https://gohugo.io/) (which I used for this web site!) take text from files (usually written in Markdown) and generate web pages, usually supporting taxonomies of pages (either via file organization or tagging individual files), though lacking good support for generating global indexes.
* [MkDocs](https://www.mkdocs.org/) is another static site generator geared to technical documentation that seems to fit between tools like Hugo and Read The Docs: it builds web pages from Markdown by auto-discovering documents and provides a browsable index, as well as supporting search.

For wiki-like documentation, I think it's particularly important that pages be easy to discover and browse. This usually means that a global index should exist, because otherwise finding documentation for something requires either guessing where it is (navigating categories to find it), searching for it (guessing some key words that relate to the topic and exist in the documentation) or relying on documentation authors to have provided a link.