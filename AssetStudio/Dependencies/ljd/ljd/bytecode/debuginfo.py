#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#


class VariableInfo():
	T_VISIBILE = 0
	T_INTERNAL = 1

	def __init__(self):
		self.start_addr = 0
		self.end_addr = 0
		self.type = -1
		self.name = ""


class DebugInformation():
	def __init__(self):
		self.addr_to_line_map = []
		self.upvalue_variable_names = []
		self.variable_info = []

	def lookup_line_number(self, addr):
		try:
			return self.addr_to_line_map[addr]
		except IndexError:
			return 0

	def lookup_local_name(self, addr, slot):
		for info in self.variable_info:
			if info.start_addr > addr:
				break
			if info.end_addr <= addr:
				continue
			elif slot == 0:
				return info
			else:
				slot -= 1

		return None

	def lookup_upvalue_name(self, slot):
		try:
			return self.upvalue_variable_names[slot]
		except IndexError:
			return None
