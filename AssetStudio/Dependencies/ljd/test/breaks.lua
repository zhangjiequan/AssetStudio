--[[
--]]

for i=1,2,3 do
	if x and y then
		print("Then")
	else
		break
	end
end

for i=1,2,3 do
	if x then
		print("Then")
	else
		break
	end

	print ("Something")

	if y then
		break
	end
end

for i=1,2,3 do
	if x then
		print("Then")
	else
		if y then
			break
		end
	end

	print ("Something")

	if y then
		break
	end
end

for i=1,2,3 do
	if x then
		print("Then")
		if y then
			break
		end
	else
		break
	end
end

for i=1,2,3 do
	if x then
		print("Then")
		if y then
			print ("Nested then")
		else
			break
		end
	else
		break
	end
end

for i=1,2,3 do
	if x then
		print("Then")
	else
		break
	end

	if y then
		print ("Y then")
	else
		break
	end
end

print ("Too bad")

for i=1,2,3 do
	if x then
		print("Then")
		if y then
			print ("Y then")
			if z then
				print ("Z then")
			end
		end
		break
	end

	if y then
		print ("Y then")
	else
		break
	end
end

for i=1,2,3 do
	if x then
		if y then
			if z then
				if xi then
					print ("Xi then")
				end
			end
		end
		break
	else
		break
	end

	if y then
		print ("Y then")
	else
		break
	end
end

for i=1,2,3 do
	if x and y and z and xi then
		print ("Xi then")
		break
	else
		break
	end

	if y then
		print ("Y then")
	else
		break
	end
end

for i=1,2,3 do
	if x then
		print ("X then")
		if y then
			print ("Y then")
			if z then
				print ("Z then")
				if xi then
					print ("Xi then")
				end
			end
		end
		break
	else
		break
	end

	if y then
		print ("Y then")
	else
		break
	end
end

for i=1,2,3 do
	if x then
		if z then
			print("Z Then")
		else
			break
		end

		print ("Something")

		if y then
			print ("Y then")
		else
			break
		end
	else
		break
	end

end

for i=1,2,3 do
	if x then
		if z then
			print("Z Then")
		else
			break
		end

		print ("Something")
	else
		break
	end

	if y then
		print ("Y then")
	else
		break
	end
end

function updateAnimation()
	local currentTime = getElapsedTime()
	local startSequence = private.currentSequence + 1
	local endSequence = #private.sequence

	for i=startSequence, endSequence, 1 do
		local entry = private.sequence[i]

		if entry.time <= currentTime then
			if entry.command == "start" then
				goToSlide(entry.element, 2)
				goToTime(entry.element, entry.animationTime)
				play(entry.element)
			else
				if entry.command == "step" then
					goToSlide(entry.element, 2)
					goToTime(entry.element, entry.animationTime)
				else
					pause(entry.element)
				end
			end

			if entry.name ~= nil then
				setAttribute(getElement("name", entry.element), "textstring", entry.name)
			end

			private.currentSequence = i

			break
		else 
			break
		end
	end 

	if #private.sequence == private.currentSequence then
		private.playing = false
	end

	return 
end

--[[
--]]
