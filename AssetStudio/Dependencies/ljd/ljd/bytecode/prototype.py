#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

import ljd.bytecode.constants as constants
import ljd.bytecode.debuginfo as debug


class Flags():
	def __init(self):
		self.has_sub_prototypes = False
		self.is_variadic = False
		self.has_ffi = False
		self.has_jit = True
		self.has_iloop = False


class Prototype():
	def __init__(self):
		self.flags = Flags()

		self.arguments_count = 0

		self.framesize = 0

		self.first_line_number = 0
		self.lines_count = 0

		self.instructions = []
		self.constants = constants.Constants()
		self.debuginfo = debug.DebugInformation()
