from django import template

register = template.Library()


# ==========================================
# CUSTOM FILTER (Used with a pipe: |currency)
# ==========================================
@register.filter(name='currency')
def currency(value):
    """Formats a decimal or float into a standard currency format."""
    try:
        return f"${float(value):.2f}"
    except (ValueError, TypeError):
        return ""


# ==========================================
# CUSTOM SIMPLE TAG (Used like: {% sale_price price 20 %})
# ==========================================
@register.simple_tag
def sale_price(original_price, discount_percentage):
    """Calculates a discounted price on the fly."""
    try:
        price = float(original_price)
        discount = float(discount_percentage)
        new_price = price - (price * (discount / 100))
        return f"${new_price:.2f}"
    except (ValueError, TypeError):
        return ""


# ==========================================
# URL PARAMETER MERGER (For Pagination + Filtering)
# ==========================================
@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """
    Safely updates URL GET parameters.
    Example: If URL is '?category=shirts&sort=newest', and we pass 'page=2',
    it returns 'category=shirts&sort=newest&page=2'.
    """
    # 1. Grab the current URL parameters from the request
    query = context['request'].GET.copy()

    # 2. Update them with whatever we pass into the tag (like page=2)
    for k, v in kwargs.items():
        query[k] = v

    # 3. Return the newly encoded URL string
    return query.urlencode()