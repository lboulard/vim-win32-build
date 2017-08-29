@ECHO OFF
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

IF "%BASE%" == "" SET BASE=%~dp0

IF NOT "%APPVEYOR_HTTP_PROXY_IP%" == "" (
 SET HTTP_PROXY=http://%APPVEYOR_HTTP_PROXY_IP%:%APPVEYOR_HTTP_PROXY_PORT%
 SET HTTPS_PROXY=%HTTP_PROXY%
 ECHO # Using HTTP proxy %HTTP_PROXY%
)

IF "%TARGET_CPU%" == "" (
ECHO ** ERROR: You need to enter VisualStudio Windows SDK 7.1 environment
EXIT /B 1
)

GOTO :config_%TARGET_CPU%
ECHO ** ERROR: Unsupported CPU %TARGET_CPU%
EXIT /B 1

:config_x86
SET ARCH=x86
SET VIM_CPU=i386
GOTO :config

:config_amd64
:config_x64
SET ARCH=amd64
SET VIM_CPU=AMD64
GOTO :config

:config

SET DOWNLOADS=%BASE%downloads\
SET BUILD=%BASE%dist\%ARCH%\
SET DEPS=%BASE%deps\
SET DEPS_BUILD=%BASE%builds\
SET VIMSRC=%BASE%vim\
SET VIMSRC_BUILD=%BASE%dist\%ARCH%\vim\

SET XPM=%VIMSRC_BUILD%src\xpm\%TARGET_CPU%

SET PERL_VER=526
SET PERL_VERSION=5.26.0
SET PERL_URL=http://www.cpan.org/src/5.0/perl-5.26.0.tar.gz
SET PERL_OUT_DIR=%DEPS_BUILD%%ARCH%
SET PERL_BUILD_DIR=%PERL_OUT_DIR%\perl-%PERL_VERSION%
SET PERL_ARCHIVE=%DOWNLOADS%perl_src.tgz
SET PERL_DIR=%DEPS%Perl_%PERL_VER%_%ARCH%

SET LUA_VER=51
SET LUA_URL_x86=http://downloads.sourceforge.net/luabinaries/lua5_1_4_Win32_dllw4_lib.zip
SET LUA_URL_amd64=http://downloads.sourceforge.net/luabinaries/lua-5.1.4_Win64_dllw4_lib.zip
SET LUA_URL=!LUA_URL_%ARCH%!
SET LUA_ARCHIVE=%DOWNLOADS%lua_%ARCH%.zip
SET LUA_DIR=%DEPS%lua_%LUA_VER%_%ARCH%

SET TCL_VER_LONG=8.6
SET TCL_VER=%TCL_VER_LONG:.=%
SET TCL_VERSION=8.6.7
SET TCL_URL=https://prdownloads.sourceforge.net/tcl/tcl867-src.zip
SET TCL_OUT_DIR=%DEPS_BUILD%%ARCH%
SET TCL_BUILD_DIR=%TCL_OUT_DIR%\tcl%TCL_VERSION%
SET TCL_ARCHIVE=%DOWNLOADS%tcl_src.zip
SET TCL_DIR=%DEPS%tcl_%TCL_VER%_%ARCH%

SET RUBY_VER=23
SET RUBY_VER_LONG=2.3.0
SET RUBY_VERSION=2.3.1
SET RUBY_URL=http://cache.ruby-lang.org/pub/ruby/2.3/ruby-2.3.1.zip
SET RUBY_ARCH_x86=i386-mswin32
SET RUBY_ARCH_amd64=x64-mswin64
SET RUBY_ARCH=!RUBY_ARCH_%ARCH%!
SET RUBY_OUT_DIR=%DEPS_BUILD%%ARCH%
SET RUBY_BUILD_DIR=%RUBY_OUT_DIR%\ruby-%RUBY_VERSION%
SET RUBY_ARCHIVE=%DOWNLOADS%ruby_src.zip
SET RUBY_DIR=%DEPS%Ruby_%RUBY_VER%_%ARCH%

SET PYTHON_VER=27
IF "%APPVEYOR_BUILD_FOLDER%" == "" (
SET PYTHON_DIR_x86=C:\Python27
SET PYTHON_DIR_amd64=C:\Python27
) ELSE (
SET PYTHON_DIR_x86=C:\Python27
SET PYTHON_DIR_amd64=C:\Python27-x64
)
SET PYTHON_DIR=!PYTHON_DIR_%ARCH%!

SET PYTHON3_VER=35
IF "%APPVEYOR_BUILD_FOLDER%" == "" (
SET PYTHON3_DIR_x86=C:\Python35
SET PYTHON3_DIR_amd64=C:\Python35
) ELSE (
SET PYTHON3_DIR_x86=C:\Python35
SET PYTHON3_DIR_amd64=C:\Python35-x64
)
SET PYTHON3_DIR=!PYTHON3_DIR_%ARCH%!

:: Racket
SET RACKET_VER=3m_9zltds
::SET RACKET_URL_x86=https://mirror.racket-lang.org/releases/6.4/installers/racket-minimal-6.4-i386-win32.exe
SET RACKET_URL_x86=https://download.racket-lang.org/releases/6.6/installers/racket-minimal-6.6-i386-win32.tgz
::SET RACKET_URL_amd64=https://mirror.racket-lang.org/releases/6.4/installers/racket-minimal-6.4-x86_64-win32.exe
SET RACKET_URL_amd64=https://download.racket-lang.org/releases/6.6/installers/racket-minimal-6.6-x86_64-win32.tgz
SET RACKET_URL=!RACKET_URL_%ARCH%!
::SET RACKET_DIR_x86=%PROGRAMFILES(X86)%\Racket
::SET RACKET_DIR_amd64=%PROGRAMFILES%\Racket
::SET RACKET_DIR=!RACKET_DIR_%ARCH%!
SET RACKET_DIR=%DEPS%Racket_%RACKET_VER%_%ARCH%
SET RACKET_ARCHIVE=%DOWNLOADS%racket_%ARCH%.tgz
SET MZSCHEME_VER=%RACKET_VER%

SET GETTEXT_URL_x86=https://github.com/mlocati/gettext-iconv-windows/releases/download/v0.19.8.1-v1.14/gettext0.19.8.1-iconv1.14-shared-32.zip
SET GETTEXT_URL_amd64=https://github.com/mlocati/gettext-iconv-windows/releases/download/v0.19.8.1-v1.14/gettext0.19.8.1-iconv1.14-shared-64.zip
SET GETTEXT_URL=!GETTEXT_URL_%ARCH%!
SET GETTEXT_ARCHIVE=%DOWNLOADS%gettext_%ARCH%.zip
SET GETTEXT_DIR=%DEPS%GetText_%ARCH%

SET WINPTY_URL=https://github.com/rprichard/winpty/releases/download/0.4.3/winpty-0.4.3-msvc2015.zip
SET WINPTY_ARCH_x86=ia32_xp
SET WINPTY_ARCH_amd64=x64_xp
SET WINPTY_ARCH=!WINPTY_ARCH_%ARCH%!
SET WINPTY_ARCHIVE=%DOWNLOADS%winpty_bin.zip
SET WINPTY_DIR=%DEPS%winpty

SET UPX_URL=http://upx.sourceforge.net/download/upx391w.zip
SET UPX_ARCHIVE=%DOWNLOADS%upx_bin.zip
SET UPX_DIR=%DEPS%upx
IF ERRORLEVEL 1 GOTO :EOF

:NextCommand
SET OP=%~1
IF /I "%OP:~0,8%" == "Prepare-" GOTO :CommandPrepare
IF "%OP%" == "" SET OP=build
SHIFT
CALL :Command%OP% || EXIT /B
IF NOT "%~1" == "" GOTO :NextCommand
EXIT /B 0

:: -----------------------------------------------------------------------
:CommandDownload
:CommandFetch
IF NOT EXIST %BASE%downloads MKDIR %BASE%downloads

CALL :GetRemoteFile %LUA_URL% %LUA_ARCHIVE% || EXIT /B
CALL :GetRemoteFile %PERL_URL% %PERL_ARCHIVE% || EXIT /B
CALL :GetRemoteFile %TCL_URL% %TCL_ARCHIVE% || EXIT /B
CALL :GetRemoteFile %RUBY_URL% %RUBY_ARCHIVE% || EXIT /B
CALL :GetRemoteFile %RACKET_URL% %RACKET_ARCHIVE% || EXIT /B
CALL :GetRemoteFile %GETTEXT_URL% %GETTEXT_ARCHIVE% || EXIT /B
CALL :GetRemoteFile %WINPTY_URL% %WINPTY_ARCHIVE% || EXIT /B
CALL :GetRemoteFile %UPX_URL% %UPX_ARCHIVE% || EXIT /B

GOTO :EOF

:: -----------------------------------------------------------------------
:CommandPrepare

CALL :FindBinary 7z.exe "C:\Program Files\7-Zip" || EXIT /B

IF NOT EXIST %DEPS%\. MKDIR %DEPS%

SET ARG=%~1
IF "!ARG!" == "" (
 SET PACKAGE=All
) ELSE (
 IF /I "!ARG:~0,8!" == "Prepare-" (SET PACKAGE=!ARG:~8!)
)
GOTO :Install!PACKAGE!
ECHO ** ERROR: Unnown package !PACKAGE!
ECHO Package is one of All/GetText/UPX/Lua/Perl/Tcl/Ruby/Racket
EXIT /B 1

:InstallAll
FOR %%z IN (GetText Winpty UPX Lua Perl Tcl Ruby Racket) DO ( CALL :Install%%z || EXIT /B )
GOTO :EOF

:InstallLua
ECHO # Lua %ARCH% %LUA_VER%
CALL :Extract %LUA_ARCHIVE% %LUA_DIR%
GOTO :EOF

:InstallPerl
ECHO # Perl %ARCH% %PERL_VERSION%
IF EXIST "%PERL_DIR%" RD /Q /S "%PERL_DIR%"
IF EXIST "%PERL_BUILD_DIR%" RD /Q /S "%PERL_BUILD_DIR%"
IF NOT EXIST "%PERL_OUT_DIR%\." MKDIR "%PERL_OUT_DIR%" || EXIT /B 1
CALL :Extract %PERL_ARCHIVE% %PERL_OUT_DIR%
PUSHD %PERL_BUILD_DIR%\win32 || EXIT /B 1
ECHO ON
SET ARGS=INST_TOP=%PERL_DIR% CCTYPE=MSVC100FREE
IF "%ARCH%" == "x86" (
 SET ARGS=!ARGS! WIN64=undef
)
nmake -nologo -f Makefile !ARGS! || EXIT /B
nmake -nologo -f Makefile install !ARGS! || EXIT /B
@ECHO OFF
POPD
RD /Q /S %PERL_BUILD_DIR% || EXIT /B
GOTO :EOF

:InstallTcl
ECHO # TCL %ARCH% %TCL_VER_LONG%
IF EXIST "%TCL_DIR%" RD /Q /S %TCL_DIR%
CALL :Extract %TCL_ARCHIVE% %TCL_OUT_DIR%
PUSHD %TCL_BUILD_DIR%\win || EXIT /B 1
ECHO ON
nmake -nologo -f makefile.vc release
nmake -nologo -f makefile.vc install INSTALLDIR=%TCL_DIR%
@ECHO OFF
POPD
RD /Q /S %TCL_BUILD_DIR%
GOTO :EOF

:InstallRuby
ECHO # Ruby %ARCH% %RUBY_VER_LONG%
CALL :Extract %RUBY_ARCHIVE% %RUBY_OUT_DIR%

PUSHD %RUBY_BUILD_DIR%
ECHO ON
CALL win32\configure.bat --target=%RUBY_ARCH% ^
  --disable-install-doc ^
  --without-ext "socket,fiddle,openssl,curses,pty,readline,dbm,gdbm,fcntl,tk,syslog" ^
  --disable-rubygems ^
  --disable-debug-env ^
  --prefix=$(RUBY_DIR) || EXIT /B
SET CL=/MP
nmake || EXIT /B
nmake install || EXIT /B
XCOPY /I /Y /S .ext\include %RUBY_DIR%\include\ruby-%RUBY_VER_LONG% || EXIT /B
@ECHO OFF
POPD
RD /Q /S %RUBY_BUILD_DIR% || EXIT /B
GOTO :EOF

:InstallRacket
ECHO # Racket %ARCH% %RACKET_VER%
CALL :Extract %RACKET_ARCHIVE% %DEPS%tmp\Racket_%ARCH%
IF EXIST "%RACKET_DIR%" RD /Q /S %RACKET_DIR%
MOVE %DEPS%tmp\Racket_%ARCH%\racket %RACKET_DIR% || EXIT /B 1
RD %DEPS%tmp\Racket_%ARCH%
GOTO :EOF

:InstallGetText
ECHO # GetText %ARCH%
CALL :Extract %GETTEXT_ARCHIVE% %GETTEXT_DIR%
GOTO :EOF

:InstallWinpty
IF EXIST %WINPTY_DIR% GOTO :EOF
ECHO # winpty
CALL :Extract %WINPTY_ARCHIVE% %WINPTY_DIR%
GOTO :EOF

:InstallUPX
IF EXIST "%UPX_DIR%\upx.exe" GOTO :EOF
ECHO # UPX
REM Custom command to keep only upx.exe from archive
7z e %UPX_ARCHIVE% *\upx.exe -o%UPX_DIR% -y > NUL || EXIT /B 1
GOTO :EOF

:: -----------------------------------------------------------------------
:CommandBuild

IF NOT EXIST "%DEPS%" (
 ECHO Do %~dp0 prepare to install and prepare dependencies
 EXIT /B 1
)

IF NOT EXIST %BUILD%. MD %BUILD%

SET BUILDOPTIONS=CPU=%VIM_CPU% CVARS=/MP CPUNR=pentium4 WINVER=0x500 ^
 DEBUG=no FEATURES=HUGE MBYTE=yes CSCOPE=yes ICONV=yes GETTEXT=yes ^
 DYNAMIC_PERL=yes PERL="%PERL_DIR%" PERL_VER=%PERL_VER% ^
 DYNAMIC_LUA=yes LUA="%LUA_DIR%" LUA_VER=%LUA_VER% ^
 DYNAMIC_TCL=yes TCL="%TCL_DIR%" TCL_VER=%TCL_VER% TCL_VER_LONG=%TCL_VER_LONG% ^
 DYNAMIC_RUBY=yes RUBY="%RUBY_DIR%" RUBY_VER=%RUBY_VER% RUBY_VER_LONG=%RUBY_VER_LONG% ^
 DYNAMIC_PYTHON=yes PYTHON="%PYTHON_DIR%" PYTHON_VER=%PYTHON_VER% ^
 DYNAMIC_PYTHON3=yes PYTHON3="%PYTHON3_DIR%" PYTHON3_VER=%PYTHON3_VER% ^
 DYNAMIC_MZSCHEME=yes "MZSCHEME=%RACKET_DIR%" ^
 XPM="%XPM%"

IF EXIST "%VIMSRC_BUILD%" RD /Q /S %VIMSRC_BUILD%
git clone --shared %VIMSRC% %VIMSRC_BUILD% || EXIT /B 1

:: Incorporate patches
IF EXIST patch FOR %%i IN (%BASE%\patch\*.patch) DO git -C %VIMSRC_BUILD% apply -v %%i
IF ERRORLEVEL 1 GOTO :EOF

PUSHD %VIMSRC_BUILD%src

PATH %PERL_DIR%\bin;%RUBY_DIR%\bin;%PATH%

ECHO ON

:: Build GVim
nmake -f Make_mvc.mak ^
 IME=yes GIME=yes GUI=yes OLE=yes DIRECTX=yes %BUILDOPTIONS% gvim.exe || EXIT /B 1

:: Build Vim
nmake -f Make_mvc.mak ^
 IME=no  GIME=no  GUI=no  OLE=no  DIRECTX=no  %BUILDOPTIONS% || EXIT /B 1
@ECHO OFF

PUSHD po
nmake -f Make_mvc.mak ^
 GETTEXT_PATH=%GETTEXT_DIR%\bin VIMRUNTIME=%VIMSRC_BUILD%\runtime ^
 install-all > NUL || EXIT /B 1
POPD

:: Build both 64- and 32-bit versions of gvimext.dll for the installer
START /B /WAIT CMD /C "SetEnv /x64 && CD GvimExt && nmake clean all" || EXIT /B 1
MOVE GvimExt\gvimext.dll GvimExt\gvimext64.dll
START /B /WAIT CMD /C "SetEnv /x86 && CD GvimExt && nmake clean all"  || EXIT /B 1

@ECHO OFF
POPD
GOTO :EOF

:: -----------------------------------------------------------------------
:CommandPackage

CD %VIMSRC_BUILD%src || EXIT /B 1

CALL :FindBinary 7z.exe "C:\Program Files\7-Zip" || EXIT /B

IF "%APPVEYOR_REPO_TAG%" == "true" (
SET VIMVER=%APPVEYOR_REPO_TAG_NAME%
) ELSE (
FOR /F "delims=" %%i in ('git -C %VIMSRC% describe --tags --abbrev^=0') DO SET VIMVER=%%i
)
PATH %UPX_DIR%;%PATH%

C:\msys64\usr\bin\bash -lc ^
 "cd $(cygpath '%VIMSRC_BUILD%')/runtime/doc && touch ../../src/auto/config.mk && make uganda.nsis.txt"

ECHO ON
COPY /Y ..\README.txt ..\runtime\
COPY /Y ..\vimtutor.bat ..\runtime\
COPY /Y *.exe ..\runtime\
COPY /Y xxd\*.exe ..\runtime\
COPY /Y tee\*.exe ..\runtime\
MKDIR ..\runtime\GvimExt
COPY /Y GvimExt\gvimext*.dll ..\runtime\GvimExt\
COPY /Y GvimExt\README.txt ..\runtime\GvimExt\
COPY /Y GvimExt\*.inf ..\runtime\GvimExt\
COPY /Y GvimExt\*.reg ..\runtime\GvimExt\
COPY /Y %WINPTY_DIR%\%WINPTY_ARCH_x86%\bin\winpty.dll ..\runtime\winpty32.dll
COPY /Y %WINPTY_DIR%\%WINPTY_ARCH_amd64%\bin\winpty.dll ..\runtime\winpty64.dll
COPY /Y %WINPTY_DIR%\%WINPTY_ARCH%\bin\winpty-agent.exe ..\runtime\
COPY /Y %BASE%\extras\diff.exe ..\runtime\
COPY /Y %GETTEXT_DIR%\bin\libiconv*.dll ..\runtime\
COPY /Y %GETTEXT_DIR%\bin\libintl-8.dll ..\runtime\
COPY /Y %LUA_DIR%\lua5.1.dll ..\runtime\lua51.dll

:: Library that may be required on platform (pthread for x64 or gcc_s_sjlj on x86)
@FOR %%f IN (libwinpthread-1.dll libgcc_s_sjlj-1.dll) DO @(
  @IF EXIST "%GETTEXT_DIR%\bin\%%f" COPY /Y "%GETTEXT_DIR%\bin\%%f" ..\runtime\
)

SET dir=%BUILD%\vim-%VIMVER:v=%-%ARCH%
IF EXIST "%dir%" RD /Q /S "%dir%"
MKDIR %dir%
XCOPY ..\runtime %dir% /Y /E /V /I /H /R /Q
IF EXIST "%BASE%\gvim-%VIMVER:v=%-%ARCH%.zip" DEL /F "%BASE%\gvim-%VIMVER:v=%-%ARCH%.zip"
7z a "%BASE%\gvim-%VIMVER:v=%-%ARCH%.zip" %dir%

COPY /Y %BASE%\extras\diff.exe %VIMSRC_BUILD%\..
COPY /Y %WINPTY_DIR%\%WINPTY_ARCH_x86%\bin\winpty.dll %VIMSRC_BUILD%..\winpty32.dll
COPY /Y %WINPTY_DIR%\%WINPTY_ARCH_amd64%\bin\winpty.dll %VIMSRC_BUILD%..\winpty64.dll
COPY /Y %WINPTY_DIR%\%WINPTY_ARCH%\bin\winpty-agent.exe %VIMSRC_BUILD%..
COPY /Y gvim.exe gvim_ole.exe
COPY /Y vim.exe vimw32.exe
COPY /Y xxd\xxd.exe xxdw32.exe
COPY /Y tee\tee.exe teew32.exe
COPY /Y install.exe installw32.exe
COPY /Y uninstal.exe uninstalw32.exe
PUSHD ..\nsis
"C:\Program Files (x86)\NSIS\makensis" /DVIMRT=..\runtime gvim.nsi "/XOutFile %BASE%\gvim-%VIMVER:v=%-%ARCH%.exe"
POPD
@ECHO OFF
GOTO :EOF

:: -----------------------------------------------------------------------
:FindBinary
:: call :FindBinary <name> <defautlInstallPath>
IF "%~$PATH:1" == "" PATH %~2;%PATH%
GOTO :EOF

:: -----------------------------------------------------------------------
:GetRemoteFile
:: call :GetRemoteFile <URL> <localfile>
IF NOT EXIST %2 (
 ECHO # Downloading %2
 curl -fsS --retry 3 --retry-delay 5 --connect-timeout 30 -L "%1" -o %2 || EXIT /B 1
)
GOTO :EOF

:: -----------------------------------------------------------------------
:Extract
SET EXT=%~x1
CALL :Extract%EXT% %*
IF ERRORLEVEL 1 EXIT /B
GOTO :EOF

:Extract.Zip
7z x -y %1 %3 -o%2 > NUL || EXIT /B 1
GOTO :EOF

:Extract.Tgz
7z e -so %1 | 7z x -y -bd -si -ttar -o%2 > NUL || EXIT /B 1
GOTO :EOF
