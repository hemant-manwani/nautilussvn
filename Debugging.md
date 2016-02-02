# Introduction #

There are several ways to debug a running program.

The most basic method and the one that is most popular with beginning programmers is littering print statements throughout the code to let you know what's going on. However, apart from littering (which makes for ugly code) it's also not very flexible. It also tends a to happen a lot that these statements end up in the repository, which is not cool.

Experts on the other hand mostly prefer attaching debuggers to running processes instead. However, is this possible for us as a Nautilus extension? It might be, but my experience with debuggers is limited to debugging Java applications from Eclipse.

# What makes a debugging tool #

Next to being easy to use, flexible and whatnot good debugging tools give  you the ability to:

  * Inspect any aspect of the program
  * Change any variables on the fly
  * Dynamically run code
  * Etc.

# What we currently do #

  * We have a context menu entry which starts up an IPython shell in the context of the context menu callback. This allows us to inspect and modify any aspect of the program dynamically, which is truly awesome.

  * We do litter debugging statements around in the code as:

```
# Begin debugging code
print "Debug: foo() did something"
# End debugging code
```

> If we're not able to attach a debugger we should look into eliminating these statements by using decorators to attach them from the outside so instead we'd do (is it possible to attach it to a certain statement or something like that?):

```
@debug
def foo():
    pass
```

> The resulting debugging module should also be able to filter what print statements are shown, so we aren't faced with information overflow. Also by flipping a switch it should be disabled entirely (simple condition).