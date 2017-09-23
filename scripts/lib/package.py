#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Package parsing."""

import string
from .rfc822 import RFC822


class PackageException(Exception):
    """Failure in package definition."""

    def __init__(self, name, field, reason):
        """Create a PackageException with `name` as package name,
`field` as name of incorrect field, `reason` for details of failure.
"""
        super().__init__(name, field, reason)
        self.package = name
        self.field = field
        self.reason = reason

    def __str__(self):
        return 'PackageException: package {}, field {}, {}'.format(self.package,
                                                                   self.field,
                                                                   self.reason)


class UnknownArchitecture(Exception):
    """An undefined architecture as been encounter while parsing package
definitions."""
    def __init__(self, arch):
        """Create a `UnknownArchitecture` object for `arch` string."""
        super().__init__("Unknown architecture {}".format(arch))


class Architecture:
    """Define an `Architecture` object."""

    def __init__(self, name, alias=None):
        """Create an architecture named `name`.
A list of alias can be given in `alias` parameter.
"""
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
class _AllArchitecture(Architecture):

    def __init__(self, excludes=None):
        super().__init__('all', ['All', 'ALL'])
        self.excludes = excludes or []

    def match(self, name):
        return all([not arch.match(name) for arch in self.excludes])

    def same(self, name):
        return super().match(name)


class Architectures:
    """Registers and manage Architectures."""

    def __init__(self):
        """Create a new `Architectures` object.
By default `any` and `all` are created to respectively match source package and
all binary package.
"""
        self._known = []
        self.any = self.register(Architecture('any', ['ANY', 'Any'])) # Any source package
        self.all = self.register(_AllArchitecture(excludes=[self.any]))

    def register(self, arch):
        """Register a new architecture in global pool."""
        assert isinstance(arch, Architecture)
        self._known.append(arch)
        return arch

    def find(self, name):
        """Return `Architecture` object named `name`."""
        for arch in self._known:
            if arch.same(name):
                return arch
        raise UnknownArchitecture(name)

    def match(self, target):
        """Return list of architectures matching `target`.
`target` is a compatible `Architecture` object."""
        return [arch for arch in self._known if target.match(arch.name)]


Arch = Architectures()
Arch.register(Architecture('x86', ['X86', '386', 'i386']))
Arch.register(Architecture('x64', ['X64', 'amd64', 'AMD64']))


class Resource:
    """Package resource."""

    def __init__(self, arch, archive, url):
        """Resource defined by `arch`, an `Architecture` object,
`archive`, name of local archive to store downloaded file,
`url`, URL to resource that need to be downloaded.
"""
        self.archive = archive
        self.url = url
        self.arch = arch
        self.checksums = None

    def get(self):
        """Returns tuple `(arch, archive, url)`.
`arch` is an Arch object, `archive` is the name of local archive on file system,
`url` is the URL from where to fetch archive."""
        return self.arch, self.archive, self.url


class Template(string.Template):
    """Adapt `string.Template` to support `id` with `-` in name."""
    idpattern = r'[_a-z][_a-z0-9-]*'


def _title_key(key):
    title = []
    while True:
        for char in '-_+':
            key, sep, rem = key.partition(char)
            if sep:
                break
        title.append(key.capitalize())
        key = rem
        if sep:
            title.append(sep)
        else:
            break
    return ''.join(title)

class Package:
    """Describe a package."""

    NAME = 'name'
    VERSION = 'version'
    SOURCE = 'source'
    BINARY = 'binary'
    ARCHIVE = 'archive'
    INSTALL = 'install'
    CHECKSUM = 'checksum'

    def __init__(self):
        """Create a new package."""
        self._values = dict()

    def __getattr__(self, name):
        if self.defined(name):
            return self._values[name]
        raise AttributeError(name)

    def valid(self):
        """A package is valid when at least a name and version is defined."""
        return self.defined(Package.NAME) and \
                self.defined(Package.VERSION)

    def defined(self, name):
        """Check if field is defined."""
        name = name.lower().replace('-', '_')
        return name in self._values.keys()

    def get(self, name):
        """Returns field content or None if not defined."""
        return self._values.get(name.lower().replace('-', '_'))

    def expand(self, var):
        """Substitute `$var` or `${var}` in string `s`.
`var` is taken from defined header in package."""
        tmpl = Template(var)
        class IDict(dict):
            """Dictionary when 'a-b' and 'a_b' are equivalent."""
            def __missing__(self, key):
                key = self[key.lower().replace('-', '_')]
                return key
        return tmpl.safe_substitute(IDict(self._values))

    def set(self, name, value):
        """Set attribute `name` to `value`.
Raise `PackageException` if `name` was already defined.
"""
        name = name.lower().replace('-', '_')
        if self.defined(name):
            raise PackageException(self.name, _title_key(name), 'already defined')
        self._values[name] = value

    def __as_arch_list(self, name, arch=None):
        entries = list()
        if self.defined(name):
            for line in self._values[name].splitlines():
                try:
                    target, archive, url = line.split(maxsplit=2)
                except ValueError as ex:
                    raise PackageException(self.name, _title_key(name), str(ex))
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
        resources = self.__as_arch_list(name, arch)
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
        """Return a list of tuple `(algo, checksum)` matching `filename`."""
        if self.defined(Package.CHECKSUM):
            tokens = iter(self.checksum.split())
            return [(algo, h) for path, algo, h in zip(tokens, tokens, tokens)
                    if path == filename]
        return []

    def install_paths(self):
        """Returns list of installation paths per architecture.
This is a list of tuple `(arch, path)`. `path` is expanded.
"""
        installs = list()
        if self.defined(Package.INSTALL):
            tokens = iter(self._values[Package.INSTALL].split())
            for arch_name, path in zip(tokens, tokens):
                arch = Arch.find(arch_name)
                installs.append((arch, self.expand(path)))
        return installs

    def __str__(self):
        name = self._values.get(Package.NAME, '?')
        version = self._values.get(Package.VERSION, '?')
        return 'Package({}, {})'.format(name, version)

    def __repr__(self):
        return '[Package: {}]'.format(['{}: {}'.format(_title_key(k), v)
                                       for k, v in self._values.items()])

    @staticmethod
    def read(io):
        """Returns all parsed and valid packages."""
        pkgs = []
        for msg in RFC822(io).messages():
            pkg = Package()
            name = ''
            for key, value in msg:
                k = key.lower()
                if k == 'package':
                    pkg.set(Package.NAME, value)
                    name = value
                elif k == Package.NAME:
                    raise PackageException(name, key, 'not allowed in keys')
                else:
                    pkg.set(k, value)
            if pkg.valid():
                pkgs.append(pkg)
        return pkgs
