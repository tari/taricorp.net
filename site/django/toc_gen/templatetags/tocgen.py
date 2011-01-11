from django import template
register = template.Library()

from django.utils.http import urlquote
from BeautifulSoup import BeautifulSoup

@register.tag(name='tocgen')
def do_tocgen(parser, token):
    args = token.split_contents()
    var_out = 'contents' if len(args) <= 1 else args[1]
    nodelist = parser.parse(('endtocgen',))
    parser.delete_first_token()
    return TocGenNode(nodelist, var_out)
    
class TocGenNode(template.Node):
    def __init__(self, nodelist, var_name):
        self.nodelist = nodelist
        self.var_name = var_name
    def render(self, context):
        soup = BeautifulSoup(self.nodelist.render(context))
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
        # Set contents var for our page so it can be inserted
        print "context[%s] = %s" %(self.var_name, contents)
        context[self.var_name] = contents
        # Now re-render the page with updated context
        return self.nodelist.render(context)

def nested_append(nlist, element, depth):
    """Appends element to nlist at depth levels in, where levels are delimited
       by sublists and begin at 1 for the list root.  Levels prior to depth
       will be created if they do not exist, and depths less than 1 are
       treated as if they were 1.
       
       Example:
       >>> a = []
       >>> nested_append(a, '1.0', 1)
       # a = ['1.0']
       >>> nested_append(a, '2.0', 2)
       # a = ['1.0', ['2.0']]
       >>> nested_append(a, ['3.0','3.1'], 2)
       # a = ['1.0', ['2.0', ['3.0', '3.1']]]
       >>> nested_append(a, '1.1', 1)
       # a = ['1.0', ['2.0', ['3.0', '3.1']], '1.1']
       
       Note that the second call for level 2 is equivalent to two calls to
       nested_append at level 3 with elements '3.0' and '3.1'."""
    if depth <= 1:
        # Have hit the target level
        nlist.append(element)
    else:
        if len(nlist) is 0 or not isinstance(nlist[-1], list):
            # Next level doesn't exist yet, so create it
            nlist.append([])
        nested_append(nlist[-1], element, depth - 1)
