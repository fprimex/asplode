import os
import gzip
import tarfile
import datetime
import re
import shutil
from zipfile import ZipFile, BadZipfile
from pathlib import Path


import plac


# plac annotation format
# arg = (help, kind, abbrev, type, choices, metavar)
@plac.annotations(cd =      ("Directory to change to before extraction, ala tar",
                             "option", "C", None, Path, "DIR"))
@plac.annotations(verbose = ("Enable verbose output",
                             "flag", "v", None, None, None))
@plac.annotations(name =    ("Path to the archive file",
                             "positional", None, Path, None, "ARCHIVE"))
def asplode(name, verbose=False, cd=Path(".")):
    raw_exts = r'zip|tar|tgz|tar\.gz|tar\.bz2|tar\.bz|gz'
    archive_exts = set(raw_exts.replace("\\", "").split("|"))

    start_dir = Path(".").absolute()
    name = Path(name)

    if not name.is_file():
        return 1

    # Match on the filename
    # [base].[ext]
    # where ext is one of zip, tar, gz, tgz, tar.gz, or tar.bz2
    m = re.match(r'^(?P<base>.*?)[.](?P<ext>' + raw_exts + r')$',
                 str(name.absolute()))

    if not m:
        # Not a compressed file that we're going to try to extract
        return 1

    if verbose:
        print(f' Extracting {name.name}')

    basepath = Path(m.groups()[0])
    ext = m.groups()[1]

    try:
        if ext == 'zip':
            cfile = ZipFile(name)
        elif ext == 'gz':
            cfile = gzip.open(name, 'r')
        else:
            cfile = tarfile.open(name, 'r:*')
    except (IOError, tarfile.ReadError, BadZipfile):
        print(f' Error reading file for extraction {name}')
        return

    try:
        # extract to a dir of its own to start with.
        extract_dir = Path(datetime.datetime.now().isoformat())
        if ext == 'gz':
            extract_dir.mkdir()
            f = open(extract_dir / basepath.name, 'wb')
            chunk = 1024*8
            buff = cfile.read(chunk)
            while buff:
                f.write(buff)
                buff = cfile.read(chunk)
            f.close()
        else:
            cfile.extractall(extract_dir.name)
    except OSError:
        print(f' Error extracting {name}')
        return
    finally:
        cfile.close()

    # If there's no directory at all, then it was probably an empty archive
    if not extract_dir.is_dir():
        return

    try:
        extract_files = list(extract_dir.glob("**"))
        if len(extract_files) == 1 and extract_files[0] == basepath.name:
            # If there's only one file/dir in the dir, and that file/dir
            # matches the base name of the archive, move the file/dir back one
            # into the parent dir and remove the extract directory.
            # The classic tar.gz -> dir and txt.gz -> file cases.
            shutil.move(extract_dir / extract_files[0], str(start_dir))
            shutil.rmtree(extract_dir.name)

            # Set the name of the extracted dir for recursive decompression
            extract_dir = extract_files[0]
        else:
            # If there's more than one file in the dir, or if that file/dir
            # doesn't match the base name of the archive rename the extract dir
            # to the basename of the archive.
            # The 'barfing files all over pwd' case, the 'archive contains
            # var/log/blah/blah' case, and the 'archive contains a single,
            # differently named file' case.
            shutil.move(extract_dir.name, basepath.name)

            # Set the name of the extracted dir for recursive decompression
            extract_dir = basepath
    except shutil.Error as e:
        print(' Error arranging directories:')
        print(' ' + e)
        return

    # See if there's anything left to do
    if not extract_dir.is_dir():
        return

    # Get a list of files for recursive decompression.
    # Right now, to be compatible with the one that used to ship with zdgrab,
    # this only looks at the results one directory deep. Later I'll add true
    # recursive searching, but I think more options to include/exclude things
    # need to be added at the same time as that feature.
    sub_files = []
    for path in extract_dir.glob(r'*'):
        if path.suffix[1:] in archive_exts:
            sub_files.append(path)

    # Extract anything compressed that this archive had in it.
    os.chdir(extract_dir)
    for sub_file in sub_files:
        asplode(sub_file)
    os.chdir(str(start_dir))


def main(argv=None):
    plac.call(asplode)
    return 0
