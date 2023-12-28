#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

_TAB_WIDTH = " " * 8


class IndentedStream():
	def __init__(self, fd):
		self.fd = fd

		self.indent = 0
		self.line_open = False

	def write_multiline(self, fmt, *args, **kargs):
		assert not self.line_open

		if len(args) + len(kargs) > 0:
			text = fmt.format(*args, **kargs)
		else:
			text = fmt

		lines = text.split("\n")

		if lines[0] == "":
			lines.pop(0)

		if lines[-1] == "":
			lines.pop(-1)

		spaces = "\t" * self.indent

		for line in lines:
			self.fd.write(spaces + line + "\n")

	def start_line(self):
		assert not self.line_open
		self.line_open = True

		self.fd.write("\t" * self.indent)

	def write(self, fmt="", *args, **kargs):
		assert self.line_open

		if len(args) + len(kargs) > 0:
			text = fmt.format(*args, **kargs)
		elif isinstance(fmt, str):
			text = fmt
		else:
			text = str(fmt)

		assert "\n" not in text

		self.fd.write(text)

	def end_line(self):
		assert self.line_open

		self.fd.write("\n")

		self.line_open = False

	def write_line(self, *args, **kargs):
		self.start_line()
		self.write(*args, **kargs)
		self.end_line()

	def open_block(self, *args, **kargs):
		if len(args) + len(kargs) > 0:
			self.write_line(*args, **kargs)

		self.indent += 1

	def close_block(self, *args, **kargs):
		if len(args) + len(kargs) > 0:
			self.write_line(*args, **kargs)

		self.indent -= 1
