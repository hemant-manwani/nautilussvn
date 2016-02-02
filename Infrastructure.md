# Requirements #

  * Landing Page
  * Issue Tracking
  * Code Review
  * Wiki
    * Required: per-page permissions
    * Required: support for hierarchical relations (Page has Children)
    * Bonus: ability to edit individual sections, not the entire page
    * Bonus: support for comments on the same page
  * File Hosting
  * Translations
  * Project Activity
  * Mailing Lists
  * Developer Blog
  * Repository Hosting

# Possible solutions #

## Adam's Preferences ##

  * rabbitvcs.org points to a homepage we've put together with links to disparate tools
  * We modify our current wordpress blog to be usable as a homepage

  * Landing Page - Our own HTML
  * Issue Tracking - Mantis or Google Code
  * Code Review - Review Board or something simple we could develop ourselves, or continue to use Google Code
  * Wiki - DokuWiki (it's what I know), MediaWiki would probably be ok too
  * File Hosting - Our own HTML
  * Translations - Continue to use Launchpad, Poedit
  * Project Activity - Not sure about this one, maybe roll our own feed
  * Mailing Lists - Continue using what we're using
  * Developer Blog - Integrate our current WordPress blog into the site, or base the site on WordPress
  * Repository Hosting - Our own SVN server or keep it on Google Code (with new project for RabbitVCS)

## Bruce's Preferences ##

  * Landing Page - Anything, preferably something with a nice design
  * Issue Tracking - Trac or Google Code
  * Code Review - Review Board or Google Code
  * Wiki - Trac (with an option to migrate later)
  * File Hosting - Google Code + Launchpad (PPA)
  * Translations - Launchpad
  * Project Activity - Trac or Google Code
  * Mailing Lists - Google Groups
  * Developer Blog - Current WordPress instance with a new theme
  * Repository Hosting - Preferably a DVCS (Google Code, Launchpad, GitHub, Bitbucket.org)

## Jason's Preferences ##

  * Landing page - Clean but a good "hub". Need to be able to change layout after an initial period if we realise we've misjudged what we need.
  * Wiki - I've been using DokuWiki at work and home for a while, and it's great. Tried MediaWiki at work, too complicated.
  * Code download - I think that we should try to have at least the downloads in a globally accessible location. We should aim for this for the source as well, but it's not as easy as that.
  * Repository Hosting - should we try to keep it as SVN? :P
  * Mailing lists - as they are, but we need a new rabbitvcs (non dev) group.

# Chosen solution #

> _This is not yet final._

  * Landing Page - WordPress with custom theme
  * Issue Tracking - Trac
  * Code Review - Review Board + Google Code
  * Wiki - DokuWiki
  * File Hosting - Launchpad
  * Translations - Launchpad
  * Project Activity - Trac + Google Code
  * Mailing Lists - Google Groups
  * Developer Blog - WordPress
  * Repository Hosting - Mercurial (Google Code) + mirror with Bitbucket.org