// ==UserScript==
// @name           NautilusSvn Google Code 
// @namespace      brucevdkooij@gmail.com
// @description    Change stuff about NautilusSvn's Google Code page.
// @include        http://code.google.com/p/nautilussvn/*
// ==/UserScript==


var issue_links = document.evaluate("//a[@href='/p/nautilussvn/wiki/Issues?tm=3']", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
for (var i = 0 ; i < issue_links.snapshotLength; i++) {
  var issue_link = issue_links.snapshotItem(i)
  issue_link.href = "http://code.google.com/p/nautilussvn/issues/list?can=2&q=-status%3AStalled+-milestone%3AFuture+-priority%3Alow+-owner%3Aadamplumb&colspec=Stars+ID+Type+Status+Priority+Milestone+Owner+Summary&x=stars&y=status&cells=tiles"
}
