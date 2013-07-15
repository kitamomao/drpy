#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import io
import argparse
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import codecs
import re, pprint
import anydbm

def pp(obj):
	pp = pprint.PrettyPrinter(indent=4, width=160)
	str = pp.pformat(obj)
	return re.sub(r"\\u([0-9a-f]{4})", lambda x: unichr(int("0x"+x.group(1), 16)), str)

class DictBasedTextReplacer:
	def __init__(self, dictname):
		if dictname is not None:
			self.dictname = dictname
		self.dicttrie = Trie()

	"""create a trie from a text"""
	def create_dict(self, basename):
		try:
			f = open(basename+".dic", 'r')
			self.read_dicttable(f)
			f.close()
			self.save_trie(basename)
		except IOError as e:
			print "I/O error({0}): {1}".format(e.errno, e.strerror)

	def read_dicttable(self, stream):
		for line in stream:
			line = unicode(line, 'euc-jp').encode('utf-8').strip()
			if re.search("^$|^#", line):
				continue
			k, v = re.compile("\s+").split(line)
			self.dicttrie.add(unicode(k, 'utf-8'), unicode(v, 'utf-8'))

	def _save_trie(self, trie, label, depth):
		self._triefile.write(str(depth)) # suppress newline
		self._triefile.write(" "*depth)
		self._triefile.write(label)
		if trie.value is not None:
			self._triefile.write(" ")
			self._triefile.write(trie.value)
		self._triefile.write('\n')
		self._num += 1
		for char, node in trie.root.items():
			self._save_trie(node, char, depth+1)

	def save_trie(self, basename):
		print "save_trie:", basename
		# create a trie file
		self._triefile = open(basename+".trie", 'w')
		# create an index dbm file
		self._db = anydbm.open(basename+".db", "c")
		self._db.clear()
		for k in sorted(self.dicttrie.root.keys()):
			v = self.dicttrie.root[k]
			self._ptr = self._triefile.tell()
			self._num = 0
			self._save_trie(v, k, 1)
			self._db[str(k)] = u"{0},{1}".format(self._ptr, self._num)
		self._triefile.close()
		self._db.close()

	def replace_text_stream(self, basename, stream):
		self.dicttrie = Trie()
		self._triefile = open(basename+".trie", "r")
		self._db = anydbm.open(basename+".db", "r")
		for line in stream: # sys.stdin or file stream
			print self.replace_text(line.strip())
		self._triefile.close()
		self._db.close()

	def replace_text(self, text):
		result = []
		if type(text) is not unicode:
			text = unicode(text, 'utf-8')
		while text:
			dbe = self._db.get(str(text[0]))
			if dbe is not None:
				if self.dicttrie.value is None:
					self.read_trie(dbe.split(","))
				l, v = self.dicttrie.lookup2(text) # length and value
				if v:
					result.append(v)
					text = text[l:]
					continue
			result.append(text[0])
			text = text[1:] # shift one character and go to the next iteration
		return u"".join(result)

	def read_trie(self, dbe):
		ptr = int(dbe[0])
		length = int(dbe[1])
		self._triefile.seek(ptr, 0)
		s = []
		for line in self._triefile:
			line = line.strip()
			a = re.compile("\s+").split(line)
			depth = k = v = None
			depth = int(a[0])
			k = a[1]
			if len(a) == 3:
				v = a[2]
			if depth > 0:
				if depth == 1:
					s = []
				""" Accumulate characters into the list 's' until v is not None
				Depth value occasionally changes so we use s[0:depth] value instead of the entire list."""
				if len(s) >= depth:
					s[depth-1] = k # some value already stored so overwrite it
				else:
					s.append(k)
				if v is not None:
					self.dicttrie.add(u"".join(s[0:depth]), unicode(v, "utf-8"))
			length -= 1
			if length < 0:
				break;

"""
Trie class in python extracted and modified in part from Wikipedia
(http://en.wikipedia.org/wiki/Trie)
"""
from collections import defaultdict

class Trie:
	def __init__(self):
		self.root = defaultdict(Trie)
		self.value = None
		self._num = 0

	def add(self, s, value):
		"""Add the string 's' to the
		`Trie` and map it to the given value."""
		head, tail = s[0], s[1:]
		cur_node = self.root[head]
		if not tail:
			cur_node.value = value
			return # No further recursion
		cur_node.add(tail, value)

	def lookup(self, s, default=None):
		""" Look up the value corresponding to
		the string `s`. Expand the trie to cache the search."""
		head, tail = s[0], s[1:]
		node = self.root[head]
		if tail:
			return node.lookup(tail)
		return node.value or default

	def lookup2(self, s, default=None):
		""" Look up the value corresponding to
		the string `s`. Return a word length and a value pair"""
		i = 0
		result = [None, None]
		node = self
		for c in s:
			node = node.root[c]
			if node:
				i += 1
				v = node.value
				if v:
					result = [i, v]
			else:
				break
		return result

	def remove(self, s):
		"""Remove the string s from the Trie.
		Returns *True* if the string was a member."""
		head, tail = s[0], s[1:]
		if head not in self.root:
			return False # Not contained
		node = self.root[head]
		if tail:
			return node.remove(tail)
		else:
			del node
			return True

	def prefix(self, s):
		"""Check whether the string `s` is a prefix
		of some member. Don't expand the trie on negatives (cf.lookup)"""
		if not s:
			return self.value
		head, tail = s[0], s[1:]
		if head not in self.root:
			return False # Not contained
		node = self.root[head]
		return node.prefix(tail)

DEFAULT_DICT_NAME = "DICT"

def main():
	try:
		p_parser = argparse.ArgumentParser(add_help=False)
		p_parser.add_argument(
			'-D',
			dest = 'dict_name',
			help = 'specify a dictionary file name',
			default = DEFAULT_DICT_NAME
		)

		group = p_parser.add_mutually_exclusive_group()
		group.add_argument(
			'-c',
			help = 'create a dictionary file',
			default = False,
			action="store_true"
		)
		group.add_argument(
			'-u',
			help = 'update a dictionary file',
			default = False,
			action="store_true"
		)
		c_parser = argparse.ArgumentParser(parents=[p_parser])
		c_parser.add_argument(
			'-s', '--source',
			help = 'specify a dictionary source file',
			default = DEFAULT_DICT_NAME
		)
		u_parser = argparse.ArgumentParser(parents=[p_parser])
		u_parser.add_argument(
			'-i', '--input',
			help = 'specify an input file for the text replacement',
			default = sys.stdin
		)
		i_parser = argparse.ArgumentParser(parents=[p_parser])
		i_parser.add_argument(
			'-i', '--input',
			help = 'specify an input file for the text replacement',
			default = sys.stdin
		)

		if "-c" in sys.argv:
			args = c_parser.parse_args()
			dr = DictBasedTextReplacer(os.path.splitext(args.dict_name)[0])
			dr.create_dict(os.path.splitext(args.source)[0])
		else:
			if "-u" in sys.argv:
				args = u_parser.parse_args()
			else:
				args = i_parser.parse_args()
			dr = DictBasedTextReplacer(os.path.splitext(args.dict_name)[0])
			if args.u:
				basename = os.path.splitext(args.dict_name)[0]
				if os.path.exists(basename+".dic") \
					and (not os.path.exists(basename+".trie") \
					or os.stat(basename+".trie").st_mtime < os.stat(basename+".dic").st_mtime):
					print "Creating dictionary..."	
					dr.create_dict()
			if type(args.input) == str:
				if not os.path.exists(args.input):
					sys.exit('Error %s was not found' % args.input)
				else:
					f = open(args.input, "r")
					dr.replace_text_stream(os.path.splitext(args.dict_name)[0], f)
					f.close()
			else:
				dr.replace_text_stream(os.path.splitext(args.dict_name)[0], sys.stdin)
	except Exception, e:
		print >> sys.stderr, 'error: could not parse arguments: %s' %e
		sys.exit(1)

if __name__ == '__main__':
	main()
