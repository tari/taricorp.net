---
author: tari
comments: true
date: 2012-08-29 00:32:11+00:00
layout: post
slug: treating-configuration-as-code-with-pythons-import-hooks
title: Treating configuration as code with Python's import hooks
wordpress_id: 799
categories:
- Software
tags:
- configuration
- DSLs
- haskell
- hook
- import
- ini-file
- python
---

# Rationale

I was reading up on web frameworks available when programming in Haskell earlier
today, and I liked the use of domain-specific languages (DSLs) within frameworks
such as the [routing syntax in Yesod](http://www.yesodweb.com/). Compared to how
routes are specified [in
Django](https://docs.djangoproject.com/en/1.4/topics/http/urls/) (as a similar
example that I'm already familiar with), the DSL is both easier to read (because
it doesn't need to be valid code in the hosting language) and faster (since it
ends up getting compiled into the application as properly executable code).

A pattern I find myself using rather often in Python projects is to have a small
module (usually called config) that encapsulates an
[INI-style](https://en.wikipedia.org/wiki/INI_file) configuration file. It feels
like an ugly solution though, since it generally just exports a
[ConfigParser](https://docs.python.org/2/library/configparser.html) instance.
Combined with consideration of DSLs in Haskell, that got me thinking: what if
there were an easier way that made INI configuration files act like Python
source such that they could just be imported and have the contents of the file
exposed as simple Python types (thus hiding some unnecessary complexity)?

# Implementation

I was aware of Python's import hook mechanisms, so I figured that it should be a
good way to approach this problem, and it ended up being a good excuse to learn
more about the import hook mechanism. Thus, the following code provides a way to
expose INI-style configuration as Python modules. It should be compatible with
Python 3 after changing the import of ConfigParser on line 1 to configparser,
but I only tested it on Python 2.7.

```python
import ConfigParser, imp, os, sys

class INILoader(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def load_module(self, name):
        if name in sys.modules:
            return sys.modules[name]

        module = imp.new_module(name)
        if name == self.prefix:
            # 'from config import foo' gets config then config.foo,
            # so we need a dummy package.
            module.__package__ = name
            module.__path__ = []
            module.__file__ = __file__
        else:
            # Try to find a .ini file
            module.__package__, _, fname = name.rpartition('.')
            fname += '.ini'
            module.__file__ = fname
            if not os.path.isfile(fname):
                raise ImportError("Could not find a .ini file matching " + name)
            else:
                load_ini_module(fname, module)

        sys.modules[name] = module
        return module

    def find_module(self, name, path=None):
        if name.startswith(self.prefix):
            return self
        else:
            return None

def load_ini_module(f, m):
    """Load ini-style file ``f`` into module ``m``."""
    cp = ConfigParser.SafeConfigParser()
    cp.read(f)
    for section in cp.sections():
        setattr(m, section, dict(cp.items(section)))

def init(package='config'):
    """Install the ini import hook for the given virtual package name."""
    sys.meta_path.append(INILoader(package))
```

Most of this code should be fairly easy to follow. The magic of the import hook
itself is all in the INILoader class, and exactly how that works is specified in
[PEP 302](http://legacy.python.org/dev/peps/pep-0302/).

# Usage

So how do you use this? Basically, you must simply run init(), then any imports
from the specified package (config by default) will be resolved from an .ini
file rather than an actual Python module. Sections in a file are exposed as
dictionaries under the module.

An example is much more informative than the preceding short description, so
here's one. I put the code on my Python path as INIImport.py and created foo.ini
with the following contents:

    
    [cat]
    sound=meow
    [dog]
    sound=woof
    [cow]
    sound=moo

It has three sections, each describing an animal. Now I load up a Python console
and use it:
    
    >>> import INIImport
    >>> INIImport.init()
    >>> from config import foo
    >>> foo.cat
    {'sound': 'meow'}
    >>> foo.dog['sound']
    'woof'

This has the same semantics as a normal Python module, so it can be reloaded or
aliased just like any other module:
    
    >>> import config.foo
    >>> foo == config.foo
    True
    >>> reload(config.foo)
    <module 'config.foo' from 'foo.ini'>

The ability to reload this module is particularly handy, because my normal
configuration module approach doesn't provide an easy way to reload the file.

## Improvements, Limitations

Some addition improvements come to mind if I were to release this experiment as
production-quality code. Notably, additional path manipulations for finding .ini
files would be useful, such as taking a path argument to init(), supplying a set
of directories to search within. Having a way to remove the import hook that it
installs would also be good, and straightforward to implement. There's no way to
get all the sections in the module, so it would also be useful to export the
sections somehow-- perhaps by having the module support the mapping protocol (so
all the sections could be retrieved with module.items(), for example).

The main limitation of this scheme is that it has no way to determine the
desired type of loaded configuration values, so everything is a string. This is
a typical limitation when using the ConfigParser module, but compared to a more
robust configuration scheme such as defining objects in a Python file (such as
Django does), this might be an annoying loss of expressiveness. The values can
always be coerced to the required type when retrieving them, but that's a bit of
unnecessary extra code in whatever uses the configuration.

It may also be useful to provide a way to write configuration back to a file
when modifying a config module, but my simplistic implementation makes no
attempt at such. Doing so would not be terribly difficult, just involving some
wrapper objects to handle member assignment for sections and items, then
providing a mechanism for saving the current values back to the original file.

## Postlude

This made for an interesting experiment, and it should be a handy example for
how to implement import hooks in Python. You may use this code freely within
your own work, but I'd appreciate if you leave a note here that it was useful,
and link back to this post.
