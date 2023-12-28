def get_jump_destination(addr, instruction):
	return addr + instruction.CD + 1


def set_jump_destination(addr, instruction, value):
	instruction.CD = value - addr - 1
