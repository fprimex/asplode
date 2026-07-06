# asplode (and my other Zendesk related projects) Are Now Archived.

I have not worked on this codebase for quite some time, and don't wish to give
people false hope that I am going to maintain it going forward. I had hoped
someone in the community might be willing to work with me as a maintainer, but
that has not happened.

Cheers, it's been fun :)

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
