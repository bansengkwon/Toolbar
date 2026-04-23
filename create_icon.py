#!/usr/bin/env python3
"""
图标生成脚本
创建简单的默认图标用于打包
"""

import os
from PIL import Image, ImageDraw, ImageFont


def create_default_icon(size=512):
    """创建默认的应用图标"""
    # 创建图片
    img = Image.new('RGBA', (size, size), color=(59, 130, 246, 255))  # 蓝色背景
    draw = ImageDraw.Draw(img)
    
    # 绘制简单的文件夹图标
    margin = size // 8
    folder_color = (255, 255, 255, 255)  # 白色
    
    # 文件夹主体
    folder_top = margin * 2
    folder_bottom = size - margin
    folder_left = margin
    folder_right = size - margin
    
    # 绘制文件夹形状
    draw.rectangle(
        [folder_left, folder_top + margin//2, folder_right, folder_bottom],
        fill=folder_color,
        outline=(200, 200, 200, 255),
        width=2
    )
    
    # 文件夹标签
    tab_width = (folder_right - folder_left) // 3
    tab_height = margin // 2
    draw.rectangle(
        [folder_left, folder_top, folder_left + tab_width, folder_top + tab_height],
        fill=folder_color
    )
    
    # 添加文字 "TB"
    try:
        font_size = size // 4
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "TB"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 + margin // 2
    
    draw.text((text_x, text_y), text, fill=(59, 130, 246, 255), font=font)
    
    return img


def create_macos_icon():
    """创建 macOS 图标 (.icns)"""
    print("创建 macOS 图标...")
    
    # 创建 1024x1024 的基础图标
    base_icon = create_default_icon(1024)
    
    # 创建图标集
    iconset_dir = "resources/icon.iconset"
    os.makedirs(iconset_dir, exist_ok=True)
    
    sizes = [
        (16, 16),
        (32, 32),
        (64, 64),
        (128, 128),
        (256, 256),
        (512, 512),
        (1024, 1024)
    ]
    
    for width, height in sizes:
        icon = base_icon.resize((width, height), Image.Resampling.LANCZOS)
        
        # 普通分辨率
        if width <= 512:
            icon.save(f"{iconset_dir}/icon_{width}x{height}.png")
        
        # 双倍分辨率 (@2x)
        if width <= 512:
            icon_2x = base_icon.resize((width*2, height*2), Image.Resampling.LANCZOS)
            icon_2x.save(f"{iconset_dir}/icon_{width}x{height}@2x.png")
    
    # 使用 iconutil 编译成 icns
    result = os.system(f"iconutil -c icns {iconset_dir} -o resources/icon.icns")
    
    # 清理
    import shutil
    shutil.rmtree(iconset_dir)
    
    if result == 0:
        print("✓ macOS 图标创建成功: resources/icon.icns")
    else:
        print("✗ macOS 图标创建失败，请手动安装 iconutil")
        # 保存为 PNG 作为备用
        base_icon.save("resources/icon.png")
        print("  已保存为 resources/icon.png")


def create_windows_icon():
    """创建 Windows 图标 (.ico)"""
    print("创建 Windows 图标...")
    
    # 创建 256x256 的基础图标
    base_icon = create_default_icon(256)
    
    # 创建不同尺寸的图标
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = []
    
    for width, height in sizes:
        icon = base_icon.resize((width, height), Image.Resampling.LANCZOS)
        icons.append(icon)
    
    # 保存为 ICO
    icons[0].save(
        "resources/icon.ico",
        format='ICO',
        sizes=sizes,
        append_images=icons[1:]
    )
    
    print("✓ Windows 图标创建成功: resources/icon.ico")


def main():
    """主函数"""
    print("Toolbar 图标生成工具")
    print("=" * 40)
    
    # 创建资源目录
    os.makedirs("resources", exist_ok=True)
    
    # 创建图标
    try:
        create_macos_icon()
    except Exception as e:
        print(f"macOS 图标创建失败: {e}")
    
    try:
        create_windows_icon()
    except Exception as e:
        print(f"Windows 图标创建失败: {e}")
    
    print("\n" + "=" * 40)
    print("图标生成完成！")
    print("文件位置: resources/")


if __name__ == "__main__":
    main()
