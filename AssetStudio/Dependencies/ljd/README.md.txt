LuaJIT raw-bytecode decompiler (LJD)
===

The original name was _ljwthgnd_ as in _LuaJIT 'What The Hell is Going On'
Decompiler_ named under the LuaJIT C sources variable naming convention.


__WARNING!__ This code is nor finished, nor tested yet! There is no even
slightest warranty that resulting code is even near to the original. Use it at
your own risk of the wasted time.

__SECOND WARNING!__ And, BTW, this all is a one huge prototype. Because the
"release" version should be written into lua itself. Because it's cool to
decompile the decompiler - a great test too!

Requirements
---

Python __3.0+__ from python.org


How to use it
---

There is no argument parsing right now, so comment out things in the ```main.py```
script and launch it as in ```main.py path/to/file.luac```

TODO
---

There is a lot of work to do, in the order of priority

0. Logical subexpressions in while statements:
	```lua
		while x < (xi and 2 or 3) do
			print ("Hello crazy world!")
		end
	```

	Logical subexpressions (the subexpressions used as operands in
	ariphmetic or comparison operations inside other exrpressions) are
	currently supported only for ifs. To support them for whiles and
	repeat untils an expression unwarping logic should be moved at the
	very beginning. But it won't work without all fixes being done in
	a loop unwarping logic. So we need to split that and move the fixes 
	before expressions before loops before ifs. That's not that easy...

1. AST Mutations:
	1. Use the line information (or common sense if there is no line
	   information) to squash similar expressions into a single expression.

2. Formatting improvements
	1. Use the line information (or common sense) to preserve empty lines
	   and break long statements like in the original code.
	   
	   This is mostly done, but only in the "common sense" part.

	2. Use method-style calls and definitions for tables.

3. Features not supported:
	1. GOTO statement (from lua 5.2). All the required functionality is
		now in place, but that's rather a low-priority task right now.

	2. Local sub-blocks:
	```lua
	do
		...
	end
	```
	   These subblocks are not reflected anyhow directly in the bytecode.
	   The only way to guess them is to watch local variable scopes, which
	   is simple enough in case of non-stripped bytecode and a bit
	   harder otherwise.
