---
title: Marking token boundaries in TI-BASIC with Unicode magic
slug: ti-basic-unicode-splits
draft: true
date: 2022-05-25T03:01:18.380Z
---
Users who are accustomed to writing TI-BASIC on computers in plain text like any other programming language are probably familiar with sometimes needing to explicitly mark where token boundaries occur. 
Perhaps the most common example of needing to do this is when the string "pi" appears in a string and it must be written as "p\i" to prevent the tokenizer from converting it to "π". This approach was first used in [Token](https://www.cemetech.net/downloads/files/515)[IDE](url=https://www.ticalc.org/archives/files/fileinfo/433/43315.html) and is also supported by [SourceCoder](https://www.cemetech.net/sc/).

It's surprisingly tricky to detect when a break like this needs to be inserted when converting tokens back into plain text, as [url=https://www.cemetech.net/forum/viewtopic.php?p=296823]discussed previously here on Cemetech[/url]: TI-BASIC (at least the 8x variant) was designed to only ever be written in tokens, so (as long as we use the same strings for each token that the calculator displays) some way to mark token boundaries is required where a suffix of the concatenation of two valid tokens is also valid as another token.
Since that formalism is a little confusing when written in words, an example: if we have tokens "a", "ab", "bc", and "c" then without any token break indicator it is ambiguous how to tokenize the plaintext string "abc": it could be [a, bc] or [ab, c]. Inserting a break (\) disambiguates "a\bc" as [a, bc] and "ab\c" as [ab, c].

---

That's all well and good, but backslashes are kind of ugly and break the flow when you're reading code (even if they are necessary due to the language design). It occurs to me that Unicode has thousands of interesting characters, at least some of which could be used as explicit token breaks like we typically use backslash for while making code somewhat nicer to read.

[Unicode TR14](https://www.unicode.org/reports/tr14/) describes the blessed Unicode line breaking algorithm that guides when it is permitted to split text across multiple lines inside a block of text. While not strictly useful for the desired application of splitting tokens with no or little effect on how the code looks to humans, it does provide some pointers to interesting characters, including:
 * Glue characters like Zero Width Joiner (ZWJ), U+200D: an invisible character that prevents breaking the text on either side of it (of particular use in emoji sequences as described by [TR51](https://www.unicode.org/reports/tr51/)!). The opposite of what we want.
 * Next Line (NEL), U+0085: forces the following text to appear on a new line. This behaves the same as most programmers[^typewriters] would expect a Carriage Return or Line Feed character (or the combination of the two) to behave, and it turns out that section 5.8 of the Unicode standard spends many paragraphs on suggesting how applications treat each of the possible newline characters. The variety of options exist largely due to historical differences in how computer systems record line breaks, where `NEL` in particular is probably unfamiliar to most because it was used by [EBCDIC](https://en.wikipedia.org/wiki/EBCDIC) computers which were mostly IBM machines and are very uncommon these days. Interesting, but not useful for this application.
 * Assorted punctuation, such as '!', '}' and '['. These forbid line breaks before or after them depending on the orientation, such as ')' forbidding a break before it because a close parentheses logically binds to the text that precedes it. Getting closer, but line breaks aren't really relevant to wanting to mark the boundaries between tokens.

[^typewriters]: typewriter users might also recognize these terms, since they were included in the ASCII character set in 1967 due to their importance to teletypes, where there is a physical distinction between simply advancing the feed by one line and moving the carriage back to the start of the line.

Right next to ZWJ in the code space we find an interesting character: U+200D `ZERO WIDTH NON-JOINER` (ZWNJ). Unicode Section 23.2 says this (and ZWJ for the opposite) is designed to mark where connections between characters are forbidden, as in cursive scripts or if a [ligature](https://en.wikipedia.org/wiki/Ligature_(writing)) might be used. Inserting a ZWNJ between two characters that might otherwise be joined forces them to be disconnected.

If one figuratively squints at the intent of ZWNJ, it seems similar to the needs outlined for TI-BASIC: we want to prevent characters from running together in some situations. Where normally a tokenizer will eagerly join characters into tokens, a ZWNJ could be inserted as a break character that is otherwise invisible to human readers.

<table>
  <tr><th>Split mode</th><th>Plaintext</th><th>Tokenized</th></tr>
  <tr><td>None</td><td><code>Disp "I like to eat pie</code></td><td><code>Disp "I like to eat pie</code</td></tr>
  <tr><td>Traditional</td><td><code>Disp "I like to eat p\ie</code></td><td><code>Disp "I like to eat pie</code></td></tr>
  <tr><td>Invisible</td><td><code>Disp "I like to eat p&zwnj;ie</code></td><td><code>Disp "I like to eat pie</code</td></tr>
</table>