import ljd.ast.nodes as nodes
import ljd.ast.traverse as traverse


def insert_table_record(constructor, key, value):
	array = constructor.array.contents
	records = constructor.records.contents

	if isinstance(key, nodes.MULTRES):
		assert len(records) == 0 \
			or isinstance(records[-1], nodes.TableRecord)

		records.append(value)
		return

	while isinstance(key, nodes.Constant)			\
				and key.type == key.T_INTEGER	\
				and key.value >= 0:
		index = key.value

		if index == 1 and len(array) == 0:
			record = nodes.ArrayRecord()
			record.value = nodes.Primitive()
			record.value.type = nodes.Primitive.T_NIL

			array.append(record)

		if (index > len(array)):
			break

		record = nodes.ArrayRecord()
		record.value = value

		if len(array) == 0 or index == len(array):
			array.append(record)
		else:
			array[index] = record

		return

	record = nodes.TableRecord()
	record.key = key
	record.value = value

	if len(records) == 0:
		records.append(record)
		return

	last = records[-1]

	if isinstance(last, (nodes.FunctionCall, nodes.Vararg)):
		records.insert(-1, record)
	else:
		records.append(record)


def has_same_table(node, table):
	class Checker(traverse.Visitor):
		def __init__(self, table):
			self.found = False
			self.table = table

		def visit_table_element(self, node):
			if is_equal(self.table, node):
				self.found = True

		def _visit(self, node):
			if not self.found:
				traverse.Visitor._visit(self, node)

		def _visit_list(self, nodes_list):
			if not self.found:
				traverse.Visitor._visit_list(self, nodes_list)

	checker = Checker(table)
	traverse.traverse(checker, node)

	return checker.found


def is_equal(a, b):
	if type(a) != type(b):
		return False

	if isinstance(a, nodes.Identifier):
		return a.type == b.type and a.slot == b.slot
	elif isinstance(a, nodes.TableElement):
		return is_equal(a.table, b.table)		\
			and is_equal(a.key, b.key)
	else:
		assert isinstance(a, nodes.Constant)
		return a.type == b.type and a.value == b.value
