from django.contrib.auth.models import Group
from django.conf import settings

from django import template
register = template.Library()


#best_items indices
from ..scraping_code import best_items_indices, search_results_indices

register = template.Library()
@register.filter
def return_source_product(row):
    return row[best_items_indices["source_product"]]

@register.filter
def return_target_price(row):
    return row[best_items_indices["target_price"]]

@register.filter
def return_amz_link(row):
    return row[best_items_indices["amz_link"]]


@register.filter
def return_search_results(row):
    return row[best_items_indices["search_results"]]

@register.filter
def return_product(item):
    return item[search_results_indices["product"]]

@register.filter
def return_retailer_price(item):
    return item[search_results_indices["retailer_price"]]

@register.filter
def return_retailer_name(item):
    return item[search_results_indices["retailer_name"]]

@register.filter
def return_web_address(item):
    return item[search_results_indices["web address"]]
