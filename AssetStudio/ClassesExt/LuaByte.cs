using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace AssetStudio
{
    internal class LuaByte : TextAsset
    {
        private LuaByteInfo m_LuaByteInfo;

        public LuaByte(ObjectReader reader, LuaByteInfo luaByteInfo) : base(reader)
        {
            m_LuaByteInfo = luaByteInfo;
        }

        public override byte[] GetProcessedScript()
        {
            if (!m_LuaByteInfo.HasDecompiled)
            {
                LuaDecompileUtils.DecompileLua(m_LuaByteInfo);
            }
            // 不能用 UTF8 好像显示时候默认 GBK 解码
            return Encoding.Default.GetBytes(m_LuaByteInfo.StrContent);
        }

        public override byte[] GetRawScript()
        {
            return m_LuaByteInfo.RawByte;
        }
    }
}
