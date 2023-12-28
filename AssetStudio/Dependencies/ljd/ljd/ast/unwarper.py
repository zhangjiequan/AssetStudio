import copy

import ljd.ast.nodes as nodes
import ljd.ast.traverse as traverse
import ljd.ast.slotworks as slotworks

binop = nodes.BinaryOperator


# ##
# ## REMEMBER
# ##
# ## Block indices are unreliable while you are mangling them!
# ##
# ## P.S. Probably they should not be named indices... But they ARE used as indices during other phases. Sometimes.
# ## 
# ##


class _StatementsCollector(traverse.Visitor):
	def __init__(self):
		self.result = []

	def visit_statements_list(self, node):
		if len(node.contents) > 0:
			self.result.append(node)


def unwarp(node):
	# There could be many negative jumps within while conditions, so
	# filter them first
	_run_step(_unwarp_loops, node, repeat_until=False)

	_run_step(_unwarp_loops, node, repeat_until=True)
	_run_step(_unwarp_expressions, node)
	_run_step(_unwarp_ifs, node)

	_glue_flows(node)


def _run_step(step, node, **kargs):
	for statements in _gather_statements_lists(node):
		statements.contents = step(statements.contents, **kargs)

	# Fix block indices in case anything was moved
	for statements in _gather_statements_lists(node):
		for i, block in enumerate(statements.contents):
			block.index = i


def _gather_statements_lists(node):
	collector = _StatementsCollector()
	traverse.traverse(collector, node)
	return collector.result


def _glue_flows(node):
	for statements in _gather_statements_lists(node):
		blocks = statements.contents

		if hasattr(blocks[-1], 'warp'):
			assert isinstance(blocks[-1].warp, nodes.EndWarp)

			for i, block in enumerate(blocks[:-1]):
				warp = block.warp

				assert _is_flow(warp)

				target = warp.target

				assert target == blocks[i + 1]

				target.contents = block.contents + target.contents
				block.contents = []

			statements.contents = blocks[-1].contents


# ##
# ## IFs AND EXPRESSIONs PROCESSING
# ##

def _unwarp_expressions(blocks):
	pack = []
	pack_set = set()

	start_index = 0
	while start_index < len(blocks) - 1:
		start = blocks[start_index]
		warp = start.warp

		if isinstance(warp, nodes.UnconditionalWarp):
			if warp.type == nodes.UnconditionalWarp.T_FLOW:
				start_index += 1
				continue

		body, end, end_index = _extract_if_body(start_index,
							blocks, None)

		if body is None:
			raise NotImplementedError("GOTO statements are not"
								" supported")

		expressions = _find_expressions(start, body, end)

		assert pack_set.isdisjoint(expressions)

		expressions_set = set(expressions)

		assert len(expressions_set) == len(expressions)

		if len(expressions) == 0:
			start_index += 1
			continue

		pack += list(reversed(expressions))
		pack_set |= expressions_set

		endest_end = _find_endest_end(expressions)

		if endest_end != end:
			end_index = blocks.index(endest_end)

		start_index = end_index

	return _unwarp_expressions_pack(blocks, pack)


def _find_endest_end(expressions):
	endest_end = expressions[0][1]

	for _start, exp_end, _slot, _slot_type in expressions[1:]:
		if exp_end.index > endest_end.index:
			endest_end = exp_end

	return endest_end


def _unwarp_ifs(blocks, top_end=None, topmost_end=None):
	boundaries = []

	start_index = 0

	while start_index < len(blocks) - 1:
		start = blocks[start_index]
		warp = start.warp

		if isinstance(warp, nodes.UnconditionalWarp):
			if warp.type == nodes.UnconditionalWarp.T_FLOW:
				start_index += 1
				continue

		body, end, end_index = _extract_if_body(start_index,
							blocks, topmost_end)

		if body is None:
			raise NotImplementedError("GOTO statements are not"
								" supported")

		is_end = isinstance(body[-1].warp, nodes.EndWarp)

		_unwarp_if_statement(start, body, end, end)

		if is_end:
			_set_end(start)
		else:
			_set_flow_to(start, end)

		boundaries.append((start_index, end_index - 1))

		start_index = end_index

	return _remove_processed_blocks(blocks, boundaries)


def _extract_if_body(start_index, blocks, topmost_end):
	end = _find_branching_end(blocks[start_index:], topmost_end)

	try:
		end_index = blocks.index(end)
	except ValueError:
		if end == topmost_end:
			end_index = len(blocks)
		else:
			return None, None, None

	body = blocks[start_index + 1:end_index]

	return body, end, end_index


def _unwarp_expressions_pack(blocks, pack):
	replacements = {}

	for start, end, slot, slot_type in reversed(pack):
		end = replacements.get(end, end)

		start_index = blocks.index(start)
		end_index = blocks.index(end)

		body = blocks[start_index + 1:end_index]

		_unwarp_logical_expression(start, end, body)

		statements = start.contents + end.contents

		if slot_type == nodes.Identifier.T_SLOT:
			min_i = len(start.contents)
			split_i = _split_by_slot_use(statements, min_i,
							end.warp, slot)
		else:
			split_i = len(start.contents)

		max_i = len(statements)

		if split_i > max_i:
			end.contents = start.contents + end.contents
			start.contents = []

			blocks = blocks[:start_index] + blocks[end_index:]

			_replace_targets(blocks, start, end)

			replacements[start] = end

			slotworks.eliminate_temporary(end)

			_set_flow_to(start, end)
		else:
			blocks = blocks[:start_index + 1] + blocks[end_index:]

			start.contents = statements[:split_i]
			end.contents = statements[split_i:]

			# We need to kill the start's warp before slot
			# elimination or it could result in a cycled AST.
			_set_flow_to(start, end)

			slotworks.eliminate_temporary(start)

	return blocks


def _split_by_slot_use(statements, min_i, warp, slot):
	known_slots = set([slot])

	split_i = min_i

	for i, statement in enumerate(statements):
		if isinstance(statement, nodes.Assignment):
			sets = _extract_destination_slots(statement)

			if i < min_i:
				known_slots |= sets
			else:
				known_slots -= sets

			if len(known_slots) == 0:
				break

		split_i = i + 1

	if split_i < len(statements):
		return split_i

	if isinstance(warp, nodes.ConditionalWarp):
		known_slots -= _gather_slots(warp)

		if len(known_slots) == 0:
			split_i += 1

	return split_i


def _extract_destination_slots(statement):
	sets = set()

	for node in statement.destinations.contents:
		if not isinstance(node, nodes.Identifier):
			continue

		if node.type == nodes.Identifier.T_SLOT:
			sets.add(node.slot)

	return sets


def _gather_slots(node):
	class Collector(traverse.Visitor):
		def __init__(self):
			self.slots = set()

		def visit_identifier(self, node):
			if node.type == nodes.Identifier.T_SLOT:
				self.slots.add(node.slot)

	collector = Collector()

	traverse.traverse(collector, node)

	return collector.slots


def _find_expressions(start, body, end):
	# Explicitly allow the local a = x ~= "b" case
	slot, slot_type = _get_simple_local_assignment_slot(start, body, end)

	if slot >= 0:
		return [(start, end, slot, slot_type)]

	expressions = []

	# We have something at the end, but not the true/false?

	i = 0
	extbody = [start] + body

	is_local = False
	sure_expression = False

	while i < len(extbody):
		block = extbody[i]

		subs = _find_subexpressions(block, body[i:])

		if len(subs) != 0:
			endest_end = _find_endest_end(subs)
			new_i = extbody.index(endest_end)

			# Loop? No way!
			if new_i <= i:
				return expressions

			# It should end with a conditional warp if that's
			# really a subexpression-as-operand
			end_warp = endest_end.warp

			if not isinstance(end_warp, nodes.ConditionalWarp):
				return expressions

			expressions = subs + expressions
			i = new_i
			continue

		if isinstance(block.warp, nodes.ConditionalWarp):
			condition = block.warp.condition

			is_end = block.warp.false_target == end
			is_binop = isinstance(condition, nodes.BinaryOperator)
			block_slot = getattr(block.warp, "_slot", slot)

			if is_end:
				if is_binop:
					return expressions
				elif slot < 0 and block_slot >= 0:
					slot = block_slot
					slot_type = nodes.Identifier.T_SLOT
					sure_expression = True
				elif slot != block_slot:
					return expressions
				else:
					sure_expression = True
		elif isinstance(block.warp, nodes.UnconditionalWarp):
			if block == start and len(block.contents) == 0:
				return []

		if len(block.contents) == 0:
			i += 1
			continue

		if block != start and len(block.contents) > 1:
			return expressions

		assignment = block.contents[-1]

		if not isinstance(assignment, nodes.Assignment):
			if block == start:
				i += 1
				continue

			return expressions

		destinations = assignment.destinations.contents

		if len(destinations) != 1:
			if block == start:
				i += 1
				continue

			return expressions

		dst = destinations[0]

		if not isinstance(dst, nodes.Identifier):
			if block == start:
				i += 1
				continue

			return expressions

		if isinstance(block.warp, nodes.ConditionalWarp):
			if block == start:
				i += 1
				continue

			return expressions

		if slot < 0:
			# If all encounters are locals, which means
			# that the first encounter is a local
			if dst.type == nodes.Identifier.T_LOCAL:
				is_local = True
			elif dst.type == nodes.Identifier.T_UPVALUE:
				return []

			slot = dst.slot
			slot_type = dst.type
		elif slot == dst.slot:
			slot_type = dst.type

			if dst.type == nodes.Identifier.T_UPVALUE:
				return []
		else:
			assert block != start

			return []

		i += 1

	if slot < 0:
		return []

	true, _false, body = _get_terminators(body)

	if true is not None:
		sure_expression = True

	if len(expressions) > 0:
		sure_expression = True

	if not sure_expression and is_local:
		return expressions

	return expressions + [(start, end, slot, slot_type)]


def _find_subexpressions(start, body):
	try:
		body, end, _end_index = _extract_if_body(0, [start] + body, None)
	except ValueError:
		# a warp target is not in a list
		return []

	if body is None:
		return []

	return _find_expressions(start, body, end)


def _get_simple_local_assignment_slot(start, body, end):
	if len(body) != 2:
		return -1, None

	true, _false, body = _get_terminators(body)

	if true is None:
		return -1, None
	else:
		slot = true.contents[0].destinations.contents[0]
		return slot.slot, slot.type


def _find_expression_slot(body):
	slot = None

	for block in reversed(body):
		if len(block.contents) != 1:
			continue

		slot = block.contents[0].destinations.contents[0]
		break

	return slot


def _unwarp_logical_expression(start, end, body):
	slot = _find_expression_slot(body)

	assert slot is not None

	true, false, body = _get_terminators(body)

	expression = _compile_expression([start] + body, end, true, false)

	dst = copy.deepcopy(slot)

	assignment = nodes.Assignment()
	assignment.destinations.contents.append(dst)
	assignment.expressions.contents.append(expression)

	start.contents.append(assignment)


def _compile_expression(body, end, true, false):
	parts = _unwarp_expression(body, end, true, false)

	if len(parts) < 3:
		assert len(parts) == 1
		return parts[0]

	explicit_parts = _make_explicit_subexpressions(parts)
	return _assemble_expression(explicit_parts)


#
# The logical expressions:
#
# There are terminators: a true, a false and an end
#
# For an if case the true will be a "then" clause and the false - an "else" or
# "after-the-if" clause. The end is required for a single-variable (unary)
# components and is only used at during topmost phase.
#
# The last block in expression is always "double terminal" - both ends are
# pointing at terminators. It's rather useless so we just append it's condition
# (inverted if needed - it's easy to see if true end targets the false
# terminator) at the end of processing.
#
# Then we need to pack all other blocks into subexpressions. Subexpressions
# always end with a _terminal block_, i.e. the block which warp points to a
# terminator. Idea is that we can guess the operator only right of a
# terminal block, because we can check if the block's warp condition is
# inverted or not.
#
# If that's an "OR" clause then it will jump out of the current expression if
# the condition is true, so the condition is inverted and the false branch is
# pointing at the way out (at the TRUE terminator - because the result of the
# expression level will be true). (because in the bytecode there
# is only one JMP, so a ConditionalWarp's true branch is actually a fake and
# always points to the next block - in the bytecode a "positive" jump
# will be represented by a normal negative jump with inverted condition).
#
# Otherwise, if that's an "AND" clause then it will jump out of the current
# expression level if a condition is false, so the condition is not inverted
# and a false branch points to the false.
#
# This way we can understand which operators go just right of terminal blocks.
# Everything in-between these block is considered a subexpression. And just
# because we don't know where exactly the subexpression ends we are using
# greedy approach and trying to pack into a subexpression as much blocks as
# possible, including any terminal blocks pointing at the same terminator
# with the same inversion status (that is - we are always using the
# rightmost block if there are consequitive similar terminal blocks, ignoring
# all the blocks to the left).
#
# Then comes the trick: the subexpression is a component of this expression and
# we know the operator to the right of it. We can guess now what will
# be evaluated if the subexpression evaluates to "false" and what - if it's
# "true". If the operator is "AND" then the subexpression failure will cause
# the expression failure too, i.e. the "FALSE" target remains the same and the
# true terminator is set to the next block (after the "AND").
#
# If the operator is "OR" the the subexpression success will cause the success
# of the expression, so the "TRUE" target remains the same, but the false
# target is set to the next block (after the "OR").
#
# Now we have a subexpression and both TRUE and FALSE terminators for it.
# Recurse and repeat.
#
def _unwarp_expression(body, end, true, false):
	parts = []

	if true is not None:
		terminator_index = min(true.index, false.index)

		if end is not None:
			terminator_index = min(end.index, terminator_index)
	else:
		assert end is not None

		terminator_index = end.index

	terminators = set((true, false, end))

	subexpression_start = 0

	i = 0
	while i < len(body) - 1:
		block = body[i]
		warp = block.warp

		target = _get_target(warp)

		#
		# A chance for
		# (foo and (bar and y or z)) or x
		# type expressions, because the first "foo and ... )) or" part
		# will be broken by the "or z))" part in the code below.
		#
		# So we are going to intercept subexpressions by it's start
		# instead of an end, but only if we are already at the
		# subexpression start (so nothing formally changes, but creates
		# a bit more correct execution order)
		#
		if target.index < terminator_index:
			if i != subexpression_start:
				i += 1
				continue

			target_index = body.index(target)
			last_block = body[target_index - 1]

			last_block_target = _get_target(last_block.warp)

			if last_block_target.index < terminator_index:
				i += 1
				continue

			assert last_block_target in terminators

			subexpression = body[i:target_index]
		else:
			#assert target in terminators

			while i < len(body) - 2:
				next_block = body[i + 1]
				next_target = _get_target(next_block.warp)

				if next_target != target:
					break

				next_inv = _is_inverted(next_block.warp, true, end)

				this_inv = _is_inverted(warp, true, end)

				# Special hack for unary expressions (x, not x)...
				if next_inv != this_inv:
					break

				block = next_block
				warp = next_block.warp
				i += 1

			subexpression = body[subexpression_start:i + 1]

		last_block = subexpression[-1]
		last_block_index = body.index(last_block)

		next_block = body[last_block_index + 1]

		operator = _get_operator(last_block, true, end)

		subexpression = _compile_subexpression(subexpression, operator,
							last_block, next_block,
							true, end)

		parts.append(subexpression)
		parts.append(operator)

		i = last_block_index + 1
		subexpression_start = i

	last = body[-1]

	if isinstance(last.warp, nodes.ConditionalWarp):
		if _is_inverted(last.warp, true, end):
			last = _invert(last.warp.condition)
		else:
			last = last.warp.condition

		parts.append(last)
	else:
		assert isinstance(last.warp, (nodes.EndWarp,
						nodes.UnconditionalWarp))

		src = _get_last_assignment_source(last)

		if src is None:
			src = nodes.Primitive()

			if last.warp.target == true:
				src.type = nodes.Primitive.T_TRUE
			else:
				src.type = nodes.Primitive.T_FALSE

		parts.append(src)

	return parts


def _get_target(warp, allow_end=False):
	if isinstance(warp, nodes.ConditionalWarp):
		return warp.false_target
	else:
		if allow_end and isinstance(warp, nodes.EndWarp):
			return getattr(warp, "_target", None)

		assert isinstance(warp, nodes.UnconditionalWarp)
		return warp.target


def _set_target(warp, target):
	if isinstance(warp, nodes.ConditionalWarp):
		warp.false_target = target
	else:
		assert isinstance(warp, nodes.UnconditionalWarp)
		warp.target = target


def _get_operator(block, true, end):
	if isinstance(block.warp, nodes.UnconditionalWarp):
		src = _get_last_assignment_source(block)

		if isinstance(src, nodes.Constant):
			is_true = src.value != 0
		elif isinstance(src, nodes.BinaryOperator):
			is_true = True
		elif isinstance(src, nodes.Primitive):
			is_true = src.type == nodes.Primitive.T_TRUE
		elif isinstance(src, nodes.Identifier):
			is_true = True
		else:
			#assert src is None

			is_true = block.warp.target == true

		if is_true:
			return binop.T_LOGICAL_OR
		else:
			return binop.T_LOGICAL_AND
	else:
		is_inverted = _is_inverted(block.warp, true, end)

		if is_inverted:
			return binop.T_LOGICAL_OR
		else:
			return binop.T_LOGICAL_AND


def _get_last_assignment_source(block):
	if len(block.contents) == 0:
		return None

	assignment = block.contents[-1]
	#assert isinstance(assignment, nodes.Assignment)
	return assignment.expressions.contents[0]


def _get_and_remove_last_assignment_source(block):
	assignment = block.contents.pop()
	assert isinstance(assignment, nodes.Assignment)
	return assignment.expressions.contents[0]


def _compile_subexpression(subexpression, operator,
						block, next_block, true, end):
	warp = block.warp

	if len(subexpression) == 1:
		if isinstance(warp, nodes.UnconditionalWarp):
			return _get_and_remove_last_assignment_source(block)
		elif _is_inverted(warp, true, end):
			return _invert(warp.condition)
		else:
			return warp.condition
	else:
		if isinstance(warp, nodes.UnconditionalWarp):
			if operator == binop.T_LOGICAL_OR:
				subtrue = warp.target
				subfalse = next_block
			else:
				subtrue = next_block
				subfalse = warp.target
		else:
			if operator == binop.T_LOGICAL_OR:
				subtrue = warp.false_target
				subfalse = warp.true_target
			else:
				subtrue = warp.true_target
				subfalse = warp.false_target

		return _unwarp_expression(subexpression, None, subtrue, subfalse)


def _is_inverted(warp, true, end):
	if isinstance(warp, nodes.UnconditionalWarp):
		return warp.target == end

	if warp.false_target == true:
		return True
	elif warp.false_target == end:
		assert not isinstance(warp.condition, nodes.BinaryOperator)

		if not isinstance(warp.condition, nodes.UnaryOperator):
			return False

		return warp.condition.type == nodes.UnaryOperator.T_NOT

	return False


_NEGATION_MAP = [None] * 100

_NEGATION_MAP[binop.T_LESS_THEN] = binop.T_GREATER_OR_EQUAL
_NEGATION_MAP[binop.T_GREATER_THEN] = binop.T_LESS_OR_EQUAL
_NEGATION_MAP[binop.T_LESS_OR_EQUAL] = binop.T_GREATER_THEN
_NEGATION_MAP[binop.T_GREATER_OR_EQUAL] = binop.T_LESS_THEN

_NEGATION_MAP[binop.T_NOT_EQUAL] = binop.T_EQUAL
_NEGATION_MAP[binop.T_EQUAL] = binop.T_NOT_EQUAL


def _invert(expression):
	if isinstance(expression, nodes.UnaryOperator):
		return expression.operand

	if not isinstance(expression, nodes.BinaryOperator):
		node = nodes.UnaryOperator()
		node.type = nodes.UnaryOperator.T_NOT
		node.operand = expression

		return node

	# Just in case
	expression = copy.deepcopy(expression)

	new_type = _NEGATION_MAP[expression.type]

	assert new_type is not None

	expression.type = new_type

	return expression


def _get_terminators(body):
	if len(body) < 2:
		return None, None, body

	last = body[-1]

	if len(last.contents) != 1:
		return None, None, body

	assignment = last.contents[0]

	if not isinstance(assignment, nodes.Assignment):
		return None, None, body

	src = assignment.expressions.contents[0]

	if not isinstance(src, nodes.Primitive) or src.type != src.T_TRUE:
		return None, None, body

	prev = body[-2]

	if len(prev.contents) != 1:
		return None, None, body

	src = prev.contents[0].expressions.contents[0]

	if not isinstance(src, nodes.Primitive) or src.type != src.T_FALSE:
		return None, None, body

	return last, prev, body[:-2]


def _assemble_expression(parts):
	if not isinstance(parts, list):
		return parts

	node = nodes.BinaryOperator()
	node.left = _assemble_expression(parts[-3])

	node.type = parts[-2]
	assert isinstance(node.type, int)

	node.right = _assemble_expression(parts[-1])

	i = len(parts) - 4

	while i > 0:
		operator = parts[i]
		component = parts[i - 1]

		upper_node = nodes.BinaryOperator()
		upper_node.right = node
		upper_node.left = _assemble_expression(component)

		upper_node.type = operator

		node = upper_node

		i -= 2

	return node


# Split the topmost expression into smaller subexpressions at each
# operator change to simplify the assembly phase
def _make_explicit_subexpressions(parts):
	patched = []

	i = 0

	last_operator = parts[1]
	subexpression_start = -1

	while i < len(parts) - 1:
		component = parts[i]
		operator = parts[i + 1]

		if operator < last_operator:
			subexpression_start = i
			last_operator = operator
		elif subexpression_start > 0:
			if operator > last_operator				\
					and (i - subexpression_start) % 2 != 0:
				subexpression = parts[subexpression_start:i]

				patched.append(subexpression)
				subexpression_start = -1
		else:
			patched += [component, operator]

		i += 2

	if subexpression_start >= 0:
		patched.append(parts[subexpression_start:])
	else:
		patched.append(parts[-1])

	return patched


def _unwarp_if_statement(start, body, end, topmost_end):
	expression, body, false = _extract_if_expression(start, body, end,
								topmost_end)

	node = nodes.If()
	node.expression = expression

	# has an else branch
	if false != end and false != topmost_end:
		else_start = false

		else_start_index = body.index(else_start)

		then_body = body[:else_start_index]

		then_warp_out = then_body[-1].warp

		assert _is_jump(then_warp_out)
		assert then_warp_out.target in (end, topmost_end)

		else_body = body[else_start_index:]

		else_warp_out = else_body[-1].warp

		if isinstance(else_warp_out, nodes.UnconditionalWarp):
			if else_warp_out.type == nodes.UnconditionalWarp.T_JUMP:
				assert else_warp_out.target in (end, topmost_end)
			else:
				assert else_warp_out.target == end
		else:
			print ("err: unwarper.py assert isinstance(else_warp_out, nodes.EndWarp), Block indices are unreliable while you are mangling them! P.S. Probably they should not be named indices... But they ARE used as indices during other phases. Sometimes.")

		_set_end(then_body[-1])
		then_blocks = _unwarp_ifs(then_body, then_body[-1], topmost_end)
		node.then_block.contents = then_blocks

		_set_end(else_body[-1])
		else_blocks = _unwarp_ifs(else_body, else_body[-1], topmost_end)
		node.else_block.contents = else_blocks
	else:
		warp_out = body[-1].warp

		if not isinstance(warp_out, nodes.EndWarp):
			assert isinstance(warp_out, nodes.UnconditionalWarp)
			assert warp_out.target in (end, topmost_end)

		_set_end(body[-1])
		then_blocks = _unwarp_ifs(body, body[-1], topmost_end)
		node.then_block.contents = then_blocks

	start.contents.append(node)


def _extract_if_expression(start, body, end, topmost_end):
	for i, block in enumerate(body):
		if len(block.contents) != 0:
			break

	assert i < len(body)

	expression = [start] + body[:i]
	body = body[i:]

	falses = set()

	for i, block in enumerate(body[:-1]):
		if not isinstance(block.warp, nodes.UnconditionalWarp):
			continue

		if block.warp.type != nodes.UnconditionalWarp.T_JUMP:
			continue

		if block.warp.target != end and block.warp.target != topmost_end:
			continue

		falses.add(body[i + 1])

	falses.add(end)

	if topmost_end is not None:
		falses.add(topmost_end)

	false, end_i = _search_expression_end(expression, falses)

	assert end_i >= 0

	body = expression[end_i:] + body
	expression = expression[:end_i]

	assert len(expression) > 0

	true = body[0]

	expression = _compile_expression(expression, None, true, false)

	return expression, body, false


def _search_expression_end(expression, falses):
	expression_end = -1
	false = None

	for i, block in enumerate(expression):
		target = _get_target(block.warp)

		if target not in falses:
			continue

		if false is None or target == false:
			false = target
			expression_end = i + 1
		else:
			break

	assert false is not None

	return false, expression_end


def _find_branching_end(blocks, topmost_end):
	end = blocks[0]

	for block in blocks:
		warp = block.warp

		target = _get_target(warp, allow_end=True)

		if isinstance(warp, nodes.EndWarp) and target is None:
			assert block == end
			return block

		if isinstance(warp, nodes.UnconditionalWarp) and target == end:
			return end

		if target.index > end.index:
			end = target

	return end


def _remove_processed_blocks(blocks, boundaries):
	remains = []
	last_end_index = -1

	for start, end in boundaries:
		if start == end:
			up_to_index = start
		else:
			up_to_index = start + 1

		remains += blocks[last_end_index + 1:up_to_index]
		last_end_index = end

	remains += blocks[last_end_index + 1:]

	return remains


# ##
# ## LOOPS PROCESSING
# ##


def _unwarp_loops(blocks, repeat_until):
	loops = _find_all_loops(blocks, repeat_until)

	if len(loops) == 0:
		return blocks

	fixed = _cleanup_breaks_and_if_ends(loops, blocks)

	for start, end in fixed:
		start_index = blocks.index(start)
		end_index = blocks.index(end)

		if repeat_until:
			body = blocks[start_index:end_index]
		else:
			body = blocks[start_index + 1:end_index]

		loop = _unwarp_loop(start, end, body)
		body = loop.statements.contents

		block = nodes.Block()
		block.first_address = body[0].first_address
		block.last_address = body[-1].last_address
		block.index = start.index + 1
		block.contents.append(loop)

		block.warp = nodes.UnconditionalWarp()
		block.warp.type = nodes.UnconditionalWarp.T_FLOW
		block.warp.target = end

		_replace_targets(blocks, body[0], block)

		_set_end(body[-1])
		_unwarp_breaks(start, body, end)

		blocks = blocks[:start_index + 1] + [block] + blocks[end_index:]

	return blocks


def _cleanup_breaks_and_if_ends(loops, blocks):
	outer_start_index = -1
	outer_end = None

	current_start_index = -1
	current_end = None

	fixed = []

	for start, end in loops:
		if start.index in (outer_start_index, current_start_index):
			end_i = blocks.index(end)
			last_in_body = blocks[end_i - 1]
			warp = last_in_body.warp

			assert isinstance(warp, nodes.UnconditionalWarp)
			assert warp.target == start

			# Break
			if start.index == outer_start_index:
				assert outer_end is not None

				outer_end_i = blocks.index(outer_end)
				warp.target = blocks[outer_end_i - 1]

				assert blocks[outer_end_i - 2] != end
			else:
				assert current_end is not None
				assert start.index == current_start_index

				current_end_i = blocks.index(current_end)

				last = blocks[current_end_i - 1]

				if last == end:
					last = _create_next_block(end)
					last.warp = end.warp

					_set_flow_to(end, last)

					blocks.insert(current_end_i, last)

				warp.target = last
		else:
			fixed.append((start, end))

			if current_end is not None				\
					and current_start_index < start.index	\
					and current_end.index >= end.index:
				outer_start_index = current_start_index
				outer_end = current_end
			else:
				outer_start_index = -1
				outer_end = None

			current_start_index = start.index
			current_end = end

	return fixed


def _replace_targets(blocks, original, replacement):
	for block in blocks:
		warp = block.warp

		if isinstance(warp, nodes.UnconditionalWarp):
			if warp.target == original:
				warp.target = replacement
		elif isinstance(warp, nodes.ConditionalWarp):
			if warp.true_target == original:
				warp.true_target = replacement

			if warp.false_target == original:
				warp.false_target = replacement
		elif isinstance(warp, nodes.EndWarp):
			pass
		else:
			if warp.way_out == original:
				warp.way_out = replacement

			if warp.body == original:
				warp.body = replacement


def _unwarp_loop(start, end, body):
	if len(body) > 0:
		last = body[-1]
	else:
		last = start

	if isinstance(start.warp, nodes.IteratorWarp):
		assert isinstance(last.warp, nodes.UnconditionalWarp)
		assert last.warp.target == start

		loop = nodes.IteratorFor()
		loop.statements.contents = body
		loop.identifiers = start.warp.variables
		loop.expressions = start.warp.controls
		loop._addr = body[0].first_address

		_set_flow_to(start, body[0])

	elif isinstance(start.warp, nodes.NumericLoopWarp):
		assert isinstance(last.warp, nodes.UnconditionalWarp)
		assert last.warp.target == start

		loop = nodes.NumericFor()
		loop.statements.contents = body
		loop.variable = start.warp.index
		loop.expressions = start.warp.controls
		loop._addr = body[0].first_address
		_set_flow_to(start, body[0])

	# While (including "while true" and "repeat until false" which will be
	# while true)
	elif isinstance(last.warp, nodes.UnconditionalWarp):
		assert last.warp.target == start

		# while true
		if _is_flow(start.warp):
			loop = nodes.While()
			loop.expression = nodes.Primitive()
			loop.expression.type = nodes.Primitive.T_TRUE

			loop.statements.contents = body
		else:
			# There shouldn't be many problems similar to ifs, as
			# we are processing loops in the order from innermost
			# to outermost
			for i, block in enumerate(body):
				assert len(block.contents) == 0

				if _is_flow(block.warp):
					break

			assert i < len(body)

			expression = [start] + body[:i]
			body = body[i:]

			# Sometimes expression may decide to jump to the
			# outer loop start instead
			_fix_expression(expression, start, end)

			true = body[0]
			false = end

			expression = _compile_expression(expression, None,
								true, false)

			# If something jumps to the start (instead of the end)
			# - that's a nested if
			loop = nodes.While()
			loop.expression = expression
			loop.statements.contents = body

		_fix_nested_ifs(body, start)

		_set_flow_to(start, body[0])

	# Repeat until
	else:
		assert isinstance(last.warp, nodes.ConditionalWarp)
		assert last.warp.false_target == start

		i = len(body) - 1

		while i >= 0:
			block = body[i]
			warp = block.warp

			if _is_flow(warp):
				i += 1
				break

			if len(block.contents) != 0:
				break

			i -= 1

		expression = body[i:]
		body = body[:i + 1]

		assert len(expression) > 0

		first = expression[0]
		if _is_jump(first.warp):
			# Don't append to the body - it already has it
			expression.pop(0)
			body[-1].contents.append(nodes.Break())

		false = body[0]
		# Don't use end as it could be broken by a previous
		# repeat until pass
		true = expression[-1].warp.true_target

		loop = nodes.RepeatUntil()
		loop.expression = _compile_expression(expression, None,
								true, false)

		start_copy = copy.copy(start)
		start.contents = []

		if len(body) > 1:
			_set_flow_to(start_copy, body[1])
		else:
			_set_end(start_copy)

		_set_flow_to(start, start_copy)

		body[0] = start_copy

		loop.statements.contents = body

	return loop


def _create_next_block(original):
	block = nodes.Block()
	block.first_address = original.last_address + 1
	block.last_address = block.first_address
	block.index = original.index + 1
	block.warpins_count = original.warpins_count

	return block


def _set_flow_to(block, target):
	block.warp = nodes.UnconditionalWarp()
	block.warp.type = nodes.UnconditionalWarp.T_FLOW
	block.warp.target = target


def _set_end(block):
	target = None

	if block.warp is not None:
		target = _get_target(block.warp, allow_end=True)

	block.warp = nodes.EndWarp()

	setattr(block.warp, "_target", target)


def _is_flow(warp):
	return isinstance(warp, nodes.UnconditionalWarp)	\
		and warp.type == nodes.UnconditionalWarp.T_FLOW


def _is_jump(warp):
	return isinstance(warp, nodes.UnconditionalWarp)	\
		and warp.type == nodes.UnconditionalWarp.T_JUMP


def _fix_nested_ifs(blocks, start):
	# We can't point both targets of a conditional warp to the
	# same block. We will have to create a new block
	last = _create_next_block(blocks[-1])

	if isinstance(blocks[-1].warp, nodes.ConditionalWarp):
		blocks[-1].warp.false_target = last
	else:
		_set_flow_to(blocks[-1], last)

	blocks.append(last)
	_set_end(last)

	for block in blocks[:-1]:
		target = _get_target(block.warp)

		if target == start:
			_set_target(block.warp, last)


def _fix_expression(blocks, start, end):
	for block in blocks:
		if len(block.contents) != 0:
			break

		target = _get_target(block.warp)

		if target.index < start.index:
			_set_target(block.warp, end)


def _gather_possible_ends(block):
	warp = block.warp

	ends = set((block,))

	while _is_jump(warp):
		block = warp.target
		warp = block.warp

		ends.add(block)

	return ends


BREAK_INFINITE = 0
BREAK_ONE_USE = 1


def _unwarp_breaks(start, blocks, next_block):
	blocks_set = set([start] + blocks)

	ends = _gather_possible_ends(next_block)

	breaks = set()

	patched = []

	for i, block in enumerate(blocks):
		warp = block.warp

		if not isinstance(warp, nodes.UnconditionalWarp):
			patched.append(block)
			continue

		target = _get_target(warp)

		if target in blocks_set:
			patched.append(block)
			continue

		#assert target in ends, "GOTO statements are not supported"

		if block.warpins_count != 0:
			new_block = _create_next_block(block)
			new_block.warpins_count = block.warpins_count
			_set_flow_to(block, new_block)

			patched.append(block)
			patched.append(new_block)

			block = new_block
		else:
			patched.append(block)

		block.contents.append(nodes.Break())

		if i + 1 == len(blocks):
			_set_end(block)
		else:
			_set_flow_to(block, blocks[i + 1])

		breaks.add(block)

	blocks[:] = patched

	if len(breaks) == 0:
		return

	breaks_stack = []
	warpsout = []
	pending_break = None

	for i, block in enumerate(reversed(blocks)):
		if block in breaks:
			pending_break = None

			if block.warpins_count == 0:
				breaks_stack.append((BREAK_ONE_USE, block))
			else:
				breaks_stack.append((BREAK_INFINITE, block))

			continue

		warp = block.warp

		if not isinstance(warp, nodes.ConditionalWarp):
			if _is_flow(warp):
				pending_break = None

			continue

		target = _get_target(warp)

		if target in blocks_set:
			continue

		assert target in ends, "GOTO statements are not supported"

		if pending_break is None:
			assert len(breaks_stack) > 0

			top_break = breaks_stack[-1]

			_set_target(warp, top_break[1])

			if top_break[0] == BREAK_ONE_USE:
				pending_break = breaks_stack.pop()

				warpsout = []
			else:
				warpsout.append(block)
		else:
			_set_target(warp, pending_break[1])
			warpsout.append(block)

		if len(block.contents) > 0:
			pending_break = None

	while len(breaks_stack) > 0 and breaks_stack[-1][0] == BREAK_INFINITE:
		breaks_stack.pop()

	# And pray for the best...
	while len(warpsout) > 0 and len(breaks_stack) > 0:
		_set_target(warpsout.pop().warp, breaks_stack.pop()[1])


#
# We don't need any complex checks here.
#
# Just search for any negative jump - that's a loop and what it's jumping to is
# a loop start.
#
def _find_all_loops(blocks, repeat_until):
	# Duplicates are NOT possible
	loops = []

	i = 0

	while i < len(blocks):
		block = blocks[i]
		warp = block.warp

		if isinstance(warp, nodes.UnconditionalWarp):
			if warp.type == nodes.UnconditionalWarp.T_FLOW:
				i += 1
				continue

			if warp.target.index <= block.index:
				assert not repeat_until
				assert i < len(blocks) - 1
				loops.append((warp.target, blocks[i + 1]))

		elif repeat_until and isinstance(warp, nodes.ConditionalWarp):
			if warp.false_target.index > block.index:
				i += 1
				continue

			start = warp.false_target
			first = block
			end = block
			last_i = i

			# Find the end of the expression
			while i < len(blocks):
				block = blocks[i]
				warp = block.warp

				if block != first and len(block.contents) != 0:
					break

				if isinstance(warp, nodes.EndWarp):
					break

				# Go up to a first negative jump of an
				# another loop

				target = _get_target(warp)
				if target.index < block.index:
					if target == start:
						start = target
						end = block
						last_i = i
					else:
						break

				i += 1

			# And then rollback to the last known negative jump
			# of our loop
			i = last_i

			# There always should be at least one return block
			end_index = blocks.index(end)
			end = blocks[end_index + 1]

			loops.append((start, end))

		i += 1

	# Reverse the order so inner "while" loops are processed before
	# outer loops
	return list(reversed(sorted(loops, key=lambda x: x[0].index)))


def _get_previous_block(block, blocks):
	block_index = blocks.index(block)

	assert block_index > 0

	return blocks[block_index - 1]
