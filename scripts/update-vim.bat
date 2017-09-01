@SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
PUSHD "%~dp0/.."
git -C vim fetch || EXIT /B 1
git -C vim checkout --detach origin/master || EXIT /B 1
@FOR /F "delims=" %%i in ('git -C vim describe --tags') DO SET TAG=%%i
git add -v vim || EXIT /B 1
git commit -m "Vim update to %TAG%" && git tag %TAG%
POPD
