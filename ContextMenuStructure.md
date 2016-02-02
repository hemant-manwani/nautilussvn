# Table of contents #


# Notes #

  * The term "file" is used loosely to indicate both files and directories.
  * When a directory is selected sometimes a condition needs to be checked recursively.
  * Added files count as "under version control" (versioned) too.

# Menu structure #
Based on [TortoiseSVN's menus](http://code.google.com/p/nautilussvn/wiki/TortoiseSVN).

## Topmenu ##
| **Menu entry**             | **Condition**                                      | **Recursive** |
|:---------------------------|:---------------------------------------------------|:--------------|
| Checkout                   | not a working copy AND directory selected          | no            |
| Update                     | `1..*` versioned item(s) AND NOT added             | no            |
| Commit                     | `1..*` (added OR modified OR deleted item(s))      | yes           |
| NautilusSvn                | always                                             |               |

## Submenu NautilusSvn ##
| **Menu entry**             | **Condition**                                      | **Recursive** |
|:---------------------------|:---------------------------------------------------|:--------------|
| Diff                       | 2 items OR modified item                           | no`[1]`       |
| Show log                   | 1 versioned item AND NOT added                     | no            |
| Repo-browser               |                                                    |               |
| Check for modifications    |                                                    |               |
| Revision graph             |                                                    |               |
| ---------------------      |                                                    |               |
| Add                        | `1..*` unversioned item(s)                         | yes           |
| Add to ignore list         | only `1..*` unversioned item(s)                    | no            |
| ---------------------      |                                                    |               |
| Update to revision         |                                                    |               |
| Rename                     | 1 versioned item                                   | no            |
| Delete                     | `1..*` versioned item(s)                           | no            |
| Revert                     | `1..*` (added OR deleted OR modified item(s))      | yes           |
| Get lock                   |                                                    |               |
| ---------------------      |                                                    |               |
| Branch/tag                 |                                                    |               |
| Switch                     |                                                    |               |
| Merge                      |                                                    |               |
| ---------------------      |                                                    |               |
| Blame                      | 1 versioned item AND NOT added                     | no            |
| ---------------------      |                                                    |               |
| Create patch               |                                                    |               |
| Properties                 | `1..*` (versioned item(s))                         | no            |
| ---------------------      |                                                    |               |
| Help                       | always                                             |               |
| Settings                   | always                                             |               |
| About                      | always                                             |               |

`[1]` It's possible to do directory diffs, so maybe in a later version.

# Mockup #
The icons used in the mockup are from the default GNOME iconset or the Tango iconset. Rename was based on Gedit's logo. The lock was based on the screenlock icon from GNOME. The logo is a combination of Nautilus's logo (a nautilus shell) and Tango's file manager icon.

![http://nautilussvn.googlecode.com/svn/wiki/images/mockups/mockup_context_menu.png](http://nautilussvn.googlecode.com/svn/wiki/images/mockups/mockup_context_menu.png)