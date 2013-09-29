# coding utf-8

from py_w3c.validators.html.validator import HTMLValidator
from pyquery import PyQuery as pq
from urlparse import urlparse


def validate(url, threshold=3):
    url_list = set([url])
    url_list_validated = set([])
    errors = dict()

    w3c_validator = HTMLValidator()

    parsed_url = urlparse(url)
    base_url = parsed_url.scheme + '://' + parsed_url.netloc

    next_url = None

    while len(url_list) > 0 and len(url_list_validated) < threshold:
        next_url = url_list.pop()

        if next_url in url_list_validated:
            continue

        # validate next url
        w3c_validator.validate(next_url)
        errors[next_url] = w3c_validator.errors

        # add it to validated
        url_list_validated.add(next_url)

        # fetch more urls
        more_links = fetch_more_links(next_url, parsed_url)

        # normalize to correct domain
        full_links = [base_url + path for path in more_links]

        # add to list
        for link in full_links:
            url_list.add(link)

    return errors

def fetch_more_links(url, parsed_url):
    d = pq(url=url)

    anchors = []
    for anchor in d('a[href]'):
        href = anchor.attrib['href']

        parsed_href = urlparse(href)

        if (parsed_url.netloc == parsed_href.netloc or parsed_href.netloc is '') and '/' in parsed_href.path and '.pdf' not in parsed_href:
            anchors.append(parsed_href.path) 

    return anchors
