#!/usr/bin/python3
#
# The MIT License (MIT)
#
# Copyright (c) 2013 Andrian Nord
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import sys
import io

import ljd.rawdump.parser
import ljd.pseudoasm.writer
import ljd.ast.builder
import ljd.ast.validator
import ljd.ast.locals
import ljd.ast.slotworks
import ljd.ast.unwarper
import ljd.ast.mutator
import ljd.lua.writer
#zzw 20180714 support str encode
import gconfig

def dump(name, obj, level=0):
    indent = level * '\t'

    if name is not None:
        prefix = indent + name + " = "
    else:
        prefix = indent

    if isinstance(obj, (int, float, str)):
        print(prefix + str(obj))
    elif isinstance(obj, list):
        print (prefix + "[")

        for value in obj:
            dump(None, value, level + 1)

        print (indent + "]")
    elif isinstance(obj, dict):
        print (prefix + "{")

        for key, value in obj.items():
            dump(key, value, level + 1)

        print(indent + "}")
    else:
        print(prefix + obj.__class__.__name__)

        for key in dir(obj):
            if key.startswith("__"):
                continue

            val = getattr(obj, key)
            dump(key, val, level + 1)


def main():
    file_in = sys.argv[1]

    header, prototype = ljd.rawdump.parser.parse(file_in)
    #print ("good")
    if not prototype:
        return 1

    # TODO: args
    # ljd.pseudoasm.writer.write(sys.stdout, header, prototype)

    ast = ljd.ast.builder.build(prototype)

    assert ast is not None

    ljd.ast.validator.validate(ast, warped=True)

    ljd.ast.mutator.pre_pass(ast)

    # ljd.ast.validator.validate(ast, warped=True)

    ljd.ast.locals.mark_locals(ast)

    # ljd.ast.validator.validate(ast, warped=True)

    ljd.ast.slotworks.eliminate_temporary(ast)

    # ljd.ast.validator.validate(ast, warped=True)

    if True:
       # ljd.ast.unwarper.unwarp(ast)

        # ljd.ast.validator.validate(ast, warped=False)

        if True:
            ljd.ast.locals.mark_local_definitions(ast)

            # ljd.ast.validator.validate(ast, warped=False)

            ljd.ast.mutator.primary_pass(ast)

            ljd.ast.validator.validate(ast, warped=False)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
    ljd.lua.writer.write(sys.stdout, ast)

    return 0


if __name__ == "__main__":
    # zzw 20180714 support str encode
    gconfig.gFlagDic['strEncode'] = 'utf-8'
    retval = main()
    sys.exit(retval)

# vim: ts=8 noexpandtab nosmarttab softtabstop=8 shiftwidth=8
