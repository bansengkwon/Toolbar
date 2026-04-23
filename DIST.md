# dist 目录文件说明

本文件描述了项目打包后 `dist` 目录中生成的文件及其区别。

## 文件类型及区别

### Toolbar.app

- **类型**：macOS 应用包（application bundle）
- **本质**：这是一个目录结构，包含了应用的所有资源、代码和配置文件
- **用途**：直接双击可以运行应用
- **结构**：包含 Contents 目录，内部有 MacOS、Resources 等子目录
- **特点**：符合 macOS 应用标准结构，用户体验好

### Toolbar

- **类型**：可执行文件（executable）
- **本质**：PyInstaller 生成的独立二进制文件
- **用途**：可以直接执行，但通常不直接提供给最终用户
- **特点**：是 `Toolbar.app/Contents/MacOS/` 目录下的实际可执行文件
- **使用**：在终端中可以直接运行 `./Toolbar`

### Toolbar.dmg

- **类型**：磁盘镜像文件（disk image）
- **本质**：一个包含应用的容器文件，类似于虚拟磁盘
- **用途**：用于应用分发，用户可以通过挂载 DMG 来安装应用
- **特点**：通常包含应用图标和 Applications 文件夹的快捷方式
- **使用**：双击打开后，可以将应用拖放到 Applications 文件夹

## 关系

- `Toolbar` 是核心可执行文件
- `Toolbar.app` 是包含 `Toolbar` 的应用包
- `Toolbar.dmg` 是包含 `Toolbar.app` 的分发容器

## 应用场景

- **开发测试**：直接使用 `Toolbar` 可执行文件
- **本地使用**：使用 `Toolbar.app` 应用包
- **分发给用户**：使用 `Toolbar.dmg` 磁盘镜像文件

## 生成说明

这些文件通过运行 `python build.py` 脚本生成：

- `Toolbar` 和 `Toolbar.app` 由 PyInstaller 直接生成
- `Toolbar.dmg` 由构建脚本创建，包含 `Toolbar.app`

## 分发建议

对于最终用户，建议使用 `Toolbar.dmg` 文件进行分发，因为：

1. 它提供了标准的 macOS 安装体验
2. 包含了完整的应用结构
3. 可以通过拖放方式安装到 Applications 文件夹
4. 便于用户管理和卸载应用
