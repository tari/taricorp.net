---
layout: page
title: MishaBot
date: 2012-06-27 16:11:10.000000000 -06:00
categories: []
tags: []
status: publish
type: page
---

MishaBot is a combination IRC bot and web interface that acts as a link
scraper.  The bot component connects to IRC and silently logs web links to a
database.  The web interface grabs links from the database and presents them to
the user.

{% comment %}
The best way to explain what it does is by demonstration, so run on over to <a
    href="http://mishabot.taricorp.net/">http://mishabot.taricorp.net/</a> to
see the web interface.</p>
{% endcomment %}

## Design

The IRC bot portion of the code is implemented in Python, on top of
[python-irclib][irclib] and communicates with an SQL database to store links.

[irclib]: http://python-irclib.sourceforge.net/

The web interface is decoupled into the server-side and client-side code. The
server side is implemented in Python on top of the Flask framework, but its
only purpose is to act as a database connector for the clients. The client-side
code is a lump of Javascript that handles polling the server for new data, then
presents it to the user.

I think this highly decoupled approach is better than the traditional approach
taken by web applications of having the server generate pages from templates,
since it forces all features to have accessible hooks, thus allowing alternate
clients to be easily designed, and it is easier to experiment with changes to
the presentation.

### Planned features

As long as this project continues to hold my interest, I'll be adding additional features. Some highlights of what I want to add:

 * Clean bot reloading. The database layer in use (SQLObject) doesn't handle
   reloading modules that use it gracefully, so simply reloading modules isn't
an option for applying code changes to a running instance of the bot.  To allow
new code to be loaded without disconnecting the bot from IRC, a new instance can
be started that receives state information from the currently running isntance.
To avoid dropping the open network connections, they can be passed to the new
instance via a UNIX domain socket.
 * Link filtering in the interface. The current version has some rudimentary
   filter capabilities (select a single channel to show), but there's room for
it to be much more capable.
 * Allow users on IRC to "subscribe" to the bot, to have it announce link
   information to them.

## Code

As with most of my projects, MishaBot is open-source, provided under the
zlib/libpng license.  The repository is over on
[Bitbucket](https://bitbucket.org/tari/mishabot/).
