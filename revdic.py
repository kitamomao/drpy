#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
import argparse

def main():
	parser = argparse.ArgumentParser(usage='%(prog)s [-d] < foo.dic > foo-reverse.dic')
	parser.add_argument(
		'-d',
		help = 'suppress duplicated keys',
		default = False,
		action="store_true"
	)
	args = parser.parse_args()
	check = {}
	for line in sys.stdin:
		if type(line) is not unicode:
			line = unicode(line, 'euc-jp').encode('utf-8').strip()

		if re.search("^$|^#", line):
			continue
		else:
			k, v = line.split()
			if args.d and check.get(k) is not None:
				pass
			else:
				text = "{0}\t{1}".format(v, k)
				print unicode(text, "utf-8").encode('euc-jp')
				check[v] = True

if __name__ == '__main__':
	main()

