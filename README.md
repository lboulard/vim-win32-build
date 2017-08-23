[![Build status](https://ci.appveyor.com/api/projects/status/2arjuao3028n44p1?svg=true)](https://ci.appveyor.com/project/lboulard/vim-win32-build)

# GVim/Vim Win32 builder

Generate installers and archives for x86 and AMD64 CPU architecture using
Windows SDK 7.1 build environment.

Inspired by <https://github.com/vim/vim-win32-installer> project and home grew
scripts.

Recent versions now use `ninja.exe` to parallel builds of packages dependencies
and _Vim_. Build creates both _x86_ and _amd64_ of _Vim_.

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
administrator.

Make sure that Python 3.5 `python.exe` is accessible from `PATH` variable.

First install dependencies for python scripts:

```dosbatch
 python.exe -m pip install --user -r requirements.txt
```

### Download archives and installers

```dosbatch
download.bat
7z x downloads\ninja-win.zip ninja.exe
```

It can take a long depending of you Internet connection speed.

### Prepare GVim/Vim dependencies

List and version of GVim/Vim dependencies used for build and packages:

- [UPX](http://upx.sourceforge.net/) 3.91
- [GetText](https://github.com/mlocati/gettext-iconv-windows) 0.19.8.1 and iconv 1.14
- [LuaBinaries](http://luabinaries.sourceforge.net/download.html) 5.1.4
- [Perl](http://www.perl.org) 5.26.0
- [Tcl](http://www.tcl.tk) 8.6.7
- [Racket](https://download.racket-lang.org/) 6.6
- [Ruby](https://www.ruby-lang.org/en/downloads/) 2.3.1
- [ninja](https://ninja-build.org) 1.7.2

To prepare all required software for building GVim/Vim at next step, run:

```dosbatch
configure.bat
ninja packages
```

It is possible to only prepare a specific package:
 - _UPX_: `ninja upx` to unzip UPX for NSI package creation phase.
 - _GetText_: `ninja winpty` to extract GetText archive.
 - _Lua_: `ninja lua_x86 lua_x64` to extract Lua archive.
 - _Perl_: `ninja perl_x86 perl_x64l` to extract and compile Perl.
 - _Tcl_: `ninja tcl_x86 tcl_x64` to extract and compile Tcl.
 - _Racket_: `ninja racket_x86 racket_x64` to extract Racket archive
 - _Ruby_: `ninja ruby_x86 ruby_x64` to extract and compile Ruby.

Not that Ruby needs to be compiled using VisualStudio before being able to
compile GVim/Vim. There is not ready to use archive for Ruby + VisualStudio.
Ruby preparation is the longest of all tasks.

### Build GVim/Vim and package installations

```dosbatch
ninja gvim
```

You shall now have files `gvim-8.0.xxx-ARCH.exe` and `gvim-8.0.xxx-ARCH.zip` in
root folder.

## Patches

By default a patch to embed Lua DLL in final delivery is incorporated in this
project.

You can add custom patches in `patch` directory.
