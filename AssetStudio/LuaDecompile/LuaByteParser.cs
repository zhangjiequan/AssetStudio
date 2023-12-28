using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace AssetStudio
{
    public static class LuaByteParser
    {
        private static readonly byte[] LuacMagicNum = new byte[] { 0x1B, 0x4C, 0x75, 0x61 };
        private static readonly byte[] LuaJitMagicNum = new byte[] { 0x1B, 0x4C, 0x4A };
        public static bool TryParseLuaByte(byte[] luaBytes, out LuaByteInfo luaByteInfo)
        {
            luaByteInfo = null;
            if (luaBytes.Length > 5) //长度大于一个文件头，可以尝试解析
            {
                {
                    luaByteInfo = TryParseLuaJit(luaBytes);
                }

                if (luaByteInfo == null)
                {
                    luaByteInfo = TryParseLuac(luaBytes);
                }
            }

            return luaByteInfo != null;
        }

        private static LuaByteInfo TryParseLuaJit(byte[] luaBytes)
        {
            MemoryStream byteStream = new MemoryStream(luaBytes);
            BinaryReader luaByteReader = new BinaryReader(byteStream);
            if (CompareMagicNum(luaByteReader, LuaJitMagicNum))
            {
                byte version = luaByteReader.ReadByte();
                return new LuaByteInfo(luaBytes, LuaCompileType.LuaJit, version);
            }
            else
            {
                return null;
            }
        }

        private static LuaByteInfo TryParseLuac(byte[] luaBytes)
        {
            MemoryStream byteStream = new MemoryStream(luaBytes);
            BinaryReader luaByteReader = new BinaryReader(byteStream);
            if (CompareMagicNum(luaByteReader, LuacMagicNum))
            {
                byte version = luaByteReader.ReadByte();
                return new LuaByteInfo(luaBytes, LuaCompileType.Luac, version);
            }
            else
            {
                return null;
            }
        }

        private static bool CompareMagicNum(BinaryReader br, byte[] magicNum)
        {
            return br.ReadBytes(magicNum.Length).SequenceEqual(magicNum);
        }
    }
}