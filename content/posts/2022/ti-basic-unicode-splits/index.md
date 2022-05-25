---
title: Marking token boundaries in TI-BASIC with Unicode magic
slug: ti-basic-unicode-splits
draft: true
date: 2022-05-25T03:01:18.380Z
---
Users who are accustomed to writing TI-BASIC on computers in plain text like any other programming language are probably familiar with sometimes needing to explicitly mark where token boundaries occur. I've been doing some thinking about this lately, and have arrived at a proposal for a way to improve the situation for some uses.

## Background

8x calculators support a dialect of BASIC that we refer to as TI-BASIC (which is distinct from the dialects supported on other calculator families but similar).

TI-BASIC is tokenized.

## The need for breaks

As alluded to in the beginning, because the canonical representation of TI-BASIC is as a stream of tokens, sometimes an marker needs to be inserted in the textual representation of that stream of tokens that indicates where a string that might be interpreted as a single token should instead be interpreted as multiple tokens.

Perhaps the most common example of needing to do this is when the string "pi" appears in a string and it must be written as "p**\\**i" to prevent the tokenizer from converting it to "π". This approach of inserting a backslash was first used in [Token](https://www.cemetech.net/downloads/files/515)[IDE](url=https://www.ticalc.org/archives/files/fileinfo/433/43315.html) and is also supported by [SourceCoder](https://www.cemetech.net/sc/).

It's surprisingly tricky to detect when a break like this needs to be inserted when converting tokens back into plain text, as [discussed previously on on Cemetech](https://www.cemetech.net/forum/viewtopic.php?p=296823): TI-BASIC (at least the 8x variant) was designed to only ever be written in tokens, so (as long as we use the same strings for each token that the calculator displays) some way to mark token boundaries is required where a suffix of the concatenation of two valid tokens is also valid as another token.

Since that formalism is a little confusing when written in words, an example: if we have tokens "`a`", "`ab`", "`bc`", and "`c`" then without any token break indicator it is ambiguous how to tokenize the plaintext string "`abc`": it could be [`a`, `bc`] or [`ab`, `c`]. Inserting a break (`\`) disambiguates "`a\bc`" as [`a`, `bc`] and "`ab\c`" as [`ab`, `c`]. If detokenizing [`ab`,`c`], the output suffix "`bc`" when encountering the `c` token is also a valid token so we know a break must be inserted to disambiguate.

---

That's all well and good, but backslashes are kind of ugly and break the flow when you're reading code (even if they are necessary due to the language design). It occurs to me that Unicode has thousands of interesting characters, at least some of which could be used as explicit token breaks like we typically use backslash for while making code somewhat easier for humans to read.

## Exploring Unicode alternatives

[Unicode TR14](https://www.unicode.org/reports/tr14/) describes the blessed Unicode line breaking algorithm that guides when it is permitted to split text across multiple lines inside a block of text. While not strictly useful for the desired application of splitting tokens with no or little effect on how the code looks to humans, it does provide some pointers to interesting characters, including:
 * Glue characters like Zero Width Joiner (ZWJ), U+200D: an invisible character that prevents breaking the text on either side of it (of particular use in emoji sequences as described by [TR51](https://www.unicode.org/reports/tr51/)!). The opposite of what we want.
 * Next Line (NEL), U+0085: forces the following text to appear on a new line. This behaves the same as most programmers[^typewriters] would expect a Carriage Return or Line Feed character (or the combination of the two) to behave, and it turns out that section 5.8 of the Unicode standard spends many paragraphs on suggesting how applications treat each of the possible newline characters. The variety of options exist largely due to historical differences in how computer systems record line breaks, where `NEL` in particular is probably unfamiliar to most because it was used by [EBCDIC](https://en.wikipedia.org/wiki/EBCDIC) computers which were mostly IBM machines and are very uncommon these days. Interesting, but not useful for this application.
 * Assorted punctuation, such as '!', '}' and '['. These forbid line breaks before or after them depending on the orientation, such as ')' forbidding a break before it because a close parentheses logically binds to the text that precedes it. Getting closer, but line breaks aren't really relevant to wanting to mark the boundaries between tokens.

[^typewriters]: typewriter users might also recognize these terms, since they were included in the ASCII character set in 1967 due to their importance to teletypes, where there is a physical distinction between simply advancing the feed by one line and moving the carriage back to the start of the line.

Right next to ZWJ in the code space we find an interesting character: U+200D `ZERO WIDTH NON-JOINER` (ZWNJ). Unicode Section 23.2 says this (and ZWJ for the opposite) is designed to mark where connections between characters are forbidden, as in cursive scripts or if a [ligature](https://en.wikipedia.org/wiki/Ligature_(writing)) might be used. Inserting a ZWNJ between two characters that might otherwise be joined forces them to be disconnected.

### ZWNJ

If one figuratively squints at the intent of ZWNJ, it seems similar to the needs outlined for TI-BASIC: we want to prevent characters from running together in some situations. Where normally a tokenizer will eagerly join characters into tokens, a ZWNJ could be inserted as a break character that is otherwise invisible to human readers.

With this in mind, we could label the use of a backslash to escape tokens as the traditional method and compare it to use of ZWNJ (call it "invisible" breaks) or doing nothing:

<table>
  <tr><th>Split mode</th><th>Plaintext</th><th>Tokenized</th></tr>
  <tr><td>None</td><td><code>Disp "I like to eat pie</code></td><td><code>Disp "I like to eat &pi;e</code</td></tr>
  <tr><td>Traditional</td><td><code>Disp "I like to eat p\ie</code></td><td><code>Disp "I like to eat pie</code></td></tr>
  <tr><td>Invisible</td><td><code>Disp "I like to eat p&zwnj;ie</code></td><td><code>Disp "I like to eat pie</code</td></tr>
</table>

As already established, not inserting a break is ambiguous and because tokenizers must take the longest prefix of a given input as a token:[^prefix] the "pi" ends up incorrectly transformed to the Greek letter pi. In the traditional break style, we insert a backslash to force "pi" to be interpreted as two Latin letters rather than being translated to the Greek pi token.

[^prefix]: This requirement may not be obvious: if there are two tokens "Y" and "Yellow" for instance, given input "Yellow" a tokenizer must choose the longer of the tokens matching the input (namely, "Yellow"). If it did not, it would be impossible to reliably recognize the token "Yellow" because "Y" might be treated as a token instead, leaving "ellow" to be tokenized separately.

In the invisible mode, there is still a break present but it is **not visible in the written text**: I have inserted a ZWNJ character (HTML `&zwnj;`) which can be interpreted by a tokenizer in the same way as a backslash (which is to say, ignored other than forcing a token split).

## Discussion

Although I'm pleased with the idea to insert ZWNJs into human-readable BASIC programs, doing so in general seems limited by readers' needs to only some contexts although it also offers some interestig possibilities.

If a person might visually read out the plaintext source code and convert it to tokens (such as by typing it into a physical calculator), the loss of visual breaks means that the human must attempt to resolve any ambiguities that appear. While an experienced TI-BASIC programmer can probably discern intent from the program's context in order to disambiguate, **depending on a reader's skill seems like a suboptimal solution**. As a counterpoint however, a novice programmer may not even be familiar with the backslash-as-break "traditional" convention either: in that case invisible breaks could be superior.

If a user is expected to be able to copy and paste Unicode text to convert it into tokens (such as in source code published to the web, like this article), invisible splits are convenient and easy to read as long as tokenizers can be assumed to understand them. If a user might do visual transcription (such as manually typing code from a book into a calculator), traditional (visible) splits may be preferred.

### Increasing break frequency

Invisible breaks also present an interesting opportunity to mark more token boundaries than only those required to disambiguate textual source code: what if a ZWNJ were inserted on **every token boundary**? Doing so would make a given program's source code forward-compatible with alternate token sets that have more tokens! Because breaks must be inserted where ambiguity is known, adding more tokens can introduce new ambiguities that might not be handled by an older detokenizer (which has a smaller set of known tokens).

If it can be assumed that every pair of tokens has break character between them, then a tokenizer can simply split its input text on break characters and emit tokens matching exactly the strings that are separated by breaks.

Unfortunately this would represent a somewhat different mode of operation for tokenizers when compared with the traditional longest-prefix matching. It may be possible to support both modes concurrently however, if a tokenizer first attempted an exact match of the input up to the next break character and fell back to longest-prefix matching in case of no exact match.

This break-every-token approach is possible with traditional breaks as well as invisible, which is easier to illustrate. Consider a program fragment written for a monochrome-display TI-83+: "`Red cat`". The string "Red" is a token in its own right on the CSE and CE 8x calculators (because they have color screens), so interpreting this as a program for color calculators would tokenize it differently. This becomes clear if we insert breaks around every token:

 * Monochrome: `R\e\d\ \c\a\t`
 * Color: `Red\ \c\a\t`

A program written as the monochrome version with breaks around every token as illustrated here **cannot be mistaken** for the color one, and the color one cannot be mistaken for the monochrome! While doing so with visible break characters makes it much more difficult to read the code, invisible breaks would not affect readability.

### Concluding

I think it would be pretty cool if existing tools added support for these proposed invisible break characters. They're not appropriate for all use cases (so perhaps shouldn't be the default), but can be useful and would be even more useful with the proposed change to the usual tokenization algorithm.