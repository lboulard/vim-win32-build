#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import argparse
import types
from jinja2 import Environment, FileSystemLoader
try:
    import colorama
    colorama.init()
except ImportError:
    pass

from lib.package import Package

class ConfigDir:
    def __init__(self, builds, packages, downloads):
        self.builds = builds
        self.packages = packages
        self.downloads = downloads

Config = ConfigDir('builds', 'pkgs', 'downloads')

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
    def archive(self):
        archives = types.SimpleNamespace()
        for resource in self.package.resources():
            archive = os.path.join(self.config.downloads, resource.archive)
            setattr(archives, str(resource.arch), os.path.normpath(archive))
        return archives

    @property
    def install(self):
        install_paths = self.package.install_paths()
        if install_paths:
            installs = types.SimpleNamespace()
            packages_dir = self.config.packages
            for arch, path in install_paths:
                arch = str(arch)
                if not os.path.isabs(path):
                    path = os.path.abspath(os.path.join(packages_dir, path))
                    if not hasattr(installs, arch):
                        setattr(installs, arch, path)
                elif os.path.exists(path) and not hasattr(installs, arch):
                    setattr(installs, arch, path)
            return installs
        raise ConfigException(
            "install not defined for package {}".format(self.package.name)
        )

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
        raise ConfigException('Vim-Version not defined for package {}'.format(pkg.name))

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

def render(pathname, templatepath, config, searchpath):
    if searchpath[-1] != '/':
        searchpath += '/'
    env = Environment(loader=FileSystemLoader(searchpath=searchpath))
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
    parser.add_argument('-t', '--template-dir', type=str,
                        dest='template_dir', default='./',
                        help='Generate ninja file')
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
        render(args.batch, args.batch + '.j2', config,
               searchpath=args.template_dir)
    if args.ninja:
        render(args.ninja, args.ninja + '.j2', config,
               searchpath=args.template_dir)


if __name__ == '__main__':
    main()
