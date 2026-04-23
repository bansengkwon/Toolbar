# Toolbar - 文件搜索工具

一个基于 Python + PyQt6 开发的桌面文件搜索工具，支持模糊匹配搜索、批量删除等功能。

## 功能特性

- **文件/文件夹搜索**：支持模糊匹配，快速定位文件和文件夹
- **智能匹配**：文件夹匹配时自动跳过子目录，提高搜索效率
- **批量操作**：支持全选、批量删除文件和文件夹
- **实时反馈**：搜索过程显示加载动画，实时显示搜索耗时和结果数量
- **权限处理**：删除时自动检测权限，给出明确的错误提示
- **跨平台**：支持 macOS 和 Windows 系统

## 技术架构

项目采用 MVVM（Model-View-ViewModel）架构：

```
Toolbar/
├── models/              # 数据层
│   └── file_model.py   # 文件模型，处理文件系统操作
├── views/              # 视图层
│   ├── main_window.py          # 主窗口
│   ├── loading_dialog.py       # 加载对话框
│   └── delete_confirm_dialog.py # 删除确认对话框
├── viewmodels/         # 视图模型层
│   └── main_viewmodel.py       # 主视图模型，业务逻辑处理
├── main.py            # 程序入口
└── requirements.txt   # 依赖列表
```

## 安装要求

- Python 3.8+
- PyQt6 6.4.0+

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/bansengkwon/Toolbar.git
cd Toolbar
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行程序

```bash
python main.py
```

## 使用说明

### 基本使用流程

1. **设置根目录**
   - 在"根目录"输入框中手动输入路径
   - 或点击"选择目录"按钮浏览选择

2. **输入搜索关键字**
   - 在搜索框中输入要查找的文件或文件夹名称
   - 支持模糊匹配（如输入"doc"可匹配"document.txt"）

3. **开始搜索**
   - 点击"搜索"按钮或按回车键
   - 搜索过程中会显示加载对话框
   - 搜索完成后显示结果列表

4. **选择要删除的项目**
   - 勾选列表中的复选框选择项目
   - 或点击"全选"选择所有项目
   - 实时显示已选中数量

5. **删除项目**
   - 点击"删除"按钮
   - 确认删除对话框中点击"是"
   - 系统会显示删除结果（成功/失败/权限不足）

### 搜索规则

- **文件夹匹配**：如果文件夹名称匹配关键字，则显示该文件夹并跳过其子目录
- **文件匹配**：所有文件的名称都会与关键字进行匹配
- **忽略大小写**：搜索不区分大小写
- **实时统计**：搜索完成后显示耗时和匹配项数量

### 删除规则

- **权限检测**：删除前检测是否有写权限
- **批量删除**：支持同时删除多个文件/文件夹
- **结果反馈**：删除完成后显示详细结果
  - 成功删除的数量
  - 权限不足无法删除的数量
  - 其他原因导致失败的数量

## 打包发布

### macOS (.dmg)

```bash
python build.py
```

输出文件：`dist/Toolbar.dmg`

### Windows (.exe)

```bash
python build.py
```

输出文件：`dist/Toolbar.exe`

详细打包说明请参考 [PACKAGING.md](PACKAGING.md)

## 项目结构

```
Toolbar/
├── main.py                      # 程序入口
├── requirements.txt             # 依赖列表
├── README.md                    # 项目说明
├── PACKAGING.md                 # 打包指南
├── build.py                     # 打包脚本
├── create_icon.py               # 图标生成工具
├── models/
│   └── file_model.py           # 文件模型
│       ├── FileItem            # 文件项数据类
│       ├── ItemType            # 项目类型枚举（文件/文件夹）
│       ├── fuzzy_search()      # 多线程模糊搜索
│       ├── fuzzy_search_fast() # 快速模糊搜索
│       └── delete_item()       # 删除文件/文件夹
├── views/
│   ├── main_window.py          # 主窗口
│   │   ├── 根目录输入框       # 设置搜索根目录
│   │   ├── 搜索框             # 输入搜索关键字
│   │   ├── 结果列表           # 显示搜索结果
│   │   ├── 全选复选框         # 批量选择
│   │   ├── 选中数量显示       # 实时显示选中数量
│   │   └── 删除按钮           # 执行删除操作
│   ├── loading_dialog.py       # 加载对话框
│   └── delete_confirm_dialog.py # 删除确认对话框
└── viewmodels/
    └── main_viewmodel.py       # 视图模型
        ├── SearchTask          # 搜索任务（多线程正则）
        ├── SearchTaskFast      # 快速搜索任务
        ├── search()            # 执行搜索
        ├── delete_items()      # 批量删除
        └── 各种信号            # 与视图层通信
```

## 核心功能实现

### 1. 模糊搜索

使用优化的字符串匹配算法：

```python
def fuzzy_search_fast(self, keyword: str, cancel_flag=None) -> List[FileItem]:
    """快速模糊搜索"""
    results = []
    keyword_lower = keyword.lower()
    
    for dirpath, dirnames, filenames in os.walk(self.root_dir):
        # 检查目录是否匹配
        current_dir = os.path.basename(dirpath)
        if keyword_lower in current_dir.lower():
            results.append(FileItem(...))
            dirnames.clear()  # 跳过子目录
            continue
        
        # 检查文件是否匹配
        for filename in filenames:
            if keyword_lower in filename.lower():
                results.append(FileItem(...))
    
    return results
```

### 2. 批量删除

支持批量删除并处理权限问题：

```python
def delete_items(self, items: List[FileItem]) -> int:
    """批量删除多个项目"""
    deleted_count = 0
    permission_denied = 0
    other_failed = 0
    
    for item in items:
        if self._model.delete_item(item):
            deleted_count += 1
        else:
            # 检测权限问题
            if not os.access(item.path, os.W_OK):
                permission_denied += 1
            else:
                other_failed += 1
    
    return deleted_count
```

### 3. 全选功能

实现全选/取消全选，并处理信号阻塞避免递归：

```python
def _on_select_all_changed(self, state):
    is_checked = (state != 0)
    
    # 更新状态字典
    for index in self._checked_items:
        self._checked_items[index] = is_checked
    
    # 批量更新UI，阻止信号避免递归
    for index in self._checked_items:
        checkbox = self._result_list.itemWidget(list_item)
        checkbox.blockSignals(True)
        checkbox.setChecked(is_checked)
        checkbox.blockSignals(False)
```

## 性能优化

- **多线程搜索**：使用 `ThreadPoolExecutor` 并行处理目录
- **快速匹配**：使用 `str.find()` 代替正则表达式
- **批量处理**：使用列表推导式批量匹配文件名
- **信号优化**：使用 `blockSignals()` 避免递归触发

## 错误处理

- **路径验证**：输入路径时验证是否为有效目录
- **权限检测**：删除前检测写权限，给出明确提示
- **异常捕获**：所有文件操作都有 try-except 保护
- **用户反馈**：所有操作都有状态栏和弹窗提示

## 开发计划

- [ ] 支持正则表达式搜索
- [ ] 添加文件预览功能
- [ ] 支持搜索历史记录
- [ ] 添加文件过滤选项（按类型、大小、日期）
- [ ] 支持拖拽文件到列表
- [ ] 添加深色模式主题

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱：<your-email@example.com>
- GitHub Issues

---

**注意**：删除操作不可恢复，请谨慎使用！
