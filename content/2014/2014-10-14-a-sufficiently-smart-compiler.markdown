---
author: tari
comments: true
date: 2014-10-14 04:32:15+00:00
slug: a-sufficiently-smart-compiler
title: '"A Sufficiently Smart Compiler"'
wordpress_id: 1119
categories:
- Software
tags:
- bugs
- clang
- compilers
- emscripten
- javascript
- llvm
- ub
---

On a bit of a lark today, I decided to see if I could get
[Spasm](https://wabbit.codeplex.com/) running in a web browser via
[Emscripten](http://kripken.github.io/emscripten-site/). I was
[successful](http://www.cemetech.net/forum/viewtopic.php?p=224677), but found
that something seemed to be optimizing out most of `main()` such that I had to
hack in my own main function that performed the same critical functions and (for
the sake of simplicity) hard-coded the relevant command-line options.

Looking into the problem a bit further, I observed that not all of `main()` was
being removed; there was one critical line left in. The beginning of the
function in source and the generated code were as follows.

C++ source:

```c++
int main (int argc, char **argv)
{
        int curr_arg = 1;
        bool case_sensitive = false;
        bool is_storage_initialized = false;

        use_colors = true;
        extern WORD user_attributes;
        user_attributes = save_console_attributes ();
        atexit (restore_console_attributes_at_exit);

        //if there aren't enough args, show info
        if (argc < 2) {
```

Generated Javascript (asm.js):

```javascript
function _main($argc, $argv) {
    $argc = $argc | 0;
    $argv = $argv | 0;
    HEAP8[4296] = 1;
    __Z23save_console_attributesv() | 0;
    return 0;
}
```

Spasm is known to work in general, but I found it unlikely that LLVM's optimizer
would be optimizing this code wrong as well. Building with optimizations turned
off generated correct code, so it was definitely the optimizer breaking this and
not some silly bug in Emscripten. Looking a little deeper into the
`save_console_attributes` function, we see the following code:

```c++    
WORD save_console_attributes () {
#ifdef WIN32
        CONSOLE_SCREEN_BUFFER_INFO csbiScreenBufferInfo;
        GetConsoleScreenBufferInfo (GetStdHandle (STD_OUTPUT_HANDLE), &csbiScreenBufferInfo);
        return csbiScreenBufferInfo.wAttributes;
#endif
}

<!-- more -->

Since I'm not building for a Windows target (Emscripten's runtime environment
resembles a Unix-like system), this was preprocessed down to an empty function
(returning `void`), but it's declared with a non-`void` return. Smells like
[undefined behavior](http://blog.regehr.org/archives/213)! Let's make this
function return 0:

```c++
WORD save_console_attributes () {
#ifdef WIN32
        CONSOLE_SCREEN_BUFFER_INFO csbiScreenBufferInfo;
        GetConsoleScreenBufferInfo (GetStdHandle (STD_OUTPUT_HANDLE), &csbiScreenBufferInfo);
        return csbiScreenBufferInfo.wAttributes;
#else
        return 0;
#endif
}
```

With that single change, I now get useful code in `main`. Evidently LLVM's
optimizer was smart enough to recognize the call to that function invoked UB and
optimized out the rest of `main`.

## Concluding

This issue illustrates nicely the dangers of a sufficiently smart compiler,
where updates to your compiler might break otherwise-working code because it's
subtly broken. This is particularly of concern in C, where the compilers tend to
go to extreme measures to optimize the generated code and there are a lot of
ways to inadvertently invoke undefined behavior.

Static analyzers are a big help in finding these issues. Looking more closely at
the compiler output from building Spasm, it emitted a warning regarding this
function, as well as several potential buffer overflows of the following form:
    
```c++
    char s[64];
    strncat(s, "/", sizeof(s));
```

This looks correct, but is subtly broken because the length parameter taken by
`strncat` should be the maximum allowed length of the string, excluding the null
terminator. The third parameter should be `sizeof(s) - 1` in this case,
otherwise the string's null terminator might be written out of bounds.

## Appendix

The code for my work on this is up on
[Bitbucket](https://bitbucket.org/tari/spasm-emscripten/overview) and might be
of interest to some readers. I fear that by working on this project I've
inadvertently committed to becoming the future maintainer of Spasm, which I find
to contain a significant amount of poor-quality code. Perhaps I'll have to write
a replacement for Spasm in [Rust](http://www.rust-lang.org/), which I've been
quite pleased with as a potential replacement for C, without the numerous
pitfalls and rather more modern in its capabilities.
