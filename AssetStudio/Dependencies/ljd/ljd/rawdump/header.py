#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

from ljd.util.log import errprint


_MAGIC = b'\x1bLJ'

_MAX_VERSION = 0x80

_FLAG_IS_BIG_ENDIAN = 0b00000001
_FLAG_IS_STRIPPED = 0b00000010
_FLAG_HAS_FFI = 0b00000100


class Flags():
    def __init__(self):
        self.is_big_endian = False
        self.is_stripped = False
        self.has_ffi = False


class Header():
    def __init__(self):
        self.version = 0
        self.flags = Flags()
        self.origin = b''
        self.name = b''


def read(state, header):
    r = True

    header.origin = state.stream.name

    r = r and _check_magic(state)

    r = r and _read_version(state, header)
    r = r and _read_flags(state, header)
    r = r and _read_name(state, header)
    #print("header good!")

    return r


def _check_magic(state):
    if state.stream.read_bytes(3) != _MAGIC:
        errprint("Invalid magic, not a LuaJIT format")
        return False

    return True


def _read_version(state, header):
    header.version = state.stream.read_byte()

    if header.version > _MAX_VERSION:
        errprint("Version {0}: propritary modifications",
                        header.version)
        return False

    return True


def _read_flags(parser, header):
    bits = parser.stream.read_uleb128()

    header.flags.is_big_endian = bits & _FLAG_IS_BIG_ENDIAN
    bits &= ~_FLAG_IS_BIG_ENDIAN

    header.flags.is_stripped = bits & _FLAG_IS_STRIPPED
    bits &= ~_FLAG_IS_STRIPPED

    header.flags.has_ffi = bits & _FLAG_HAS_FFI
    bits &= ~_FLAG_HAS_FFI

    # zzw.20180714 pitch: flag value is according to parser.flag when parse proto, not by header.flags
    parser.flags.is_big_endian = header.flags.is_big_endian
    parser.flags.is_stripped = header.flags.is_stripped
    parser.flags.is_big_endian = header.flags.has_ffi

    #if bits != 0:
      #  errprint("Unknown flags set: {0:08b}", bits)
     #   return False

    return True


def _read_name(state, header):
    if header.flags.is_stripped:
        header.name = state.stream.name
    else:
        length = state.stream.read_uleb128()
        header.name = state.stream.read_bytes(length).decode("utf8")

    return True
