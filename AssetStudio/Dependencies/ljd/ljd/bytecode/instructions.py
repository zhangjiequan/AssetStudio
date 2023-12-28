#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

#
# Almost direct wiki-to-code from
# http://wiki.luajit.org/Bytecode-2.0
#


# What the hell is an upvalue?
# It is value from the upper prototype, i.e. a variable stored in a closure.

# What the hell is the MULTRES thing?
# The magical VM's variable that counts the CALL* or VARG returns.
# I.e. it's used to speed-up things like foo(var1, var2, bar(var3, var4)) or
#
# function foo(...)
# 	bla-bla
# 	bar(...)
#

# Argument types

T_VAR = 0  # variable slot number
T_DST = 1  # variable slot number, used as a destination

T_BS = 2  # base slot number, read-write
T_RBS = 3  # base slot number, read-only

T_UV = 4  # upvalue number (slot number, but specific to upvalues)

T_LIT = 5  # literal
T_SLIT = 6  # signed literal

T_PRI = 7  # primitive type (0 = nil, 1 = false, 2 = true)
T_NUM = 8  # numeric constant, index into constant table
T_STR = 9  # string constant, negated index into constant table

T_TAB = 10  # template table, negated index into constant table
T_FUN = 11  # function prototype, negated index into constant table
T_CDT = 12  # cdata constant, negated index into constant table
T_JMP = 13  # branch target, relative to next instruction, biased with 0x8000


class _Instruction():
	def __init__(self, definition):
		for key, value in definition.__dict__.items():
			setattr(self, key, value)

		if self.A_type is not None:
			self.A = 0

		if self.B_type is not None:
			self.B = 0

		if self.CD_type is not None:
			self.CD = 0


class _IDef():
	_LAST_OPCODE = 0

	def __init__(self, name, A_type, B_type, CD_type, description):
		self.name = name
		self.opcode = _IDef._LAST_OPCODE
		self.A_type = A_type
		self.B_type = B_type
		self.CD_type = CD_type
		self.description = description

		self.args_count = (self.A_type is not None)	\
				+ (self.B_type is not None)	\
				+ (self.CD_type is not None)

		_IDef._LAST_OPCODE += 1

	def __call__(self):
		return _Instruction(self)


# Names and order are in sync with luaJIT bytecode for ease of changing

# class = name			A	B	C	description
# Comparison ops

ISLT = _IDef("ISLT", 		T_VAR, 	None, 	T_VAR, 	"if {A} < {D}")
ISGE = _IDef("ISGE", 		T_VAR, 	None, 	T_VAR, 	"if {A} >= {D}")
ISLE = _IDef("ISLE", 		T_VAR, 	None, 	T_VAR, 	"if {A} <= {D}")
ISGT = _IDef("ISGT", 		T_VAR, 	None, 	T_VAR, 	"if {A} > {D}")

ISEQV = _IDef("ISEQV", 		T_VAR, 	None, 	T_VAR, 	"if {A} == {D}")
ISNEV = _IDef("ISNEV", 		T_VAR, 	None, 	T_VAR, 	"if {A} ~= {D}")

ISEQS = _IDef("ISEQS", 		T_VAR, 	None, 	T_STR, 	"if {A} == {D}")
ISNES = _IDef("ISNES", 		T_VAR, 	None, 	T_STR, 	"if {A} ~= {D}")

ISEQN = _IDef("ISEQN", 		T_VAR, 	None, 	T_NUM, 	"if {A} == {D}")
ISNEN = _IDef("ISNEN", 		T_VAR, 	None, 	T_NUM, 	"if {A} ~= {D}")

ISEQP = _IDef("ISEQP", 		T_VAR, 	None, 	T_PRI, 	"if {A} == {D}")
ISNEP = _IDef("ISNEP", 		T_VAR, 	None, 	T_PRI, 	"if {A} ~= {D}")

# Unary test and copy ops

ISTC = _IDef("ISTC", 		T_DST, 	None, 	T_VAR, 	"{A} = {D}; if {D}")
ISFC = _IDef("ISFC", 		T_DST, 	None, 	T_VAR, 	"{A} = {D}; if not {D}")

IST = _IDef("IST", 		None, 	None, 	T_VAR, 	"if {D}")
ISF = _IDef("ISF", 		None, 	None, 	T_VAR, 	"if not {D}")

ISTYPE = _IDef("ISTYPE", 	T_VAR, 	None, 	T_LIT, 	"ISTYPE unknow")
ISNUM = _IDef("ISNUM", 		T_VAR, 	None, 	T_LIT, 	"ISNUM unknow")
# Unary ops

MOV = _IDef("MOV", 		T_DST, 	None, 	T_VAR, 	"{A} = {D}")
NOT = _IDef("NOT", 		T_DST, 	None, 	T_VAR, 	"{A} = not {D}")
UNM = _IDef("UNM", 		T_DST, 	None, 	T_VAR, 	"{A} = -{D}")
LEN = _IDef("LEN", 		T_DST, 	None, 	T_VAR, 	"{A} = #{D}")

# Binary ops

ADDVN = _IDef("ADDVN", 		T_DST, 	T_VAR, 	T_NUM, 	"{A} = {B} + {C}")
SUBVN = _IDef("SUBVN", 		T_DST, 	T_VAR, 	T_NUM, 	"{A} = {B} - {C}")
MULVN = _IDef("MULVN", 		T_DST, 	T_VAR, 	T_NUM, 	"{A} = {B} * {C}")
DIVVN = _IDef("DIVVN", 		T_DST, 	T_VAR, 	T_NUM, 	"{A} = {B} / {C}")
MODVN = _IDef("MODVN", 		T_DST, 	T_VAR, 	T_NUM, 	"{A} = {B} % {C}")

ADDNV = _IDef("ADDNV", 		T_DST, 	T_VAR, 	T_NUM, 	"{A} = {C} + {B}")
SUBNV = _IDef("SUBNV", 		T_DST, 	T_VAR, 	T_NUM, 	"{A} = {C} - {B}")
MULNV = _IDef("MULNV", 		T_DST, 	T_VAR, 	T_NUM, 	"{A} = {C} * {B}")
DIVNV = _IDef("DIVNV", 		T_DST, 	T_VAR, 	T_NUM, 	"{A} = {C} / {B}")
MODNV = _IDef("MODNV", 		T_DST, 	T_VAR, 	T_NUM, 	"{A} = {C} % {B}")

ADDVV = _IDef("ADDVV", 		T_DST, 	T_VAR, 	T_VAR, 	"{A} = {B} + {C}")
SUBVV = _IDef("SUBVV", 		T_DST, 	T_VAR, 	T_VAR, 	"{A} = {B} - {C}")
MULVV = _IDef("MULVV", 		T_DST, 	T_VAR, 	T_VAR, 	"{A} = {B} * {C}")
DIVVV = _IDef("DIVVV", 		T_DST, 	T_VAR, 	T_VAR, 	"{A} = {B} / {C}")
MODVV = _IDef("MODVV", 		T_DST, 	T_VAR, 	T_VAR, 	"{A} = {B} % {C}")

POW = _IDef("POW", 		T_DST, 	T_VAR, 	T_VAR, 	"{A} = {B} ^ {C} (pow)")
CAT = _IDef("CAT", 		T_DST, 	T_RBS, 	T_RBS,
		"{A} = {concat_from_B_to_C}")

# Constant ops.

KSTR = _IDef("KSTR", 		T_DST, 	None, 	T_STR, 	"{A} = {D}")
KCDATA = _IDef("KCDATA", 	T_DST, 	None, 	T_CDT, 	"{A} = {D}")
KSHORT = _IDef("KSHORT", 	T_DST, 	None, 	T_SLIT, "{A} = {D}")
KNUM = _IDef("KNUM", 		T_DST, 	None, 	T_NUM, 	"{A} = {D}")
KPRI = _IDef("KPRI", 		T_DST, 	None, 	T_PRI, 	"{A} = {D}")

KNIL = _IDef("KNIL", 		T_BS, 	None, 	T_BS, 	"{from_A_to_D} = nil")

# Upvalue and function ops.

UGET = _IDef("UGET", 		T_DST, 	None, 	T_UV, 	"{A} = {D}")

USETV = _IDef("USETV", 		T_UV, 	None, 	T_VAR, 	"{A} = {D}")
USETS = _IDef("USETS", 		T_UV, 	None, 	T_STR, 	"{A} = {D}")
USETN = _IDef("USETN", 		T_UV, 	None, 	T_NUM, 	"{A} = {D}")
USETP = _IDef("USETP", 		T_UV, 	None, 	T_PRI, 	"{A} = {D}")

UCLO = _IDef("UCLO", 		T_RBS, 	None, 	T_JMP,
		"nil uvs >= {A}; goto {D}")

FNEW = _IDef("FNEW", 		T_DST, 	None, 	T_FUN, 	"{A} = function {D}")

# Table ops.

TNEW = _IDef("TNEW", 		T_DST, 	None, 	T_LIT, 	"{A} = new table("
							" array: {D_array},"
							" dict: {D_dict})")

TDUP = _IDef("TDUP", 		T_DST, 	None, 	T_TAB, 	"{A} = copy {D}")

GGET = _IDef("GGET", 		T_DST, 	None, 	T_STR, 	"{A} = _env[{D}]")
GSET = _IDef("GSET", 		T_VAR, 	None, 	T_STR, 	"_env[{D}] = {A}")

TGETV = _IDef("TGETV", 		T_DST, 	T_VAR, 	T_VAR, 	"{A} = {B}[{C}]")
TGETS = _IDef("TGETS", 		T_DST, 	T_VAR, 	T_STR, 	"{A} = {B}.{C}")
TGETB = _IDef("TGETB", 		T_DST, 	T_VAR, 	T_LIT, 	"{A} = {B}[{C}]")
TGETR = _IDef("TGETR", 		T_DST, 	T_VAR, 	T_VAR, 	"unkown TGETR")

TSETV = _IDef("TSETV", 		T_VAR, 	T_VAR, 	T_VAR, 	"{B}[{C}] = {A}")
TSETS = _IDef("TSETS", 		T_VAR, 	T_VAR, 	T_STR, 	"{B}.{C} = {A}")
TSETB = _IDef("TSETB", 		T_VAR, 	T_VAR, 	T_LIT, 	"{B}[{C}] = {A}")

TSETM = _IDef("TSETM", 	 	T_BS, 	None, 	T_NUM,
		"for i = 0, MULTRES, 1 do"
		" {A_minus_one}[{D_low} + i] = slot({A} + i)")

TSETR = _IDef("TSETR", 		T_VAR, 	T_VAR, 	T_VAR, 	"unkow TSETR")
# Calls and vararg handling. T = tail call.

CALLM = _IDef("CALLM", 		T_BS, 	T_LIT, 	T_LIT,
		"{from_A_x_B_minus_two} = {A}({from_A_plus_one_x_C}, ...MULTRES)")

CALL = _IDef("CALL", 		T_BS, 	T_LIT, 	T_LIT,
		"{from_A_x_B_minus_two} = {A}({from_A_plus_one_x_C_minus_one})")

CALLMT = _IDef("CALLMT", 	T_BS, 	None, 	T_LIT,
		"return {A}({from_A_plus_one_x_D}, ...MULTRES)")

CALLT = _IDef("CALLT", 		T_BS, 	None, 	T_LIT,
		"return {A}({from_A_plus_one_x_D_minus_one})")

ITERC = _IDef("ITERC", 		T_BS, 	T_LIT, 	T_LIT,
		"{A}, {A_plus_one}, {A_plus_two} ="
			" {A_minus_three}, {A_minus_two}, {A_minus_one};"
		" {from_A_x_B_minus_two} ="
			" {A_minus_three}({A_minus_two}, {A_minus_one})")

ITERN = _IDef("ITERN", 		T_BS, 	T_LIT, 	T_LIT,
		"{A}, {A_plus_one}, {A_plus_two} ="
			" {A_minus_three}, {A_minus_two}, {A_minus_one};"
		" {from_A_x_B_minus_two} ="
			" {A_minus_three}({A_minus_two}, {A_minus_one})")

VARG = _IDef("VARG", 		T_BS, 	T_LIT, 	T_LIT,
		"{from_A_x_B_minus_two} = ...")

ISNEXT = _IDef("ISNEXT", 	 T_BS, 	None, 	T_JMP,
		"Verify ITERN at {D}; goto {D}")

# Returns.

RETM = _IDef("RETM", 		T_BS, 	None, 	T_LIT,
		"return {from_A_x_D_minus_one}, ...MULTRES")

RET = _IDef("RET", 	 	T_RBS, 	None, 	T_LIT,
		"return {from_A_x_D_minus_two}")

RET0 = _IDef("RET0", 		T_RBS, 	None, 	T_LIT, 	"return")
RET1 = _IDef("RET1", 		T_RBS, 	None, 	T_LIT, 	"return {A}")

# Loops and branches. I/J = interp/JIT, I/C/L = init/call/loop.

FORI = _IDef("FORI", 		T_BS, 	None, 	T_JMP,
		"for {A_plus_three} = {A},{A_plus_one},{A_plus_two}"
		" else goto {D}")

JFORI = _IDef("JFORI", 		T_BS, 	None, 	T_JMP,
		"for {A_plus_three} = {A},{A_plus_one},{A_plus_two}"
		" else goto {D}")

FORL = _IDef("FORL", 		T_BS, 	None, 	T_JMP,
		"{A} = {A} + {A_plus_two};"
		" if cmp({A}, sign {A_plus_two},  {A_plus_one}) goto {D}")

IFORL = _IDef("IFORL", 	 	T_BS, 	None, 	T_JMP,
		"{A} = {A} + {A_plus_two};"
		" if cmp({A}, sign {A_plus_two}, {A_plus_one}) goto {D}")

JFORL = _IDef("JFORL", 		T_BS, 	None, 	T_JMP,
		"{A} = {A} + {A_plus_two};"
		" if cmp({A}, sign {A_plus_two}, {A_plus_one}) goto {D}")

ITERL = _IDef("ITERL", 		T_BS, 	None, 	T_JMP,
		"{A_minus_one} = {A}; if {A} != nil goto {D}")

IITERL = _IDef("IITERL", 	T_BS, 	None, 	T_JMP,
		"{A_minus_one} = {A}; if {A} != nil goto {D}")

JITERL = _IDef("JITERL", 	T_BS, 	None, 	T_LIT,
		"{A_minus_one} = {A}; if {A} != nil goto {D}")

LOOP = _IDef("LOOP", 		T_RBS, 	None, 	T_JMP, 	"Noop")
ILOOP = _IDef("ILOOP", 		T_RBS, 	None, 	T_JMP, 	"Noop")
JLOOP = _IDef("JLOOP", 		T_RBS, 	None, 	T_LIT, 	"Noop")

JMP = _IDef("JMP", 		T_RBS, 	None, 	T_JMP, 	"	goto {D}")

# Function headers. I/J = interp/JIT, F/V/C = fixarg/vararg/C func.
# Shouldn't be ever seen - they are not stored in raw dump?

FUNCF = _IDef("FUNCF", 		T_RBS, 	None, 	None,
		"Fixed-arg function with frame size {A}")

IFUNCF = _IDef("IFUNCF", 	T_RBS, 	None, 	None,
		"Interpreted fixed-arg function with frame size {A}")

JFUNCF = _IDef("JFUNCF", 	T_RBS, 	None, 	T_LIT,
		"JIT compiled fixed-arg function with frame size {A}")

FUNCV = _IDef("FUNCV", 		T_RBS, 	None, 	None,
		"Var-arg function with frame size {A}")

IFUNCV = _IDef("IFUNCV", 	T_RBS, 	None, 	None,
		"Interpreted var-arg function with frame size {A}")

JFUNCV = _IDef("JFUNCV", 	T_RBS, 	None, 	T_LIT,
		"JIT compiled var-arg function with frame size {A}")

FUNCC = _IDef("FUNCC", 		T_RBS, 	None, 	None,
		"C function with frame size {A}")
FUNCCW = _IDef("FUNCCW", 	T_RBS, 	None, 	None,
		"Wrapped C function with frame size {A}")

UNKNW = _IDef("UNKNW", 		T_LIT, 	T_LIT, 	T_LIT, "Unknown instruction")
