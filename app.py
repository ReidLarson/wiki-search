"""API to search Wikipedia based on subdomain of the server."""

from flask import Flask, request
import json
import wikipedia
import requests

app = Flask(__name__)
app.config['SERVER_NAME'] = 'wiki-search.com:5000'


@app.route("/", subdomain="<query>", methods=['GET'])
def query_wikipedia(query):
    """Get articles from Wikipedia that match subdomain."""

    results = {"links": []}
    try:
        # Check if search leads to disambiguation page.
        results["links"] = [get_page_summary(query)]
    except wikipedia.exceptions.DisambiguationError as e:
        # If a disambiguation page, get all URLs.
        # results["links"] = get_urls_from_mw_api(query)
        results["links"] = build_urls_from_html(e.options)

    return json.dumps(results, indent=4, ensure_ascii=False)


def get_page_summary(query):
    """Get the information about a single Wikipedia page."""

    wikipedia.summary(query)
    return wikipedia.page(query).url


def get_urls_from_mw_api(query):
    """Use the MediaWiki API to get URLs that match the query."""

    # Use MediaWiki API to get page IDs - official, but different order from HTML page.
    URL = 'https://en.wikipedia.org/w/api.php'
    PARAMS = {
        'action': 'query',
        'format': 'json',
        'prop': 'info',
        'generator': 'allpages',
        'inprop': 'url',
        'gapfrom': query,
        'gaplimit': 500
    }

    r = requests.get(url=URL, params=PARAMS)
    pages = r.json()['query']['pages']
    results = []
    for page in pages.keys():
        results.append((pages[page]['fullurl']))

    return results


def build_urls_from_html(page_titles):
    """Build URLs based on the page titles from the disambiguation page."""

    # Hacky, but retains order from normal search on the website.
    results = []
    for page_title in page_titles:

        # Convert page title characters into URL characters
        page_title = page_title.replace(" ", "_")
        page_title = page_title.replace("\"", "")

        PAGE_URL = 'https://en.wikipedia.org/wiki/' + page_title
        results.append(PAGE_URL)

    return results


app.run()
