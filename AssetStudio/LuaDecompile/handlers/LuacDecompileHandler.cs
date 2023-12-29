using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;

namespace AssetStudio
{
    public class LuacDecompileHandler : ILuaDecompileHandler
    {
        private Dictionary<byte, string> versionHandlerMap = new Dictionary<byte, string>()
    {
        { 0x51, "lua51/luadec.exe" },
        { 0x52, "lua52/luadec.exe" },
        { 0x53, "lua53/luadec.exe" },
    };

        private const string EXE_DIR = "Dependencies/luadec";
        private const string TEMP_FILE = "tempCompiledLua.lua";
        private static readonly string DecompileArg = $"-se UTF8 {TEMP_FILE}";

        public byte[] Decompile(LuaByteInfo luaByteInfo)
        {
            var isSupport = versionHandlerMap.TryGetValue(luaByteInfo.VersionCode, out string subPath);
            if (!isSupport)
            {
                // 不支持的版本，原样输出
                return luaByteInfo.ProcessedByte;
            }
            else
            {
                // 反编译
                return TryDecompile(luaByteInfo, subPath);
            }
        }

        private byte[] TryDecompile(LuaByteInfo luaByteInfo, string exePath)
        {
            File.WriteAllBytes(TEMP_FILE, luaByteInfo.RawByte);     
            var decompileProcess = new OutputProcess();
            decompileProcess.StartInfo.FileName = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, EXE_DIR, exePath);
            decompileProcess.StartInfo.Arguments = DecompileArg;
            decompileProcess.StartInfo.StandardOutputEncoding = Encoding.Default;
            decompileProcess.StartInfo.UseShellExecute = false;
            try
            {
                decompileProcess.Start();
                decompileProcess.WaitForExit();
                if (decompileProcess.ExitCode == 0)
                {
                    // 编译完成结果缓存起来;
                    luaByteInfo.SetDecompiledContent(Encoding.Default.GetBytes(decompileProcess.Output));
                }
                else
                {
                    Console.WriteLine(decompileProcess.Error);
                }
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
            }
            finally
            {
                decompileProcess.Close();
            }
            return luaByteInfo.ProcessedByte;
        }

    }
}