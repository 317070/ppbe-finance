from django import template

register = template.Library()
@register.filter
def initials(value):
    return '. '.join([word[0] for word in value.split(' ') if word])+'.'

@register.filter
def notes(value):
    if "at" in value.lower():
        return "Member fee"
    return value

@register.filter
def hideIBAN(value):
    value = list(value)
    for i in xrange(4,len(value)-2):
        value[i] = "*"
    return ' '.join(''.join(value[i:i+4]) for i in xrange(0, len(value), 4))
    