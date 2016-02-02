# Introduction #

Forget all about bytes and think of Unicode strings as sets of symbols. Now, there are at least 4 ways to encode the the Greek symbol Omega (Ω or U+03A9) as binary:

| **Encoding name** | **Binary representation** |
|:------------------|:--------------------------|
| ISO-8859-7        | `\xD9` "Native" Greek encoding |
| UTF-8             | `\xCE\xA9`                |
| UTF-16            | `\xFF\xFE\xA9\x03`        |
| UTF-32            | `\xFF\xFE\x00\x00\xA9\x03\x00\x00` |


The `\u` escape sequence is used to denote Unicode codes. This is somewhat like the traditional C-style `\xNN` to insert binary values.

When you convert Unicode symbols to bytes you are encoding. To encode the symbol Ω (`u'\u03A9'`) to UTF-8 you use `u'\u03A9'.encode('utf-8')` which results in `'\xce\xa9'`. To decode this bytestring back into Unicode you use `unicode('\xce\xa9', 'utf-8')` which once again results in `u'\u03a9'`.

# Resources #

  * [Unicode In Python, Completely Demystified](http://farmdev.com/talks/unicode/)
  * [All About Python and Unicode](http://boodebr.org/main/python/all-about-python-and-unicode)
  * [The Truth About Unicode In Python](http://www.cmlenz.net/archives/2008/07/the-truth-about-unicode-in-python)