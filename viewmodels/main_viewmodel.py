from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
from typing import List, Optional
from models.file_model import FileModel, FileItem, ItemType


class SearchTask(QRunnable):
    def __init__(self, model: FileModel, keyword: str, callback):
        super().__init__()
        self._model = model
        self._keyword = keyword
        self._callback = callback
        self._is_cancelled = False
    
    def run(self):
        if not self._is_cancelled:
            # 传递取消标志函数给模糊搜索
            def cancel_flag():
                return self._is_cancelled
            
            results = self._model.fuzzy_search(self._keyword, cancel_flag)
            if not self._is_cancelled:
                self._callback(results)
    
    def cancel(self):
        self._is_cancelled = True


class SearchTaskFast(QRunnable):
    """更快的搜索任务，使用优化的搜索算法"""
    def __init__(self, model: FileModel, keyword: str, callback, status_callback=None):
        super().__init__()
        self._model = model
        self._keyword = keyword
        self._callback = callback
        self._status_callback = status_callback
        self._is_cancelled = False
    
    def run(self):
        import time
        start_time = time.time()
        
        if not self._is_cancelled:
            # 传递取消标志函数给模糊搜索
            def cancel_flag():
                return self._is_cancelled
            
            # 使用更快的搜索方法
            results = self._model.fuzzy_search_fast(self._keyword, cancel_flag)
            
            elapsed_time = time.time() - start_time
            
            if not self._is_cancelled:
                if self._status_callback:
                    self._status_callback(f"搜索完成，耗时 {elapsed_time:.2f} 秒，找到 {len(results)} 个匹配项")
                self._callback(results)
    
    def cancel(self):
        self._is_cancelled = True


class MainViewModel(QObject):
    search_results_changed = pyqtSignal(list)
    delete_confirm_requested = pyqtSignal(FileItem)
    status_message_changed = pyqtSignal(str)
    search_started = pyqtSignal()
    search_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._model: Optional[FileModel] = None
        self._current_keyword: str = ""
        self._results: List[FileItem] = []
        self._thread_pool = QThreadPool()
        self._current_task: Optional[SearchTask] = None

    def set_root_directory(self, path: str):
        self._model = FileModel(path)
        self.status_message_changed.emit(f"已设置根目录: {path}")

    def search(self, keyword: str):
        # 取消之前的任务
        if self._current_task:
            self._current_task.cancel()
        
        self._current_keyword = keyword
        if not self._model:
            self.status_message_changed.emit("请先选择根目录")
            return

        if not keyword:
            self._results = []
            self.search_results_changed.emit([])
            return

        self.search_started.emit()
        self.status_message_changed.emit("正在搜索中...")
        
        def on_search_finished(results):
            self._current_task = None
            self._results = results
            self.search_results_changed.emit(self._results)
            self.search_finished.emit()
        
        def on_status_update(message):
            self.status_message_changed.emit(message)
        
        # 使用更快的搜索方法
        self._current_task = SearchTaskFast(self._model, keyword, on_search_finished, on_status_update)
        self._thread_pool.start(self._current_task)
    
    def cancel_search(self):
        if self._current_task:
            self._current_task.cancel()
            self._current_task = None
            # 清空结果，确保不会显示已取消的搜索结果
            self._results = []
            self.search_results_changed.emit([])
            self.status_message_changed.emit("搜索已取消")
            self.search_finished.emit()
    
    def cleanup(self):
        self.cancel_search()
        self._thread_pool.waitForDone(1000)

    def get_result_at_index(self, index: int) -> Optional[FileItem]:
        if 0 <= index < len(self._results):
            return self._results[index]
        return None

    def request_delete(self, index: int):
        item = self.get_result_at_index(index)
        if item:
            self.delete_confirm_requested.emit(item)

    def confirm_delete(self, index: int) -> bool:
        if not self._model:
            self.status_message_changed.emit("请先设置根目录")
            return False
            
        item = self.get_result_at_index(index)
        if not item:
            return False

        success = self._model.delete_item(item)
        if success:
            # 重新搜索以更新结果
            self.search(self._current_keyword)
            self.status_message_changed.emit(f"已删除: {item.name}")
        else:
            self.status_message_changed.emit(f"删除失败: {item.name}")
        return success
    
    def delete_items(self, items: List[FileItem]) -> int:
        """批量删除多个项目"""
        if not self._model:
            self.status_message_changed.emit("请先设置根目录")
            return 0
        
        deleted_count = 0
        permission_denied = 0
        other_failed = 0
        
        for item in items:
            try:
                if self._model.delete_item(item):
                    deleted_count += 1
                else:
                    # 检查是否是权限不足
                    import os
                    if os.path.exists(item.path):
                        # 检查是否有删除权限
                        # 对于文件夹，尝试创建临时文件来测试写权限
                        # 对于文件，尝试打开写入模式
                        has_permission = True
                        try:
                            if item.item_type == ItemType.FOLDER:
                                # 尝试在父目录创建临时文件
                                parent_dir = os.path.dirname(item.path)
                                if parent_dir:
                                    test_file = os.path.join(parent_dir, '.delete_test_' + str(os.getpid()))
                                    with open(test_file, 'w') as f:
                                        f.write('test')
                                    os.remove(test_file)
                            else:
                                # 尝试以写入模式打开文件
                                with open(item.path, 'a'):
                                    pass
                        except (PermissionError, OSError):
                            has_permission = False
                        
                        if not has_permission:
                            # 没有写权限，权限不足
                            permission_denied += 1
                        else:
                            # 有写权限但删除失败，是其他原因
                            other_failed += 1
                    else:
                        # 文件/文件夹已不存在
                        deleted_count += 1
            except Exception as e:
                print(f"处理 {item.path} 时出错: {e}")
                other_failed += 1
        
        # 构建消息
        messages = []
        if deleted_count > 0:
            messages.append(f"已成功删除 {deleted_count} 个项目")
        if permission_denied > 0:
            messages.append(f"权限不足，无法删除 {permission_denied} 个项目")
        if other_failed > 0:
            messages.append(f"其他原因导致 {other_failed} 个项目删除失败")
        
        if messages:
            self.status_message_changed.emit('; '.join(messages))
        else:
            self.status_message_changed.emit("删除操作完成")
        
        if deleted_count > 0:
            # 重新搜索以更新结果
            self.search(self._current_keyword)
        
        return deleted_count