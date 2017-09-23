#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""RFC822 like parsing.

There is just enough to read a succession of fields separated by empty lines.
Multilines are supported and line separators are kept. Only space on first
column is removed.
"""

import string

KEY_CHARS = string.ascii_letters + '-_+' + string.digits


class RFC822Exception(Exception):
    """Error while parsing RFC822 like messages."""
    pass


class RFC822:
    """Very simple RFC822 implementation.
Just enough to parse packages definitions.
"""

    def __init__(self, io):
        """Create parser on file like object `io`.
`io` shall support reading lines using iteration, `close()` method
and `closed` attribute.
"""
        self.io = io
        self.n = 0

    def __error(self, msg):
        """Raise `RFC822Exception` from current line."""
        raise RFC822Exception('line {}: {}'.format(self.n, msg))

    def __fields(self):
        """Generator on each field in message.
Stop on empty line or when there is no longer input to read.
"""
        def _concat(field):
            if len(field) == 1:
                field = field[0].rstrip()
            else:
                field = ''.join(field)
            return field
        header = []
        for line in self.io:
            self.n += 1
            if line == '\n':
                if header:
                    break
            elif line[0] in ' \t':
                if header:
                    if len(line) == 3 and line[1] == '.' and line[2] == '\n':
                        header.append('\n')
                    else:
                        header.append(line[1:])
                else:
                    self.__error('unexpected whitespace at start of line')
            else:
                if header:
                    yield _concat(header)
                header = [line]
        else:
            self.io.close()
        if header:
            yield _concat(header)

    def messages(self):
        """Generator that yield each message."""
        while not self.io.closed:
            message = list()
            for field in self.__fields():
                try:
                    key, value = field.split(':', 1)
                except ValueError:
                    self.__error('no header found')
                key, value = key.rstrip(), value.lstrip()
                if not key:
                    self.__error('empty header')
                if not all([c in KEY_CHARS for c in key]):
                    self.__error('key shall only contain ASCII,digits letters or "-_+"')
                message.append((key, value))
            yield message
