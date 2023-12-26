using System.Text;

namespace AssetStudio
{
    public class LuaByteInfo
    {
        private byte[] m_Bytes;
        private LuaCompileType m_CompileType;
        private byte m_Version;
        private string m_DecompileContent;

        public byte[] RawByte => m_Bytes;
        public LuaCompileType CompileType => m_CompileType;
        public byte VersionCode => m_Version;
        public bool HasDecompiled;


        public string StrContent
        {
            get
            {
                if (string.IsNullOrEmpty(m_DecompileContent))
                {
                    return Encoding.UTF8.GetString(m_Bytes);
                }
                else
                {
                    return m_DecompileContent;
                }
            }
        }

        public LuaByteInfo(byte[] luaBytes, LuaCompileType compileType, byte version)
        {
            m_Bytes = luaBytes;
            m_CompileType = compileType;
            m_Version = version;
        }

        public void SetDecompiledContent(string decompiledStr)
        {
            m_DecompileContent = decompiledStr;
        }
    }
}
