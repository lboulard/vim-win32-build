#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
import argparse
import hashlib
import requests
from tqdm import tqdm
try:
    import colorama
    colorama.init()
except ImportError:
    pass

from lib.package import Arch, Package, PackageException

class Download:

    def __init__(self, resource, directory=''):
        self.resource = resource
        self.directory = directory
        self.filename = os.path.join(directory, resource.archive)

    def outdated(self):
        if os.path.exists(self.filename):
            return not self.verify()
        return True

    def fetch(self):
        """Download remote file from resource url and write to resource archive.
        Return False in case of error, True when download correctly completed.
        """
        if self.directory and not os.path.exists(self.directory):
            os.mkdir(self.directory)
        chunk = 32 * 1024
        print('    Fetching {}'.format(self.resource.archive))
        try:
            r = requests.get(self.resource.url, stream=True)
            r.raise_for_status()
            size = int(r.headers.get('content-length', 0))
            with tqdm(total=size, unit='B', unit_scale=True) as pbar:
                with open(self.filename, 'wb+') as f:
                    for data in r.iter_content(chunk):
                        pbar.update(len(data))
                        f.write(data)
        except requests.exceptions.RequestException as exp:
            print(exp, file=sys.stderr)
            return False
        except ConnectionError as exp:
            print(exp, file=sys.stderr)
            return False
        except TimeoutError as exp:
            print(exp, file=sys.stderr)
            return False
        except KeyBoardInterrupt:
            print(exp, file=sys.stderr)
            return False
        return True

    def verify(self):
        """Returns True is file hash is valid.
        Will also report True if no checksum was defined.
        """
        resource = self.resource
        if resource.checksums:
            algo_hash, file_hash = None, ''
            for algo, hash in resource.checksums:
                if algo in hashlib.algorithms_available:
                    algo_hash, file_hash = algo, hash
            if algo_hash is None:
                print('** WARNING: ' +
                      'verification skipped, no supported algorithm found')
            else:
                print('    Verifing {}'.format(resource.archive))
                ctx = hashlib.new(algo_hash)
                with open(self.filename, 'rb', buffering=0) as f:
                    for buf in iter(lambda : f.read(32768), b''):
                        ctx.update(buf)
                if not (file_hash.lower() == ctx.hexdigest().lower()):
                    print('    Bad checksum for {}'.format(resource.archive))
                    return False
        return True


class WouldDownload(Download):

    def fetch(self):
        resource = self.resource
        print('    Will fetch {0.url}'.format(resource))
        print('      and save in {0.archive}'.format(resource))
        return True

    def verify(self):
        if self.resource.checksums:
            print('    Will verify checksum of {}'
                  .format(self.resource.archive))
        return True


def get_all(packages, arch='all', nop=False):
    matched_arch = Arch.match(Arch.find(arch))
    matched_arch.append(Arch.any)
    if not nop:
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', a)
    for package in packages:
        print('  For package {} ({})'.format(package.name, package.version))
        resources = package.resources()
        for resource in resources:
            if not any((resource.arch.match(a.name) for a in matched_arch)):
                continue
            if nop:
                klass = WouldDownload
            else:
                klass = Download
            down = klass(resource, directory='downloads')
            if down.outdated():
                if not down.fetch():
                    print('** ERROR: failed to download {}'
                          .format(resource.url))
                    return False
                if not down.verify():
                    print('** ERROR: Invalid checksum for {}'
                          .format(resource.archive))
                    return False
        if len(resources) == 0:
            print('    No archive to fetch')
    return True


def usage(out=sys.stderr):
    print("Usage: {} packages.txt [...]"
          .format(os.path.basename(sys.argv[0])), file=out)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Download external packages.')
    parser.add_argument('packages', type=argparse.FileType(encoding='utf-8'),
                        nargs='+', help='list of packages to read')
    parser.add_argument('-n', '--nop', dest='nop', action='store_true',
                        help='Describe what will be done')
    parser.add_argument('-a', '--arch', type=str, dest='arch', default='',
                        help='Only download for specific architecture')
    args = parser.parse_args()
    if args.arch:
        arch = args.arch
    else:
        arch = os.getenv('ARCH', 'all')
    pkgs = []
    for f in args.packages:
        pkgs += Package.read(f)
    if not get_all(pkgs, arch, nop=args.nop):
        sys.exit(1)


if __name__ == '__main__':
    main()
