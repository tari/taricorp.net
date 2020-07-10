---
date: 2015-09-13
title: Claude Shannon hates this one weird trick!
slug: quickcheck-source-coding
subtitle: Checking dubious claims with Rust, Quickcheck, and TDD.
draft: true
---

There was a question posted to /r/AskComputerScience recently: ["does this
compression scheme look fishy to you?"][reddit]. [The algorithm in
question][algorithm-github], called "press" by its author, makes some.. bold
claims in the README:

[reddit]: https://www.reddit.com/r/AskComputerScience/comments/3lo9yv/does_this_compression_scheme_look_fishy_to_you/
[algorithm-github]: https://github.com/aunk/press

> By stringing together 1/0s, using 1's as negative and a 0 as a positive, I've
> sublimely made a perfect compression. Through outputting into hexadecimal.
> This shortens <=4096 'bits' into a 2-byte hexadecimal.

I know enough to immediately scoff at these claims, and if somebody hadn't
specifically asked about it, I would have left it there and not thought twice.
Since somebody asked, however, I thought it would be fun to give this a thorough
examination.

<!-- more -->

## Shannon says "no"

The first few lines of the README, above, seem to imply this might be some kind
of [arithmetic coding][arith-coding]. On the other hand, the author's fixation
with hexadecimal seems to imply there's some aspect in which they fail to
completely understand the nature of base conversions.

[arith-coding]: https://en.wikipedia.org/wiki/Arithmetic_coding

For now disregarding what's actually going on in the code (we'll get to that
shortly), but [Shannon's source coding theorem][shannon-theorem] states that the
size of a losslessly-compressed message cannot be less than the Shannon entropy
of the plaintext (uncompressed) message. The claims are vague here, so we can't
immediately discard them as invalid.

[shannon-theorem]: https://en.wikipedia.org/wiki/Shannon%27s_source_coding_theorem

Up to 4096 bits can indeed be encoded to two bytes. In a simple case, one could
encode strings of zero-bits in a 16-bit number, and all of the numbers in the
range 0-4096 can be represented in 16 bits (which has a range 0-65535).

So far so plausible. It gets a little more interesting if we take the claim of
"perfect compression" literally, meaning that a compressed message will not
exceed the ceiling of the Shannon entropy of the uncompressed message in
bits[^ceiling]. For later reference, Shannon entropy can be defined as follows:

[^ceiling]: We take the ceiling of the entropy because it doesn't make sense to
            emit a fractional bit, so a real implementation must round the number of bits
            up.

<div>
$$
H(X) = - \Sigma_i P(x_i) \mathrm{log}_b P(x_i)
$$
</div>

Where the message has an alphabet of \\(n\\) possible elements \\(x\_0 \\ldots x\_n\\),
\\(P(x\_i)\\) is the probability of a given character in the message being \\(x\_i\\)
(that is, the number of times the character appears divided by the message
length), and \\(b = 2\\) when expressing \\(H\\) in bits.

Since I don't really want to do a formal analysis of this, it's time to break
out the code and do some concrete tests, attempting to disprove the claims.

## Time for code

I don't really want to go testing the provided implementation of this system, so
I'm instead going to write my own white-box implementation that should be easier
to run tests on. Since I like working in Rust and there are some particularly
useful tools available for this task, I choose to write implementation in Rust.

Let's first examine the reference C++ implementation, specifically the encoder
(with formatting adjusted to be more readable)[^what-decoder]:

[^what-decoder]: I honestly couldn't figure out how the decoder was supposed to
                 work, but it seems to vaguely match what we'd expect the encoder to emit.

```c++
std::ifstream  in(argv[i+1], std::ios::in);
std::ofstream  out(argv[i+2], std::ios::out | std::ios::binary);

int Y = 1;
while (!(in.eof())) {
    char P=in.get();
    char ha[4098]= { P };

    for (int j=0;j<=4096;j++) {
        if (ha[j]==0) {
            out << (char)Y-1 ;
            Y=1;
        } else if (ha[j]==1) {
            Y++;
            continue;
        } else {
            Y=1;
            break;
        }
    }
}
```

This takes "bits" from an input stream, writing bytes to an output file. The
"bits" here are actually individual '0' or '1' characters, but we'll do better
in the reimplementation and use actual bits. The decoder must be the opposite,
taking bytes in and emitting bits. Doing a kind of test-driven development,
we'll start by writing the skeleton of the encoder and decoder.

```rust
#[derive(Clone, Copy, Debug, PartialEq, Eg)]
enum Bit {
    Zero,
    One
}

struct Compress<I> where I: Iterator<Item=Bit> {
    src: I
}

impl<I> Iterator for Compress<I> where I: Iterator<Item=Bit> {
    type Item = u8;

    fn next(&mut self) -> Option<u8> {
        unimplemented!();
    }
}

struct Decompress<I> where I: Iterator<Item=u8> {
    src: I
}

impl<I> Iterator for Decompress<I> where I: Iterator<Item=u8> {
    type Item = Bit;

    fn next(&mut self) -> Option<Bit> {
        unimplemented!();
    }
}

fn main() {
    unimplemented!();
}
```

Rust doesn't have a single-bit data type, but I chose to emulate it here with an
enumeration that has two variants, zero and one. A boolean value could have
worked too, but this approach is clearer to understand. I let the compiler
automatically implement a number of traits so `Bit` values can be copied,
displayed and compared.

### Invariants

With some type signatures defined, we can write some tests for the system. There
are two axioms that we expect will always be true of any lossless compression
scheme.  Given \\(e = C(x)\\) as the compressor and \\(x = D(e)\\) as the
decompressor:

1. \\(x = D(C(x))\\). A compressed message is always decompressed to the original.
2. \\(|C(x)| \\geq H(x)\\). The size of the compressed message may not be less than
   the Shannon entropy of the uncompressed input.

Using [quickcheck][quickcheck][^note-qc], we can write simple tests for these
axioms and let the computer generate test cases attempting to cause them to
fail, indicating either a bug in our implementation or a false axiom.

[^note-qc]: The Rust version of quickcheck is a port of the Haskell library of
            the same name. This kind of formalized approach to software design is fairly
            common among Haskell programmers I find, and I think most Rust programmers
            appreciate the value of this approach too.

[quickcheck]: https://crates.io/crates/quickcheck

Testing these two properties, we can both test that the algorithm is correct,
and detect if the creator has somehow disproven the source coding theorem. If
both tests pass it is a correct algorithm that appears to obey the principles of
information theory, and if the second fails but the first passes we appear to
have found a counterexample to the theorem.

### Using quickcheck

First, we'll write a test that decompressing a compressed message yields the
same message back.

```rust
impl quickcheck::Arbitrary for Bit {
    fn arbitrary<G: quickcheck::Gen>(g: &mut G) -> Self {
        g.choose(&[Bit::Zero, Bit::One]).unwrap().clone()
    }
}

#[test]
fn codec_is_lossless() {
    fn encodes_losslessly(xs: Vec<Bit>) -> bool {
        let roundtrip = Decompress {
            src: Compress {
                src: xs.iter().cloned()
            }
        };
        roundtrip.collect::<Vec<_>>() == xs
    }

    quickcheck(encodes_losslessly as fn(Vec<Bit>) -> bool);
}
```

There's nothing particularly novel here. We implement quickcheck's `Arbitrary`
trait for `Bit`s so it can generate random lists of them for us, and define a
test function (that will be run when we do `cargo test`) which uses quickcheck
to ensure that compressing then decompressing a list of `Bit`s yields an
equivalent list back.

If quickcheck can find a case where `encodes_losslessly` returns `false`, it
will automatically attempt to minimize the test case, simplifying debugging.
This is the second half of what makes quickcheck very nice to use- not only can
it generate tests, but it can minimize them to remove unnecessary parts of the
test case it generates.

---

Writing a similar test for preservation of entropy is not particularly
remarkable either:

```rust

```

I perhaps went a little bit overboard on the implementation of `entropy` in
making it so generic, but I like to think it could be adapted to some other
application in the future.

### Implementing codecs

With tests out of the way, we can (finally) get around to implementing the
(de)compressor. Referring back to the C++ compressor code, it's pretty easy:

 * Initialize counter to 1.
 * If bit is zero, output `counter - 1` and reset to 1.
 * Otherwise increment `counter`.

So, it looks like the idea is that strings of ones will encode to a number of
ones, and zeroes cause the counter to be emitted. In short: any number of ones
followed by a zero encodes to the number of ones. We'll throw together a simple
implementation:

```rust

```

Perhaps unsurprisingly, the tests failed. This is shown to not be lossless, and
entropy is not preserved (but that's entirely allowable in a lossy codec).

```
running 3 tests
test tests::validate_entropy_computation ... ok
test tests::codec_is_lossless ... FAILED
test tests::entropy_is_preserved ... FAILED

failures:

---- tests::codec_is_lossless stdout ----
        thread 'tests::codec_is_lossless' panicked at '[quickcheck] TEST FAILED.  Arguments: ([One])', registry/src/github.com-0a35038f75765ae4/quickcheck-0.2.24/src/tester.rs:113


---- tests::entropy_is_preserved stdout ----
        thread 'tests::entropy_is_preserved' panicked at '[quickcheck] TEST FAILED. Arguments: ([Zero, One, Zero])', registry/src/github.com-0a35038f75765ae4/quickcheck-0.2.24/src/tester.rs:113
```

### Fixing it

We see from the failure on `codec_is_lossless` that it can emit wrong data if
the input is a single one. Looking at the implementation, that makes sense- when
the end of input is reached in the encoder, any buffered ones are not emitted.
This is a relatively simple fix:

```rust

```

Testing again, we find that empty input is still a problem. Turns out we should
only flush the encoder if it's received data to begin with, in general meaning
if the one-counter indicates there are any buffered. Conveniently, this
simplifies the code a little bit, by observing that there's nothing to be
flushed if `counter` is greater than one.
