#!/usr/bin/env python3

import sys
import re
from subprocess import Popen, PIPE

PATCHRE = re.compile(r'patch ([\.a-z0-9_-]+)[ ]*:[ ]*(.*)', flags=re.IGNORECASE)

def root():
    cmd = ["git", "hash-object", "-t", "tree", "/dev/null"]
    r = b''
    with Popen(cmd, stdout=PIPE, stderr=sys.stderr) as proc:
        r += proc.stdout.read()
    return r.decode().strip()

def gettag(ref="HEAD"):
    cmd = ["git", "describe", "--exact-match", "--tags", ref]
    r = b''
    with Popen(cmd, stdout=PIPE, stderr=sys.stderr) as proc:
        r += proc.stdout.read()
    return r.decode().strip()

def previoustag(ref="HEAD^"):
    # git describe --tag --abbrev=0 HEAD^
    cmd=['git', 'describe', '--tag', '--abbrev=0', ref]
    r = b''
    with Popen(cmd, stdout=PIPE, stderr=sys.stderr) as proc:
        r += proc.stdout.read()
    return r.decode().strip()

def gitlog(fromtag, head='HEAD'):
    # git -C vim log --format=%s %PREVIOUSTAG%..HEAD
    cmd=['git', '-C', 'vim', 'log', '--format=%s', fromtag + '..' + head]
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

def findcurrenttag():
    ref, n ="HEAD", 0
    tag = gettag()
    while not tag and n < 50:
        n = n + 1
        tag = gettag(ref + "~" + str(n))
    return tag

def main():
    if len(sys.argv) > 1:
        head = sys.argv[1]
        tag = gettag(head)
    else:
        tag = findcurrenttag() or 'HEAD'
    if tag:
        fromtag = previoustag(tag + "^") or root()
        log = gitlog(fromtag, tag)
        j = [transform(l) for l in log.splitlines()]
        print('\\n'.join(j))
    else:
        print('\\n')

if __name__ == '__main__':
    main()
