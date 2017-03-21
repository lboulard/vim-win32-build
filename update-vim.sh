#!/bin/sh
git submodule --quiet update --init --recursive || exit
git submodule --quiet foreach git pull -q --tags origin master || exit
if [ "$1" != "-f" ]; then
	log=$(git -C vim log -1 --oneline --since="$(date -d '8 hour ago')" 2>/dev/null) || exit
	if test -n "$log"; then
		echo "Last commit too recent: $(git -C vim log -1 --format="%ci, %cr"), $log"
		exit 1
	fi
fi
git add vim || exit
if test -n "$(git diff-index --name-only HEAD --)" ; then
	tag=$(git -C vim describe --tags 2>/dev/null)
	git commit -q -m "Vim update to $tag" && git tag $tag
else
	exit 1
fi
