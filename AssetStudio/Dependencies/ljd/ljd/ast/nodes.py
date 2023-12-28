#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#


# We should visit stuff in it's execution order. That's important


class FunctionDefinition():
	def __init__(self):
		self.arguments = IdentifiersList()
		self.statements = StatementsList()

		self._upvalues = None
		self._debuginfo = None
		self._instructions_count = 0

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_function_definition, self)

		visitor._visit(self.arguments)
		visitor._visit(self.statements)

		visitor._leave_node(visitor.leave_function_definition, self)


class TableConstructor():
	def __init__(self):
		self.array = RecordsList()
		self.records = RecordsList()

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_table_constructor, self)

		visitor._visit(self.array)
		visitor._visit(self.records)

		visitor._leave_node(visitor.leave_table_constructor, self)


class ArrayRecord():
	def __init__(self):
		self.value = None

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_array_record, self)

		visitor._visit(self.value)

		visitor._leave_node(visitor.leave_array_record, self)


class TableRecord():
	def __init__(self):
		self.key = None
		self.value = None

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_table_record, self)

		visitor._visit(self.key)
		visitor._visit(self.value)

		visitor._leave_node(visitor.leave_table_record, self)


class Assignment():
	T_LOCAL_DEFINITION = 0
	T_NORMAL = 1

	def __init__(self):
		self.expressions = ExpressionsList()
		self.destinations = VariablesList()
		self.type = -1

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_assignment, self)

		visitor._visit(self.expressions)
		visitor._visit(self.destinations)

		visitor._leave_node(visitor.leave_assignment, self)


class BinaryOperator():
	T_LOGICAL_OR = 0  # left or right
	T_LOGICAL_AND = 10  # left and right

	T_LESS_THEN = 20  # left < right
	T_GREATER_THEN = 21  # left > right
	T_LESS_OR_EQUAL = 22  # left <= right
	T_GREATER_OR_EQUAL = 23  # left >= right

	T_NOT_EQUAL = 24  # left ~= right
	T_EQUAL = 25  # left == right

	T_CONCAT = 30  # left .. right

	T_ADD = 40  # left + right
	T_SUBTRACT = 41  # left - right

	T_MULTIPLY = 50  # left * right
	T_DIVISION = 51  # left / right
	T_MOD = 52  # left % right

	T_POW = 70  # left ^ right

	def __init__(self):
		self.type = -1
		self.left = None
		self.right = None

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_binary_operator, self)

		visitor._visit(self.left)
		visitor._visit(self.right)

		visitor._leave_node(visitor.leave_binary_operator, self)


class UnaryOperator():
	T_NOT = 60  # not operand
	T_LENGTH_OPERATOR = 61  # #operand
	T_MINUS = 62  # -operand

	def __init__(self):
		self.type = -1
		self.operand = None

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_unary_operator, self)

		visitor._visit(self.operand)

		visitor._leave_node(visitor.leave_unary_operator, self)


class StatementsList():
	def __init__(self):
		self.contents = []

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_statements_list, self)

		visitor._visit_list(self.contents)

		visitor._leave_node(visitor.leave_statements_list, self)


class IdentifiersList():
	def __init__(self):
		self.contents = []

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_identifiers_list, self)

		visitor._visit_list(self.contents)

		visitor._leave_node(visitor.leave_identifiers_list, self)


class RecordsList():
	def __init__(self):
		self.contents = []

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_records_list, self)

		visitor._visit_list(self.contents)

		visitor._leave_node(visitor.leave_records_list, self)


class VariablesList():
	def __init__(self):
		self.contents = []

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_variables_list, self)

		visitor._visit_list(self.contents)

		visitor._leave_node(visitor.leave_variables_list, self)


class ExpressionsList():
	def __init__(self):
		self.contents = []

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_expressions_list, self)

		visitor._visit_list(self.contents)

		visitor._leave_node(visitor.leave_expressions_list, self)


# Called Name in the Lua 5.1 reference
class Identifier():
	T_SLOT = 0
	T_LOCAL = 1
	T_UPVALUE = 2
	T_BUILTIN = 3

	def __init__(self):
		self.name = None
		self.type = -1
		self.slot = -1

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_identifier, self)
		visitor._leave_node(visitor.leave_identifier, self)


# helper vararg/varreturn

class MULTRES():
	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_multres, self)
		visitor._leave_node(visitor.leave_multres, self)


class TableElement():
	def __init__(self):
		self.table = None
		self.key = None

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_table_element, self)

		visitor._visit(self.key)
		visitor._visit(self.table)

		visitor._leave_node(visitor.leave_table_element, self)


class Vararg():
	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_vararg, self)
		visitor._leave_node(visitor.leave_vararg, self)


class FunctionCall():
	def __init__(self):
		self.function = None
		self.arguments = ExpressionsList()

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_function_call, self)

		visitor._visit(self.arguments)
		visitor._visit(self.function)

		visitor._leave_node(visitor.leave_function_call, self)


class If():
	def __init__(self):
		self.expression = None
		self.then_block = StatementsList()
		self.elseifs = []
		self.else_block = StatementsList()

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_if, self)

		visitor._visit(self.expression)
		visitor._visit(self.then_block)

		visitor._visit_list(self.elseifs)

		visitor._visit(self.else_block)

		visitor._leave_node(visitor.leave_if, self)


class ElseIf():
	def __init__(self):
		self.expression = None
		self.then_block = StatementsList()

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_elseif, self)

		visitor._visit(self.expression)
		visitor._visit(self.then_block)

		visitor._leave_node(visitor.leave_elseif, self)

# ##


class Block():
	def __init__(self):
		self.index = -1
		self.warp = None
		self.contents = []
		self.first_address = 0
		self.last_address = 0
		self.warpins_count = 0

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_block, self)

		visitor._visit_list(self.contents)
		visitor._visit(self.warp)

		visitor._leave_node(visitor.leave_block, self)


class UnconditionalWarp():
	T_JUMP = 0
	T_FLOW = 1

	def __init__(self):
		self.type = -1
		self.target = None
		self.is_uclo = False

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_unconditional_warp, self)

		# DO NOT VISIT self.target - warps are not part of the tree

		visitor._leave_node(visitor.leave_unconditional_warp, self)


class ConditionalWarp():
	def __init__(self):
		self.condition = None
		self.true_target = None
		self.false_target = None

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_conditional_warp, self)

		visitor._visit(self.condition)
		# DO NOT VISIT self.true_target - warps are not part of the tree
		# DO NOT VISIT self.false_target - warps are not part of the tree

		visitor._leave_node(visitor.leave_conditional_warp, self)


class IteratorWarp():
	def __init__(self):
		self.variables = VariablesList()
		self.controls = ExpressionsList()
		self.body = None
		self.way_out = None

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_iterator_warp, self)

		visitor._visit(self.variables)
		visitor._visit(self.controls)
		# DO NOT VISIT self.body - warps are not part of the tree
		# DO NOT VISIT self.way_out - warps are not part of the tree

		visitor._leave_node(visitor.leave_iterator_warp, self)


class NumericLoopWarp():
	def __init__(self):
		self.index = Identifier()
		self.controls = ExpressionsList()
		self.body = None
		self.way_out = None

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_numeric_loop_warp, self)

		visitor._visit(self.index)
		visitor._visit(self.controls)
		# DO NOT VISIT self.body - warps are not part of the tree
		# DO NOT VISIT self.way_out - warps are not part of the tree

		visitor._leave_node(visitor.leave_numeric_loop_warp, self)


class EndWarp():
	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_end_warp, self)
		visitor._leave_node(visitor.leave_end_warp, self)


# ##


class Return():
	def __init__(self):
		self.returns = ExpressionsList()

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_return, self)

		visitor._visit(self.returns)

		visitor._leave_node(visitor.leave_return, self)


class Break():
	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_break, self)
		visitor._leave_node(visitor.leave_break, self)


class While():
	def __init__(self):
		self.expression = None
		self.statements = StatementsList()

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_while, self)

		visitor._visit(self.expression)
		visitor._visit(self.statements)

		visitor._leave_node(visitor.leave_while, self)


class RepeatUntil():
	def __init__(self):
		self.expression = None
		self.statements = StatementsList()

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_repeat_until, self)

		visitor._visit(self.statements)
		visitor._visit(self.expression)

		visitor._leave_node(visitor.leave_repeat_until, self)


class NumericFor():
	def __init__(self):
		self.variable = None
		self.expressions = ExpressionsList()
		self.statements = StatementsList()

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_numeric_for, self)

		visitor._visit(self.variable)
		visitor._visit(self.expressions)
		visitor._visit(self.statements)

		visitor._leave_node(visitor.leave_numeric_for, self)


class IteratorFor():
	def __init__(self):
		self.expressions = ExpressionsList()
		self.identifiers = VariablesList()
		self.statements = StatementsList()

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_iterator_for, self)

		visitor._visit(self.expressions)
		visitor._visit(self.identifiers)
		visitor._visit(self.statements)

		visitor._leave_node(visitor.leave_iterator_for, self)


class Constant():
	T_INTEGER = 0
	T_FLOAT = 1
	T_STRING = 2
	T_CDATA = 3

	def __init__(self):
		self.type = -1
		self.value = None

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_constant, self)
		visitor._leave_node(visitor.leave_constant, self)


class Primitive():
	T_NIL = 0
	T_TRUE = 1
	T_FALSE = 2

	def __init__(self):
		self.type = -1

	def _accept(self, visitor):
		visitor._visit_node(visitor.visit_primitive, self)
		visitor._leave_node(visitor.leave_primitive, self)
