#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
import argparse
import types
from jinja2 import Template, StrictUndefined, Environment, FileSystemLoader
try:
    import colorama
    colorama.init()
except ImportError:
    pass

from lib.package import Arch, Package, PackageException

class ConfigDir:
    def __init__(self, builds, packages):
        self.builds = builds
        self.packages = packages

Config = ConfigDir('builds', 'pkgs')

class ConfigException(Exception):
    pass

class ConfigPackage:
    def __init__(self, package, config=Config):
        self.package = package
        self.config = config

    @property
    def version(self):
        return self.package.version

    @property
    def install(self):
        pkg = self.package
        if pkg.defined(Package.INSTALL):
            installs = types.SimpleNamespace()
            packages_dir = self.config.packages
            it = iter(pkg.get(Package.INSTALL).split())
            for arch, path in zip(it, it):
                arch = str(Arch.find(arch))
                path = pkg.expand(path)
                if not os.path.isabs(path):
                    path = os.path.abspath(os.path.join(packages_dir, path))
                    if not hasattr(installs, arch):
                        setattr(installs, arch, path)
                elif os.path.exists(path) and not hasattr(installs, arch):
                    setattr(installs, arch, path)
            return installs
        raise ConfigException('install not defined for package {}'.format(pkg.name))

    @property
    def vim_version(self):
        pkg = self.package
        if pkg.defined('Vim-Version'):
            version = pkg.get('Vim-Version').split()
            if len(version) == 1:
                return version[0]
            elif len(version) > 1:
                return version
            else:
                raise ConfigException('Incorrect Vim-Version in package {}'
                                      .format(pkg.name))
        raise ConfigExceptin('Vim-Version not defined for package {}'.format(pkg.name))

    @property
    def source_dir(self):
        pkg = self.package
        if pkg.defined('Source-Dir'):
            builds_dir = self.config.builds
            sources_dir = types.SimpleNamespace()
            source = pkg.expand(pkg.get('Source-Dir'))
            for arch in self.install.__dict__.keys():
                path = os.path.join(builds_dir, arch, source)
                setattr(sources_dir, arch, os.path.abspath(path))
            return sources_dir
        raise ConfigException('Source-Dir not defined for package {}'
                              .format(pkg.name))


class VimPackage(Package):

    def __init__(self, version):
        super().__init__()
        self.set(Package.NAME, 'vim')
        self.set(Package.VERSION, version)


def make_config(packages, vim_version):
    configs = dict()
    for package in packages:
        configs[package.name] = ConfigPackage(package)
    vim = VimPackage(vim_version)
    configs[vim.name] = ConfigPackage(vim)
    return configs

def render(pathname, templatepath, config):
    env = Environment(loader=FileSystemLoader(searchpath="./"))
    template = env.get_template(templatepath)
    print('generating config file \"{}\"'.format(pathname))
    with open(pathname, 'w+') as f:
        f.write(template.render(**config))

def main():
    parser = argparse.ArgumentParser(description='Download external packages.')
    parser.add_argument('packages', type=argparse.FileType(encoding='utf-8'),
                        nargs='+', help='list of packages to read')
    parser.add_argument('-o', '--ninja', type=str, dest='ninja',
                        default='', help='Generate ninja file')
    parser.add_argument('-b', '--batch', type=str, dest='batch',
                        default='', help='Generate dosbatch file')
    parser.add_argument('--vim', type=str, dest='vim_version', default='',
                        required=True, help='Generate dosbatch file')
    args = parser.parse_args()
    packages = []
    for f in args.packages:
        packages += Package.read(f)
    config = make_config(packages, vim_version=args.vim_version[1:])
    if args.batch:
        render(args.batch, args.batch + '.j2', config)
    if args.ninja:
        render(args.ninja, args.ninja + '.j2', config)


if __name__ == '__main__':
    main()
