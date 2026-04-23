# Toolbar 打包指南

本文档介绍如何将 Toolbar 项目打包成可执行文件。

## 支持的平台

- **macOS**: `.dmg` 格式
- **Windows**: `.exe` 格式

## 快速开始

### 1. 安装依赖

```bash
pip install pyinstaller
```

### 2. 运行打包脚本

```bash
python build.py
```

打包完成后，可执行文件会在 `dist/` 目录中。

## 手动打包

### macOS (.dmg)

#### 步骤 1: 使用 PyInstaller 创建应用

```bash
pyinstaller \
  --name=Toolbar \
  --windowed \
  --onefile \
  --icon=resources/icon.icns \
  --add-data="resources:resources" \
  --clean \
  --noconfirm \
  main.py
```

#### 步骤 2: 创建 DMG 文件

**方法 A: 使用 create-dmg (推荐)**

```bash
# 安装 create-dmg
brew install create-dmg

# 创建 DMG
create-dmg \
  --volname "Toolbar" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 450 185 \
  "dist/Toolbar.dmg" \
  "dist/Toolbar.app"
```

**方法 B: 使用 hdiutil (系统自带)**

```bash
hdiutil create \
  -volname "Toolbar" \
  -srcfolder "dist/Toolbar.app" \
  -ov \
  "dist/Toolbar.dmg"
```

### Windows (.exe)

#### 步骤 1: 使用 PyInstaller 创建可执行文件

```bash
pyinstaller \
  --name=Toolbar \
  --windowed \
  --onefile \
  --icon=resources/icon.ico \
  --add-data="resources;resources" \
  --clean \
  --noconfirm \
  main.py
```

**注意**: Windows 上 `--add-data` 使用分号 `;` 作为分隔符，macOS 使用冒号 `:`。

#### 步骤 2: (可选) 创建安装程序

可以使用 Inno Setup 或 NSIS 创建 Windows 安装程序。

## 图标制作

### macOS 图标 (.icns)

1. 准备 1024x1024 像素的 PNG 图片
2. 使用在线工具转换: https://cloudconvert.com/png-to-icns
3. 或者使用命令行:

```bash
# 创建图标集
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png

# 编译成 icns
iconutil -c icns icon.iconset

# 清理
rm -rf icon.iconset
```

### Windows 图标 (.ico)

1. 准备 256x256 像素的 PNG 图片
2. 使用在线工具转换: https://www.icoconverter.com/
3. 或者使用 Python:

```bash
pip install Pillow
```

```python
from PIL import Image

# 打开图片
img = Image.open("icon.png")

# 保存为 ICO
img.save("icon.ico", format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
```

## 目录结构

```
Toolbar/
├── main.py              # 主程序入口
├── build.py             # 打包脚本
├── requirements.txt     # 依赖列表
├── resources/           # 资源文件
│   ├── icon.icns       # macOS 图标
│   ├── icon.ico        # Windows 图标
│   └── README.txt      # 资源说明
├── models/             # 数据模型
├── views/              # 视图层
├── viewmodels/         # 视图模型层
└── dist/               # 打包输出目录 (自动生成)
    ├── Toolbar.dmg     # macOS 安装包
    └── Toolbar.exe     # Windows 可执行文件
```

## 常见问题

### Q: 打包后的应用无法运行？

**A**: 检查以下几点：
1. 确保所有依赖都已安装
2. 检查 `--add-data` 参数是否正确
3. 查看 PyInstaller 的日志输出

### Q: 图标没有显示？

**A**: 
- macOS: 确保图标格式为 `.icns`
- Windows: 确保图标格式为 `.ico`
- 检查图标文件路径是否正确

### Q: 如何减小打包后的文件大小？

**A**:
```bash
# 使用 UPX 压缩
pyinstaller --upx-dir=/path/to/upx ...

# 排除不必要的模块
pyinstaller --exclude-module=module_name ...
```

### Q: macOS 上提示"无法打开应用"？

**A**: 需要签名或调整安全设置：
```bash
# 移除隔离属性
xattr -rd com.apple.quarantine dist/Toolbar.app

# 或者签名（需要 Apple Developer ID）
codesign --deep --force --verify --verbose --sign "Developer ID" dist/Toolbar.app
```

## 高级配置

### 自定义 spec 文件

PyInstaller 会生成 `.spec` 文件，可以手动编辑以实现更复杂的配置：

```bash
# 生成 spec 文件
pyinstaller --name=Toolbar main.py

# 编辑 Toolbar.spec 文件
# 然后使用 spec 文件打包
pyinstaller Toolbar.spec
```

### 隐藏控制台（Windows）

```python
# 在 main.py 中添加
import sys

if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
```

## 参考链接

- [PyInstaller 官方文档](https://pyinstaller.readthedocs.io/)
- [create-dmg GitHub](https://github.com/create-dmg/create-dmg)
- [Inno Setup](https://jrsoftware.org/isinfo.php)
