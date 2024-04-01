[![Build status](https://ci.appveyor.com/api/projects/status/2arjuao3028n44p1?svg=true)](https://ci.appveyor.com/project/lboulard/vim-win32-build)

# GVim/Vim Win32 builder

Generate installers and archives for x86 and AMD64 CPU architecture using
Visual C++ 2019 build tools.

Inspired by <https://github.com/vim/vim-win32-installer> project and home grew
scripts.

Recent versions use `ninja.exe` to parallel builds of packages dependencies and
_Vim_. Build creates both platform version _x86_ and _amd64_ of _Vim_.

## Tribute to Bram Moolenaar

[Bram Moolenaar passed away 2023 August 3rd at the age of 62](https://groups.google.com/g/vim_announce/c/tWahca9zkt4)
Bram Moolenaar was author and maintainer of Vim for 30 years.
A group of volunteers started caring for Vim project since.

Thank you Bram for all you did in this world!
«Que la terre vous soit légère» (“May the earth rest lightly on you”).

## Requirements

### Git, Curl and 7-Zip

- Git: <https://git-scm.com>
- Curl: <https://curl.haxx.se/download.html>
- 7-Zip: <http://www.7-zip.org/>

You can also use `curl` found inside Git installation in place of Windows
native one.

Install 7-Zip version matching operating system architecture. On x86 system,
installs 32bit version. On x64/AMD64 system, installs 64bit version.

### MSYS2 install

- MSYS2: <http://www.msys2.org/>

In order to generate file `uganda.nsis.txt`, a suite of Unix tools is required.
MSYS2 is expected to be installed at `C:\msys64`. Basic installation is enough,
only _bash_, _GNU make_, _uniq.exe_ and _sed.exe_ are used while generating
`uganda.nsis.txt`

> This is heavy requirement for such a light task.
> TODO: embed _sed.exe_ and do text transformation in dosbatch script.

### Computer installation of Python 2.7 and 3.11

It is not possible to fetch and extract Python software just for building Vim.
Python 2.7 is expected to be installed in `C:\Python27`. Python 3.11 is
expected to be installed in `C:\Program Files\Python311`.

### Microsoft Software

#### Visual Studio 2015 (until tag v8.1.0611)

Visual C++ 2015 compiler can be downloaded free of charge on this page:
<http://landinghub.visualstudio.com/visual-cpp-build-tools>. This is the direct
download link:

- [Visual C++ 2015 Build Tools](http://go.microsoft.com/fwlink/?LinkId=691126&fixForIE=.exe)

#### Visual Studio 2017 (until tag v8.2.3114)

Install Visual Studio 2017 Community edition. You need to create a (free)
account at Microsoft.

#### Visual Studio 2019

Install Visual Studio 2019 Community edition. You need to create a (free)
account at Microsoft.

## Usage

Open a DOS prompt and go to project root. Run DOS prompt as normal user, not as
administrator.

First create a virtualenv in `.venv` folder to further get runtime
dependencies. Then install dependencies:

```dosbatch
py -3 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Download archives and installers

```dosbatch
download.bat
```

It can take a long depending of network connection speed.

### Prepare GVim/Vim dependencies

List and version of GVim/Vim dependencies used for build and packages:

- [UPX](http://upx.sourceforge.net/) 4.2.3
- [GetText](https://github.com/mlocati/gettext-iconv-windows) 0.21 and iconv 1.16
- [LuaBinaries](http://luabinaries.sourceforge.net/download.html) 5.1.4
- [WinPTY](https://github.com/rprichard/winpty) 0.4.3
- [Libsodium](https://doc.libsodium.org) 1.0.18
- [dmake](https://cpan.metacpan.org/authors/id/S/SH/SHAY/) 4.12.2.2
- [Perl](http://www.perl.org) 5.32.1
- [Tcl](http://www.tcl.tk) 8.6.11
- [Ruby](https://www.ruby-lang.org/en/downloads/) 3.2.2
- [ninja](https://ninja-build.org) 1.11.1
- [NSIS](http://nsis.sourceforge.net) 3.09

> Racket 7.9 does not compile due to a missing include header in distribution.

To prepare all required software for building GVim/Vim at next step, run:

```dosbatch
7z x downloads\ninja-win.zip ninja.exe
configure.bat
ninja packages
```

It is possible to only prepare a specific package:
 - _UPX_: `ninja upx` to unzip UPX for NSI package creation phase.
 - _GetText_: `ninja winpty` to extract GetText archive.
 - _Lua_: `ninja lua_x86 lua_x64` to extract Lua archive.
 - _Perl_: `ninja perl_x86 perl_x64` to extract and compile Perl.
 - _Tcl_: `ninja tcl_x86 tcl_x64` to extract and compile Tcl.
 - _Ruby_: `ninja ruby_x86 ruby_x64` to extract and compile Ruby.

Not that Ruby needs to be compiled using VisualStudio before being able to
compile GVim/Vim. There is not ready to use archive for Ruby + VisualStudio.
Ruby preparation is the longest of all tasks.

### Build GVim/Vim and package installations

```dosbatch
ninja gvim
```

You shall now have files `gvim-9.1.xxx-ARCH.exe` and `gvim-9.1.xxx-ARCH.zip` in
root folder.

## Patches

By default a patch to embed Lua DLL in final delivery is incorporated in this
project.

You can add custom patches in `patch` directory.
