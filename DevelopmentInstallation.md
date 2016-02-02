> **<font color='red'>WARNING: Only follow these instructions if you actually want to hack on NautilusSvn, otherwise stick to installing the <a href='SnapshotInstallation.md'>development snapshot</a>. If you are an end-user please do not follow these instructions.</font>**

It's a good idea organize your code in the following way, this makes it easy to switch between branches and whatnot without fiddling too much.

## Directory structure ##

```
mkdir -p ~/Development/nautilussvn/branches
ln -s ~/Development/nautilussvn/trunk ~/Development/nautilussvn/current
```

You'll notice later that this will make it easy to switch between branches, you simply have to change the directory current is pointing to (as long as the branch doesn't deviate too much).

## Checking out NautilusSvn ##

Do want the SVN HEAD?
```
svn checkout http://nautilussvn.googlecode.com/svn/trunk ~/Development/nautilussvn/trunk
```

...or the development snapshot?
```
svn checkout http://nautilussvn.googlecode.com/svn/tags/latest-snapshot ~/Development/nautilussvn/trunk
```


Of course, you can replace `~/Development` with wherever you want it to reside. Let's link everything to the current directory:

```
mkdir -p ~/.nautilus/python-extensions
ln -s ~/Development/nautilussvn/current/nautilussvn/lib/extensions/nautilus/NautilusSvn.py ~/.nautilus/python-extensions/NautilusSvn.py
mkdir -p ~/.icons
ln -s ~/Development/nautilussvn/current/nautilussvn/data/icons/hicolor ~/.icons/ 
```

## Setting up a local PYTHONPATH ##

```
~/Development/python 
~/Development/python/nautilussvn symbolic link to ~/Development/nautilussvn/current/nautilussvn
```

Change `~/.profile` to include the line:

```
export PYTHONPATH="/home/bruce/Development/python"
```

And parse this file in your `~/.bashrc` so this environment variable is also available to Bash (note that ~/.profile needs to executable):

```
# Source .profile
if [ -f ~/.profile ]; then
  . ~/.profile
fi
```

Placing it in `~/.profile` is needed because your GNOME session isn't started from a shell, so `~/.bashrc` etc. is not parsed. You'll have to restart your session (logout/login) for the changes to take effect. Or you can load the extension immediately using (it won't be available to any programs not started from the shell though):

```
export PYTHONPATH="$PYTHONPATH:/home/$USER/Development/python/"
[run nautilus now]
```

## Running for Debugging ##

Firstly, you need to terminate Nautilus itself and the status checker service...

```
nautilus -q ; pgrep -f service.py | xargs kill
```

...and then start it up:

```
nautilus --no-desktop . ; pgrep -f service.py | xargs kill
```

I recommend either logging to console (set in the settings menu for NautilusSVN), or my preference: running

```
tail -n 0 -f ~/.config/nautilussvn/NautilusSvn.log
```

...in a separate nice, wide console.

When you're done, just run

```
nohup nautilus > /dev/null &
```

...and you can close the terminal.