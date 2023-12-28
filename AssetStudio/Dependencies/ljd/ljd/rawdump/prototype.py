#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

from ljd.util.log import errprint

import ljd.bytecode.instructions as ins

import ljd.rawdump.constants
import ljd.rawdump.debuginfo
import ljd.rawdump.code


FLAG_HAS_CHILD = 0b00000001
FLAG_IS_VARIADIC = 0b00000010
FLAG_HAS_FFI = 0b00000100
FLAG_JIT_DISABLED = 0b00001000
FLAG_HAS_ILOOP = 0b00010000


class _State():
    def __init__(self, parser):
        for key, value in parser.__dict__.items():
            setattr(self, key, value)

        self.upvalues_count = 0
        self.complex_constants_count = 0
        self.numeric_constants_count = 0
        self.instructions_count = 0
        self.debuginfo_size = 0
'''
zzw 20180716
| size(1 uleb128) | flag(1 byte) | arguments_count(1 byte) 
| framesize(1 byte) | upvalues_count(1 byte) | complex_constants_count(1 uleb128) 
| numeric_constants_count(1 uleb128) | instructions_count(1 uleb128) [| debuginfo_size(1 uleb128)
| first_line_number(1 uleb128) | lines_count(1 uleb128) ] | instructions(protoheader define) 
| constants(protoheader define) | debginfo(protoheader flage define) |
'''

def read(parser, prototype):
    parser = _State(parser)

    size = parser.stream.read_uleb128()

    if size == 0:
        return False

    if not parser.stream.check_data_available(size):
        errprint("File truncated")
        return False

    start = parser.stream.pos

    r = True

    r = r and _read_flags(parser, prototype)
    r = r and _read_counts_and_sizes(parser, prototype)
    r = r and _read_instructions(parser, prototype)
    r = r and _read_constants(parser, prototype)
    r = r and _read_debuginfo(parser, prototype)

    end = parser.stream.pos

    if r:
        assert end - start == size,                     \
            "Incorrectly read: from {0} to {1} ({2}) instead of {3}"\
            .format(start, end, end - start, size)

    return r


def _read_flags(parser, prototype):
    bits = parser.stream.read_byte()

    prototype.flags.has_ffi = bool(bits & FLAG_HAS_FFI)
    bits &= ~FLAG_HAS_FFI

    prototype.flags.has_iloop = bool(bits & FLAG_HAS_ILOOP)
    bits &= ~FLAG_HAS_ILOOP

    prototype.flags.has_jit = not (bits & FLAG_JIT_DISABLED)
    bits &= ~FLAG_JIT_DISABLED

    prototype.flags.has_sub_prototypes = bool(bits & FLAG_HAS_CHILD)
    bits &= ~FLAG_HAS_CHILD

    prototype.flags.is_variadic = bool(bits & FLAG_IS_VARIADIC)
    bits &= ~FLAG_IS_VARIADIC

    if bits != 0:
        errprint("Unknown prototype flags: {0:08b}", bits)
        return False

    return True


def _read_counts_and_sizes(parser, prototype):
    prototype.arguments_count = parser.stream.read_byte()
    prototype.framesize = parser.stream.read_byte()

    parser.upvalues_count = parser.stream.read_byte()
    parser.complex_constants_count = parser.stream.read_uleb128()
    parser.numeric_constants_count = parser.stream.read_uleb128()
    parser.instructions_count = parser.stream.read_uleb128()

    if parser.flags.is_stripped:
        parser.debuginfo_size = 0
    else:
        parser.debuginfo_size = parser.stream.read_uleb128()

    if parser.debuginfo_size == 0:
        return True

    prototype.first_line_number = parser.stream.read_uleb128()
    prototype.lines_count = parser.stream.read_uleb128()

    parser.lines_count = prototype.lines_count

    return True


def _read_instructions(parser, prototype):
    i = 0

    if prototype.flags.is_variadic:
        header = ins.FUNCV()
    else:
        header = ins.FUNCF()

    header.A = prototype.framesize
    prototype.instructions.append(header)

    while i < parser.instructions_count:
        instruction = ljd.rawdump.code.read(parser)

        if not instruction:
            return False

        #print ("inst：%s" % instruction.name)
        #print ("opcode:%x" % instruction.opcode)
        #print ("A:%x" % instruction.A)
        #print ("B:%x" % instruction.B)
        #print ("CD:%x" % instruction.CD)
        prototype.instructions.append(instruction)

        i += 1

    return True


def _read_constants(parser, prototype):
    return ljd.rawdump.constants.read(parser, prototype.constants)


def _read_debuginfo(stream, prototype):
    if stream.debuginfo_size == 0:
        return True

    return ljd.rawdump.debuginfo.read(stream,
                        prototype.first_line_number,
                        prototype.debuginfo)
