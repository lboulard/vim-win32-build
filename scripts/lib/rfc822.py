#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import string

KEY_CHARS = string.ascii_letters + '-_+'


class RFC822Exception(Exception):
	pass


class RFC822:

	def __init__(self, f):
		self.f = f
		self.n = 0

	def error(self, msg):
		raise RFC822Exception('line {}: {}'.format(n, msg))

	def headers(self):
		header = ''
		for line in self.f:
			self.n += 1
			line = line.rstrip()
			if line == '':
				if header:
					break
			elif line[0] in ' \t':
				if header:
					header += line
				else:
					self.error('unexpected whitespace at start of line')
			else:
				if header:
					yield header
				header = line
		else:
			self.f.close()
		if header:
			yield header

	def messages(self):
		while not self.f.closed:
			message = list()
			for header in self.headers():
				kv = header.split(':', 1)
				if len(kv) == 1:
					self.error('no header found')
				key, value = kv[0].rstrip(), kv[1].lstrip()
				if not all([c in KEY_CHARS for c in key]):
					self.error('key shall only contain ASCII letters or "-_+"')
				message.append((key, value))
			yield message
