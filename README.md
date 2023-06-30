# asplode

Recursively decompress archives.

By default, `asplode` will infinitely recurse to decompress all archives contained within the given archive. The option `--level` / `-l` can be provided to limit the depth of the recursion.

```
$ asplode -h
usage: asplode [-h] [-v] [-C DIR] [-l 0] ARCHIVE

positional arguments:
  ARCHIVE           Path to the archive file

options:
  -h, --help        show this help message and exit
  -v, --verbose     Enable verbose output
  -C DIR, --cd DIR  Directory to change to before extraction, ala tar (default: .)
  -l 0, --level 0   Levels of recursion (default: 0, infinite)
```
