from urllib.parse import quote_plus

PLATFORM_DOMAINS = {
    "Amazon": "https://www.amazon.in/s?k={q}",
    "Flipkart": "https://www.flipkart.com/search?q={q}",
    "IKEA": "https://www.ikea.com/in/en/search/?q={q}",
    "Swiggy": "https://www.swiggy.com/search?query={q}",
    "Zomato": "https://www.zomato.com/search?q={q}",
    "OYO": "https://www.oyorooms.com/search/?location={q}",
}

def search_url(platform, query):
    template = PLATFORM_DOMAINS.get(platform)
    return template.format(q=quote_plus(query)) if template else None

def attach_platform_links(items):
    out = []
    for item in items:
        item = dict(item)
        platform = item.get("platform")
        query = item.get("search_query") or item.get("name") or ""
        item["url"] = search_url(platform, query)
        out.append(item)
    return out
