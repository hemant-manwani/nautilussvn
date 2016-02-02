# NautilusSvn 0.12 #

  * Improved status checking and emblem support.
  * Complete rewrite of extension and user interface layer.
  * An entirely new context menu in Nautilus including submenus.
  * New UIs: Add, Copy/Branch, Cleanup, Export, Import, Lock, Merge, Relocate, Revert, Rename, Settings, Switch, Unlock, Update-to-Revision.
  * Updated UIs: Checkout, Commit, Popup Dialogs, Log, Notifications, Properties.
  * Many UIs now have context menus.
  * Working packages and installation instructions for major distros (Ubuntu, Fedora).
  * Internationalization support.

# NautilusSvn 0.13 #

  * Improved status checking and emblem support. Manual status refresh no longer required.
  * Do a code review for the entire code base and refactor based on the results, with the goal of making the code more elegant, flexible, maintainable, robust etc.. Subtasks include:
    * Eliminate all redundancy (e.g. context menu generation)
    * Logically organize helper functions (for example helper.path, helper.string etc.)
    * Make all functionality more robust (e.g. defensive coding, handling exceptions properly without "crashing" the extension)
    * Make sure all forms are validated and don't cause breakage
  * Implementation of a Nautilus Property Page.
  * Increase the depth and usefulness of the extension and dialogs

# NautilusSvn v0.14 #

  * Complete VCS abstraction layer. Support for Git.
  * Implementation of a repository browser.

# NautilusSvn 0.15 #

  * Implementation of a plugin system. Google Code integration as an example plugin.
  * Statistics functionality (graphing).

# NautilusSvn 0.16 #

  * Modify the context menu to use the Freedesktop.org [Desktop Menu Specification](http://standards.freedesktop.org/menu-spec/latest) and the [Desktop Entry Specification](http://standards.freedesktop.org/desktop-entry-spec/latest/).
  * Context menu reordering support in settings manager, basically this would be an embedded version of [Alacarte](http://en.wikipedia.org/wiki/Alacarte).