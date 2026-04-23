import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Generator, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class ItemType(Enum):
    FILE = "file"
    FOLDER = "folder"


@dataclass
class FileItem:
    path: str
    name: str
    item_type: ItemType


class FileModel:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self._cache = None
        self._cache_lock = threading.Lock()

    def _compile_pattern(self, keyword: str) -> re.Pattern:
        """编译正则表达式模式，支持模糊匹配"""
        # 将关键字转换为正则表达式模式
        # 例如 "abc" -> ".*a.*b.*c.*"
        pattern = '.*' + '.*'.join(re.escape(c) for c in keyword) + '.*'
        return re.compile(pattern, re.IGNORECASE)

    def _scan_directory(self, dirpath: str, dirnames: List[str], filenames: List[str], 
                       pattern: re.Pattern, cancel_flag=None) -> Generator[FileItem, None, None]:
        """扫描单个目录，返回匹配的文件项"""
        # 检查当前目录是否匹配
        current_dir = os.path.basename(dirpath)
        is_root_dir = dirpath == self.root_dir
        
        if current_dir and not is_root_dir:
            if pattern.search(current_dir):
                yield FileItem(
                    path=dirpath,
                    name=current_dir,
                    item_type=ItemType.FOLDER
                )
                # 匹配到文件夹，跳过子目录
                dirnames.clear()
                return
        
        # 检查文件
        for filename in filenames:
            if cancel_flag and cancel_flag():
                return
            if pattern.search(filename):
                full_path = os.path.join(dirpath, filename)
                yield FileItem(
                    path=full_path,
                    name=filename,
                    item_type=ItemType.FILE
                )

    def fuzzy_search(self, keyword: str, cancel_flag=None) -> List[FileItem]:
        """优化的模糊搜索，使用正则表达式和多线程"""
        if not keyword:
            return []
        
        results = []
        pattern = self._compile_pattern(keyword)
        
        # 使用多线程并行处理目录
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            for dirpath, dirnames, filenames in os.walk(self.root_dir):
                if cancel_flag and cancel_flag():
                    # 取消所有未完成的任务
                    for future in futures:
                        future.cancel()
                    break
                
                # 提交目录扫描任务
                future = executor.submit(
                    lambda dp, dns, fns: list(self._scan_directory(dp, dns, fns, pattern, cancel_flag)),
                    dirpath, dirnames[:], filenames[:]
                )
                futures.append(future)
            
            # 收集结果
            for future in as_completed(futures):
                if cancel_flag and cancel_flag():
                    break
                try:
                    items = future.result()
                    results.extend(items)
                except Exception:
                    pass
        
        return results

    def fuzzy_search_fast(self, keyword: str, cancel_flag=None) -> List[FileItem]:
        """更快的搜索，使用简单的字符串匹配（适合大多数场景）"""
        if not keyword:
            return []
        
        results = []
        keyword_lower = keyword.lower()
        keyword_len = len(keyword_lower)
        
        # 预编译路径分隔符
        path_sep = os.sep
        
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            if cancel_flag and cancel_flag():
                break
            
            # 快速检查当前目录是否匹配
            current_dir = os.path.basename(dirpath)
            is_root_dir = dirpath == self.root_dir
            
            if current_dir and not is_root_dir:
                # 使用 find 方法比 in 操作符更快
                if current_dir.lower().find(keyword_lower) != -1:
                    results.append(FileItem(
                        path=dirpath,
                        name=current_dir,
                        item_type=ItemType.FOLDER
                    ))
                    dirnames.clear()
                    continue
            
            # 批量处理文件，减少循环开销
            if filenames:
                # 使用列表推导式批量匹配
                matching_files = [
                    (filename, os.path.join(dirpath, filename))
                    for filename in filenames
                    if filename.lower().find(keyword_lower) != -1
                ]
                
                for filename, full_path in matching_files:
                    if cancel_flag and cancel_flag():
                        break
                    results.append(FileItem(
                        path=full_path,
                        name=filename,
                        item_type=ItemType.FILE
                    ))
        
        return results

    def delete_item(self, item: FileItem) -> bool:
        try:
            print(f"尝试删除: {item.path}, 类型: {item.item_type}")
            if item.item_type == ItemType.FOLDER:
                import shutil
                shutil.rmtree(item.path)
                print(f"成功删除文件夹: {item.path}")
            else:
                os.remove(item.path)
                print(f"成功删除文件: {item.path}")
            return True
        except PermissionError:
            print(f"权限不足，无法删除: {item.path}")
            return False
        except Exception as e:
            print(f"删除失败: {e}")
            return False