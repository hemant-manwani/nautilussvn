# How fast is svn status? #

```
sudo bash -c "sync; echo 3 > /proc/sys/vm/drop_caches"
time svn status > /dev/null
```

# How fast is NautilusSvn? #

```
nautilus -q
cd ~/Development/tortoisesvn
sudo bash -c "sync; echo 3 > /proc/sys/vm/drop_caches"
time nautilus --no-desktop . # close with ALT + F4 as soon as it is loaded
```