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
            return m_LuaByteInfo.ProcessedByte;
        }

        public override byte[] GetRawScript()
        {
            return m_LuaByteInfo.RawByte;
        }
    }
}
