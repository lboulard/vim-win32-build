[![Build status](https://ci.appveyor.com/api/projects/status/2arjuao3028n44p1?svg=true)](https://ci.appveyor.com/project/lboulard/vim-win32-build)

# GVim/Vim Win32 builder

Generate installers and archives for x86 and AMD64 CPU architecture using
Windows SDK 7.1 build environment.

Inspired by <https://github.com/vim/vim-win32-installer> project and home grew
scripts.

## Requirements

### Git, Curl and 7-Zip

- Git: <https://git-scm.com>
- Curl: <https://curl.haxx.se/download.html>
- 7-Zip: <http://www.7-zip.org/>

You can also use `curl` found inside Git installation in place of Windows
native one.

Install 7-Zip version matching operating system architecture. On x86 system,
installs 32bit version. On x64/AMD64 system, installs 64bit version.

### Computer installation of Python 2.7 and 3.5

It is not possible to fetch and extract Python software just for building Vim.
Python 2.7 is expected to be installed in `C:\Python27`. Python 3.5 is expected
to be installed in `C:\Python35`.

### Microsoft Software

- [Windows SDK 7.1: Microsoft Windows SDK for Windows 7 and .NET Framework 4 (ISO)]
  (https://www.microsoft.com/en-us/download/details.aspx?id=8442)
- [Microsoft Visual C++ 2010 Service Pack 1 Compiler Update for the Windows SDK 7.1]
  (https://www.microsoft.com/en-us/download/details.aspx?id=4422)

You shall install SDK 7.1 before any VisualStudio 2010+ version.  If you want
to install VisualStudio 2010 on same computer as Windows SDK 7.1, installs in
order: Windows SDK 7.1, VisualStudio 2010, VisualStudio 2010 SP1, Windows SDK
7.1 Compiler update. If you do not respect this order, installation of Windows
SDK 7.1 will fail or installed compiler will not match installed VisualStudio
or SDK version.

If you plan to install VisualStudio 2012 and later, Windows SDK 7.1 should be
installed first too as recommended by Microsoft. Late installation of Windows
SDK 7.1 seems to work but no guaranty are made.

#### Installation on Windows 10

It is possible to install SDK 7.1 on Windows 10 by removing first VisualStudio
2010 Redistributable Package (x86 and x64). Then run installation from Windows
SDK 7.1 ISO by starting `Setup\SDKSetup.exe` executable. Do not forget to also
install Visual C++ 2010 Compiler SP1 Update for Windows SDK 7.1.

Then, you can reinstall VisualStudio 2010 runtime from those URL:

- [Microsoft Visual C++ 2010 SP1 Redistributable Package (x86)]
  (https://www.microsoft.com/en-US/download/details.aspx?id=8328)
- [Microsoft Visual C++ 2010 SP1 Redistributable Package (x64)]
 (https://www.microsoft.com/en-US/download/details.aspx?id=13523)

You shall download VisualStudio Redistributable Package matching installation
language of your operating system.

## Usage

Open a DOS prompt and go to project root. Run DOS prompt as normal user, not as
administrator. If you run as administrator, `build.bat` script may overwrite
already installed package like ActiveTcl.

You shall first enter SDK 7.1 build environment:

```dosbatch
setenv
```

To enter x86 environment, type `setenv /x86`, to enter x64/AMD64 environment,
type `setenv /x64`.

It is possible (and recommended) to open two CMD windows, each for an
environment. `build.bat` support running tasks in parallel from each
environment.

### Download archive and installer

```dosbatch
build download
```

It can take a long depending of you Internet connection speed.

### Prepare GVim/Vim dependencies

List and version of GVim/Vim dependencies used for build and packages:

- [UPX](http://upx.sourceforge.net/) 3.91
- [GetText](https://github.com/mlocati/gettext-iconv-windows) 0.19.8.1 and iconv 1.14
- [LuaBinaries](http://luabinaries.sourceforge.net/download.html) 5.1.4
- [ActivePerl](http://www.activestate.com/activeperl/downloads) 5.24
- [ActiveTcl](http://www.activestate.com/activetcl/downloads) 8.6
- [Racket](https://download.racket-lang.org/) 6.6
- [Ruby](https://www.ruby-lang.org/en/downloads/) 2.3.1

To prepare all required software for building GVim/Vim at next step, run:

```dosbatch
build prepare
```

It is possible to only prepare a specific package:
 - _UPX_: `build prepare-upx` to unzip UPX for NSI package creation phase.
 - _GetText_: `build prepare-gettext` to extract GetText archive.
 - _Lua_: `build prepare-lua` to extract Lua archive.
 - _Perl_: `build prepare-perl` to extract Perl archive.
 - _Tcl_: `build prepare-tcl` to install Tcl locally.
 - _Racket_: `build prepare-racket` to extract Racket archive
 - _Ruby_: `build prepare-ruby` to extract and compile Ruby.

Not that Ruby needs to be compiled using VisualStudio before being able to
compile GVim/Vim. There is not ready to use archive for Ruby + VisualStudio.
Ruby preparation is the longest of all tasks.

### Build GVim/Vim and package installations

```dosbatch
build build package
```

You shall now have files `gvim-7.4.xxx-ARCH.exe` and `gvim-7.1.xxx-ARCH.zip` in
root folder.

## Patches

By default a patch to embed Lua DLL in final delivery is incorporated in this
project.

You can add custom patches in `patch` directory.
