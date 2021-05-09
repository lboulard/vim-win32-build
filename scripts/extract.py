#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
import argparse
import zipfile
import tarfile
import shutil
import time
try:
    import colorama
    colorama.init()
except ImportError:
    pass


class ExtractException(Exception):
    pass

def rm_error(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def guess_format(archive):
    base, ext = os.path.splitext(archive)
    if ext == '.zip':
        return 'zip', None
    #
    if ext == '.tgz':
        ext, comp = '.tar', 'gz'
    elif ext == '.tbz':
        ext, comp = '.tar', 'bz2'
    elif ext == '.txz':
        ext, comp = '.tar', 'xz'
    elif ext in ('.gz', '.bz2', '.xz'):
        comp = ext[1:]
        base, ext = os.path.splitext(base)
    if ext == '.tar':
        return 'tar', comp
    raise Exception('Unknow archive format')


def extract_tar(archive, out, comp='*'):
    """Extract from tar archive."""
    with tarfile.open(archive, 'r:' + comp) as tar:
        tar.extractall(out)

def extract_zip(archive, out):
    """Extract from zip archive."""
    # Cannot use extractall(), it does not restore files dates.
    with zipfile.ZipFile(archive, mode='r') as z:
        for info in z.infolist():
            z.extract(info, path=out)
            pathname = os.path.join(out, info.filename)
            date_time = time.mktime(info.date_time + (0, 0, -1))
            os.utime(pathname, (date_time, date_time))

def extract(archive, path, out=None):
    out = out or path
    try:
        if os.path.exists(out):
            print('  Removing existing {}'.format(out))
            shutil.rmtree(out, onerror=rm_error)
        print('  {} -> {}'.format(archive, path))
        os.makedirs(path, exist_ok=True)
        fmt, comp = guess_format(archive)
        if fmt == 'zip':
            extract_zip(archive, path)
        elif fmt == 'tar':
            extract_tar(archive, path, comp)
        else:
            raise Exception('Unsupported archive format')
        if not os.path.exists(out):
            print('  Output path {} does not exists after archive extraction'
                  .format(out), file=sys.stderr)
            return False
        else:
            # Time of extracted root must be greater than archive
            if os.path.getmtime(out) < os.path.getmtime(archive):
                if not os.access(out, os.W_OK):
                    os.chmod(out, stat.S_IWUSR)
                now = time.time()
                os.utime(out, times=(now, now))
        return True
    except ExtractException:
        print('  Unkown archive format for {}'.format(archive), file=sys.stderr)
    return False


def main():
    parser = argparse.ArgumentParser(description='Download external packages.')
    parser.add_argument('archive',
                        help='Archive to extract')
    parser.add_argument('path', help='Output directory')
    parser.add_argument('-p', '--parent', dest='in_parent', action='store_true',
                        help='Extract to parent of target directory.' +
                        ' Last path component must match archive root.')
    args = parser.parse_args()
    archive, path, out = args.archive, args.path, None
    path = os.path.normpath(path)
    if args.in_parent:
        path, out = os.path.dirname(path), path
    if not extract(archive, path, out=out):
        print('** ERROR failed to extract {}'.format(archive), file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
