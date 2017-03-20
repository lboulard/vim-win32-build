#!/bin/sh
git submodule --quiet foreach git pull -q origin master || exit
git add vim
if test -n "$(git diff-index --name-only HEAD --)" ; then
	tag=$(git -C vim describe --tags 2>/dev/null)
	git commit -q -m "Vim update to $tag" && git tag $tag
fi
