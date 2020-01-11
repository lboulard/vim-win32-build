#!/usr/bin/env python3

import sys
import re
from subprocess import Popen, PIPE, DEVNULL

PATCHRE = re.compile(r"patch ([\.a-z0-9_-]+)[ ]*:[ ]*(.*)", flags=re.IGNORECASE)


def root():
    cmd = ["git", "hash-object", "-t", "tree", "/dev/null"]
    r = b""
    with Popen(cmd, stdout=PIPE, stderr=sys.stderr) as proc:
        r += proc.stdout.read()
    return r.decode().strip()


def gettag(ref="HEAD"):
    cmd = ["git", "describe", "--exact-match", "--tags", ref]
    r = b""
    with Popen(cmd, stdout=PIPE, stderr=DEVNULL) as proc:
        r += proc.stdout.read()
    return r.decode().strip()


def getvimtag(ref):
    # git -C vim describe --tags --exact-match ref
    cmd = ["git", "-C", "vim", "describe", "--exact-match", "--tags", ref]
    r = b""
    with Popen(cmd, stdout=PIPE, stderr=DEVNULL) as proc:
        r += proc.stdout.read()
    return r.decode().strip()


def previoustag(ref="HEAD^"):
    # git describe --tag --abbrev=0 HEAD^
    cmd = ["git", "describe", "--tags", "--abbrev=0", ref]
    r = b""
    with Popen(cmd, stdout=PIPE, stderr=sys.stderr) as proc:
        r += proc.stdout.read()
    return r.decode().strip()


def previouschange(ref=""):
    prefix = ref.split("-", 1)[0]
    while True:
        tag = previoustag((ref or "HEAD") + "^")
        if not ref:
            return tag
        s = tag.split("-", 1)[0]
        if s != prefix:
            return tag
        ref = tag


def getvimcommit(ref="HEAD"):
    # git ls-tree -d HEAD vim
    # Output format: <mode> SP <type> SP <object> TAB <file>
    cmd = ["git", "ls-tree", "-d", ref, "vim"]
    r = b""
    with Popen(cmd, stdout=PIPE, stderr=sys.stderr) as proc:
        r += proc.stdout.read()
    line = r.decode().strip()
    s, _ = line.split("\t", 1)
    _, _, commit = s.split()
    return commit


def vimrevlist(rev1, rev2):
    # git -C rev-list rev1..rev2
    cmd = ["git", "-C", "vim", "rev-list", rev1 + ".." + rev2]
    r = b""
    with Popen(cmd, stdout=PIPE, stderr=sys.stderr) as proc:
        r += proc.stdout.read()
    return r.decode().splitlines()


def getvimlog(ref="HEAD"):
    # git -C vim show -s --format=%s ref
    cmd = ["git", "-C", "vim", "show", "-s", "--format=%s", ref]
    r = b""
    with Popen(cmd, stdout=PIPE, stderr=sys.stderr) as proc:
        r += proc.stdout.read()
    return r.decode().strip()


# Create a list of tuple (commit, tag, description)
def gitlog(rev1, rev2="HEAD"):
    rev1, rev2 = getvimcommit(rev1), getvimcommit(rev2)
    # git -C vim log --format=%s rev1..rev2
    cmd = ["git", "-C", "vim", "log", "--format=%s", rev1 + ".." + rev2]
    r = b""
    with Popen(cmd, stdout=PIPE, stderr=sys.stderr) as proc:
        r += proc.stdout.read()
    s = r.decode()
    line = s.splitlines()
    r = []
    for commit in vimrevlist(rev1, rev2):
        tag = getvimtag(commit)
        msg = getvimlog(commit)
        r.append((commit, tag, msg))
    return r


TAGURL = "https://github.com/vim/vim/releases/tag/"
COMMITURL = "https://github.com/vim/vim/commit/"

# Tranform a line like:
#   "patch X.Y.ZZZ: ...."
# into
#   "* [X.Y.ZZZ](https://github.com/vim/vim/releases/tag/vX.Y.ZZZ): ...\n"
def transform(msg, commit="", tag=""):
    m = PATCHRE.fullmatch(msg)
    if m:
        return "* [{0}]({url}{tag}): {msg}".format(
            tag.lstrip("v"), tag=tag, msg=m.group(2), url=TAGURL
        )
    else:
        return "* [{0}]({url}{commit}): {msg}".format(
            commit[:7], commit=commit, msg=msg, url=COMMITURL
        )


def findcurrenttag():
    ref, n = "HEAD", 0
    tag = gettag()
    while not tag and n < 50:
        n = n + 1
        tag = gettag(ref + "~" + str(n))
    return tag


def main():
    fromtag = None
    if len(sys.argv) > 1:
        head = sys.argv[1]
        tag = gettag(head) or head
        if len(sys.argv) > 2:
            fromtag = sys.argv[2]
            fromtag = gettag(fromtag) or fromtag
    else:
        tag = findcurrenttag() or "HEAD"
    if tag:
        if not fromtag:
            fromtag = previouschange(tag)
        if not fromtag:
            fromtag = root()
            descr = ""
        else:
            vimtag = getvimtag(fromtag)
            if vimtag:
                descr = "Changes since [{0}]({url}{tag}):\\n\\n".format(
                    vimtag.lstrip("v"), tag=vimtag, url=TAGURL
                )
            else:
                vimcommit = getvimcommit(fromtag)
                descr = "Changes since [{0}]({url}{commit}):\\n\\n".format(
                    vimcommit[:7], commit=vimcommit, url=COMMITURL
                )
        logs = gitlog(fromtag, tag)
        j = [transform(msg, commit, tag) for commit, tag, msg in logs]
        if j:
            print(descr + "\\n".join(j))
    else:
        print("\\n")


if __name__ == "__main__":
    main()
