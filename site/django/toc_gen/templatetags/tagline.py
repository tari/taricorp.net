from django import template
register = template.Library()

from tagline_resource import taglines
from random import randint

class TaglineNode(template.Node):
    def __init__(self, text):
        self.text = text
    def render(self, context):
        return self.text

@register.tag(name='r_tagline')
def do_tagline(parser, token):
    line = taglines[randint(0, len(taglines)-1)]
    return TaglineNode(line)
    