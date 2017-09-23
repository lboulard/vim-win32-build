from io import StringIO
from nose.tools import raises, eq_
from lib.rfc822 import RFC822, RFC822Exception

def test_single_line():
	"""Check parsing field of one line"""
	t = """Key: value
"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	eq_(k, [[("Key", "value")]])

def test_missing_final_carriage():
	"""Check parsing field of one line without last carriage"""
	t = """Key: value"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	eq_(k, [[("Key", "value")]])

def test_two_lines():
	"""Check parsing message of two fields/lines"""
	t = """Key1: value1
Key2: value2
"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	eq_(k, [[("Key1", "value1"), ("Key2", "value2")]])

def test_messages_separation():
	"""Verify one empty line separates messages"""
	t = """Key1: value1

Key2: value2
"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	eq_(k, [[("Key1", "value1")], [("Key2", "value2")]])

def test_messages_separation_with_multiple_lines():
	"""Verify multiple empty lines separates messages"""
	t = """Key1: value1


Key2: value2
"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	eq_(k, [[("Key1", "value1")], [("Key2", "value2")]])

def test_space_continuation():
	"""Verify field value split on multiple lines."""
	t = """Key: value1
 value2
"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	eq_(k, [[("Key", "value1\nvalue2\n")]])

def test_space_continuation_empty_line():
	"""Verify that single dot becomes an empty line on parsing"""
	t = """Key: value1
 .
 value2
"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	eq_(k, [[("Key", "value1\n\nvalue2\n")]])

@raises(RFC822Exception)
def test_bad_space_first_line():
	"""Verify space on first line raise an error"""
	t = """ Key: value
	"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	print(k)

@raises(RFC822Exception)
def test_bad_tab_first_line():
	"""Verify space on first line raise an error"""
	t = """\tKey: value
	"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	print(k)

@raises(RFC822Exception)
def test_bad_key():
	"""Only accept ASCII letters, digits and '_', '+' and '_' chars"""
	t = """Ke y: value
"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	print(k)

@raises(RFC822Exception)
def test_noheader():
	"""Check failure on missing ':' on same line"""
	t = """
Package: mypackage
Version: 1.0
BadHeader
"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	print(k)

@raises(RFC822Exception)
def test_empty_header_name():
	"""Check failure of missing char before ':'"""
	t = """
Package: mypackage
Version: 1.0
: value
"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	print(k)

@raises(RFC822Exception)
def test_lost_double_colon():
	"""Check failure for standalone ':'"""
	t = """
Package: mypackage
Version: 1.0
:
"""
	c = StringIO(t)
	k = list(RFC822(c).messages())
	print(k)
