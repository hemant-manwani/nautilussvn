# Introduction #

This FAQ applies to the upcoming release, v0.12, and not the current (legacy) release v0.11.

# You're not a hax0r if you don't use $ svn! The GUI sucks, so you suck! #

Yeah.. uhh... look, don't get us wrong, we love the command line! We use it all the time ourselves, we do a lot finding, grepping, sedding, xarging, piping, redirecting and all that. We've got some real mean one-liners stashed away in our ~/.bash\_aliases file.

But we're really into this visual paradigm towards file management thing. Let's take a look at where using the svn command just isn't very awesome (if you didn't create some crazy aliases or build some crazy MC extension on top of it):

  * Quickly giving you a sense of the state of a working copy. svn status either shows too much, or you get RSI in the process. With NautilusSvn you can just browse like you always do and the statuses will be displayed as pretty emblems.

  * Quickly doing something with the output of a command. I personally can do [596CPM](http://speedtest.aoeu.nl/) but it's things like this that just kill me. Here's a typical example:
```
$ svn status
?      a_file
?      another_file
?      another_one
?      and_another_one
?      a_pretty_directory

$ svn add a_file another_file
```

  * Just committing a few specific files. Even with some crazy aliases there's no way you can beat the mouse with its super duper clickability and the power of checkboxes.

# Why not just use (KDESvn, eSvn, RapidSVN, QSvn, Subcommander etc.)? #

What can we say, we're just crazy about Nautilus and TortoiseSVN. Though many of these client support a lot of versioning functionality, a lot of these do not integrate into a file manager (KDESvn being the only real exception) and none of these are true TortoiseSVN clones.

We wish the developers of all these projects the best of luck and in the true spirit of open source we'll be sure to lift any interesting features they implement. ;-)

# Noes!!! Anything but SVN! #

Sorry, our sincerest apologies. However, with an eye to the future we've started abstracting away from the actual VCS implementation. By doing this we increase the reusability of major components of the system, so that in the future it will be trivially easy to support a different VCS whether that be Bazaar, Monotone, Git or any other VCS. We're not there yet, but we believe we're well underway. We've made sure that this goal would not interfer with our support of Subversion.

Git support is on [our roadmap](http://code.google.com/p/nautilussvn/wiki/Roadmap) for v0.14. After that release you're more than welcome to write a VCS plugin to support your favorite VCS.

# Can we use this under Thunar? #

Not yet, but this is definitely something on our minds. We've abstracted the versioning and Nautilus extension bits so much that this'll be a cakewalk in the near future. This won't be in v0.12 though.

# Does this run on `*`BSD? #

We haven't tried it yet, but if you'd like to do some testing, please let us know!