class ContentsGenerator(object):
    """Generate table of contents from headings."""
    
    @staticmethod
    def process(folder, params):
        print "Processing with ContentsGenerator.\n\tparams=%s" %params
        # Walk nodes, then pages of each node.  Set page.contents to the TOC
        for node in ...:
            for page in node.pages:
                page.contents = []
