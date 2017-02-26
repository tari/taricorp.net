---
layout: page
title: GCNClient GUI
date: 2011-12-11 01:12:08.000000000 -07:00
categories: []
tags: []
status: publish
type: page
published: true
---

This is a basic GUI for configuring the [globalCalcNet][gcn] client program,
written in C#.  It's known to work on Windows, and should be capable of
operating properly on non-Windows platforms with minimal modification. You may
also want to see the [discussion thread for this program on
Cemetech][discussion].

<figure>
    <img src="/images/2011/clientgui-1.1.png" />
</figure>

# Download

Current version is 1.1.
[Installer](/images/2011/GCN-Client-GUI.zip)
and [ZIP
archive](/images/2011/GCNClient_GUI.zip)
(program only) are available. If you're interested in seeing how it does
something or modifying it, you can also grab the [source package](/images/2011/gcnclientGUI-1.1-src.zip).

If you are unable to run the program, ensure you have the .NET 3.5 or newer
runtimes (or equivalent, for non-Windows systems) installed. It can be
downloaded [from Microsoft][dotnet]. For non-Windows systems, [Mono][mono]
should do the job.

### Old versions

1.0: [Binary package](/images/2011/gcnclientgui.zip) (for .NET 4.0 of newer,
includes Windows binary for the client itself), or [source
package](/images/2011/gcnclientGUI-src.zip) (Visual Studio 2010 project).

# Troubleshooting

If it doesn't work, ensure the [gcnclient
program](http://www.ticalc.org/archives/files/fileinfo/434/43462.html) itself
works properly before complaining to me.  You can get detailed output from the
client program itself by checking the "Show output window" box. In most cases,
failures are related to misconfigurations in libusb.  There's a little
[bit of discussion](http://www.cemetech.net/forum/viewtopic.php?t=6556)
of the project over on Cemetech, which is a good place to ask for help (I hang
out there as well).

When the client exits with 0xC0000135, the GUI says to "see the help", which
doesn't exist (except this is it).  This error is due to a libusb
misconfiguration making the client unable to start, but shouldn't occur anymore
since version 1.1, since it now includes the requisite libusb dependencies.

[gcn]: http://www.cemetech.net/projects/item.php?id=35
[discussion]: http://www.cemetech.net/forum/viewtopic.php?t=6556
[dotnet]: https://www.microsoft.com/en-us/download/details.aspx?displaylang=en&id=17851
[mono]: http://www.mono-project.com/Main_Page
