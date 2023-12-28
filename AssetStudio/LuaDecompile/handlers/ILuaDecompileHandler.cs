namespace AssetStudio
{
    public interface ILuaDecompileHandler
    {
        byte[] Decompile(LuaByteInfo luaByteInfo);
    }
}