using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AssetStudio
{
    public class TypeTree
    {
        public List<TypeTreeNode> m_Nodes;
        public byte[] m_StringBuffer;

        public bool ContainsNamePath(string namePath)
        {
            var outputItems = Transform();
            foreach (var outputItem in outputItems)
            {
                if (outputItem.NamePath.Contains(namePath))
                {
                    return true;
                }
            }
            return false;
        }
        
        private class PathItem
        {
            public int Index;
            public int Level;
            public string TypePath;
            public string NamePath;
        }
        
        private List<PathItem> Transform()
            {
                List<PathItem> output = new List<PathItem>();
                Dictionary<int, string> typePaths = new Dictionary<int, string>();
                Dictionary<int, string> namePaths = new Dictionary<int, string>();
        
                foreach (var item in m_Nodes)
                {
                    int level = item.m_Level;
                    int index = item.m_Index;
                    string m_Type = item.m_Type;
                    string m_Name = item.m_Name;
        
                    if (level == 0)
                    {
                        typePaths[level] = m_Type;
                        namePaths[level] = m_Name;
                    }
                    else
                    {
                        typePaths[level] = typePaths[level - 1] + "." + m_Type;
                        namePaths[level] = namePaths[level - 1] + "." + m_Name;
                    }
        
                    // Reset paths for higher levels
                    List<int> keysToRemove = new List<int>();
                    foreach (var key in typePaths.Keys)
                    {
                        if (key > level)
                        {
                            keysToRemove.Add(key);
                        }
                    }
                    foreach (var key in keysToRemove)
                    {
                        typePaths.Remove(key);
                        namePaths.Remove(key);
                    }
                    PathItem pathItem = new PathItem
                    {
                        Index = index,
                        Level = level,
                        TypePath = typePaths[level],
                        NamePath = namePaths[level]
                    };
                    output.Add(pathItem);
                }
                return output;
            }
    }
}
