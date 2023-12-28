#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

import ljd.ast.nodes as nodes
import ljd.ast.traverse as traverse
from ljd.ast.helpers import insert_table_record


def eliminate_temporary(ast):
	_eliminate_multres(ast)

	slots, unused = _collect_slots(ast)
	_eliminate_temporary(slots)

	# _remove_unused(unused)

	_cleanup_invalid_nodes(ast)

	return ast


def _eliminate_temporary(slots):
	simple = []
	massive = []
	tables = []
	iterators = []

	for info in slots:
		assignment = info.assignment

		if not isinstance(assignment, nodes.Assignment):
			assert isinstance(assignment, (nodes.IteratorWarp,
							nodes.NumericLoopWarp,
							nodes.FunctionDefinition))

			src = info.references[1].identifier
			simple.append((info.references, src))
			continue

		assert len(assignment.expressions.contents) == 1

		is_massive = len(assignment.destinations.contents) > 1

		if is_massive:
			_fill_massive_refs(info, simple, massive, iterators)
		else:
			_fill_simple_refs(info, simple, tables)

	_eliminate_simple_cases(simple)
	_eliminate_into_table_constructors(tables)
	_eliminate_mass_assignments(massive)
	_eliminate_iterators(iterators)


def _fill_massive_refs(info, simple, massive, iterators):
	ref = info.references[1]
	holder = _get_holder(ref.path)

	src = info.assignment.expressions.contents[0]

	assert isinstance(src, (nodes.FunctionCall,
				nodes.Vararg,
				nodes.Primitive))
	if isinstance(holder, nodes.Assignment):
		dst = holder.destinations.contents[0]

		#assert len(info.references) == 2
		orig = info.references[0].identifier

		assignment = ref.path[-3]

		assert isinstance(assignment, nodes.Assignment)

		massive.append((orig, info.assignment, assignment, dst))
	elif isinstance(holder, nodes.IteratorWarp):
		assert len(info.references) == 2
		iterators.append((info.assignment, src, holder))
	elif isinstance(src, nodes.Primitive) and src.type == src.T_NIL:
		#assert len(info.references) == 2

		# Create a new primitive, so it won't mess with the
		# writer's ignore list
		src = nodes.Primitive()
		src.type = nodes.Primitive.T_NIL

		simple.append((info, ref, src))


def _fill_simple_refs(info, simple, tables):
	src = info.assignment.expressions.contents[0]

	if isinstance(src, nodes.FunctionCall) and len(info.references) > 3:
		return

	src_is_table = isinstance(src, nodes.TableConstructor)

	for ref in info.references[1:]:
		holder = _get_holder(ref.path)

		is_element = isinstance(holder, nodes.TableElement)

		path_index = ref.path.index(holder)

		statement = _get_holder(ref.path[:path_index])

		statement_is_assignment = isinstance(statement, nodes.Assignment)

		if statement_is_assignment:
			is_dst = statement.destinations.contents[0] == holder
		else:
			is_dst = False

		# Could be more then one reference here
		if src_is_table and is_element and is_dst:
			#assert holder.table == ref.identifier
			tables.append((info, ref))
		else:
			simple.append((info, ref, None))


LIST_TYPES = (nodes.VariablesList,
		nodes.IdentifiersList,
		nodes.ExpressionsList,
		nodes.StatementsList)


def _get_holder(path):
	for node in reversed(path[:-1]):
		if not isinstance(node, LIST_TYPES):
			return node

	return None


def _eliminate_simple_cases(simple):
	for info, ref, src in simple:
		holder = ref.path[-2]
		dst = ref.identifier

		if src is None:
			src = info.assignment.expressions.contents[0]

		_mark_invalidated(info.assignment)

		if isinstance(holder, LIST_TYPES):
			nodes = holder.contents
			found = _replace_node_in_list(nodes, dst, src)
		else:
			found = _replace_node(holder, dst, src)

		if found == None:
			print("err: slotworks.py assert found")


def _eliminate_into_table_constructors(tables):
	for info, ref in tables:
		constructor = info.assignment.expressions.contents[0]
		table_element = ref.path[-2]
		assignment = ref.path[-4]

		assert isinstance(assignment, nodes.Assignment)

		assert len(assignment.expressions.contents) == 1

		_mark_invalidated(assignment)

		key = table_element.key
		value = assignment.expressions.contents[0]

		insert_table_record(constructor, key, value)


def _eliminate_mass_assignments(massive):
	for identifier, assignment, base_assignment, globalvar in massive:
		destinations = assignment.destinations.contents
		found = _replace_node_in_list(destinations, identifier, globalvar)

		_mark_invalidated(base_assignment)

		assert found


def _replace_node(holder, original, replacement):
	for key, value in holder.__dict__.items():
		if value == original:
			setattr(holder, key, replacement)
			return True

	return False


def _replace_node_in_list(nodes, original, replacement):
	try:
		index = nodes.index(original)
	except ValueError:
		return False

	nodes[index] = replacement
	return True


def _eliminate_iterators(iterators):
	processed_warps = set()

	for assignment, src, warp in iterators:
		if warp in processed_warps:
			continue

		for i, slot in enumerate(assignment.destinations.contents):
			if hasattr(warp.controls.contents[i], 'slot') and hasattr(slot, 'slot'):
				#assert warp.controls.contents[i].slot == slot.slot
				if warp.controls.contents[i].slot != slot.slot:
					print ("err: slotworks.py assert warp.controls.contents[i].slot == slot.slot")

		warp.controls.contents = [src]
		processed_warps.add(warp)

		_mark_invalidated(assignment)


def _mark_invalidated(node):
	setattr(node, "_invalidated", True)


def _is_invalidated(node):
	return getattr(node, "_invalidated", False)


def _remove_unused(unused):
	pass


def _collect_slots(ast):
	collector = _SlotsCollector()
	traverse.traverse(collector, ast)

	return collector.slots, collector.unused


def _eliminate_multres(ast):
	traverse.traverse(_MultresEliminator(), ast)
	_cleanup_invalid_nodes(ast)


class _MultresEliminator(traverse.Visitor):
	def __init__(self):
		self._last_multres_value = None

	def leave_assignment(self, node):
		src = node.expressions.contents[0]
		dst = node.destinations.contents[0]

		if isinstance(dst, nodes.MULTRES):
			assert len(node.destinations.contents) == 1
			assert len(node.expressions.contents) == 1

			assert isinstance(src, (nodes.FunctionCall, nodes.Vararg))

			assert self._last_multres_value is None

			self._last_multres_value = src

			_mark_invalidated(node)
		else:
			for i, src in enumerate(node.expressions.contents):
				if isinstance(src, nodes.MULTRES):
					break
			else:
				return

			assert self._last_multres_value is not None

			node.expressions.contents[i] = self._last_multres_value
			self._last_multres_value = None

	def _process_multres_in_list(self, nodes_list):
		for i, node in enumerate(nodes_list):
			if isinstance(node, nodes.MULTRES):
				break
		else:
			return

		assert self._last_multres_value is not None

		nodes_list[i] = self._last_multres_value
		self._last_multres_value = None

	def visit_function_call(self, node):
		self._process_multres_in_list(node.arguments.contents)

	def visit_return(self, node):
		self._process_multres_in_list(node.returns.contents)


class _SlotReference():
	def __init__(self):
		self.path = []
		self.identifier = None


class _SlotInfo():
	def __init__(self):
		self.slot = 0

		self.assignment = None
		self.references = []
		self.termination = None

		self.function = None


class _SlotsCollector(traverse.Visitor):
	class _State():
		def __init__(self):
			self.known_slots = {}
			self.function = None

	# ##

	def __init__(self):
		self._states = []
		self._path = []
		self._skip = None

		self.slots = []
		self.unused = []

		self._push_state()

	# ##

	def _state(self):
		return self._states[-1]

	def _push_state(self):
		self._states.append(_SlotsCollector._State())

	def _pop_state(self):
		self._states.pop()

	def _commit_info(self, info):
		assert len(info.references) > 0

		if len(info.references) == 1:
			self.unused.append(info)
		else:
			self.slots.append(info)

	def _commit_slot(self, slot, node):
		info = self._state().known_slots.get(slot)

		if info is None:
			return

		info.termination = node

		del self._state().known_slots[slot]

		self._commit_info(info)

	def _register_slot(self, slot, node):
		self._commit_slot(slot, node)

		info = _SlotInfo()
		info.slot = slot
		info.assignment = node
		info.function = self._state().function

		self._state().known_slots[slot] = info

	def _register_all_slots(self, node, slots):
		for slot in slots:
			if not isinstance(slot, nodes.Identifier):
				continue

			if slot.type != nodes.Identifier.T_SLOT:
				continue

			self._register_slot(slot.slot, node)

	def _commit_all_slots(self, slots, node):
		for slot in slots:
			if not isinstance(slot, nodes.Identifier):
				continue

			self._commit_slot(slot.slot, node)

	def _register_slot_reference(self, slot, node):
		info = self._state().known_slots.get(slot)

		if info is None:
			return

		reference = _SlotReference()
		reference.identifier = node

		# Copy the list, but not contents
		reference.path = self._path[:]

		info.references.append(reference)

	# ##

	def visit_assignment(self, node):
		self._visit(node.expressions)
		self._skip = node.expressions

		self._register_all_slots(node, node.destinations.contents)

	def leave_assignment(self, node):
		self._skip = None

	def visit_identifier(self, node):
		if node.type == nodes.Identifier.T_SLOT:
			self._register_slot_reference(node.slot, node)

	# ##

	def visit_function_definition(self, node):
		self._push_state()
		self._state().function = node

	def leave_function_definition(self, node):
		self._pop_state()

	def leave_block(self, node):
		for info in self._state().known_slots.values():
			self._commit_info(info)

		self._state().known_slots = {}

	def visit_iterator_warp(self, node):
		self._commit_all_slots(node.variables.contents, node)

	def visit_numeric_loop_warp(self, node):
		self._commit_slot(node.index.slot, node)

	# ##

	def _visit_node(self, handler, node):
		self._path.append(node)

		traverse.Visitor._visit_node(self, handler, node)

	def _leave_node(self, handler, node):
		self._path.pop()

		traverse.Visitor._leave_node(self, handler, node)

	def _visit(self, node):
		if self._skip == node:
			return

		traverse.Visitor._visit(self, node)


def _cleanup_invalid_nodes(ast):
	traverse.traverse(_TreeCleanup(), ast)


class _TreeCleanup(traverse.Visitor):
	def visit_block(self, node):
		patched = []

		for subnode in node.contents:
			if not _is_invalidated(subnode):
				patched.append(subnode)

		node.contents = patched
