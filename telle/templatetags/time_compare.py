from django import template
from datetime import date

register = template.Library()

@register.filter
def future_dates_only(comp_date):
   if comp_date > date.today():
       return comp_date
   else:
       return None
