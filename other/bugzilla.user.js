// ==UserScript==
// @name           Bugzilla
// @namespace      brucevdkooij@gmail.com
// @description    Copies saved links to top and adds a quick search field to Bugzilla
// @include        http://bugzilla.gnome.org/*
// ==/UserScript==

// Crazy hack because JS doesn't support multiline strings
var search_box_html =  (<r><![CDATA[
    <form class="boogleform" name="queryform" action="buglist.cgi" method="get">
        <input id="quicksearch" type="text" name="query" value=""/>
        <input type="submit" value="Search"/>
    </form>

  ]]></r>).toString();

// FIXME: For some reason the script is executed twice so let's do 
// a quick check
var body_node = document.evaluate(
        "/html/body", 
        document, 
        null, 
        XPathResult.FIRST_ORDERED_NODE_TYPE, 
        null
    ).singleNodeValue
if (!body_node) return

// TODO Blank the date container, if any

// ^^

// Immediatly redirect back to the bug report and the correct comment
// because we really don't care about seeing who was messages.
if (/.*process_bug.cgi$/.exec(window.location)) {
    // TODO: ^^
}

// Bug listing and individual bug views
else if (/buglist.cgi|show_bug.cgi/.exec(window.location)) {
    // Find some information we need to fill up the search box
    
    // If we already have a search query we're done
    search_query = /query=([^&]+)/.exec(window.location)
    if (search_query) {
        // Let's clean the query up
        search_query = decodeURIComponent(search_query[1])
        search_query = search_query.replace(/\+/g, " ")
    }
    
    // If not, let's get some information from the page or the URL
    if (!search_query) {
        var product_url = window.location
        
        // When somebody is viewing a bug we'll need to use the product
        // filed against instead of the URL
        if (/show_bug.cgi/.exec(window.location)) {
            // We don't have an ID so here's the next best thing
            product_url = document.evaluate(
                "//td[contains(., 'Product:')]/following-sibling::*/a[@href]", 
                document, 
                null, 
                XPathResult.FIRST_ORDERED_NODE_TYPE, 
                null
            ).singleNodeValue
        }
        
        // Bah, none of this works for saved searches which have the product
        // but shortend (also without classes it would be hard to summarize
        // FIXME: ^^
        
        // Get the actual product from the URL
        // Regretfully we won't always have a product
        product = (/product=([^&]+)/).exec(product_url)
        if (product) {
            product = product[1]
            search_query = "product:" + product
        }
    }
    
    //
    // Alright now let's actually attach our stuff
    //
    
    // Let's use the body div as our primary container
    var body = document.evaluate(
        "id('body')", 
        document, 
        null, 
        XPathResult.FIRST_ORDERED_NODE_TYPE, 
        null
    ).singleNodeValue
    
    // Our own container
    var container = document.createElement("div")
    container.setAttribute("style", "margin-bottom: 2.3em;")
    body.insertBefore(container, body.firstChild)
    
    // Add a quick search box
    var search_box = document.createElement("div")
    search_box.setAttribute("style", "float: right;")
    search_box.innerHTML = search_box_html
    container.appendChild(search_box)
    
    // We have to append first before we can use getElementById (since
    // it seems individual elements don't have getElementById)
    if (search_query) document.getElementById("quicksearch").value = search_query
    
    // Copy the saved searches to the top
    var saved_searches = document.evaluate(
        "id('links-saved')/div[2]", 
        document, 
        null, 
        XPathResult.FIRST_ORDERED_NODE_TYPE, 
        null
    ).singleNodeValue
    saved_searches_cloned = saved_searches.cloneNode(true)
    saved_searches_cloned.setAttribute("style", "float: left;")
    container.appendChild(saved_searches_cloned)
}

