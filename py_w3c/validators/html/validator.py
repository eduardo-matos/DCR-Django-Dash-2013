import urllib2
import urllib
import sys
import getopt
import random

from xml.sax import parseString
from StringIO import StringIO

from py_w3c.multipart import Multipart
from py_w3c.handler import ValidatorHandler
from py_w3c.exceptions import ValidationFault
from py_w3c import __version__

VALIDATOR_URL = 'http://validator.w3.org/check'


_user_agents = (
    'Mozilla/5.0 (X11; U; OpenBSD i386; en-US; rv:1.9.2.8) Gecko/20101230 Firefox/3.6.8',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.8) Gecko/20100804 Gentoo Firefox/3.6.8',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.8) Gecko/20100723 SUSE/3.6.8-0.1.1 Firefox/3.6.8',
    'Mozilla/5.0 (X11; U; Linux i686; zh-CN; rv:1.9.2.8) Gecko/20100722 Ubuntu/10.04 (lucid) Firefox/3.6.8',
    'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.2.8) Gecko/20100723 Ubuntu/10.04 (lucid) Firefox/3.6.8',
    'Mozilla/5.0 (X11; U; Linux i686; fi-FI; rv:1.9.2.8) Gecko/20100723 Ubuntu/10.04 (lucid) Firefox/3.6.8',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.8) Gecko/20100727 Firefox/3.6.8',
    'Mozilla/5.0 (X11; U; Linux i686; de-DE; rv:1.9.2.8) Gecko/20100725 Gentoo Firefox/3.6.8',
    'Mozilla/5.0 (X11; U; FreeBSD i386; de-CH; rv:1.9.2.8) Gecko/20100729 Firefox/3.6.8',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; pt-BR; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; he; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; fr; rv:1.9.2.8) Gecko/20100722 Firefox 3.6.8 GTB7.1',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0C)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; de; rv:1.9.2.8) Gecko/20100722 Firefox 3.6.8',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; de; rv:1.9.2.3) Gecko/20121221 Firefox/3.6.8',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; zh-TW; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)',
)



class HTMLValidator(object):
    def __init__(self, validator_url=VALIDATOR_URL, charset=None, doctype=None,
        verbose=False):
        self.validator_url = validator_url
        self.result = None
        self.uri = ''
        self.uploaded_file = ''
        self.output = 'soap12'
        self.charset = charset
        self.doctype = doctype
        self.errors = []
        self.warnings = []
        self.verbose = verbose

    def _validate(self, url, headers=None, post_data=None):
        ''' sends request to the validator, if post_data is not empty, sends POST request, otherwise sends GET request. 
        Returns True if validation occurs, otherwise otherwise raises exception '''
        if not headers:
            headers = {'User-Agent': 'Mozilla/5.1 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36'}
        req = urllib2.Request(url, headers=headers, data=post_data)
        resp = urllib2.urlopen(req)
        self._process_response(resp.read())
        return True

    def validate(self, uri):
        ''' validates by uri '''
        get_data = {'uri': uri, 'output': self.output}
        if self.charset:
            get_data['charset'] = self.charset
        if self.doctype:
            get_data['doctype'] = self.doctype
        get_data = urllib.urlencode(get_data)
        return self._validate(self.validator_url + '?' + get_data)

    def validate_file(self, filename_or_file, name='file'):
        ''' validates by filename or file content '''
        m = Multipart()
        m.field('output', self.output)
        if self.doctype:
            m.field('doctype', self.doctype)
        if self.charset:
            m.field('charset', self.charset)
        if isinstance(filename_or_file, str):
            with open(filename_or_file, "r") as w:
                content = w.read()
        elif isinstance(filename_or_file, file):
            content = filename_or_file.read()
        elif isinstance(filename_or_file, StringIO):
            content = filename_or_file.getvalue()
        else:
            raise Exception("File name or file only. Got %s instead" % type(filename_or_file))
        m.file('uploaded_file', name, content, {'Content-Type': 'text/html'})
        ct, body = m.get()
        return self._validate(self.validator_url, headers={'Content-Type': ct}, post_data=body)

    def validate_fragment(self, fragment):
        ''' validates by fragment. Full html fragment only. '''
        post_data = {'fragment': fragment, 'output': self.output}
        if self.doctype:
            post_data['doctype'] = self.doctype
        if self.charset:
            post_data['charset'] = self.charset
        post_data = urllib.urlencode(post_data)
        return self._validate(self.validator_url, post_data=post_data)

    def _process_response(self, response):
        val_handler = ValidatorHandler()
        parseString(response, val_handler)
        if val_handler.fault_occured:
            raise ValidationFault("Fault occurs. %s" % val_handler.fault_message)
        if self.verbose:
            print "Errors: %s" % len(self.errors)
            print "Warnings: %s" % len(self.warnings)
        self.result = val_handler
        self.warnings = val_handler.warnings
        self.errors = val_handler.errors

def main(argv=None):
    usage = "  Usage: \n    w3c_validate http://yourdomain.org"
    if argv is None:
        argv = sys.argv
    if len(argv) != 2:
        print usage
        sys.exit(2)
    if argv[1] in ("-v", "--version"):
        print __version__
        sys.exit(0)
    val = HTMLValidator(verbose=False)
    val.validate(argv[1])
    print "---warnings---(%s)" % len(val.warnings)
    for warning in val.warnings:
        print "line:%s; col:%s; message:%s" % (warning.get("line"), warning.get("col"), warning.get("message"))
    print "---errors---(%s)" % len(val.errors)
    for error in val.errors:
        print "line:%s; col:%s; message:%s" % (error.get("line"), error.get("col"), error.get("message"))
    sys.exit(0)

