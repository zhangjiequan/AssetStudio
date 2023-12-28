#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

import sys

import ljd.bytecode.debuginfo


VARNAME_END = 0
VARNAME_FOR_IDX = 1
VARNAME_FOR_STOP = 2
VARNAME_FOR_STEP = 3
VARNAME_FOR_GEN = 4
VARNAME_FOR_STATE = 5
VARNAME_FOR_CTL = 6
VARNAME__MAX = 7


INTERNAL_VARNAMES = [
	None,
	"<index>",
	"<limit>",
	"<step>",
	"<generator>",
	"<state>",
	"<control>"
]


def read(parser, line_offset, debuginfo):
	r = True

	r = r and _read_lineinfo(parser, line_offset, debuginfo.addr_to_line_map)
	r = r and _read_upvalue_names(parser, debuginfo.upvalue_variable_names)
	r = r and _read_variable_infos(parser, debuginfo.variable_info)

	return r


def _read_lineinfo(parser, line_offset, lineinfo):
	if parser.lines_count >= 65536:
		lineinfo_size = 4
	elif parser.lines_count >= 256:
		lineinfo_size = 2
	else:
		lineinfo_size = 1

	lineinfo.append(0)

	while len(lineinfo) < parser.instructions_count + 1:
		line_number = parser.stream.read_uint(lineinfo_size)
		lineinfo.append(line_offset + line_number)

	return True


def _read_upvalue_names(parser, names):
	while len(names) < parser.upvalues_count:
		string = parser.stream.read_zstring()
		names.append(string.decode("utf-8"))

	return True


def _read_variable_infos(parser, infos):
	# pc - program counter
	last_addr = 0

	while True:
		info = ljd.bytecode.debuginfo.VariableInfo()

		internal_vartype = parser.stream.read_byte()

		if internal_vartype >= VARNAME__MAX:
			prefix = internal_vartype.to_bytes(1, sys.byteorder)
			suffix = parser.stream.read_zstring()

			info.name = (prefix + suffix).decode("utf-8")
			info.type = info.T_VISIBILE

		elif internal_vartype == VARNAME_END:
			break
		else:
			index = internal_vartype
			info.name = INTERNAL_VARNAMES[index]
			info.type = info.T_INTERNAL

		start_addr = last_addr + parser.stream.read_uleb128()
		end_addr = start_addr + parser.stream.read_uleb128()

		info.start_addr = start_addr
		info.end_addr = end_addr

		last_addr = start_addr

		infos.append(info)

	return True
