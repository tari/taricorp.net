## Custom filters for taricorp.net as rendered by Hyde

from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.http import urlquote

def unordered_list_a(value, autoescape=None):
    """
    Like the built-in unordered_list filter, but makes each list
    element also be a link within the current page, and url quotes
    all links.
    
    Where unordered_list might return <li>Fish</li>, unordered_list_a would
    return <li><a href="#Fish">Fish</a></li>.
    (Taken from Django 1.2 implementation of unordered_list)
    """
    if autoescape:
        from django.utils.html import conditional_escape
        escaper = conditional_escape
    else:
        escaper = lambda x: x
    def convert_old_style_list(list_):
        """
        Converts old style lists to the new easier to understand format.

        The old list format looked like:
            ['Item 1', [['Item 1.1', []], ['Item 1.2', []]]

        And it is converted to:
            ['Item 1', ['Item 1.1', 'Item 1.2]]
        """
        if not isinstance(list_, (tuple, list)) or len(list_) != 2:
            return list_, False
        first_item, second_item = list_
        if second_item == []:
            return [first_item], True
        old_style_list = True
        new_second_item = []
        for sublist in second_item:
            item, old_style_list = convert_old_style_list(sublist)
            if not old_style_list:
                break
            new_second_item.extend(item)
        if old_style_list:
            second_item = new_second_item
        return [first_item, second_item], old_style_list
    def _helper(list_, tabs=1):
        indent = u'\t' * tabs
        output = []

        list_length = len(list_)
        i = 0
        while i < list_length:
            title = list_[i]
            sublist = ''
            sublist_item = None
            if isinstance(title, (list, tuple)):
                sublist_item = title
                title = ''
            elif i < list_length - 1:
                next_item = list_[i+1]
                if next_item and isinstance(next_item, (list, tuple)):
                    # The next item is a sub-list.
                    sublist_item = next_item
                    # We've processed the next item now too.
                    i += 1
            if sublist_item:
                sublist = _helper(sublist_item, tabs+1)
                sublist = '\n%s<ul>\n%s\n%s</ul>\n%s' % (indent, sublist,
                                                         indent, indent)
            title = escaper(force_unicode(title))
            output.append('%s<li><a href="#%s">%s</a>%s</li>' % (indent,
                    urlquote(title), title, sublist))
            i += 1
        return '\n'.join(output)
    value, converted = convert_old_style_list(value)
    return mark_safe(_helper(value))
unordered_list_a.is_safe = True
unordered_list_a.needs_autoescape = True

## Django boilerplate
from django import template
register = template.Library()
register.filter('unordered_list_a', unordered_list_a)