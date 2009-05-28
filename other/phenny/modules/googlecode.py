#!/usr/bin/env python
"""
googlecode.py - Google Code lookups
Copyright 2009, Bruce van der Kooij <brucevdkooij@gmail.com>
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import urllib2
from urllib2 import HTTPError
import lxml.html

# Keeps all the content
bugs_cache = {}

def bug_lookup(phenny, input): 
    bug_number = input.group("bug_number")
    issue_url = "http://code.google.com/p/nautilussvn/issues/detail?id="
    url = issue_url + str(bug_number)

    # Tidy up the document and convert to XHTML
    # TODO: we should really check the Modified-Since header.
    if not bug_number in bugs_cache: 
        try:
            # Alright let's parse it (the status one is a bit strange)
            document = lxml.html.parse(urllib2.urlopen(url))
            bugs_cache[bug_number] = {
                "url": url,
                "title": document.xpath("string(id('issueheader')//span[@class='h3'])"),
                "reporter": document.xpath("string(//div[@class='author']/a)"),
                "status": re.sub("\s+", "", document.xpath("string(id('issuemeta')//td[preceding-sibling::*[contains(., 'Status')]])")),
                "priority": document.xpath("string(id('issuemeta')//a[contains(., 'Priority')])").replace("Priority-", ""),
                "type": document.xpath("string(id('issuemeta')//a[contains(., 'Type')])").replace("Type-", "")
            }
        except HTTPError:
            pass

    # And we're done!
    # Might have been an error so let's take a peek and see if it's in the cache
    if bug_number in bugs_cache:
        phenny.say("Bug %(url)s %(type)s %(priority)s %(reporter)s %(status)s, %(title)s" % bugs_cache[bug_number])
    else:
        phenny.say("No bug found")
   
bug_lookup.rule = r"(?i).*Bug #?(?P<bug_number>[0-9]+).*"

