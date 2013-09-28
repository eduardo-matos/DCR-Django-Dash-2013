# coding utf-8

from py_w3c.validators.html.validator import HTMLValidator
from pyquery import PyQuery as pq
from urlparse import urlparse


class Validator(object):
    url = None
    errors = None
    warnings = None
    anchors=[]
    errors= {}
    threshold = 3

    _validator_w3c = None

    def __init__(self, url):
        self.url = url
        self._validator_w3c = HTMLValidator()

        self.anchors = self._fetch_anchors()
        self.anchors.append(self.url)

        a = [anchor for anchor in self.anchors if urlparse(anchor).netloc and urlparse(anchor).netloc in self.url]

        self.anchors = list(set(a))[:self.threshold]

        for an in self.anchors:
            self._validator_w3c.validate(an)
            self.errors[an] = self._validator_w3c.errors

    def _fetch_anchors(self):
        d = pq(url=self.url)

        anchors = []
        for anchor in d('a[href]'):
            anchors.append(anchor.attrib['href'])

        return anchors
