@ECHO OFF
SET ConEmuAnsi=OFF
SET ConEmuHooks=OFF
SET SDK_ARCH=%1
SHIFT
CALL "C:\Program Files\Microsoft SDKs\Windows\v7.1\bin\SetEnv.Cmd" /release /win7 /%SDK_ARCH%
CALL %1 %2 %3 %4 %5 %6 %7 || EXIT /B
