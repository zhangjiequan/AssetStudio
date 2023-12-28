function assignment()
	function generator()
		return 1, 2, 3
	end

	a = 1
	b, c, d = nil
	e, f, g = 1, 2, 3
	local i, k, l = 3, 2, g + 1
	
	local m, n, o, p = 1, generator()

	print (a, b, c, d, e, f, g, i, k, l)
end

function vararg(...)
	a = ...
	c, d = ...
	t = {...}
	s = {1, 2, 3, ...}

	local f, g, h = ...

	t.x = ...

	assignment(...)

	if t.x == 3 then
		return a, t, s, ...
	else
		return ...
	end
end

function tables()
	function generator(x, y, z)
		return x, y, z
	end

	t = {
		[123.322] = 3,
		[3] = {
			"a", "b", "c"
		},
		generator("a", "b", "c"),
		generator("d", "e", "f")
	}

	t.var = 1
	t.str = "Nope"

	function t:foo(var)
		self.var = var;
		self.str = "!!!" .. var 
	end 

	t:foo(123)

	print(t)
end

function logical()
	x = 3

	print ("if true")

	if true then
		print ("That's true")
	end

	print ("if false")

	if false then
		print ("That's false")
	end

	print ("Ordinary if")

	if x == 123 then
		print ("Good number")
	end

	print ("No then, only else")

	if x == 1 then
	else
		print ("Not one!")
	end

	print ("elseifs")

	if x == 3 then
		print("is three!")
	elseif x == 5 then
		print("is five!")
	elseif x == 8 then
		print("is eight!")
		return
	else
		print("is something else!")
	end

	print ("ordinary if")

	if x == 6 then
		print("Is six!")
	else
		print("Whatever else!")
	end	

	print ("The same if as expression")

	local a = ((x == 6) and print("Is six!")) or print("Whatever else!")

	print ("Nested if")

	if x == 666 then
		print("Hellish X!")

		if x > 321 then
			if x > 333 then
				print ("X > 321 AND 333 - Isn't that obvious already?")
			end
		else
			print ("Seriously???")
		end
	else
		print("Not bad enough!")

		if x ~= 42 then
			print ("And it doesn't answer anything")
		end
	end
end

function logical_expressions()
	x = 0
	y = 1
	z = 2

	print ("simple or expression")

	b = x or y

	print ("simple or not expression")

	b = not x or y

	print ("simple and expression")

	b = x and y

	print ("simple or expression with binary comparison")

	b = (x < 100) or y

	print ("simple and expression with binary comparison")

	b = (x < 100) and y

	print ("simple and expression with binary comparison and function call")

	b = (x < 100) and print(y)

	print ("simple and expression with double binary comparison")

	b = (x < 100) and (y > 100)

	print ("(and) or expression")

	b = (x and y) or z

	print ("(or) and expression")

	b = (x or y) and z
	print ("(and) and expression")

	b = (x and y) and z

	print ("(or) or expression")
	b = (x or y) or z

	print ("or (and) expression")

	b = x or (y and x)

	print ("and (or) expression")

	b = x and (y or x)

	print ("and (and) expression")

	b = x and (y and x)

	print ("or (or) expression")

	b = x or (y or x)

	print ("ond (or) and expression")

	b = x and (y or x) and z

	print ("or (and) or expression")

	b = x or (y and x) or z

	print ("and of two ors")

	b = (x or z) and (y or z)

	print ("or of two ands")

	b = (x and z) or (y and z)

	print ("and (or) and (or) expression with comparisons")

	b = x < 100 and (y < 100 or x < 100) and (z < 100 or x < 100)

	print ("and (or) and or expression with comparisons")

	b = x < 100 and (y < 100 or x < 100) and z < 100 or x < 100

	print ("or (and) or (and) expression with comparisons")

	b = x < 100 or (y < 100 and x < 100) or (z < 100 and x < 100)

	print ("and (and) and (and) expression with comparisons")

	b = x < 100 and (y < 100 and x < 100) and (z < 100 and x < 100)

	print ("or (or) or (or) expression with comparisons")

	b = x < 100 or (y < 100 or x < 100) or (z < 100 or x < 100)

	print ("4 and expression with comparisons")

	b = x < 100 and y < 100 and x < 100 and z < 100 and x < 100

	print ("4 or expression with comparisons")

	b = x < 100 or y < 100 or x < 100 or z < 100 or x < 100

	print ("and (or or) and (or or) expression with comparisons")

	b = x < 100 and (y < 100 or x < 100 or z < 100)
			and (y < 100 or x < 100 or z < 100)
	print ("and (or and or) and (or and or) expression with comparisons")

	b = x < 100 and (y < 100 or (x < 100 and x > 100) or z < 100)
			and (y < 100 or (x < 100 and x > 100) or z < 100)

	print ("or (and or and) or (and or and) expression with comparisons")

	b = x < 100 or (y < 100 and (x < 100 or x > 100) and z < 100)
			or (y < 100 and (x < 100 or x > 100) and z < 100)

	print ("simple or and expression with binary comparison")

	b = x or (y and (x < 100))

	print ("normal logical expression")

	b = (x and y) or ((y > 3) and (((x/2) < 1) or (y > 100)) and (x ~= 2))

	print ("precalculated true expression")

	c = true or (x and y) or true

	print ("precalculated false expression")

	d = false and ((x and y) or true)

	print ("precalculated false expression with function")

	e = error() and false and ((x and y) or true)

	print ("precalculated true expression with function")

	e = error() and true and ((x and y) or true)

	print ("precalculated? false expression with variable")

	local z = false

	f = z and ((x and y) or true)

	print ("precalculated false expression with nil")

	f = nil and ((x and y) or true)
	
	print("if with expression")

	a = x or y
	a = x and y
	a = x < 100 or y < 100
	a = x < 100 and y < 100

	if x or y then
		print ("x or y")
	end

	if x and y then
		print ("x and y")
	end

	if x < 100 or y < 100 then
		print ("x or y with comparisons")
	end

	if x < 100 and y < 100 then
		print ("x and y with comparisons")
	end

	if x or y then
		print ("x or y")
	else
		print ("ELSE x or y")
	end

	if x and y then
		print ("x and y")
	else
		print ("ELSE x and y")
	end

	if x < 100 or y < 100 then
		print ("x or y with comparisons")
	else
		print ("ELSE x or y with comparisons")
	end

	if x < 100 and y < 100 then
		print ("x and y with comparisons")
	else
		print ("ELSE x and y with comparisons")
	end

	if (x < 100 and y < 100) or z < 100 then
		print ("(and) or with comparisons")
	else
		print ("ELSE (and) or with comparisons")
	end

	if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
		print ("True terminator!")
	else
		print ("False terminator!")
	end

	if x < 300 and y < 300 then
		print ("True terminator!")

		if x < 300  and z < 300 then
			print("Nested if")
		end
	else
		print ("False terminator!")

		if x < 300 and z < 300 then
			print("Enclosed nested if")
		end

		print ("Enclosure")
	end

	while x > 300 and y < 300 do
		print ("In while")
	end

	repeat
		print ("In repeat until")
	until x < 300 and y > 300

	print(x, y, b, c, d, e, f)
end

function functions()
	function func1(x, y)
		function sub(z)
			return z
		end

		return x, y, sub
	end

	x, y, z = func1(1, 2)
	print(z(4))

	x = func1(1, 2)

	func1(1, 2)

	function func2(x)
		print (x)
	end

	function func3(x)
		return x*2
	end

	func2(func3(3))

	function func4(x, y, z)
		print (x, y, z)
	end

	func4(1, 2, func2(3))
end

function locals(x, y, ...)
	local a, b, c = ...

	function generator()
		return 1, 2, 3
	end

	local d, e, f  = generator()

	local g, h, i, k = 4, generator()

	local l, m, n = f, e
end


function loops()
	function iterate_over(table)
		function iterator(table, index)
			key, value = next(table, index)

			return key, value, 1, 2, 3
		end

		return iterator, table, nil
	end

	t = {1, 2, 3}

	print ("numeric for without step")

	for i=1, 100 do
		print(i)
	end

	print ("numeric for with step")

	for i=1, 100, 2 do
		print(i)
	end

	print ("iterator for")

	for key, value in pairs(t) do
		print(key, value)
	end

	print("iterator for with another iterator")

	for key, value in ipairs(t) do
		print(key, value)
	end

	print("iterator for with crazy custom iterator")

	for key, value, x, y, z in iterate_over(t) do
		print(key, value, x, y, z)
	end

	print("iterator for with dissected iterator")

	a, b, c = pairs(t)

	for key, value in a, b, c do
		print(key, value)
	end

	print ("while")

	x = 3

	while x > 0 do
		x = x - 1
	end
	
	print ("while with copy check")

	y = 0
	x = y

	while x do
		x = y
	end

	print ("repeat until")

	repeat
		x = x + 1
	until x > 5

	print ("repeat until with copy check")

	repeat
		x = y
	until not x

	print ("While with break")

	while x > 5 do
		break
	end

	print ("Repeat until with break")

	repeat
		break
	until x < 3

	print ("Numeric for with break")

	for i=0,1,2 do
		break
	end

	print ("Iterator for with break")

	for key,value in pairs(t) do
		break
	end

	print ("Loop with break and function inside")

	t = {}

	for i=0,100 do
		y = 3
		t[i] = function ()
			return i + y
		end

		if i == 5 then
			print ("then")
			break
		else
			print ("else")
		end
	end
end

function upvalues()
	test = 0

	function sub(x)
		test = test + 1
		test = 3
		test = "asd"
		test = 4.0
		return test + x
	end

	print(sub(3))
end


function subblock()
	print ("Subblock with locals")

	x = 3

	do
		local a = 2

		print(a + x)
	end

	y = 4
end
