- [README 中文](./README_zh.md)
- [README English](./README.md)

# AssetStudio

![Last Commit](https://img.shields.io/github/last-commit/zhangjiequan/AssetStudio?style=flat-square)
[![Open Issues](https://img.shields.io/github/issues-raw/zhangjiequan/AssetStudio?style=flat-square)](https://github.com/zhangjiequan/AssetStudio/issues)
![Contributors](https://img.shields.io/github/contributors/zhangjiequan/AssetStudio?style=flat-square)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen?style=flat-square)

![Platform](https://img.shields.io/badge/platform-windows-lightgrey?style=flat-square)
![Downloads](https://img.shields.io/github/downloads/zhangjiequan/AssetStudio/total?style=flat-square)
[![License](https://img.shields.io/github/license/zhangjiequan/AssetStudio?style=flat-square)](./LICENSE)

[![GitHub watchers](https://img.shields.io/github/watchers/zhangjiequan/AssetStudio?style=flat-square)](https://github.com/zhangjiequan/AssetStudio/watchers)
[![GitHub forks](https://img.shields.io/github/forks/zhangjiequan/AssetStudio?style=flat-square)](https://gitpop2.vercel.app/zhangjiequan/AssetStudio)
[![GitHub stars](https://img.shields.io/github/stars/zhangjiequan/AssetStudio?style=flat-square)](https://github.com/zhangjiequan/AssetStudio/stargazers)

[![Github CI Status](https://github.com/zhangjiequan/AssetStudio/actions/workflows/build.yml/badge.svg)](https://github.com/zhangjiequan/AssetStudio/actions)

![Custom](https://img.shields.io/badge/zhangjiequan-Jackie@Baioo-green)


AssetStudio - Based on the archived Perfare's AssetStudio, I continue Perfare's work to keep AssetStudio up-to-date, with support for new Unity versions and additional improvements.

## What This Fork Offers Over the Original Repository
* Support for New Unity Versions
  * Added support for Unity 2021.3.10+, 2022.2, and 2022.3.
* Enhanced Shader Preview and Export
  * Add pretty printing functionality to enhance shader information readability.
  * Fix errors by implementing lazy generation for ShaderSubProgram as needed.
---

**None of the repo, the tool, nor the repo owner is affiliated with, or sponsored or authorized by, Unity Technologies or its affiliates.**

AssetStudio is a tool for exploring, extracting and exporting assets and assetbundles.

## Features
* Support version:
  * 3.4 - 2022.3
* Support asset types:
  * **Texture2D** : convert to png, tga, jpeg, bmp
  * **Sprite** : crop Texture2D to png, tga, jpeg, bmp
  * **AudioClip** : mp3, ogg, wav, m4a, fsb. support convert FSB file to WAV(PCM)
  * **Font** : ttf, otf
  * **Mesh** : obj
  * **TextAsset**
  * **Shader**
  * **MovieTexture**
  * **VideoClip**
  * **MonoBehaviour** : json
  * **Animator** : export to FBX file with bound AnimationClip

## Requirements

- AssetStudio.net472
   - [.NET Framework 4.7.2](https://dotnet.microsoft.com/download/dotnet-framework/net472)
- AssetStudio.net5
   - [.NET Desktop Runtime 5.0](https://dotnet.microsoft.com/download/dotnet/5.0)
- AssetStudio.net6
   - [.NET Desktop Runtime 6.0](https://dotnet.microsoft.com/download/dotnet/6.0)


## Usage

### Load Assets/AssetBundles

Use **File-Load file** or **File-Load folder**.

When AssetStudio loads AssetBundles, it decompresses and reads it directly in memory, which may cause a large amount of memory to be used. You can use **File-Extract file** or **File-Extract folder** to extract AssetBundles to another folder, and then read.

### Extract/Decompress AssetBundles

Use **File-Extract file** or **File-Extract folder**.

### Export Assets

use **Export** menu.

### Export Model

Export model from "Scene Hierarchy" using the **Model** menu.

Export Animator from "Asset List" using the **Export** menu.

#### With AnimationClip

Select model from "Scene Hierarchy" then select the AnimationClip from "Asset List", using **Model-Export selected objects with AnimationClip** to export.

Export Animator will export bound AnimationClip or use **Ctrl** to select Animator and AnimationClip from "Asset List", using **Export-Export Animator with selected AnimationClip** to export.

### Export MonoBehaviour

When you select an asset of the MonoBehaviour type for the first time, AssetStudio will ask you the directory where the assembly is located, please select the directory where the assembly is located, such as the `Managed` folder.

#### For Il2Cpp

First, use my another program [Il2CppDumper](https://github.com/Perfare/Il2CppDumper) to generate dummy dll, then when using AssetStudio to select the assembly directory, select the dummy dll folder.

## Build

* Visual Studio 2022 or newer
* **AssetStudioFBXNative** uses [FBX SDK 2020.2.1](https://www.autodesk.com/developer-network/platform-technologies/fbx-sdk-2020-2-1), before building, you need to install the FBX SDK and modify the project file, change include directory and library directory to point to the FBX SDK directory

## Open source libraries used

### Texture2DDecoder
* [Ishotihadus/mikunyan](https://github.com/Ishotihadus/mikunyan)
* [BinomialLLC/crunch](https://github.com/BinomialLLC/crunch)
* [Unity-Technologies/crunch](https://github.com/Unity-Technologies/crunch/tree/unity)

## License

AssetStudio is licensed under the [MIT](./LICENSE) license.

## Credits
If you find this tool useful, please mention my name in your credits screen. Something like "AssetStudio by Perfare & zhangjiequan" or "Thanks to Perfare & zhangjiequan" would be very much appreciated.

## Collaborate
Feel free to fork the project and make modifications for yourself or to share by creating pull requests. Also, create issues for feature requests or bug reports if you want to help improving this tool, thanks!

## Contact
Contact me at zhangjiequan@qq.com
