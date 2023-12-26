namespace AssetStudio
{
    public interface ILuaDecompileHandler
    {
        string Decompile(LuaByteInfo luaByteInfo);
    }
}