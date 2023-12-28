--[[
--]]

if true then
	print("if true")
end

print ("something")

if false then
	print("if false")
end

print ("something")

if x then
	print ("something after")
end

if x and false then
	print("if and false")
end

if x then
	if false then
		print("if and false")
	end
end

if x then
	if false then
		print("if and false")
	else
		print("if and false with else!")
	end
end

if x then
	if false then
		print("if and false")
	else
		print("if and false with else!")
	end
else
	print ("Else!")
end

if x and true then
	print("if and true")
end

if x or false then
	print("if or false")
end


if x or true then
	print("if or true")
end

if x < 100 then
	print ("then")
else
	print ("else")
end

if x < 100 and y < 100 then
	print ("semi-nested then")
else
	print ("else")
end

if x < 100 or z > 100 then
	if y < 100 or x > 100 then
		print ("Nested then")
	end
end

if x < 100 or z > 100 then
	if y < 100 or x > 100 then
		print ("Nested then")
	end

	print ("Enclosure")
end

if x < 100 or z > 100 then
	if y < 100 or x > 100 then
		print ("Nested then")
	else
		print ("Nested else")
	end

	print ("Enclosure")
end

if x < 100 or z > 100 then
	if y < 100 or x > 100 then
		print ("Nested then")
	end

	print ("Enclosure")
else
	print ("Else")
end

if x < 100 or z > 100 then
	if y < 300 or x > 100 then
		print ("Nested then")
	else
		print ("Nested else")
	end
end


if x < 100 or z > 100 then
	if y < 100 or x > 100 then
		print ("Nested then")
	end
else
	print ("Else")
end


if x < 100 or z > 100 then
	if y < 100 or x > 100 then
		print ("Nested then")
	else
		print ("Nested else")
	end
else
	print ("Else")
end

if x < 100 or z > 100 then
	if y < 100 or x > 100 then
		print ("Nested then")
	else
		print ("Nested else")
	end
else
	if y < 100 or x > 100 then
		print ("Nested else then")
	else
		print ("Nested else else")
	end
end

if x < 100 or y < 100 then
	print ("x or y with comparisons")
end


if x < 100 and y < 100 then
	print ("x and y with comparisons")
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

if x or y then
	print ("x or y")
end

if x and y then
	print ("x and y")
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

if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
	print ("True terminator!")
else
	print ("False terminator!")
end

if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
	print ("True terminator!")

	if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
		print ("True terminator!")

		if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
			print ("True terminator!")
		else
			print ("False terminator!")
		end

		print ("Enclosed")
	else
		print ("False terminator!")
	end

	print ("Enclosed")
else
	print ("False terminator!")
end

if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
	print ("True terminator!")

	if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
		print ("True terminator!")

		if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
			print ("True terminator!")
		else
			print ("False terminator!")
		end

		print ("Enclosed")
	else
		print ("False terminator!")
	end
else
	print ("False terminator!")
end

if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
	print ("True terminator!")

	if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
		print ("True terminator!")

		if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
			print ("True terminator!")
		else
			print ("False terminator!")
		end
	else
		print ("False terminator!")
	end
else
	print ("False terminator!")
end

if (y < 300 or z > 300) then
	print ("True terminator!")

	if (x < 300 and z < 300) then
		print ("True terminator!")

		if x < 300  or z < 300 then
			print ("True terminator!")
		else
			print ("False terminator!")
		end
	else
		print ("False terminator!")
	end

	print ("Enclosed")
else
	print ("False terminator!")
end

if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
	print ("True terminator!")

	if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
		print ("True terminator!")

		if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
			print ("True terminator!")
		else
			print ("False terminator!")
		end
	else
		print ("False terminator!")
	end
else
	print ("False terminator!")

	if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
		print ("True terminator!")

		if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
			print ("True terminator!")
		else
			print ("False terminator!")
		end
	else
		print ("False terminator!")
	end
end

if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
	if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
		print ("True terminator!")

		if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
			print ("True terminator!")
		else
			print ("False terminator!")
		end
	else
		print ("False terminator!")
	end
else
	if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
		print ("True terminator!")

		if (x < 300 and (y < 300 or z > 300)) or z < 300 and error() then
			print ("True terminator!")
		else
			print ("False terminator!")
		end
	else
		print ("False terminator!")
	end
end

local a = 0

if x % 2 == 0 then
	a = 1
end

local a = x % 2 == 0 or a

local a = "test"
local b = "result"

if a == "test" then
	b = "test"
elseif a == "1234" then
	b = "1234"
elseif a == "asd" then
	b = "asd"
elseif a == "fadasd" then
	b = "fadasd"
else
	b = "Otherwise"
end

print ("Same thing as expression")

b = (a == "test" and "test") or (a == "1234" and "1234") or (a == "asd" and "asd") or (a == "fadasd" and "fadasd") or "Otherwise"

print (a, b)

local a = "test"
if a == "test" then
	b = "test"
	if  a == "1234" then
		b = "1234"

		if a == "asd" then
			a = "asd"

			if a == "fadasd" then
				b = "fadasd"
			end
		end
	end
end

local a = "test"
local b = "result"
if a == "test" then
	b = "test"
	if a == "test" then
		b = "test"
	elseif a == "1234" then
		b = "1234"
	elseif a == "asd" then
		b = "asd"
	elseif a == "fadasd" then
		b = "fadasd"
	else
		b = "Otherwise"
	end
elseif a == "1234" then
	b = "1234"
elseif a == "asd" then
	b = "asd"
elseif a == "fadasd" then
	b = "fadasd"
else
	b = "Otherwise"
end

print (a, b)

if componentInfo.details ~= nil then
	layout = componentInfo.details.layout

	if layout == "table" then
		mainFrame = "tableFrame"
	else
		if layout == "header" then
			mainFrame = "headerFrame"
		else
			if layout == "long" then
				mainFrame = "fullFrame"
			else
				if layout == "short" then
					mainFrame = "topFrame"
				end
			end

		end
	end
end

print ("asd")

local value = 1.3

if scaleinfo.floorValue then
	value = math.floor(value*scaleinfo.factor)
else
	value = math.ceil(value*scaleinfo.factor)
end

function func(button, buttonElement)
	local stateEntry = buttonElement.buttonState
	local targetSlide = nil

	if buttonElement.active then
		if stateEntry.mouseClick or stateEntry.keyboardPress then
			targetSlide = "click"
		else
			if stateEntry.mouseOver or stateEntry.keyboard then
				targetSlide = "highlight"
			else
				targetSlide = "normal"
			end
		end
	else
		targetSlide = "unselect"
	end

	local _, curSide = getCurrentSlide(buttonElement.element)
end


local sliderelement = {}
local centerValue = ""

if sliderelement.scale[1].displayCenter then
	if sliderelement.scale[2] ~= nil and sliderelement.scale[2].displayCenter then
		centerValue = formatNumber(
				math.abs(getSliderCenterValue(sliderValue, sliderelement.scale[1])),
				sliderelement.scale[1].valueSuffix,
				math.abs(getSliderCenterValue(sliderValue, sliderelement.scale[2])),
				sliderelement.scale[2].valueSuffix)
	end
else
	if sliderelement.scale[1].displayCenter then
		centerValue = formatNumber(math.abs(getSliderCenterValue(sliderValue, sliderelement.scale[1])), sliderelement.scale[1].valueSuffix)
	else
		if sliderelement.scale[2] and sliderelement.scale[2].displayCenter then
			centerValue = formatNumber(math.abs(getSliderCenterValue(sliderValue, sliderelement.scale[2])), sliderelement.scale[2].valueSuffix)
		end
	end
end

function setElementPosition(anarkElement, x, y, xUseHalfPixel, yUseHalfPixel)
	if config.verifyPixelExact then
		local testx = x

		if testx and ((xUseHalfPixel and private.offsetx % 1 == 0)
				or (not xUseHalfPixel and private.offsetx % 1 ~= 0)) then
			testx = testx + 0.5
		end

		local testy = y

		if testy and ((yUseHalfPixel and private.offsety % 1 == 0)
				or (not yUseHalfPixel and private.offsety % 1 ~= 0)) then
			testy = testy + 0.5
		end

		if (testx ~= nil and testx % 1 ~= 0)
				or (testy ~= nil and testy % 1 ~= 0) then
			DebugError("Widget system warning. Given position for element " .. tostring(anarkElement) .. " uses subpixels. This will lead to graphical issues. x/y: " .. tostring(x) .. " / " .. tostring(y) .. " - using halfpixels (x/y): " .. tostring(xUseHalfPixel) .. " / " .. tostring(yUseHalfPixel))
		end
	end

	setElementPositionUnchecked(anarkElement, x, y)
end

local relationLEDValue, maxLED, minLED, boostActive

if relationLEDValue < 0 then
	if boostActive then
		maxLED = maxLED - 1
	end
else
	minLED = relationLEDValue < 0 and boostLocal or minLED - 1
end

function aaa()
	local a, b, c

	if a == 0 then
		if b == 2 then
			print("b")
		else
			print("bend")
			return
		end
	else
		function asd()
			print(a, b, c)
		end

		return
	end

	return
end

local nins, snapref, dumpreg, snapno, printsnap, tr, snap, tracesnap

for ins=1, nins do
	if ins >= snapref then
		if dumpreg then
			out:write(format("", snapno))
		else
			out:write(format("", snapno))
		end

		printsnap(tr, snap)
		snapno = snapno + 1
		snap = tracesnap(tr, snapno)
		snapref = snap and snap[0] or 65536
	end

	local m, ot, op1, op2, ridsp = traceir(tr, ins)
	local oidx = shr(ot, 8)*6
	local t = band(ot, 31)
	local op = sub(irnames, oidx + 1, oidx + 6)

	print ("Test")
end

if x == 0 then
	print ("then")
else
end

local menu, x, y, test, xi

print("asd")

menu.onUpdate = function ()
	if x and y then
		test = x or y
	
		print ("test")

		menu.attr = x or foo(y, "macro")
	end

	return 
end

if shouldDisplayIcon(onScreen, targetElement.obstructed, (targetElement.outlined or targetElement.surfaceElement or targetElement.crate or targetElement.switchable) and targetElement.messageType ~= "missionobjective", targetElement.messageType == "missionobjective") then
	print("asd")
end


if test == 3 then
	print("Just a test")
else
end

if x == 2 then
	print("This may crash the if else above!")
end

local xi, x, y, z

if xi then
	z = x or y
	z = x or y
	z = x or y

	print ("asd")
end

if xi then
	local unlocked_defence_status = x or (y or z) < 100

	bar((x and y) or z)
end

--[[
--]]
