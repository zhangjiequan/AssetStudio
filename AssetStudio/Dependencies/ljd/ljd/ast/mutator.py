#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

import copy

from ljd.ast.helpers import *


class SimpleLoopWarpSwapper(traverse.Visitor):
	def visit_statements_list(self, node):
		blocks = node.contents

		fixed = []
		index_shift = 0

		for i, block in enumerate(node.contents):
			warp = block.warp
			fixed.append(block)

			block.index += index_shift

			if isinstance(warp, nodes.IteratorWarp):
				self._swap_iterator_warps(blocks, block)
				continue

			if isinstance(warp, nodes.NumericLoopWarp):
				self._swap_numeric_loop_warps(blocks, block)
				continue

			if isinstance(warp, nodes.UnconditionalWarp)	\
							and warp.is_uclo:
				assert block != node.contents[-1]
				next_block = node.contents[i + 1]
				self._fix_uclo_return(block, next_block)

			if not isinstance(warp, nodes.ConditionalWarp):
				continue

			if warp.true_target != warp.false_target:
				continue

			slot = getattr(warp, "_slot", -1)

			if slot < 0:
				continue

			next_index = block.index - index_shift + 1
			assert block.warp.false_target.index == next_index

			new_block = self._create_dummy_block(block, slot)

			fixed.append(new_block)

			index_shift += 1

		node.contents = fixed

	def _create_dummy_block(self, block, slot):
		new_block = nodes.Block()
		new_block.first_address = block.last_address
		new_block.last_address = new_block.first_address
		new_block.index = block.index + 1
		new_block.warpins_count = 1

		new_block.warp = nodes.UnconditionalWarp()
		new_block.warp.type = nodes.UnconditionalWarp.T_FLOW
		new_block.warp.target = block.warp.false_target

		statement = nodes.Assignment()

		identifier = nodes.Identifier()
		identifier.type = nodes.Identifier.T_SLOT
		identifier.slot = slot

		statement.destinations.contents.append(identifier)
		statement.expressions.contents.append(copy.copy(identifier))

		new_block.contents.append(statement)

		block.warp.true_target = new_block

		return new_block

	def _fix_uclo_return(self, block, next_block):
		warp = block.warp
		target = warp.target

		if len(target.contents) != 1:
			return

		statement = target.contents[0]

		if not isinstance(statement, nodes.Return):
			return

		block.contents.append(statement)
		statement._addr = block.last_address
		target.contents = []

		warp.type = nodes.UnconditionalWarp.T_FLOW
		warp.target = next_block

	def _swap_iterator_warps(self, blocks, end):
		warp = end.warp
		index = blocks.index(warp.body)

		assert index > 0

		start = blocks[index - 1]

		assert isinstance(start.warp, nodes.UnconditionalWarp)
		assert start.warp.type == nodes.UnconditionalWarp.T_JUMP
		assert start.warp.target == end

		end_addr = end.warp._addr
		start_addr = start.warp._addr

		new_end_warp = start.warp
		new_end_warp._addr = end_addr

		new_start_warp = end.warp
		new_start_warp._addr = start_addr

		end.warp = new_end_warp
		start.warp = new_start_warp

		new_end_warp.target = start

	def _swap_numeric_loop_warps(self, blocks, end):
		warp = end.warp
		index = blocks.index(warp.body)

		assert index > 0

		start = blocks[index - 1]

		assert isinstance(start.warp, nodes.UnconditionalWarp)
		assert start.warp.type == nodes.UnconditionalWarp.T_FLOW
		assert start.warp.target == warp.body

		end_addr = end.warp._addr
		start_addr = start.warp._addr

		new_end_warp = start.warp
		new_end_warp._addr = end_addr

		new_start_warp = end.warp
		new_start_warp._addr = start_addr

		end.warp = new_end_warp
		start.warp = new_start_warp

		new_end_warp.type = nodes.UnconditionalWarp.T_JUMP
		new_end_warp.target = start


class MutatorVisitor(traverse.Visitor):
	# ##

	def leave_if(self, node):
		if len(node.else_block.contents) != 1:
			return

		subif = node.else_block.contents[0]

		if not isinstance(subif, nodes.If):
			return

		elseif = nodes.ElseIf()
		elseif.expression = subif.expression
		elseif.then_block = subif.then_block

		node.elseifs.append(elseif)
		node.elseifs += subif.elseifs
		node.else_block = subif.else_block

	def visit_statements_list(self, node):
		patched = []

		i = -1

		while i < len(node.contents) - 1:
			i += 1
			statement = node.contents[i]

			patched.append(statement)

			if not isinstance(statement, nodes.Assignment):
				continue

			src = statement.expressions.contents[0]

			if not isinstance(src, nodes.TableConstructor):
				continue

			assert len(statement.destinations.contents) == 1

			dst = statement.destinations.contents[0]

			i += self._fill_constructor(dst, src, node.contents[i + 1:])

		node.contents = patched

	def _fill_constructor(self, table, constructor, statements):
		consumed = 0

		for statement in statements:
			if not isinstance(statement, nodes.Assignment):
				break

			if len(statement.destinations.contents) > 1:
				break

			dst = statement.destinations.contents[0]

			if not isinstance(dst, nodes.TableElement):
				break

			if not is_equal(dst.table, table):
				break

			assert len(statement.expressions.contents) == 1

			src = statement.expressions.contents[0]

			if has_same_table(src, table):
				break

			insert_table_record(constructor, dst.key, src)
			consumed += 1

		return consumed


def pre_pass(ast):
	traverse.traverse(SimpleLoopWarpSwapper(), ast)

	return ast


def primary_pass(ast):
	traverse.traverse(MutatorVisitor(), ast)

	return ast
