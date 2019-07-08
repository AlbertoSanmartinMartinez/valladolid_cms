
#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django import template

register = template.Library()


# Create your tags here
@register.simple_tag
def get_url(dictionary, key):
    """
    """

    return dictionary.get(key)


@register.simple_tag
def build_filter_url(dictionary):
    """
    """

    url = ''
    if dictionary != None:
        for key, val in dictionary.items():
            url += '&' + str(key) + '=' + str(val)
        return url
    else:
        return ''




#
