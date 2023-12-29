using System;
using System.IO;
using System.Text;

namespace AssetStudio
{
    public class LuaJitDecompileHandler : ILuaDecompileHandler
    {
        private const string LJD_PATH = "ljd/main.py";
        private const string PTYHON_PATH = "python/python.exe";
        private const string DEPENDENCY_PATH = "Dependencies";
        private const string TEMP_FILE = "tempCompiledLua.lua";

        public byte[] Decompile(LuaByteInfo luaByteInfo)
        {
            if (TryDecompile(luaByteInfo.RawByte, out byte[] luaCode))
            {
                // 缓存反编译结果
                luaByteInfo.SetDecompiledContent(luaCode);
            }

            return luaByteInfo.ProcessedByte;
        }

        private bool TryDecompile(byte[] luaBytes, out byte[] luaCode)
        {
            var dependencyPath = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, DEPENDENCY_PATH));
            var decompilerPath = Path.GetFullPath(Path.Combine(dependencyPath, LJD_PATH));
            var pythonExePath = Path.GetFullPath(Path.Combine(dependencyPath, PTYHON_PATH));

            File.WriteAllBytes(TEMP_FILE, luaBytes);

            var decompileProcess = BuildProcess(pythonExePath, string.Format("{0} {1}", decompilerPath, TEMP_FILE));

            bool success = true;
            luaCode = null;
            try
            {
                decompileProcess.Start();
                decompileProcess.WaitForExit();
                if (decompileProcess.ExitCode == 0)
                {
                    luaCode = Encoding.UTF8.GetBytes(decompileProcess.Output);
                }
                else
                {
                    Console.WriteLine(decompileProcess.Error);
                }
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                success = false;
            }
            finally
            {
                decompileProcess.Close();
            }

            return success;
        }

        private OutputProcess BuildProcess(string pythonExePath, string args)
        {
            var decompileProcess = new OutputProcess();
            decompileProcess.StartInfo.FileName = pythonExePath;
            decompileProcess.StartInfo.Arguments = args;
            decompileProcess.StartInfo.UseShellExecute = false;
            decompileProcess.StartInfo.StandardOutputEncoding = Encoding.UTF8;
            return decompileProcess;
        }
    }
}