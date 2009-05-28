#!/usr/bin/env python
"""
googlecode.py - Google Code lookups
Copyright 2009, Bruce van der Kooij <brucevdkooij@gmail.com>
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import tidy
import urllib2

from Ft.Xml import Parse
from Ft.Xml.XPath.Context import Context
from Ft.Xml.XPath import Evaluate

XHTML_NS = "http://www.w3.org/1999/xhtml"

# Keeps all the content
bugs_cache = {}

def bug_lookup(phenny, input): 
    issue_url = "http://code.google.com/p/nautilussvn/issues/detail?id="
    bug_number = input.group("bug_number")
    url = issue_url + str(bug_number)

    # Tidy up the document and convert to XHTML
    # TODO: we should really cache the result and next time somebody
    # requests the same report check the Modified-Since header.
    if url in bugs_cache:
        document = bugs_cache[url]
    else:
        original_content = urllib2.urlopen(url).read()
        content = str(tidy.parseString(original_content, output_xhtml=1, add_xml_decl=1))
        document = Parse(content)
        bugs_cache[url] = document
        

    # Alright let's parse it (little bit ugly due to the need for a namespace
    # and the replace calls but oh well)
    context = Context(document, processorNss={"xhtml": XHTML_NS})
    title = Evaluate("string(id('issueheader')//xhtml:span[@class='h3'])", context).replace("\n", " ")
    reporter = Evaluate("string(//xhtml:div[@class='author']/xhtml:a)", context).replace("\n", " ")
    status = Evaluate("string(id('issuemeta')//xhtml:td[preceding-sibling::*[contains(., 'Status')]])", context).replace("\n", " ")
    priority = Evaluate("string(id('issuemeta')//xhtml:a[contains(., 'Priority')])", context).replace("Priority-", "").replace("\n", " ")
    type = Evaluate("string(id('issuemeta')//xhtml:a[contains(., 'Type')])", context).replace("Type-", "").replace("\n", " ")

    # And we're done!
    phenny.say("Bug %(url)s %(type)s %(priority)s %(reporter)s %(status)s, %(title)s" % locals())
   
bug_lookup.rule = r"(?i).*Bug #?(?P<bug_number>[0-9]+).*"

