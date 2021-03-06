---
date: 2016-05-27
title: sax-ng
slug: sax-ng
subtitle: Building a small chat service
categories:
 - Software
 - Linux
tags:
 - cemetech
 - sax
 - xmpp
 - chat
 - ejabberd
 - irc
 - javascript
 - http
 - python
---

Over on [Cemetech][cemetech], we've long had an embedded chat widget called
"SAX" ("Simultaneous Asynchronous eXchange"). It behaves kind of like a
traditional shoutbox, in that registered users can use the SAX widget to chat in
near-real-time. There is also a bot that relays messages between the on-site
widget and an IRC channel, which we call "saxjax".

[cemetech]: https://www.cemetech.net/

The implementation of this, however, was somewhat lacking in efficiency. It was
first implemented around [mid][sax1]-[2006][sax2], and saw essentially no
updates until just recently. The following is a good example of how dated the
implementation was:

[sax1]: https://www.cemetech.net/news.php?year=2006&month=all&id=225
[sax2]: https://www.cemetech.net/forum/viewtopic.php?t=2022

```javascript
// code for Mozilla, etc
if (window.XMLHttpRequest) {
    xmlhttp=new XMLHttpRequest()
    xmlhttp.onreadystatechange=state_Change
    xmlhttp.open("GET",url,true)
    xmlhttp.send(null)
} else if (window.ActiveXObject) {
    // code for IE
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP")
    if (xmlhttp) {
        xmlhttp.onreadystatechange=state_Change
        xmlhttp.open("GET",url,true)
        xmlhttp.send()
    }
}
```

The presence of `ActiveXObject` here implies it was written at a time when a
large fraction of users would have been using Internet Explorer 5 or 6 (the
first version of Internet Explorer released which supported the standard form of
`XMLHttpRequest` was version 7).

Around a year ago (that's how long this post has been a draft for!), I took it
upon myself to design and implement a more modern replacement for SAX. This post
discusses that process and describes the design of the replacement, which I have
called "sax-ng."

<!-- more -->

## Legacy SAX

The original SAX implementation, as alluded to above, is based on AJAX polling.
On the server, a set of approximately the 30 most recent messages were stored in
a MySQL database and a few PHP scripts managed retrieving and modifying messages
in the database. This design was a logical choice when initially built, since
the web site was running on a shared web host (supporting little more than PHP
and MySQL) at the time.

Eventually this design became a problem, as essentially every page containing
SAX that is open at any given time regularly polls for new messages. Each poll
calls into PHP on the server, which opens a database connection to perform one 
query. Practically, this means a very large number of database connections being
opened at a fairly regular pace. In mid-2012 the connection count reached levels
where the shared hosting provider were displeased with it, and requested that we
either pay for a more expensive hosting plan or reduce resource usage.

In response, we temporarily disabled SAX, then migrated the web site to a
dedicated server provided by [OVH][ovh], who had opened a new North American
datacenter in July. We moved to the dedicated server in August of 2012. This
infrastructure change kept the system running, and opened the door to a more
sophisticated solution since we gained the ability to run proper server
applications.

[ovh]: https://www.ovh.com/us/

---

Meanwhile, the limitations of saxjax (the IRC relay bot) slowly became more
evident over time. The implementation was rather ad-hoc, in Python. It used two
threads to implement relay, with a dismaying amount of shared state used to
relay messages between the two threads. It tended to stop working correctly in
case of an error in either thread, be it due to a transient error response from
polling the web server for new messages, or an encoding-related exception thrown
from the IRC client (since Python 2.x uses bytestrings for most tasks unless
specifically told not to, and many string operations (particularly outputting
the string to somewhere) can break without warning when used with data that is
not 8-bit clean (that is, basically anything that isn't ASCII).

Practically, this meant that the bot would frequently end up in a state where it
would only relay messages one way, or relay none at all. I put some time into
making it more robust to these kinds of failures early in 2015, such that some
of the time it would manage to catch these errors and outright restart (rather
than try to recover from an inconsistent state). Doing so involved some pretty
ugly hacks though, which prompted a return to some longtime thoughts on how SAX
could be redesigned for greater efficiently and robustness.

## sax-ng

For a long time prior to beginning this work, I frequently (semi-jokingly)
suggested XMPP (Jabber) as a solution to the problems with SAX. At a high level
this seems reasonable: XMPP is a chat protocol with a number of different
implementations available, and is relatively easy to set up as a private chat
service.

On the other hand, the feature set of SAX imposes a few requirements which are
not inherently available for any given chat service:

1. An HTTP gateway, so clients can run inside a web browser.
2. Group chat, not just one-to-one conversation capability.
3. External authentication (logging in to the web site should permit connection
   to chat as well).
4. Retrieval of chat history (so a freshly-loaded page can have some amount of
   chat history shown).

As it turns out, [ejabberd][ejabberd] enables all of these, with relatively
little customization. `mod_http_bind` provides an HTTP gateway as specified in
[XEP-0206][xep-0206], `mod_muc` implements multi-user chat as specified in
[XEP-0045][xep-0045] which also includes capabilities to send chat history to
clients when they connect, and authentication can be handled by an [external
program][extauth] which speaks a simple binary protocol and is invoked by
ejabberd.

[ejabberd]: https://www.ejabberd.im/
[xep-0045]: https://xmpp.org/extensions/xep-0045.html
[xep-0206]: https://xmpp.org/extensions/xep-0206.html
[extauth]: http://docs.ejabberd.im/admin/guide/configuration/#external-script

Main implementation of the new XMPP-based system was done in about a week,
perhaps 50 hours of concerted work total (though I may be underestimating). I
had about a month of "downtime" at the beginning of this past summer,
the last week of which was devoted to building sax-ng.

### ejabberd

The first phase involved setting up an instance of ejabberd to support the rest
of the system. I opted to run it inside [Docker][docker], ideally to make the
XMPP server more self-contained and avoid much custom configuration on the
server. Conveniently, somebody had already built a [Docker configuration for
ejabberd][docker-ejabberd] with a wealth of configuration switches, so it was
relatively easy to set up.

[docker]: https://www.docker.com/
[docker-ejabberd]: https://github.com/rroemhild/docker-ejabberd

Implementing authentication against the web site was also easy, referring to the
protocol description in the [ejabberd developers guide][ejabberd-dev-guide].
Since this hooks into the website's authentication system (a highly modified
version of phpBB), this script simply connects to the mysql server and runs
queries against the database.

Actual authentication is performed with phpBB SIDs (Session ID), rather than a
user's password. It was built this way because the SID and username are stored
in a cookie, which is available to a client running in a web browser. This is
probably also somewhat more secure than storing a password in the web browser,
since the SID is changed regularly so data exposure via some vector cannot
compromise a user's web site password.

[ejabberd-dev-guide]: https://www.ejabberd.im/files/doc/dev.html#htoc8

Error handling in the authentication script is mostly nonexistent. The Erlang
approach to such problems is mostly "restart the component if it fails", so in
case of a problem (of which the only real possibility is a database connection
error) ejabberd will restart the authentication script and attempt to carry on.
In practice this has proven to be perfectly reliable.

---

In XMPP MUC (Multi-User Chat), users are free to choose any nickname they wish.
For our application, there is really only one room and we wish to enforce that
the nickname used in XMPP is the same as a user's username on the web site.
There ends up being no good way in ejabberd to require that a user take a given
nickname, but we can ensure that it is impossible to impersonate other users by
registering all site usernames as nicknames in XMPP. Registered nicknames may
only be used by the user to which they are registered, so the only
implementation question is in how to automatically register nicknames.

I ended up writing a small patch to `mod_muc_admin`, providing an `ejabberdctl`
subcommand to register a nickname. This patch is included in its entirety below.

```diff
diff --git a/src/mod_muc_admin.erl b/src/mod_muc_admin.erl
index 9c69628..3666ba0 100644
--- a/src/mod_muc_admin.erl
+++ b/src/mod_muc_admin.erl
@@ -15,6 +15,7 @@
     start/2, stop/1, % gen_mod API
     muc_online_rooms/1,
     muc_unregister_nick/1,
+    muc_register_nick/3,
     create_room/3, destroy_room/3,
     create_rooms_file/1, destroy_rooms_file/1,
     rooms_unused_list/2, rooms_unused_destroy/2,
@@ -38,6 +39,9 @@
 
 %% Copied from mod_muc/mod_muc.erl
 -record(muc_online_room, {name_host, pid}).
+-record(muc_registered,
+        {us_host = {\{<<"">>, <<"">>}, <<"">>} :: {\{binary(), binary()}, binary()} | '$1',
+         nick = <<"">> :: binary()}).
 
 %%----------------------------
 %% gen_mod
@@ -73,6 +77,11 @@ commands() ->
               module = ?MODULE, function = muc_unregister_nick,
               args = [{nick, binary}],
               result = {res, rescode}},
+     #ejabberd_commands{name = muc_register_nick, tags = [muc],
+              desc = "Register the nick in the MUC service to the JID",
+              module = ?MODULE, function = muc_register_nick,
+              args = [{nick, binary}, {jid, binary}, {domain, binary}],
+              result = {res, rescode}},
 
      #ejabberd_commands{name = create_room, tags = [muc_room],
               desc = "Create a MUC room name@service in host",
@@ -193,6 +202,16 @@ muc_unregister_nick(Nick) ->
        error
     end.
 
+muc_register_nick(Nick, JID, Domain) ->
+    {jid, UID, Host, _,_,_,_} = jlib:string_to_jid(JID),
+    F = fun (MHost, MNick) ->
+                mnesia:write(#muc_registered{us_host=MHost,
+                                             nick=MNick})
+        end,
+    case mnesia:transaction(F, [{\{UID, Host}, Domain}, Nick]) of
+        {atomic, ok} -> ok;
+        {aborted, _Error} -> error
+    end.
 
 %%----------------------------
 %% Ad-hoc commands
```

It took me a while to work out how exactly to best implement this feature, but
considering I had never worked in Erlang before it was reasonably easy. I do
suspect some familiarity with Haskell and Rust provided background to more
easily understand certain aspects of the language, though. The requirement
that I duplicate the `muc_registered` record (since apparently Erlang provides
no way to import records from another file) rubs me the wrong way, though.

In practice, then, a custom script traverses the web site database, invoking
`ejabberdctl` to register the nickname for every existing user at server startup
and then periodically or on demand when the server is running.

### Web interface

The web interface into XMPP was implemented with
[Strophe.js](http://strophe.im/), communicating with ejabberd via HTTP-bind with
the standard support in both the client library and server.

The old SAX design served a small amount of chat history with every page load so
it was immediately visible without performing any additional requests after page
load, but since the web server never receives chat data (it all goes into XMPP
directly), this is no longer possible. The MUC specification allows a server to
send chat history to clients when they join a room, but that still requires
several HTTP round-trips (taking up to several seconds) to even begin receiving
old lines.

I ended up storing a cache of messages in the browser, which is used to populate
the set of displayed messages on initial page load. Whenever a message is
received and displayed, its text, sender and a timestamp are added to the local
cache. On page load, messages from this cache which are less than one hour old
are displayed. The tricky part with this approach is avoiding duplication of
lines when messages sent as part of room history already exist, but checking the
triple of sender, text and timestamp seems to handle these cases quite reliably.

### webridge

The second major feature of SAX is to announce activity on the web site's
bulletin board, such as when people create or reply to threads. Since the entire
system was previously managed by code tightly integrated with the bulletin
board, a complete replacement of the relevant code was required.

In the backend, SAX functionality was implemented entirely in one PHP function,
so replacing the implementation was relatively easy. The function's signature
was something like `saxSay($type, $who, $what, $where)`, where `type` is a magic
number indicating what kind of message it is, such as the creation of a new
thread, a post in a thread or a message from a user. The interpretation of the
other parameters depends on the message type, and tends to be somewhat
inconsistent.

The majority of that function was a maze of comparisons against the message
type, emitting a string which was eventually pushed into the chat system. Rather
than attempt to make sense of that code, I decided to replace it with a `switch`
statement over symbolic values (whereas the old code just used numbers with no
indication of purpose), feeding simple invocations of `sprintf`. Finding the
purpose of each of the message types was most challenging among that, but it
wasn't terribly difficult as I ended up searching the entire web site source
code for references to `saxSay` and determined the meaning of the types from the
caller's context.

---

To actually feed messages from PHP into XMPP, I wrote a simple relay bot which
reads messages from a UNIX datagram socket and repeats them into a MUC room. A
UNIX datagram socket was selected because there need not be any framing
information in messages coming in (just read a datagram and copy its payload),
and this relay should not be accessible to anything running outside the same
machine (hence a UNIX socket).

The bot is implemented in Python with [Twisted][twisted], utilizing Twisted's
provided protocol support for XMPP. It is run as a service under `twistd`, with
configuration provided via environment variables because I didn't want to write
anything to handle reading a more "proper" configuration file. When the PHP code
calls `saxSay`, that function connects to a socket with path determined from web
site configuration and writes the message into that socket. The relay bot
("webridge") receives these messages and writes them into MUC.

[twisted]: https://twistedmatrix.com/

### saxjax-ng

Since keeping a web page open for chatting is not particularly convenient, we
also operate a bridge between the SAX chat and an IRC channel called saxjax. The
original version of this relay bot was of questionable quality at best: the
Python implementation ran two threads, each providing one-way communication
though a list. No concurrency primitives, little sanity.

Prior to creation of sax-ng I had put some amount of effort in improving the
reliability of that system, since an error in either thread would halt all
processing of messages in the direction corresponding to the thread in which the
error occurred. Given there was essentially no error handling anywhere in the
program, this sort of thing happened with dismaying frequency.

saxjax-ng is very similar in design to webridge, in that it's Twisted-based and
uses the Twisted XMPP library. On the IRC side, it uses Twisted's IRC library
(shocking!). Both ends of this end up being very robust when combined with
the components that provide automatic reconnection and a little bit of custom
logic for rotating through a list of IRC servers. Twisted guarantees
singlethreaded operation (that's the whole point; it's an async event loop), so
relaying a message between the two connections is simply a matter of repeating it
on the other connection.

## Contact with users

This system has been perfectly reliable since deployment, after a few changes.
Most notably, the http-bind interface for ejabberd was initially exposed on port
5280 (the default for http-bind). Users behind certain restrictive firewalls
can't connect to that port, so we quickly reconfigured our web server to
reverse-proxy to http-bind and solve that problem. Doing so also means the XMPP
server doesn't need its own copy of the server's SSL certificate.

There are still some pieces of the web site that emit messages containing HTML
entities in accordance with the old system. The new system.. doesn't emit HTML
entities because that should be the responsibility of something doing HTML
presentation (Strong Opinion) and I haven't bothered trying to find the things
that are still emitting HTML-like strings.

The reconnect logic on the web client tends to act like it's received multiples
of every message that arrives after it's tried to reconnect to XMPP, such as
when a user puts their computer to sleep and later resumes; the web client tries
to detect the lost connection and reopen it, and I think some event handlers
are getting duplicated at that point. Haven't bothered working on a fix for that
either.

# Conclusion

ejabberd is a solid piece of software and not hard to customize. Twisted is a
good library for building reliable network programs in Python, but has enough
depth that some of its features lack useful documentation so finding what you
need and figuring out how to use it can be difficult. This writeup has been
languishing for too long so I'm done writing now.
