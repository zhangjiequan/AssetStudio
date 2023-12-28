#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

import ljd.bytecode.instructions as ins
from ljd.bytecode.constants import T_NIL, T_FALSE, T_TRUE

import ljd.pseudoasm.prototype

_FORMAT = "{addr:3}\t[{line:3}]\t{name:<5}\t{a:3}\t{b}\t{c}\t; {description}"


_DESCRIPTION_HANDLERS = [None] * 255


class _State():
	def __init__(self, writer, prototype, instructions):
		for key, value in writer.__dict__.items():
			setattr(self, key, value)

		self.prototype = prototype
		self.instructions = instructions


def write(writer, prototype):
	global _MAP

	# skip the first function header
	addr = 1

	instructions = prototype.instructions

	writer = _State(writer, prototype, instructions)

	while addr < len(instructions):
		instruction = instructions[addr]
		line = prototype.debuginfo.lookup_line_number(addr)

		if instruction.opcode == ins.FNEW.opcode:
			_write_function(writer, addr, line, instruction)
		else:
			_write_instruction(writer, addr, line, instruction)

		addr += 1


def _write_instruction(writer, addr, line, instruction):
	description = _translate_description(writer, addr, line, instruction)

	writer.stream.write_multiline(_FORMAT,
		addr=addr,
		line=line,
		name=instruction.name,
		a=instruction.A if instruction.A_type is not None else "",
		b=instruction.B	if instruction.B_type is not None else "",
		c=instruction.CD if instruction.CD_type is not None else "",
		description=description
	)


def _write_function(writer, addr, line, instruction):
	prototype = writer.prototype.constants.complex_constants[instruction.CD]

	description = ljd.pseudoasm.prototype.format_header(writer, prototype)

	writer.stream.open_block(_FORMAT,
		addr=addr,
		line=line,
		name="FNEW",
		a=instruction.A,
		b="",
		c=instruction.CD,
		description=description
	)

	writer.stream.write_line()

	ljd.pseudoasm.prototype.write_body(writer, prototype)

	writer.stream.close_block()


def _translate_description(writer, addr, line, instruction):
	global _DESCRIPTION_HANDLERS

	handler = _DESCRIPTION_HANDLERS[instruction.opcode]
	description = instruction.description

	return handler(writer, description, addr, line, instruction)


def _translate(writer, addr, value, attr_type):
	prototype = writer.prototype

	if attr_type == ins.T_DST or attr_type == ins.T_BS:
		return "slot" + str(value)
	if attr_type == ins.T_VAR:
		name = _lookup_variable_name(writer, addr, value)

		if name is not None:
			return name
		else:
			return "slot" + str(value)
	elif attr_type == ins.T_UV:
		name = prototype.debuginfo.lookup_upvalue_name(value)
		return "uv" + str(value) + '"' + name + '"'
	elif attr_type == ins.T_PRI:
		if value is None or value == T_NIL:
			return "nil"
		elif value is True or value == T_TRUE:
			return "true"
		else:
			assert value is False or value == T_FALSE
			return "false"
	elif attr_type == ins.T_NUM:
		return str(prototype.constants.numeric_constants[value])
	elif attr_type == ins.T_STR:
		binary = prototype.constants.complex_constants[value]
		return '"' + binary + '"'
	elif attr_type == ins.T_TAB:
		return "table#k" + str(value)
	elif attr_type == ins.T_CDT:
		return str(prototype.constants.complex_constants[value])
	elif attr_type == ins.T_JMP:
		return str(1 + addr + value)
	elif attr_type == ins.T_LIT or attr_type == ins.T_SLIT:
		return str(value)
	elif attr_type == ins.T_BS or attr_type == ins.T_RBS:
		return "r" + str(value)
	else:
		return " "  # "r" + str(value)


def _lookup_variable_name(writer, addr, slot):
	while True:
		result = _lookup_variable_name_step(writer, addr, slot)

		if isinstance(result, tuple):
			addr = result[0]
			slot = result[1]
			continue

		return result


def _lookup_variable_name_step(writer, addr, slot):
	info = writer.prototype.debuginfo.lookup_local_name(addr, slot)

	if info is not None:
		name = info.name

		if name[0] == '<':
			name = "slot" + str(slot) + name

		return name

	instructions = writer.instructions

	knil_opcode = ins.KNIL.opcode
	constants = writer.prototype.constants.complex_constants

	while addr > 1:
		addr -= 1
		instruction = instructions[addr]

		if instruction.A_type == ins.T_BS:
			if slot >= instruction.A 				\
					and (instruction.opcode == knil_opcode	\
						or slot <= instruction.CD):
				return None

			continue

		if instruction.A_type != ins.T_DST or instruction.A != slot:
			continue

		if instruction.opcode == ins.MOV.opcode:
			# Retry with new addr and slot
			return addr, instruction.CD

		if instruction.opcode == ins.GGET.opcode:
			binary = constants[instruction.CD]
			return binary

		# field or method
		if instruction.opcode == ins.TGETS.opcode:
			table_slot = instruction.B
			table = _lookup_variable_name_step(writer, addr, table_slot)

			if table is None:
				table = "<unknown table>"

			binary = constants[instruction.CD]
			return table + "." + binary

		if instruction.opcode == ins.UGET.opcode:
			uv = instruction.CD
			name = writer.prototype.debuginfo.lookup_upvalue_name(uv)

			return "uv" + str(uv) + '"' + name + '"'

		return None

	return None


def _translate_standard(writer, addr, line, instruction):
	A = None
	B = None
	CD = None

	if instruction.A_type is not None:
		A = _translate(writer, addr, instruction.A, instruction.A_type)

	if instruction.B_type is not None:
		B = _translate(writer, addr, instruction.B, instruction.B_type)

	if instruction.CD_type is not None:
		CD = _translate(writer, addr, instruction.CD, instruction.CD_type)

	return A, B, CD


def _translate_normal(writer, description, addr, line, instruction):
	A, B, CD = _translate_standard(writer, addr, line, instruction)

	return description.format(A=A, B=B, C=CD, D=CD)


def _translate_concat(writer, description, addr, line, instruction):
	A = _translate(writer, addr, instruction.A, instruction.A_type)

	args = []

	start = instruction.B
	end = instruction.CD + 1

	while start != end:
		var = _translate(writer, addr, start, ins.T_VAR)
		args.append(var)
		start += 1

	return description.format(A=A, concat_from_B_to_C=" .. ".join(args))


def _translate_nil(writer, description, addr, line, instruction):
	args = []

	start = instruction.A
	end = instruction.CD + 1

	while start != end:
		var = _translate(writer, addr, start, ins.T_VAR)
		args.append(var)
		start += 1

	return description.format(from_A_to_D=", ".join(args))


def _translate_table_str_op(writer, description, addr, line, instruction):
	A, B, CD = _translate_standard(writer, addr, line, instruction)

	C = CD[1:-1]

	return description.format(A=A, B=B, C=C)


def _translate_new_table(writer, description, addr, line, instruction):
	A = _translate(writer, addr, instruction.A, instruction.A_type)

	size = instruction.CD

	array_size = size & 0b0000011111111111
	dict_size = 2 ** (size >> 11)

	return description.format(
		A=A,
		D_array=array_size,
		D_dict=dict_size,
	)


def _translate_mass_set(writer, description, addr, line, instruction):
	base = instruction.A

	table_var = _translate(writer, addr, base - 1, ins.T_VAR)

	first = instruction.CD

	return description.format(
		A_minus_one=table_var,
		A=base,
		D_low=first,
	)


def _translate_varg_call(writer, description, addr, line, instruction):
	base = instruction.A
	argn = instruction.CD
	retn = instruction.B - 1

	args = []
	returns = []

	i = 0
	while i < argn:
		args.append(_translate(writer, addr, base + i + 1, ins.T_VAR))
		i += 1

	i = 0
	while i < retn:
		returns.append(_translate(writer, addr, base + i, ins.T_DST))
		i += 1

	func_var = _translate(writer, addr, base, ins.T_VAR)

	return description.format(
		A=func_var,
		from_A_x_B_minus_two=", ".join(returns)  if retn >= 0 else "MULTRES",
		from_A_plus_one_x_C=", ".join(args)
	)


def _translate_call(writer, description, addr, line, instruction):
	base = instruction.A
	argn = instruction.CD - 1
	retn = instruction.B - 1

	args = []
	returns = []

	i = 0
	while i < argn:
		args.append(_translate(writer, addr, base + i + 1, ins.T_VAR))
		i += 1

	i = 0
	while i < retn:
		returns.append(_translate(writer, addr, base + i, ins.T_DST))
		i += 1

	func_var = _translate(writer, addr, base, ins.T_VAR)

	return description.format(
		A=func_var,
		from_A_x_B_minus_two=", ".join(returns) if retn >= 0 else "MULTRES",
		from_A_plus_one_x_C_minus_one=", ".join(args)
	)


def _translate_varg_tailcall(writer, description, addr, line, instruction):
	base = instruction.A
	argn = instruction.CD - 1

	args = []

	i = 0
	while i < argn:
		args.append(_translate(writer, addr, base + i + 1, ins.T_VAR))
		i += 1

	func_var = _translate(writer, addr, base, ins.T_VAR)

	return description.format(
		A=func_var,
		from_A_plus_one_x_D=", ".join(args)
	)


def _translate_tailcall(writer, description, addr, line, instruction):
	base = instruction.A
	argn = instruction.CD - 1

	args = []

	i = 0
	while i < argn:
		args.append(_translate(writer, addr, base + i + 1, ins.T_VAR))
		i += 1

	func_var = _translate(writer, addr, base, ins.T_VAR)

	return description.format(
		A=func_var,
		from_A_plus_one_x_D_minus_one=", ".join(args)
	)


def _translate_iterator(writer, description, addr, line, instruction):
	base = instruction.A

	A = _translate(writer, addr, instruction.A, ins.T_DST)
	A_plus_one = _translate(writer, addr, instruction.A + 1, ins.T_DST)
	A_plus_two = _translate(writer, addr, instruction.A + 2, ins.T_DST)

	A_minus_three = _translate(writer, addr, instruction.A - 3, ins.T_VAR)
	A_minus_two = _translate(writer, addr, instruction.A - 2, ins.T_VAR)
	A_minus_one = _translate(writer, addr, instruction.A - 1, ins.T_VAR)

	retn = instruction.B - 1

	returns = []

	i = 0
	while i < retn:
		returns.append(_translate(writer, addr, base + i, ins.T_DST))
		i += 1

	return description.format(
		A=A,
		A_plus_one=A_plus_one,
		A_plus_two=A_plus_two,
		A_minus_three=A_minus_three,
		A_minus_two=A_minus_two,
		A_minus_one=A_minus_one,
		from_A_x_B_minus_two=", ".join(returns)
	)


def _translate_vararg(writer, description, addr, line, instruction):
	returns = []

	base = instruction.A

	count = instruction.B - 2

	if count < 0:
		return description.format(from_A_x_B_minus_two="MULTRES")

	i = 0
	while i <= count:
		returns.append(_translate(writer, addr, base + i, ins.T_DST))
		i += 1

	return description.format(
		from_A_x_B_minus_two=", ".join(returns)
	)


def _translate_return_mult(writer, description, addr, line, instruction):
	returns = []

	base = instruction.A

	count = instruction.CD - 1

	i = 0
	while i < count:
		returns.append(_translate(writer, addr, base + i, ins.T_VAR))
		i += 1

	return description.format(
		from_A_x_D_minus_one=", ".join(returns)
	)


def _translate_return_many(writer, description, addr, line, instruction):
	returns = []

	base = instruction.A

	count = instruction.CD - 2

	i = 0
	while i < count:
		returns.append(_translate(writer, addr, base + i, ins.T_VAR))
		i += 1

	return description.format(
		from_A_x_D_minus_two=", ".join(returns)
	)


def _translate_return_one(writer, description, addr, line, instruction):
	A = _translate(writer, addr, instruction.A, ins.T_VAR)

	return description.format(A=A)


def _translate_for_init(writer, description, addr, line, instruction):
	idx = _translate(writer, addr, instruction.A, ins.T_BS)
	stop = _translate(writer, addr, instruction.A + 1, ins.T_BS)
	step = _translate(writer, addr, instruction.A + 2, ins.T_BS)
	ext_idx = _translate(writer, addr, instruction.A + 3, ins.T_VAR)

	return description.format(
		A=idx,
		A_plus_one=stop,
		A_plus_two=step,
		A_plus_three=ext_idx,
		D=_translate(writer, addr, instruction.CD, ins.T_JMP)
	)


def _translate_numeric_loop(writer, description, addr, line, instruction):
	stop = _translate(writer, addr, instruction.A + 1, ins.T_VAR)
	step = _translate(writer, addr, instruction.A + 2, ins.T_VAR)
	ext_idx = _translate(writer, addr, instruction.A + 3, ins.T_VAR)

	# ext_idx isn't correct var here, but for the visualisation sake we will
	# omit all the stuff with the internal idx var

	return description.format(
		A=ext_idx,
		A_plus_one=stop,
		A_plus_two=step,
		D=_translate(writer, addr, instruction.CD, ins.T_JMP)
	)


def _translate_iter_loop(writer, description, addr, line, instruction):
	A_minus_one = _translate(writer, addr, instruction.A - 1, ins.T_VAR)
	A = _translate(writer, addr, instruction.A, ins.T_VAR)

	return description.format(
		A_minus_one=A_minus_one,
		A=A,
		D=_translate(writer, addr, instruction.CD, ins.T_JMP)
	)


_HANDLERS_MAP = (
	# Comparison ops

	(ins.ISLT.opcode, 	_translate_normal),
	(ins.ISGE.opcode, 	_translate_normal),
	(ins.ISLE.opcode, 	_translate_normal),
	(ins.ISGT.opcode, 	_translate_normal),

	(ins.ISEQV.opcode, 	_translate_normal),
	(ins.ISNEV.opcode, 	_translate_normal),

	(ins.ISEQS.opcode, 	_translate_normal),
	(ins.ISNES.opcode, 	_translate_normal),

	(ins.ISEQN.opcode, 	_translate_normal),
	(ins.ISNEN.opcode, 	_translate_normal),

	(ins.ISEQP.opcode, 	_translate_normal),
	(ins.ISNEP.opcode, 	_translate_normal),

	# Unary test and copy ops

	(ins.ISTC.opcode, 	_translate_normal),
	(ins.ISFC.opcode, 	_translate_normal),

	(ins.IST.opcode, 	_translate_normal),
	(ins.ISF.opcode, 	_translate_normal),

	# Unary ops

	(ins.MOV.opcode, 	_translate_normal),
	(ins.NOT.opcode, 	_translate_normal),
	(ins.UNM.opcode, 	_translate_normal),
	(ins.LEN.opcode, 	_translate_normal),

	# Binary ops

	(ins.ADDVN.opcode, 	_translate_normal),
	(ins.SUBVN.opcode, 	_translate_normal),
	(ins.MULVN.opcode, 	_translate_normal),
	(ins.DIVVN.opcode, 	_translate_normal),
	(ins.MODVN.opcode, 	_translate_normal),

	(ins.ADDNV.opcode, 	_translate_normal),
	(ins.SUBNV.opcode, 	_translate_normal),
	(ins.MULNV.opcode, 	_translate_normal),
	(ins.DIVNV.opcode, 	_translate_normal),
	(ins.MODNV.opcode, 	_translate_normal),

	(ins.ADDVV.opcode, 	_translate_normal),
	(ins.SUBVV.opcode, 	_translate_normal),
	(ins.MULVV.opcode, 	_translate_normal),
	(ins.DIVVV.opcode, 	_translate_normal),
	(ins.MODVV.opcode, 	_translate_normal),

	(ins.POW.opcode, 	_translate_normal),
	(ins.CAT.opcode, 	_translate_concat),

	# Constant ops

	(ins.KSTR.opcode, 	_translate_normal),
	(ins.KCDATA.opcode, 	_translate_normal),
	(ins.KSHORT.opcode, 	_translate_normal),
	(ins.KNUM.opcode, 	_translate_normal),
	(ins.KPRI.opcode, 	_translate_normal),

	(ins.KNIL.opcode, 	_translate_nil),

	# Upvalue and function ops

	(ins.UGET.opcode, 	_translate_normal),

	(ins.USETV.opcode, 	_translate_normal),
	(ins.USETS.opcode, 	_translate_normal),
	(ins.USETN.opcode, 	_translate_normal),
	(ins.USETP.opcode, 	_translate_normal),

	(ins.UCLO.opcode, 	_translate_normal),

	(ins.FNEW.opcode, 	_translate_normal),

	# Table ops

	(ins.TNEW.opcode, 	_translate_new_table),

	(ins.TDUP.opcode, 	_translate_normal),

	(ins.GGET.opcode, 	_translate_normal),
	(ins.GSET.opcode, 	_translate_normal),

	(ins.TGETV.opcode, 	_translate_normal),
	(ins.TGETS.opcode, 	_translate_table_str_op),
	(ins.TGETB.opcode, 	_translate_normal),

	(ins.TSETV.opcode, 	_translate_normal),
	(ins.TSETS.opcode, 	_translate_table_str_op),
	(ins.TSETB.opcode, 	_translate_normal),

	(ins.TSETM.opcode, 	_translate_mass_set),

	# Calls and vararg handling

	(ins.CALLM.opcode, 	_translate_varg_call),
	(ins.CALL.opcode, 	_translate_call),
	(ins.CALLMT.opcode, 	_translate_varg_tailcall),
	(ins.CALLT.opcode, 	_translate_tailcall),

	(ins.ITERC.opcode, 	_translate_iterator),
	(ins.ITERN.opcode, 	_translate_iterator),

	(ins.VARG.opcode, 	_translate_vararg),

	(ins.ISNEXT.opcode, 	_translate_normal),

	# Returns

	(ins.RETM.opcode, 	_translate_return_mult),
	(ins.RET.opcode, 	_translate_return_many),
	(ins.RET0.opcode, 	_translate_normal),
	(ins.RET1.opcode, 	_translate_return_one),

	# Loops and branches

	(ins.FORI.opcode, 	_translate_for_init),
	(ins.JFORI.opcode, 	_translate_for_init),

	(ins.FORL.opcode, 	_translate_numeric_loop),
	(ins.IFORL.opcode, 	_translate_numeric_loop),
	(ins.JFORL.opcode, 	_translate_numeric_loop),

	(ins.ITERL.opcode, 	_translate_iter_loop),
	(ins.IITERL.opcode, 	_translate_iter_loop),
	(ins.JITERL.opcode, 	_translate_iter_loop),

	(ins.LOOP.opcode, 	_translate_normal),
	(ins.ILOOP.opcode, 	_translate_normal),
	(ins.JLOOP.opcode, 	_translate_normal),

	(ins.JMP.opcode, 	_translate_normal),

	# Function headers

	(ins.FUNCF.opcode, 	_translate_normal),
	(ins.IFUNCF.opcode, 	_translate_normal),
	(ins.JFUNCF.opcode, 	_translate_normal),

	(ins.FUNCV.opcode, 	_translate_normal),
	(ins.IFUNCV.opcode, 	_translate_normal),
	(ins.JFUNCV.opcode, 	_translate_normal),

	(ins.FUNCC.opcode, 	_translate_normal),
	(ins.FUNCCW.opcode, 	_translate_normal)
)


def _init():
	global _HANDLERS_MAP, _DESCRIPTION_HANDLERS

	for opcode, handler in _HANDLERS_MAP:
		_DESCRIPTION_HANDLERS[opcode] = handler

	del globals()["_init"]
	del globals()["_HANDLERS_MAP"]

_init()
