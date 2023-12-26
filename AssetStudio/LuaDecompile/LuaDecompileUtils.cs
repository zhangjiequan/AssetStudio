using System.Collections.Generic;
using System.IO;
using System.Text;

namespace AssetStudio
{
    public class LuaDecompileUtils
    {
        private static Dictionary<LuaCompileType, ILuaDecompileHandler> handlerMap = new Dictionary<LuaCompileType, ILuaDecompileHandler>()
    {
        { LuaCompileType.Luac, new LuacDecompileHandler()},
        { LuaCompileType.LuaJit, new LuaJitDecompileHandler()},
    };

        public static string DecompileLua(LuaByteInfo luaByteInfo)
        {
            luaByteInfo.HasDecompiled = true;
            bool isSupport = handlerMap.TryGetValue(luaByteInfo.CompileType, out ILuaDecompileHandler handler);
            if (!isSupport)
            {
                // 不支持的编译方式，原文返回
                return luaByteInfo.StrContent;
            }
            else
            {
                return handler.Decompile(luaByteInfo);
            }
        }
    }
}