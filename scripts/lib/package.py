#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import string
from .rfc822 import RFC822


class PackageException(Exception):
    pass


class UnknownArchitecture(Exception):
    def __init__(self, arch):
        super().__init__("Unknown architecture {}".format(arch))


class _Architecture:

    def __init__(self, name, alias=None):
        self.name = name
        self.alias = alias or []

    def match(self, name):
        """Return True if `name` is compatible with this architecture."""
        return name == self.name or name in self.alias

    def same(self, name):
        """'Returns True if `name` is same as this architecture."""
        return self.match(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Arch({})>'.format(self.name)


# Package with binaries for all architectures
class _AllArchitecture(_Architecture):

    def __init__(self, excludes=None):
        super().__init__('all', ['All', 'ALL'])
        self.excludes = excludes or []

    def match(self, name):
        return all([not arch.match(name) for arch in self.excludes])

    def same(self, name):
        return super().match(name)


class Architectures:

    def __init__(self):
        self._known = []
        self.any = self.register(_Architecture('any', ['ANY', 'Any'])) # Any source package
        self.all = self.register(_AllArchitecture(excludes=[self.any]))

    def register(self, arch):
        assert isinstance(arch, _Architecture)
        self._known.append(arch)
        return arch

    def find(self, name):
        for arch in self._known:
            if arch.same(name):
                return arch
        raise UnknownArchitecture(name)

    def match(self, target):
        return [arch for arch in self._known if target.match(arch.name)]


Arch = Architectures()
Arch.register(_Architecture('x86', ['X86', '386', 'i386']))
Arch.register(_Architecture('x64', ['X64', 'amd64', 'AMD64']))


class Resource:

    def __init__(self, arch, archive, url):
        self.archive = archive
        self.url = url
        self.arch = arch
        self.checksums = None

    def get(self):
        return self.arch, self.archive, self.url


class Template(string.Template):
    pass


class Package:
    NAME = 'name'
    VERSION = 'version'
    SOURCE = 'source'
    BINARY = 'binary'
    ARCHIVE = 'archive'
    INSTALL = 'install'
    CHECKSUM = 'checksum'

    def __init__(self):
        self._values = dict()

    def __getattr__(self, name):
        if self.defined(name):
            return self._values[name]
        name = name.lower().replace('-', '_')
        if self.defined(name):
            return self._values[name]
        raise AttributeError(name)

    def valid(self):
        return self.defined(Package.NAME) and \
                self.defined(Package.VERSION)

    def defined(self, name):
        name = name.lower().replace('-', '_')
        return name in self._values.keys()

    def get(self, name):
        return self._values.get(name.lower().replace('-', '_'))

    def expand(self, s):
        tmpl = Template(s)
        class IDict(dict):
            def __missing__(self, key):
                v = self[key.lower().replace('-', '_')]
                return v
        return tmpl.safe_substitute(IDict(self._values))

    def set(self, name, value):
        name = name.lower().replace('-', '_')
        if self.defined(name):
            raise PackageException('{} already defined'.format(name))
        self._values[name] = value

    def as_arch_list(self, name, arch=None):
        entries = list()
        if self.defined(name):
            v = iter(self._values[name].split())
            for target, archive, url in zip(v, v, v):
                if arch is None or arch.match(target):
                    entries.append((Arch.find(target), archive, self.expand(url)))
        return entries

    def resources_for_arch(self, name, arch):
        """Collect resources for sources or binaries of a given architecture.
        `name` argument can only `Package.SOURCE` or `Package.BINARY`.
        `arch` is one of defined in `Arch` module variable.
        """
        resources = list()
        if not (name == Package.SOURCE or name == Package.BINARY):
            return resources
        resources = self.as_arch_list(name, arch)
        resources = [Resource(*args) for args in resources]
        # Find corresponding checksums for each archive
        for resource in resources:
            resource.checksums = self.checksum_for_archive(resource.archive)
        return resources

    def resources(self):
        """returns a list of Resource objects.
        This is all sources and binaries resources defined in package."""
        return self.resources_for_arch(Package.SOURCE, Arch.any) + \
                self.resources_for_arch(Package.BINARY, Arch.all)

    def checksum_for_archive(self, filename):
        if self.defined(Package.CHECKSUM):
            it = iter(self.checksum.split())
            return [(algo, h) for path, algo, h in zip(it, it, it)
                    if path == filename]
        return []

    def install_paths(self):
        installs = list()
        if self.defined(Package.INSTALL):
            it = iter(self._values[Package.INSTALL].split())
            for arch_name, path in zip(it, it):
                arch = Arch.find(arch_name)
                installs.append((arch, self.expand(path)))
        return installs

    def _title_key(self, key):
        s = []
        while True:
            for c in '-_+':
                key, sep, rem = key.partition(c)
                if sep:
                    break
            s.append(key.capitalize())
            key = rem
            if sep:
                s.append(sep)
            else:
                break
        return ''.join(s)

    def __str__(self):
        name = self._values.get(Package.NAME, '?')
        version = self._values.get(Package.VERSION, '?')
        return 'Package({}, {})'.format(name, version)

    def __repr__(self):
        return '[Package: {}]'.format(['{}: {}'.format(self._title_key(k), v)
                                       for k, v in self._values.items()])

    @staticmethod
    def read(f):
        pkgs = []
        for msg in RFC822(f).messages():
            pkg = Package()
            for key, value in msg:
                k = key.lower()
                if k == 'package':
                    pkg.set(Package.NAME, value)
                elif k == Package.NAME:
                    raise PackageException('{} is not allowed in keys'
                                           .format(key))
                else:
                    pkg.set(k, value)
            if pkg.valid():
                pkgs.append(pkg)
        return pkgs
