#remove these 
  #used in 2nd Phase: from django.utils.html import escape
  #used in 2nd Phase: from django.utils.safestring import mark_safe

from django.utils.html import format_html
from django import template
from django.contrib.auth import get_user_model


register = template.Library()


user_model = get_user_model()

@register.filter
def author_details(author):
    if not isinstance(author, user_model):
        # return empty string as safe default
        return ""
    if author.first_name and author.last_name:
        name = f"{author.first_name} {author.last_name}"
        # 2nd phase with escape and safe: 
          #name = escape(f"{author.first_name} {author.last_name}")
    else:
        name = f"{author.username}"
        # 2nd phase with escape and safe: 
          # name = escape(f"{author.username}")
 
    if author.email:
        email = author.email 
        prefix = f'<a href="mailto:{email}">' 
        suffix = "</a>"
    
    else:
        prefix = ""
        suffix = ""
    
    
    return format_html('{}{}{}', prefix, name, suffix)
    
      # 2nd phase with escape and safe: 
          # return mark_safe(f"{prefix}{name}{suffix}")
    #return f"{prefix}{name}{suffix}"



