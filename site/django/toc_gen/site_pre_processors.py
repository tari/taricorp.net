from BeautifulSoup import BeautifulSoup
from django.utils.http import urlquote

class ContentsGenerator(object):
    """Generate table of contents from headings.
       Parameters:
            contents_var - variable to save contents list in under the page.
                           Default: contents
            omit_var - flag member of page to check whether a TOC should be
                       generated.  If omitted or reduces to False, TOC will be
                       created.  Default: toc_omit
    """
    
    @staticmethod
    def process(folder, params):
        (contents_var, omit_var) = ('contents', 'toc_omit')
        if 'contents_var' in params:
            contents_var = params['contents_var']
        if 'omit_var' in params:
            omit_var = params['omit_var']
        def generate_headings(file):
            def nested_append(nlist, element, depth):
                if depth <= 1:
                    # Have hit the target level
                    nlist.append(element)
                else:
                    if len(nlist) is 0 or not isinstance(nlist[-1], list):
                        # Next level doesn't exist yet, so create it
                        nlist.append([])
                    nested_append(nlist[-1], element, depth - 1)
            soup = BeautifulSoup(file.read())
            # Find headings
            hns = soup.findAll(['h2', 'h3', 'h4', 'h5', 'h6'])
            contents = []
            for h in hns:
                level = int(h.name[1]) - 1
                text = h.text
                # Put this in the global contents 
                nested_append(contents, text, level)
                # Set id so we can link to it
                h['id'] = urlquote(h.text)
            return contents
        accept_exts = ('.html')
        # Walk nodes, then pages of each node.  Set page.contents to the TOC
        node = params['node']
        #for node in params['node'].children:
        for page in node.walk_pages():
            print "\t%s" %page.file.name
            extension = page.source_file.extension
            if extension in accept_exts and bool(extension):
                if hasattr(page, omit_var) and page.__getattribute__(omit_var):
                    continue
                with open(page.source_file.path, 'r') as infile:
                    contents = generate_headings(infile)
                    page.__setattr__(contents_var, contents)
                    print "\t\t%s" %contents
            else:
                print "\t\tIgnored"
