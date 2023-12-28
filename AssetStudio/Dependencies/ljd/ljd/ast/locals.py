#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#


import ljd.ast.nodes as nodes
import ljd.ast.traverse as traverse


def mark_locals(ast):
	traverse.traverse(_LocalsMarker(), ast)


def mark_local_definitions(ast):
	traverse.traverse(_LocalDefinitionsMarker(), ast)


class _LocalsMarker(traverse.Visitor):
	class _State():
		def __init__(self):
			self.pending_slots = {}
			self.debuginfo = None
			self.addr = -1

	def __init__(self):
		self._states = []

	# ##

	def _push_state(self):
		self._states.append(_LocalsMarker._State())

	def _pop_state(self):
		self._states.pop()

	def _state(self):
		return self._states[-1]

	def _process_slots(self, addr):
		debuginfo = self._state().debuginfo

		cleanup = []

		for slot, nodes in self._state().pending_slots.items():
			varinfo = debuginfo.lookup_local_name(addr, slot)

			if varinfo is None:
				continue

			cleanup.append(slot)

			if varinfo.type == varinfo.T_INTERNAL:
				continue

			for node in nodes:
				node.name = varinfo.name
				node.type = node.T_LOCAL

                #zzw.20180712
				setattr(node, "_varinfo", varinfo)

		for slot in cleanup:
			del self._state().pending_slots[slot]

	def _reset_slot(self, slot):
		self._state().pending_slots.pop(slot, None)

	def _reset_all(self, slots):
		for slot in slots:
			if isinstance(slot, nodes.Identifier):
				self._reset_slot(slot.slot)

	# ##

	def visit_function_definition(self, node):
		self._push_state()
		self._state().debuginfo = node._debuginfo

	def leave_function_definition(self, node):
		addr = node._instructions_count
		self._process_slots(addr)

		self._pop_state()

	# ##

	def visit_variables_list(self, node):
		# Last chance for a local = local + 1 type assignments
		self._process_slots(self._state().addr)
		self._reset_all(node.contents)

	def visit_identifiers_list(self, node):
		self._reset_all(node.contents)

	def visit_numeric_loop_warp(self, node):
		self._reset_slot(node.index.slot)

	def visit_identifier(self, node):
		if node.type == nodes.Identifier.T_SLOT:
			queue = self._state().pending_slots
			slots = queue.setdefault(node.slot, [])

			slots.append(node)

	# ##

	def _process_worthy_node(self, node):
		addr = getattr(node, "_addr", None)

		if not isinstance(node, nodes.Identifier) and addr is not None:
			assert self._state().addr <= addr
			self._state().addr = addr
			self._process_slots(addr)

	# We need to process slots twice as it could be the last
	# statement in the function/block and it could be anassignment
	# as well so we need to process slots before the reset

	def _leave_node(self, handler, node):
		traverse.Visitor._leave_node(self, handler, node)

		self._process_worthy_node(node)

	def _visit_node(self, handler, node):
		self._process_worthy_node(node)

		traverse.Visitor._visit_node(self, handler, node)


class _LocalDefinitionsMarker(traverse.Visitor):
	class _State():
		def __init__(self):
			self.known_locals = [None] * 255
			self.addr = 0

	def __init__(self):
		self._states = []

	def _push_state(self):
		self._states.append(_LocalDefinitionsMarker._State())

	def _pop_state(self):
		self._states.pop()

	def _state(self):
		return self._states[-1]

	def _update_known_locals(self, local, addr):
		varinfo = self._state().known_locals[local.slot]
		#zzw 20180712
		self._state().known_locals[local.slot] = getattr(local, "_varinfo", None)#local._varinfo

		if varinfo is None:
			return False

		if varinfo.end_addr <= addr:
			return False

		return True

	# ##

	def visit_function_definition(self, node):
		self._push_state()

		for local in node.arguments.contents:
			if not isinstance(local, nodes.Vararg):
				self._update_known_locals(local, 1)

	def leave_function_definition(self, node):
		self._pop_state()

	def visit_iterator_for(self, node):
		addr = node._addr

		for local in node.identifiers.contents:
			if local.type == nodes.Identifier.T_LOCAL:
				self._update_known_locals(local, addr)

	def visit_numeric_for(self, node):
		addr = node._addr

		if node.variable.type == nodes.Identifier.T_LOCAL:
			self._update_known_locals(node.variable, addr)

	# ##

	def visit_assignment(self, node):
		dst = node.destinations.contents[0]
		addr = self._state().addr

		if not isinstance(dst, nodes.Identifier):
			return

		if dst.type != nodes.Identifier.T_LOCAL:
			return

		known_slot = self._update_known_locals(dst, addr)

		for slot in node.destinations.contents[1:]:
			if not isinstance(slot, nodes.Identifier):
				return

			if slot.type != nodes.Identifier.T_LOCAL:
				return

			also_known = self._update_known_locals(slot, addr)

			assert known_slot == also_known

		if not known_slot:
			node.type = nodes.Assignment.T_LOCAL_DEFINITION

	def _visit(self, node):
		node_addr = getattr(node, "_addr", -1)

		if node_addr >= 0:
			self._state().addr = node_addr

		traverse.Visitor._visit(self, node)
