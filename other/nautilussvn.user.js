// ==UserScript==
// @name           NautilusSvn Google Code 
// @namespace      brucevdkooij@gmail.com
// @description    Change stuff about NautilusSvn's Google Code page.
// @include        http://code.google.com/p/nautilussvn/*
// ==/UserScript==

var base_url = "http://code.google.com/p/nautilussvn/issues/list"
var custom_issues_query = "-status:Stalled+-milestone:Future+-priority:low+-owner:adamplumb"
var saved_searches = {
    "All": "",
    "New bugs": "type:Defect+status:New",
    "Bugs": "type:Defect",
    "Enhancements":  "type:Enhancement",
    "New enhancements": "type:Enhancement+status:New",
    "Release 0.12": "milestone:Release0.12",
    "Release 0.13": "milestone:Release0.13",
    "Release 0.14": "milestone:Release0.14",
    "Release 0.15": "milestone:Release0.15"
}

// Change the default tab to point to a customized query
var issue_links = document.evaluate("//a[@href='/p/nautilussvn/wiki/Issues?tm=3']", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
for (var i = 0 ; i < issue_links.snapshotLength; i++) {
  var issue_link = issue_links.snapshotItem(i)
  issue_link.href = base_url + "?q=" + custom_issues_query
}

var main_column = document.evaluate("id('maincol')", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue
var saved_searches_container = document.createElement("div")
saved_searches_container.setAttribute("style", "margin-bottom: 0.5em;")
for (var key in saved_searches) {
    saved_searches_container.innerHTML += '<a href="' + base_url + "?q=" + saved_searches[key] + '">' + key + '</a> '
}

main_column.insertBefore(
    saved_searches_container, main_column.firstChild
)
