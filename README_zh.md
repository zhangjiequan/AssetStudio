- [README 中文](./README_zh.md)
- [README English](./README.md)

# AssetStudio

![Last Commit](https://img.shields.io/github/last-commit/zhangjiequan/AssetStudio?style=flat-square)
[![Open Issues](https://img.shields.io/github/issues-raw/zhangjiequan/AssetStudio?style=flat-square)](https://github.com/zhangjiequan/AssetStudio/issues)
![Contributors](https://img.shields.io/github/contributors/zhangjiequan/AssetStudio?style=flat-square)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen?style=flat-square)

[![](https://img.shields.io/github/downloads/zhangjiequan/AssetStudio/total?style=flat-square)](https://github.com/zhangjiequan/AssetStudio/releases)
[![](https://img.shields.io/github/downloads/zhangjiequan/AssetStudio/latest/total?style=flat-square)](https://github.com/zhangjiequan/AssetStudio/releases/latest)
[![](https://img.shields.io/github/v/release/zhangjiequan/AssetStudio?style=flat-square)](https://github.com/zhangjiequan/AssetStudio/releases/latest)

[![GitHub watchers](https://img.shields.io/github/watchers/zhangjiequan/AssetStudio?style=flat-square)](https://github.com/zhangjiequan/AssetStudio/watchers)
[![GitHub forks](https://img.shields.io/github/forks/zhangjiequan/AssetStudio?style=flat-square)](https://gitpop2.vercel.app/zhangjiequan/AssetStudio)
[![GitHub stars](https://img.shields.io/github/stars/zhangjiequan/AssetStudio?style=flat-square)](https://github.com/zhangjiequan/AssetStudio/stargazers)

![Platform](https://img.shields.io/badge/platform-windows-lightgrey?style=flat-square)
[![License](https://img.shields.io/github/license/zhangjiequan/AssetStudio?style=flat-square)](./LICENSE)

[![Github CI Status](https://github.com/zhangjiequan/AssetStudio/actions/workflows/build.yml/badge.svg)](https://github.com/zhangjiequan/AssetStudio/actions)

![Custom](https://img.shields.io/badge/zhangjiequan-Jackie@Baioo-green)


AssetStudio - 基于已归档的 Perfare 的 AssetStudio，我继续 Perfare 的工作，保持 AssetStudio 的更新，支持新版本的 Unity 和额外的改进。

## 与原仓库相比，本Fork额外提供的
* 支持新版本的 Unity
  * 添加了对 Unity 2022.1.10+、2022.2 和 2022.3 的支持。
* 增强的着色器预览和导出
  * 添加美观打印功能以增强着色器信息的可读性。
  * 通过实现 ShaderSubProgram 的延迟生成来修复错误。
---

**该仓库、工具和仓库所有者均与 Unity Technologies 或其关联公司无关，也未获其赞助或授权。**

AssetStudio 是一个用于探索、提取和导出资产和资产包的工具。

## 功能
* 支持版本：
  * 3.4 - 2022.3
* 支持资产类型：
  * **Texture2D** : 转换为 png, tga, jpeg, bmp
  * **Sprite** : 裁剪 Texture2D 为 png, tga, jpeg, bmp
  * **AudioClip** : mp3, ogg, wav, m4a, fsb，支持将 FSB 文件转换为 WAV(PCM)
  * **Font** : ttf, otf
  * **Mesh** : obj
  * **TextAsset**
  * **Shader**
  * **MovieTexture**
  * **VideoClip**
  * **MonoBehaviour** : json
  * **Animator** : 导出为带有绑定 AnimationClip 的 FBX 文件

## 系统要求

- AssetStudio.net472
   - [.NET Framework 4.7.2](https://dotnet.microsoft.com/download/dotnet-framework/net472)
- AssetStudio.net5
   - [.NET Desktop Runtime 5.0](https://dotnet.microsoft.com/download/dotnet/5.0)
- AssetStudio.net6
   - [.NET Desktop Runtime 6.0](https://dotnet.microsoft.com/download/dotnet/6.0)


## 使用方法

### 加载 Assets/AssetBundles

使用 **File-Load file** 或 **File-Load folder**。

当 AssetStudio 加载资产包时，它会在内存中解压缩和读取，这可能会导致大量内存被使用。您可以使用 **File-Extract file** 或 **File-Extract folder** 将资产包提取到另一个文件夹，然后读取。

### 提取/解压 AssetBundles

Use **File-Extract file** or **File-Extract folder**。

### 导出 Assets

使用 **Export** 菜单。

### 导出 Model

从 "Scene Hierarchy" 中使用 **Model** 菜单导出模型。

从 "Asset List" 中使用 **Export** 菜单导出 Animator。

#### 带有 AnimationClip 的

从 "Scene Hierarchy" 中选择模型，然后从 "Asset List" 中选择 AnimationClip，使用 **Model-Export selected objects with AnimationClip** 进行导出。

导出 Animator 将导出绑定的 AnimationClip，或使用 **Ctrl** 从 "Asset List" 中选择 Animator 和 AnimationClip，使用 **Export-Export Animator with selected AnimationClip** 进行导出。

### 导出 MonoBehaviour

当您第一次选择 MonoBehaviour 类型的资产时，AssetStudio 会询问程序集所在的目录，请选择程序集所在的目录，例如 `Managed` 文件夹。

#### 对于 Il2Cpp

首先，使用我的另一个程序 [Il2CppDumper](https://github.com/Perfare/Il2CppDumper) 生成虚拟 dll，然后在使用 AssetStudio 选择程序集目录时，选择虚拟 dll 文件夹。

## 构建

* Visual Studio 2022 或更新版本
* **AssetStudioFBXNative** 使用 [FBX SDK 2020.2.1](https://www.autodesk.com/developer-network/platform-technologies/fbx-sdk-2020-2-1)，在构建之前，您需要安装 FBX SDK 并修改项目文件，将包含目录和库目录更改为指向 FBX SDK 目录。

## 使用的开源库

### Texture2D解码器
* [Ishotihadus/mikunyan](https://github.com/Ishotihadus/mikunyan)
* [BinomialLLC/crunch](https://github.com/BinomialLLC/crunch)
* [Unity-Technologies/crunch](https://github.com/Unity-Technologies/crunch/tree/unity)

## 线路图

### 支持lua字节码资源
反编译、预览和导出 LuaJIT、Lua 5.1、5.2 和 5.3 字节码资源。  
LuaJIT: [zhangjiequan/ljd: LuaJIT raw-bytecode decompiler](https://github.com/zhangjiequan/ljd)、[wenlong66/ljd: LuaJIT raw-bytecode decompiler](https://github.com/wenlong66/ljd)  
Lua 5.1, 5.2, and 5.3: [zhangjiequan/luadec: Lua Decompiler for lua 5.1 , 5.2 and 5.3](https://github.com/zhangjiequan/luadec)  

## 许可

AssetStudio 根据 [MIT](./LICENSE) 许可证授权。

## 致谢

如果你觉得此工具有用，请在你的致谢界面提及我的名字。像 "AssetStudio 由 Perfare & zhangjiequan 制作" 或 "感谢 Perfare & zhangjiequan" ，将不胜感激。

## 合作

随意Fork本项目并进行自定义修改，可以为自己使用，也可以通过创建pull requests来共享你的修改。如果你想帮助改进此工具，请通过提交issues来提供功能请求或错误报告，谢谢！

## 联系

通过电子邮件联系我：zhangjiequan@qq.com

## 捐赠

AssetStudio是一款免费且开源的软件。如果你觉得它不错并且对你有帮助，可以请我喝一杯咖啡！

![image.png](https://s2.loli.net/2023/11/22/1nURWl8m5Icx7HT.png)

## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=zhangjiequan/AssetStudio&type=Date)](https://star-history.com/#zhangjiequan/AssetStudio&Date)
