from django import template

register = template.Library()

@register.inclusion_tag('utils/render_stars.html')
def render_stars(note):
    full_stars = range(note)
    empty_stars = range(5 - note)
    return {'full_stars': full_stars, 'empty_stars': empty_stars}
