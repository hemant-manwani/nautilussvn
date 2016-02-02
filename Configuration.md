There are several user-definable switches in the file [helper.py](http://code.google.com/p/nautilussvn/source/browse/trunk/helper.py) that change the behaviour of the extension.

**ENABLE\_EMBLEMS** - This turns on/off the rendering of status emblems oneach file icon in the file browser.

**ENABLE\_ATTRIBUTES** - Adds revision and author columns to the list view in Nautilus.

**DIFF\_TOOL** - Specifes which executable to use for diff operations. I've tried it with gvidiff, but I mostly use Meld since it's ace.

**RECURSIVE\_STATUS** - If enabled, the file status check when drawing emblems will use recursive checks. This is a bit experimental, as it might cause high CPU loads on large working copies.

**SWAP** - Set to True to swap the order of old and new versions of files in diff tool. Default is False, new version at left and old one at right.