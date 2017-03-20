#!/bin/sh
git submodule --quiet update --init --recursive
git submodule --quiet foreach git pull -q origin master || exit
if [ "$1" != "-f" ]; then
	log=$(git -C vim log -1 --oneline --since="$(date -d '8 hour ago')" 2>/dev/null)
	if test -n "$log"; then
		echo "Last commit too recent: $log"
		exit 0
	fi
fi
git add vim
if test -n "$(git diff-index --name-only HEAD --)" ; then
	tag=$(git -C vim describe --tags 2>/dev/null)
	git commit -q -m "Vim update to $tag" && git tag $tag
fi
