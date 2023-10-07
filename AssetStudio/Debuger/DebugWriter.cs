using System.IO;
using Newtonsoft.Json;

namespace AssetStudio.Debuger
{
    public static class DebugWriter
    {
        public static void SaveObjectToJsonFile(System.Object obj, string path)
        {
            string json = JsonConvert.SerializeObject(obj, Formatting.Indented);
            File.WriteAllText($"{path}.json", json);
        }
        
        public static void SaveBinaryReaderToFile(ObjectReader reader, string outputPath)
        {
            Stream baseStream = reader.BaseStream;
            long originalPosition = baseStream.Position;
            long start = reader.byteStart;
            long size = reader.byteSize;
            baseStream.Position = start;
            
            using (FileStream fileStream = new FileStream(outputPath + ".bin", FileMode.Create, FileAccess.Write))
            {
                byte[] buffer = new byte[size];
                int bytesRead = baseStream.Read(buffer, 0, (int)size);
                if (bytesRead > 0)
                {
                    fileStream.Write(buffer, 0, bytesRead);
                }
            }
            
            baseStream.Position = originalPosition;
        }
        
        public static void SaveBinaryReaderToFile(BinaryReader reader, string outputPath)
        {
            Stream baseStream = reader.BaseStream;
            long originalPosition = baseStream.Position;
            long size = baseStream.Length - baseStream.Position;
            SaveBinaryReaderToFile(reader, originalPosition, size, outputPath);
        }
        
        public static void SaveBinaryReaderToFile(BinaryReader reader, long position, long size, string outputPath)
        {
            Stream baseStream = reader.BaseStream;
            
            long originalPosition = baseStream.Position;
            baseStream.Position = position;
            
            using (FileStream fileStream = new FileStream(outputPath + ".bin", FileMode.Create, FileAccess.Write))
            {
                byte[] buffer = new byte[size];
                int bytesRead = baseStream.Read(buffer, 0, (int)size);
                if (bytesRead > 0)
                {
                    fileStream.Write(buffer, 0, bytesRead);
                }
            }
            
            baseStream.Position = originalPosition;
        }
    }
}