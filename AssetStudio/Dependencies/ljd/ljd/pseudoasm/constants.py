#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

import ljd.bytecode.constants


def write_tables(writer, prototype):
	i = 0

	for element in prototype.constants.complex_constants:
		if isinstance(element, ljd.bytecode.constants.Table):
			_write_table(writer, i, element)

		i += 1


def _write_table(writer, index, table):
	writer.stream.open_block("ktable#{0} = [", index)

	i = 0

	for element in table.array:
		if i != 0 or element is not None:
			text = _translate_element(element)

			writer.stream.write_line("#{0}: {1},", i, text)

		i += 1

	for key, value in table.dictionary:
		key = _translate_element(key)
		value = _translate_element(value)

		writer.stream.write_line("[{0}] = {1},", key, value)

	writer.stream.close_block("]")
	writer.stream.write_line()
	writer.stream.write_line()


def _translate_element(element):
	if element is True:
		return "true"
	elif element is False:
		return "false"
	elif element is None:
		return "nil"
	elif isinstance(element, bytes):
		return '"' + element.decode("utf8") + '"'
	else:
		return str(element)
