# Idea #

Though we do a lot of informal testing and take great care to make sure the extension actually works we're currently not doing any formal testing. Formal testing (read: automated testing, unit testing etc.) is needed primarily for two reasons (there are more though):

  * As a developer you cannot do every single test from the top of your head. You will forgot to do some things which will lead to functionality X not working.

  * Regressions. Sometimes when you work on something, you break something completely else. Automated testing will help you to hunt these down immediately.

In the future we might look into using a Test Driven Development (TDD) approach.

# Types of tests #

  * Unit testing. See module [unittest](http://docs.python.org/library/unittest.html) and [the PyUnit documentation](http://pyunit.sourceforge.net/pyunit.html).

  * doctests. See module [doctest](http://docs.python.org/library/doctest.html).

# Cases #

Some cases where tests would be very useful:

  * Verifying Unicode support

  * Verifying emblem handling (are emblems added properly with the correct status?)

# Implementation #


```
.
|-- branches
|   `-- testing
|       `-- working_copy # this is the working copy that will be used for all tests
`-- trunk
    `-- nautilussvn
        `-- tests
            `-- data
                `-- working_copy # external definition to branches/testing/working_copy
```

> _generated using the tree command_