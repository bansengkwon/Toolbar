#!/usr/bin/env python3
"""
打包脚本：将 Toolbar 项目打包成可执行文件
支持 macOS (.dmg) 和 Windows (.exe)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def install_dependencies():
    """安装打包所需的依赖"""
    print("安装打包依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"], check=True)
    print("依赖安装完成")


def build_macos():
    """构建 macOS 应用"""
    print("\n=== 构建 macOS 应用 ===")
    
    # PyInstaller 配置
    cmd = [
        "pyinstaller",
        "--name=Toolbar",
        "--windowed",  # GUI 应用，不显示控制台
        "--onefile",   # 打包成单个文件
        "--icon=resources/icon.icns",  # macOS 图标
        "--add-data=resources:resources",  # 添加资源文件
        "--clean",     # 清理临时文件
        "--noconfirm", # 不确认覆盖
        "main.py"
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists("resources/icon.icns"):
        cmd.remove("--icon=resources/icon.icns")
    
    subprocess.run(cmd, check=True)
    
    # 创建 DMG
    print("创建 DMG 文件...")
    
    # 检查是否存在 create-dmg 工具
    if shutil.which("create-dmg"):
        dmg_cmd = [
            "create-dmg",
            "--volname", "Toolbar",
            "--window-pos", "200", "120",
            "--window-size", "600", "400",
            "--icon-size", "100",
            "--app-drop-link", "450", "185",
            "dist/Toolbar.dmg",
            "dist/Toolbar.app"
        ]
        subprocess.run(dmg_cmd, check=True)
    else:
        # 使用 hdiutil 创建简单的 DMG
        dmg_cmd = [
            "hdiutil", "create",
            "-volname", "Toolbar",
            "-srcfolder", "dist/Toolbar.app",
            "-ov",
            "dist/Toolbar.dmg"
        ]
        subprocess.run(dmg_cmd, check=True)
    
    print("macOS 应用打包完成: dist/Toolbar.dmg")


def build_windows():
    """构建 Windows 应用"""
    print("\n=== 构建 Windows 应用 ===")
    
    # PyInstaller 配置
    cmd = [
        "pyinstaller",
        "--name=Toolbar",
        "--windowed",  # GUI 应用，不显示控制台
        "--onefile",   # 打包成单个文件
        "--icon=resources/icon.ico",  # Windows 图标
        "--add-data=resources;resources",  # 添加资源文件（Windows 使用分号）
        "--clean",     # 清理临时文件
        "--noconfirm", # 不确认覆盖
        "main.py"
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists("resources/icon.ico"):
        cmd.remove("--icon=resources/icon.ico")
    
    subprocess.run(cmd, check=True)
    
    print("Windows 应用打包完成: dist/Toolbar.exe")


def create_resources():
    """创建资源目录和默认图标"""
    if not os.path.exists("resources"):
        os.makedirs("resources")
        print("创建 resources 目录")
    
    # 创建简单的图标说明文件
    readme_path = "resources/README.txt"
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write("""图标文件说明:
- icon.icns: macOS 应用图标 (512x512 像素)
- icon.ico: Windows 应用图标 (256x256 像素)

可以使用在线工具转换:
- https://cloudconvert.com/ (支持多种格式转换)
- https://www.icoconverter.com/ (ICO 转换)
""")


def main():
    """主函数"""
    print("Toolbar 打包工具")
    print("=" * 50)
    
    # 安装依赖
    try:
        install_dependencies()
    except subprocess.CalledProcessError:
        print("依赖安装失败，请手动安装: pip install pyinstaller")
        return
    
    # 创建资源目录
    create_resources()
    
    # 根据平台构建
    current_platform = sys.platform
    
    if current_platform == "darwin":
        # macOS
        try:
            build_macos()
        except subprocess.CalledProcessError as e:
            print(f"macOS 构建失败: {e}")
            sys.exit(1)
    elif current_platform == "win32":
        # Windows
        try:
            build_windows()
        except subprocess.CalledProcessError as e:
            print(f"Windows 构建失败: {e}")
            sys.exit(1)
    else:
        print(f"不支持的平台: {current_platform}")
        print("支持的系统: macOS (darwin), Windows (win32)")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("打包完成！")
    print(f"输出目录: {os.path.abspath('dist')}")


if __name__ == "__main__":
    main()
