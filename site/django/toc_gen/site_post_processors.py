from BeautifulSoup import BeautifulSoup
from django.utils.http import urlquote

class ContentsLinkupProcessor(object):
    @staticmethod
    def process(folder, params):
        class Processor:
            def visit_file(self, thefile):
                soup = BeautifulSoup(thefile.read_all())
                headings = soup.findAll(['h2', 'h3', 'h4', 'h5', 'h6'])
                for heading in headings:
                    heading['id'] = urlquote(heading.text)
                # Explicit conversion to unicode; prettify gives a UTF-8
                # encoded string, not a unicode object, and hyde goes through
                # a codec to write UTF-8 which breaks when given invalid ASCII
                # in a string.
                # out = unicode(soup.prettify(), 'utf-8')
                # Working around bug #686181 in beautiful soup, in which
                # unicode() and prettify() double certain tags.
                out = unicode(str(soup), 'utf-8')
                thefile.write(out)
                print "%s: patched %i headings." %(thefile, len(headings))
        folder.walk(Processor(), "*.html")
        