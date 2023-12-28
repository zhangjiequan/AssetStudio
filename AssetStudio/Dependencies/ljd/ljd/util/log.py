#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

import sys


def errprint(*args):
	fmt = None

	args = list(args)

	if isinstance(args[0], str):
		fmt = args.pop(0)

	if fmt:
		print(fmt.format(*args), file=sys.stderr)
	else:
		strs = [repr(x) for x in args]
		print(" ".join(strs), file=sys.stderr)
