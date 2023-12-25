using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace AssetStudio
{
    public static class TextAssetFactory
    {
        public static TextAsset Create(ObjectReader reader)
        {
            reader.Reset();
            reader.ReadAlignedString(); // 跳过文件名
            byte[] content = reader.ReadUInt8Array();
            bool success = LuaByteParser.TryParseLuaByte(content, out LuaByteInfo luaInfo);
            if (success)
            {
                return new LuaByte(reader, luaInfo);
            }
            else
            {
                return new TextAsset(reader);
            }
        }
    }
}
