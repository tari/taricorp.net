#!/usr/bin/env python
###
# Copyright 2010 Peter Marheine. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
# 
#   1. Redistributions of source code must retain the above copyright notice, this list of
#      conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright notice, this list
#      of conditions and the following disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY PETER MARHEINE ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL PETER MARHEINE OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those of the
# authors and should not be interpreted as representing official policies, either expressed
# or implied, of Peter Marheine.
###

def main():
    import sys, cPickle, getopt
    # Parse command-line arguments
    try:
        longopts = ["file=","seed=","lax"]
        opts, args = getopt.getopt(sys.argv[1:], "f:s:l", longopts)
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(1)
    # Act on arguments
    pfile = "markov.pkl"
    sseed = None
    m_strict = True
    for o, a in opts:
        if o in ("-f","--file="):
            pfile = a
        elif o in ("-s","--seed="):
            if a == '-':
                sseed = sys.stdin.read()
            else:
                sseed = a
        elif o in ("-l","--lax"):
            m_strict = False
    # Unpickle the map of choice
    m = MarkovMap(strict=m_strict)                
    m_modified = False
    try:
        with open(pfile, "rb") as f:
            m = cPickle.load(f)
    except IOError:
        print "IO error on %s, creating new map" %pfile
        m_modified = True
    # Seed the map if desired
    if sseed:
        m.addString(sseed)
        m_modified = True
    # Now do whatever we've been told to.
    try:
        print m.generateWord()
    except LookupError, e:
        print "Generation failure: %s" %str(e)
    #Write out the map again if necessary and exit
    if m_modified:
        with open(pfile, "wb") as f:
            cPickle.dump(m, f, protocol=2)
    
class MarkovMap:
    def __init__(self, initial="", strict=True):
        self._nodes = {}
        self.strict = strict
        self.addString(initial)
    
    def addString(self, s):
        """Adds the given string to the seed, omitting non-alphabetic and
           non-space characters."""
        s = s.lower()
        #Omit last character since it has no follower
        for i in xrange(len(s) - 1):
            c = s[i]
            if self.strict and not c.isalpha() and c != ' ':
                continue
            if c not in self._nodes:
                self._nodes[c] = MarkovMapNode()
            self._nodes[c].append(s[i+1])
    
    def generateWord(self, minLen=4, maxLen=12):
        """Generates a single word from this map."""
        if ' ' not in self._nodes:
            raise LookupError("Map lacks ' '- words cannot be generated")
        word = ""
        try:
            chain = lambda c: self._nodes[c].chain()
            c = chain(' ')
            while (c.isalpha() or not self.strict) and c != ' ':
                word += c
                #Enforce maximum length
                if len(word) >= maxLen and self._nodes[c].connectedTo(' '):
                    break;
                #Enforce minimum length
                temp = chain(c)
                while len(word) < minLen and (not self.strict or not temp.isalpha()):
                    temp = chain(c)
                c = temp
        except LookupError:
            print "Hit a dead end- try seeding the map more."
        return word

class MarkovMapNode:
    """Maps the probabilities of following a given character with any other."""
    def __init__(self):
        self._follow = {}
        self._follow_total = 0
    def __str__(self):
        return "%i connections" %self._follow_total
    def __repr__(self):
        return self.__str__()
    
    def append(self, char):
        """Add another character to the follow entries."""
        if char not in self._follow:
            self._follow[char] = 0
        self._follow[char] += 1
        self._follow_total += 1
    
    def chain(self):
        """Get a randomly chosen (weighted) follower."""
        if self._follow_total <= 0:
            raise LookupError("Chain is empty")
        import random
        target = random.random()
        for m in self._follow.iteritems():
            target -= float(m[1]) / self._follow_total
            if target < 0:
                return m[0]
        #Shouldn't happen.  If it does, blame rounding error.
        print "Warning: chain fell through.  Probably just a rounding error.."
        return self._follow.keys()[-1]
    
    def connectedTo(self, char):
        """Check whether this node is connected to the given character."""
        return char in self._follow
        
if __name__ == "__main__":
    main()