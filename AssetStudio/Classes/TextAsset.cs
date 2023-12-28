using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Text;

namespace AssetStudio
{
    public class TextAsset : NamedObject
    {
        public byte[] m_Script;

        public TextAsset(ObjectReader reader) : base(reader)
        {
            m_Script = reader.ReadUInt8Array();
            //m_Script = Encoding.UTF8.GetBytes("测试一下");
        }

        public virtual byte[] GetRawScript()
        {
            return m_Script;
        }

        public virtual byte[] GetProcessedScript()
        {
            return m_Script;
        }
    }
}
