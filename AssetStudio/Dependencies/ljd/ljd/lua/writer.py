#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

import re

import ljd.ast.nodes as nodes
import ljd.ast.traverse as traverse


CMD_START_STATEMENT = 0
CMD_END_STATEMENT = 1
CMD_END_LINE = 3
CMD_START_BLOCK = 4
CMD_END_BLOCK = 5
CMD_WRITE = 6


OPERATOR_TYPES = (nodes.BinaryOperator, nodes.UnaryOperator)

STATEMENT_NONE = -1

STATEMENT_ASSIGNMENT = 0
STATEMENT_FUNCTION_CALL = 1
STATEMENT_RETURN = 2
STATEMENT_BREAK = 3

STATEMENT_IF = 4

STATEMENT_ITERATOR_FOR = 5
STATEMENT_NUMERIC_FOR = 6
STATEMENT_REPEAT_UNTIL = 7
STATEMENT_WHILE = 8

STATEMENT_FUNCTION = 9

VALID_IDENTIFIER = re.compile(r'^\w[\w\d]*$')


class _State():
	def __init__(self):
		self.current_statement = STATEMENT_NONE
		self.function_name = None
		self.function_local = False


class Visitor(traverse.Visitor):
	def __init__(self):
		traverse.Visitor.__init__(self)

		self.print_queue = []

		self._visited_nodes = [set()]
		self._states = [_State()]

	# ##

	def _start_statement(self, statement):
		assert self._state().current_statement == STATEMENT_NONE
		self._state().current_statement = statement
		self.print_queue.append((CMD_START_STATEMENT, statement))

	def _end_statement(self, statement):
		assert statement == self._state().current_statement
		self._state().current_statement = STATEMENT_NONE
		self.print_queue.append((CMD_END_STATEMENT, statement))

	def _end_line(self):
		self.print_queue.append((CMD_END_LINE,))

	def _start_block(self):
		self.print_queue.append((CMD_START_BLOCK,))

	def _end_block(self):
		self.print_queue.append((CMD_END_BLOCK,))

	def _write(self, fmt, *args, **kargs):
		self.print_queue.append((CMD_WRITE, fmt, args, kargs))

	def _state(self):
		return self._states[-1]

	def _push_state(self):
		return self._states.append(_State())

	def _pop_state(self):
		return self._states.pop()

	# ##

	def visit_function_definition(self, node):
		is_statement = self._state().function_name is not None

		if is_statement:
			self._start_statement(STATEMENT_FUNCTION)

			if self._state().function_local:
				self._write("local ")

			self._write("function ")

			self._visit(self._state().function_name)

			self._write("(")

			self._state().function_name = None
		else:
			self._write("function (")

		self._visit(node.arguments)

		self._write(")")

		self._end_line()

		self._visit(node.statements)

		self._write("end")

		if is_statement:
			self._end_statement(STATEMENT_FUNCTION)

	# ##

	def visit_table_constructor(self, node):
		self._write("{")

		if len(node.records.contents) + len(node.array.contents) > 0:
			self._end_line()

			self._start_block()

			array = node.array.contents
			records = node.records.contents

			all_records = nodes.RecordsList()
			all_records.contents = array + records

			if len(array) > 0:
				first = array[0].value

				all_records.contents.pop(0)

				if not isinstance(first, nodes.Primitive) \
						or first.type != first.T_NIL:
					record = nodes.TableRecord()
					record.key = nodes.Constant()
					record.key.type = nodes.Constant.T_INTEGER
					record.key.value = 0
					record.value = first

					all_records.contents.insert(0, record)

			self._visit(all_records)

			self._skip(node.array)
			self._skip(node.records)

			self._end_block()
		else:
			self._skip(node.array)
			self._skip(node.records)

		self._write("}")

	def visit_table_record(self, node):
		if self._is_valid_name(node.key):
			self._write(node.key.value)

			self._skip(node.key)

			self._write(" = ")
		else:
			self._write("[")

			self._visit(node.key)

			self._write("] = ")

		self._visit(node.value)

	# visit_array_record is a passthough

	# ##

	def visit_assignment(self, node):
		is_local = node.type == node.T_LOCAL_DEFINITION

		dsts = node.destinations.contents
		srcs = node.expressions.contents

		if len(dsts) == 1 and len(srcs) == 1:
			dst = dsts[0]
			src = srcs[0]

			src_is_function = isinstance(src, nodes.FunctionDefinition)
			dst_is_simple = self._is_variable(dst)

			if src_is_function and dst_is_simple:
				self._state().function_name = dst
				self._state().function_local = is_local

				self._visit(src)

				self._skip(node.destinations)
				self._skip(node.expressions)

				return

		if is_local:
			self._write("local ")

		self._start_statement(STATEMENT_ASSIGNMENT)

		self._visit(node.destinations)

		self._write(" = ")

		self._visit(node.expressions)

		self._end_statement(STATEMENT_ASSIGNMENT)

	def _is_variable(self, node):
		if isinstance(node, nodes.Identifier):
			return True

		return self._is_global(node)

	def _is_global(self, node):
		if isinstance(node, nodes.TableElement):
			return self._is_builtin(node.table)

		return False

	def _is_builtin(self, node):
		if not isinstance(node, nodes.Identifier):
			return False

		return node.type == nodes.Identifier.T_BUILTIN

	def _is_valid_name(self, key):
		if not isinstance(key, nodes.Constant) or key.type != key.T_STRING:
			return False

		return VALID_IDENTIFIER.match(key.value)

	# ##

	def visit_binary_operator(self, node):
		is_left_op = isinstance(node.left, OPERATOR_TYPES)
		is_right_op = isinstance(node.right, OPERATOR_TYPES)

		# If the subexpressions are less in order then this expression,
		# they should go with parentheses

		left_parentheses = False
		right_parentheses = False

		binop = nodes.BinaryOperator

		if is_left_op:
			if node.type <= binop.T_LOGICAL_AND:
				left_parentheses = (
					node.left.type <= node.type
					or (node.left.type <= binop.T_LOGICAL_AND
						and node.type <= binop.T_LOGICAL_AND)
				) and node.left.type != node.type
			else:
				left_parentheses = node.left.type < node.type

		if is_right_op:
			if node.type <= nodes.BinaryOperator.T_LOGICAL_AND:
				right_parentheses = (
					node.right.type <= node.type
					or (node.right.type <= binop.T_LOGICAL_AND
						and node.type <= binop.T_LOGICAL_AND)
				) and node.right.type != node.type
			else:
				right_parentheses = node.right.type < node.type

		if left_parentheses:
			self._write("(")

		self._visit(node.left)

		if left_parentheses:
			self._write(")")

		if node.type == nodes.BinaryOperator.T_LOGICAL_OR:
			self._write(" or ")
		elif node.type == nodes.BinaryOperator.T_LOGICAL_AND:
			self._write(" and ")

		elif node.type == nodes.BinaryOperator.T_LESS_THEN:
			self._write(" < ")
		elif node.type == nodes.BinaryOperator.T_GREATER_THEN:
			self._write(" > ")
		elif node.type == nodes.BinaryOperator.T_LESS_OR_EQUAL:
			self._write(" <= ")
		elif node.type == nodes.BinaryOperator.T_GREATER_OR_EQUAL:
			self._write(" >= ")

		elif node.type == nodes.BinaryOperator.T_NOT_EQUAL:
			self._write(" ~= ")
		elif node.type == nodes.BinaryOperator.T_EQUAL:
			self._write(" == ")

		elif node.type == nodes.BinaryOperator.T_CONCAT:
			self._write(" .. ")

		elif node.type == nodes.BinaryOperator.T_ADD:
			self._write(" + ")
		elif node.type == nodes.BinaryOperator.T_SUBTRACT:
			self._write(" - ")

		elif node.type == nodes.BinaryOperator.T_DIVISION:
			self._write("/")
		elif node.type == nodes.BinaryOperator.T_MULTIPLY:
			self._write("*")
		elif node.type == nodes.BinaryOperator.T_MOD:
			self._write("%")

		else:
			assert node.type == nodes.BinaryOperator.T_POW
			self._write("^")

		if right_parentheses:
			self._write("(")

		self._visit(node.right)

		if right_parentheses:
			self._write(")")

	def visit_unary_operator(self, node):
		if node.type == nodes.UnaryOperator.T_LENGTH_OPERATOR:
			self._write("#")
		elif node.type == nodes.UnaryOperator.T_MINUS:
			self._write("-")
		elif node.type == nodes.UnaryOperator.T_NOT:
			self._write("not ")

		has_subexp = isinstance(node.operand, OPERATOR_TYPES)
		need_parentheses = has_subexp and node.operand.type < node.type

		if need_parentheses:
			self._write("(")

		self._visit(node.operand)

		if need_parentheses:
			self._write(")")

	# ##

	def visit_statements_list(self, node):
		if len(self._states) > 1:
			self._start_block()

		self._push_state()

	def leave_statements_list(self, node):
		self._pop_state()

		if len(self._states) > 1:
			self._end_block()

	def _visit_comma_separated_list(self, node):
		if node.contents == []:
			return

		for subnode in node.contents[:-1]:
			self._visit(subnode)
			self._write(", ")

		self._visit(node.contents[-1])

	visit_identifiers_list = _visit_comma_separated_list

	def visit_records_list(self, node):
		if node.contents == []:
			return

		for subnode in node.contents[:-1]:
			self._visit(subnode)

			self._write(",")
			self._end_line()

		self._visit(node.contents[-1])
		self._end_line()

	visit_variables_list = _visit_comma_separated_list
	visit_expressions_list = _visit_comma_separated_list

	# ##

	def visit_identifier(self, node):
		if node.type == nodes.Identifier.T_SLOT:
			self._write("slot{0}", node.slot)
		else:
			self._write(node.name)

	def visit_multres(self, node):
		self._write("MULTRES")

	def visit_table_element(self, node):
		key = node.key
		base = node.table

		is_valid_name = self._is_valid_name(key)

		if self._is_global(node):
			assert is_valid_name

			self._skip(base)
			self._skip(key)

			self._write(key.value)

			return

		base_is_constructor = isinstance(base, nodes.TableConstructor)

		if not base_is_constructor and is_valid_name:
			self._visit(base)
			self._write(".")

			self._write(key.value)
			self._skip(key)
		else:
			if base_is_constructor:
				self._write("(")

			self._visit(base)

			if base_is_constructor:
				self._write(")")

			self._write("[")

			self._visit(key)

			self._write("]")

	def visit_vararg(self, node):
		self._write("...")

	def visit_function_call(self, node):
		is_statement = self._state().current_statement == STATEMENT_NONE

		if is_statement:
			self._start_statement(STATEMENT_FUNCTION_CALL)

		# We are going to modify this list so we can remove the first
		# argument
		args = node.arguments.contents
		is_method = False

		if len(args) > 0 and isinstance(node.function, nodes.TableElement):
			table = node.function.table

			first_arg = node.arguments.contents[0]

			if self._is_valid_name(node.function.key):
				is_method = table == first_arg

		if is_method:
			self._visit(node.function.table)
			self._write(":")
			self._write(node.function.key.value)

			self._skip(node.function)

			args.pop(0)

			self._write("(")
			self._visit(node.arguments)
			self._write(")")

			self._skip(node.arguments)
		else:
			self._visit(node.function)

			self._write("(")
			self._visit(node.arguments)
			self._write(")")

		if is_statement:
			self._end_statement(STATEMENT_FUNCTION_CALL)

	# ##

	def visit_if(self, node):
		self._start_statement(STATEMENT_IF)

		self._write("if ")

		self._visit(node.expression)

		self._write(" then")

		self._end_line()

		self._visit(node.then_block)

		self._visit_list(node.elseifs)

		if len(node.else_block.contents) > 0:
			self._write("else")

			self._end_line()

			self._visit(node.else_block)
		else:
			self._skip(node.else_block)

		self._write("end")

		self._end_statement(STATEMENT_IF)

	def visit_elseif(self, node):
		self._write("elseif ")

		self._visit(node.expression)

		self._write(" then")

		self._end_line()

		self._visit(node.then_block)

	# ##

	def visit_block(self, node):
		self._write("--- BLOCK #{0} {1}-{2}, warpins: {3} ---",
					node.index,
					node.first_address, node.last_address,
					node.warpins_count)

		self._end_line()

		self._visit_list(node.contents)

		self._write("--- END OF BLOCK #{0} ---", node.index)

		self._end_line()

		self._end_line()
		self._visit(node.warp)
		self._end_line()

		self._end_line()

	def visit_unconditional_warp(self, node):
		if node.type == nodes.UnconditionalWarp.T_FLOW:
			self._write("FLOW")
		elif node.type == nodes.UnconditionalWarp.T_JUMP:
			self._write("UNCONDITIONAL JUMP")

		self._write("; TARGET BLOCK #{0}", node.target.index)

		self._end_line()

	def visit_conditional_warp(self, node):
		if hasattr(node, "_slot"):
			self._write("slot" + str(node._slot))
			self._write(" = ")

		self._write("if ")

		self._visit(node.condition)

		self._write(" then")
		self._end_line()

		self._write("JUMP TO BLOCK #{0}", node.true_target.index)

		self._end_line()
		self._write("else")
		self._end_line()

		self._write("JUMP TO BLOCK #{0}", node.false_target.index)

		self._end_line()

		self._write("end")
		self._end_line()

	def visit_iterator_warp(self, node):
		self._write("for ")

		self._visit(node.variables)

		self._write(" in ")

		self._visit(node.controls)

		self._end_line()
		self._write("LOOP BLOCK #{0}", node.body.index)

		self._end_line()
		self._write("GO OUT TO BLOCK #{0}", node.way_out.index)

		self._end_line()

	def visit_numeric_loop_warp(self, node):
		self._write("for ")

		self._visit(node.index)

		self._write("=")

		self._visit(node.controls)

		self._end_line()
		self._write("LOOP BLOCK #{0}", node.body.index)

		self._end_line()
		self._write("GO OUT TO BLOCK #{0}", node.way_out.index)

	# ##

	def visit_return(self, node):
		self._start_statement(STATEMENT_RETURN)

		self._write("return ")

		self._visit(node.returns)

		self._end_statement(STATEMENT_RETURN)

	def visit_break(self, node):
		self._start_statement(STATEMENT_BREAK)

		self._write("break")

		self._end_statement(STATEMENT_BREAK)

	# ##

	def visit_while(self, node):
		self._start_statement(STATEMENT_WHILE)

		self._write("while ")
		self._visit(node.expression)
		self._write(" do")

		self._end_line()

		self._visit(node.statements)

		self._write("end")
		self._end_statement(STATEMENT_WHILE)

	def visit_repeat_until(self, node):
		self._start_statement(STATEMENT_REPEAT_UNTIL)

		self._write("repeat")
		self._end_line()

		self._visit(node.statements)

		self._write("until ")
		self._visit(node.expression)

		self._end_statement(STATEMENT_REPEAT_UNTIL)

	def visit_numeric_for(self, node):
		self._start_statement(STATEMENT_NUMERIC_FOR)

		self._write("for ")
		self._visit(node.variable)
		self._write(" = ")

		self._visit(node.expressions)

		self._write(" do")

		self._end_line()

		self._visit(node.statements)

		self._write("end")
		self._end_statement(STATEMENT_NUMERIC_FOR)

	def visit_iterator_for(self, node):
		self._start_statement(STATEMENT_ITERATOR_FOR)

		self._write("for ")
		self._visit(node.identifiers)
		self._write(" in ")
		self._visit(node.expressions)
		self._write(" do")

		self._end_line()

		self._visit(node.statements)

		self._write("end")
		self._end_statement(STATEMENT_ITERATOR_FOR)

	# ##

	def visit_constant(self, node):
		if node.type != nodes.Constant.T_STRING:
			self._write(node.value)
			return

		lines = node.value.count("\n")

		if lines > 2:
			self._write("[[")

			self._write("\n")

			self._write(node.value)

			self._write("]]")
		else:
			text = node.value

			text = text.replace("\\", "\\\\")
			text = text.replace("\t", "\\t")
			text = text.replace("\n", "\\n")
			text = text.replace("\r", "\\r")
			text = text.replace("\"", "\\\"")

			self._write('"' + text + '"')

	def visit_primitive(self, node):
		if node.type == nodes.Primitive.T_FALSE:
			self._write("false")
		elif node.type == nodes.Primitive.T_TRUE:
			self._write("true")
		else:
			self._write("nil")

	def _skip(self, node):
		self._visited_nodes[-1].add(node)

	def _visit(self, node):
		assert node is not None

		if node in self._visited_nodes[-1]:
			return

		self._visited_nodes[-1].add(node)

		# TODO: add check
		# "It looks like you forgot about some node changes..."

		self._visited_nodes.append(set())

		traverse.Visitor._visit(self, node)

		self._visited_nodes.pop()


def write(fd, ast):
	assert isinstance(ast, nodes.FunctionDefinition)

	visitor = Visitor()

	traverse.traverse(visitor, ast.statements)

	_process_queue(fd, visitor.print_queue)


def _get_next_significant(queue, i):
	i += 1

	while i < len(queue):
		cmd = queue[i]

		if cmd[0] not in (CMD_END_LINE, CMD_WRITE):
			break

		i += 1

	if i < len(queue):
		return queue[i]
	else:
		return (CMD_END_BLOCK,)


def _process_queue(fd, queue):
	indent = 0

	line_broken = True

	for i, cmd in enumerate(queue):
		assert isinstance(cmd, tuple)

		if cmd[0] == CMD_START_STATEMENT:
			# assert line_broken
			pass
		elif cmd[0] == CMD_END_STATEMENT:
			fd.write("\n")
			line_broken = True

			next_cmd = _get_next_significant(queue, i)

			if next_cmd[0] not in (CMD_END_BLOCK, CMD_START_BLOCK):
				assert next_cmd[0] == CMD_START_STATEMENT

				if next_cmd[1] != cmd[1]			\
						or cmd[1] >= STATEMENT_IF	\
						or next_cmd[1] >= STATEMENT_IF:
					fd.write("\n")
		elif cmd[0] == CMD_END_LINE:
			fd.write("\n")
			line_broken = True
		elif cmd[0] == CMD_START_BLOCK:
			indent += 1
		elif cmd[0] == CMD_END_BLOCK:
			indent -= 1

			assert indent >= 0
		else:
			assert cmd[0] == CMD_WRITE

			if line_broken:
				fd.write(indent * '\t')
				line_broken = False

			_id, fmt, args, kargs = cmd

			if len(args) + len(kargs) > 0:
				text = fmt.format(*args, **kargs)
			elif isinstance(fmt, str):
				text = fmt
			else:
				text = str(fmt)

			fd.write(text)
