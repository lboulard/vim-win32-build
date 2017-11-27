#!/usr/bin/env python3

import sys
import re
from subprocess import Popen, PIPE

PATCHRE = re.compile(r'patch ([\.a-z0-9_-]+)[ ]*:[ ]*(.*)', flags=re.IGNORECASE)

def previoustag():
    # git describe --tag --abbrev=0 HEAD^
    cmd=['git', 'describe', '--tag', '--abbrev=0', 'HEAD^']
    r = b''
    with Popen(cmd, stdout=PIPE, stderr=sys.stderr) as proc:
        r += proc.stdout.read()
    return r.decode().strip()

def gitlog(fromtag):
    # git -C vim log --format=%s %PREVIOUSTAG%..HEAD
    cmd=['git', '-C', 'vim', 'log', '--format=%s', fromtag + '..HEAD']
    r = b''
    with Popen(cmd, stdout=PIPE, stderr=sys.stderr) as proc:
        r += proc.stdout.read()
    return r.decode()

# Tranform a line like:
#   "patch X.Y.ZZZ: ...."
# into
#   "* [X.Y.ZZZ](https://github.com/vim/vim/releases/tag/vX.Y.ZZZ): ...\n"
def transform(line):
    URL='https://github.com/vim/vim/releases/tag/v'
    m = PATCHRE.fullmatch(line)
    if m:
        return "* [{0}]({url}{0}): {1}".format(m.group(1), m.group(2), url=URL)
    else:
        return "* " + line

def main():
    fromtag = previoustag()
    if fromtag:
        log = gitlog(fromtag)
        j = [transform(l) for l in log.splitlines()]
        print('\\n'.join(j))

if __name__ == '__main__':
    main()
