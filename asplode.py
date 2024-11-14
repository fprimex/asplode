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
@plac.flg("verbose", "Enable verbose output")
@plac.pos("name", "Path to the archive file", type=Path, metavar="ARCHIVE")
@plac.opt("cd", "Directory to change to before extraction, ala tar (default: .)", abbrev="C", metavar="DIR")
@plac.opt("level", "Levels of recursion (default: 0, infinite)", type=int)
def asplode(name, verbose=False, cd=Path("."), level=0):
    end_recursion = False

    if level > 0:
        level -= 1
        if level == 0:
            end_recursion = True

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
        extract_files = [f for f in list(extract_dir.glob("*")) if f != extract_dir]
        if len(extract_files) == 1:
            # If there's only one file/dir in the dir, move the file/dir back
            # one into the parent dir and remove the extract directory.  The
            # classic tar.gz -> dir and txt.gz -> file cases.
            shutil.move(str(extract_files[0]), str(start_dir))
            shutil.rmtree(extract_dir.name)

            # Set the name of the extracted dir for recursive decompression
            extract_dir = start_dir / Path(extract_files[0].name)
        else:
            # If there's more than one file in the dir, rename the extract dir
            # to the basename of the archive. The 'barfing files all over pwd'
            # case, the 'archive contains usr/bin and var/log/blah/blah and
            # etc' case.
            shutil.move(str(extract_dir), basepath.name)

            # Set the name of the extracted dir for recursive decompression
            extract_dir = basepath
    except shutil.Error as e:
        print(' Error arranging directories:')
        print('  ' + str(e))
        return

    # See if there's anything left to do
    if end_recursion or not extract_dir.is_dir():
        return

    # Get a list of files for recursive decompression.
    sub_files = []
    for path in extract_dir.glob(r'*'):
        if path.suffix[1:] in archive_exts:
            sub_files.append(path)

    # Extract anything compressed that this archive had in it.
    os.chdir(extract_dir)
    for sub_file in sub_files:
        asplode(sub_file, level=level)
    os.chdir(str(start_dir))


def main(argv=None):
    plac.call(asplode)
    return 0
