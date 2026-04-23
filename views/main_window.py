from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QListWidget, QLabel, QFileDialog, QApplication,
                             QListWidgetItem, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt
from models.file_model import FileItem, ItemType
from viewmodels.main_viewmodel import MainViewModel
from views.delete_confirm_dialog import DeleteConfirmDialog
from views.loading_dialog import LoadingDialog


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._viewmodel = MainViewModel()
        self._loading_dialog = LoadingDialog(self)
        self._loading_dialog.setModal(True)
        self._loading_dialog.rejected.connect(self._on_search_canceled)
        self._setup_ui()
        self._bind_signals()

    def _setup_ui(self):
        self.setWindowTitle("Toolbar - 文件搜索工具")
        self.setMinimumSize(800, 600)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        path_layout = QHBoxLayout()
        path_layout.setSpacing(10)
        path_layout.addWidget(QLabel("根目录:"))
        self._path_input = QLineEdit()
        self._path_input.setPlaceholderText("手动输入路径或点击选择按钮...")
        self._path_input.returnPressed.connect(self._on_path_input_entered)
        path_layout.addWidget(self._path_input, 1)
        self._select_dir_btn = QPushButton("选择目录")
        self._select_dir_btn.clicked.connect(self._on_select_directory)
        path_layout.addWidget(self._select_dir_btn)
        main_layout.addLayout(path_layout)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("输入关键字进行模糊搜索...")
        self._search_input.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self._search_input)
        self._search_btn = QPushButton("搜索")
        self._search_btn.clicked.connect(self._on_search_clicked)
        search_layout.addWidget(self._search_btn)
        main_layout.addLayout(search_layout)

        self._result_list = QListWidget()
        self._result_list.setSpacing(5)
        main_layout.addWidget(self._result_list)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self._select_all_checkbox = QCheckBox("全选")
        self._select_all_checkbox.stateChanged.connect(self._on_select_all_changed)
        button_layout.addWidget(self._select_all_checkbox)
        self._selection_count_label = QLabel("(0)")
        self._selection_count_label.setStyleSheet("color: #666; font-size: 12px;")
        button_layout.addWidget(self._selection_count_label)
        button_layout.addStretch()
        self._delete_btn = QPushButton("删除")
        self._delete_btn.clicked.connect(self._on_delete_clicked)
        self._delete_btn.setEnabled(False)
        button_layout.addWidget(self._delete_btn)
        main_layout.addLayout(button_layout)

        self._status_label = QLabel("就绪")
        self._status_label.setStyleSheet("color: #666; font-size: 12px;")
        main_layout.addWidget(self._status_label)

        self.setLayout(main_layout)

    def _on_select_all_changed(self, state):
        is_checked = (state != 0)
        
        # 先更新状态字典
        for index in self._checked_items:
            self._checked_items[index] = is_checked
        
        # 批量更新所有复选框状态，使用 blockSignals 避免触发信号
        for index in self._checked_items:
            list_item = self._result_list.item(index)
            checkbox = self._result_list.itemWidget(list_item)
            # 阻止信号
            checkbox.blockSignals(True)
            # 设置状态
            checkbox.setChecked(is_checked)
            # 恢复信号
            checkbox.blockSignals(False)
        
        # 更新状态
        self._update_selection_count()
        self._update_delete_button_state()

    def _bind_signals(self):
        self._viewmodel.search_results_changed.connect(self._on_search_results_changed)
        self._viewmodel.delete_confirm_requested.connect(self._on_delete_confirm_requested)
        self._viewmodel.status_message_changed.connect(self._on_status_message_changed)
        self._viewmodel.search_started.connect(self._on_search_started)
        self._viewmodel.search_finished.connect(self._on_search_finished)

    def _on_select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择根目录")
        if dir_path:
            self._viewmodel.set_root_directory(dir_path)
            self._path_input.setText(dir_path)

    def _on_path_input_entered(self):
        import os
        dir_path = self._path_input.text().strip()
        if dir_path:
            if os.path.isdir(dir_path):
                self._viewmodel.set_root_directory(dir_path)
                self._status_label.setText(f"已设置根目录: {dir_path}")
            else:
                # 路径非法时给出弹窗提示
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("错误")
                msg_box.setText(f"路径 '{dir_path}' 不是有效的目录")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.setModal(True)  # 设置为模态
                msg_box.exec()
                self._status_label.setText(f"错误：路径 '{dir_path}' 不是有效的目录")

    def _on_search_text_changed(self, text: str):
        if not text:
            self._viewmodel.search("")

    def _on_search_clicked(self):
        import os
        from PyQt6.QtWidgets import QMessageBox
        # 先验证根目录
        dir_path = self._path_input.text().strip()
        if not dir_path or not os.path.isdir(dir_path):
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("错误")
            msg_box.setText("输入的根路径不合法")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            return
        
        # 设置根目录
        self._viewmodel.set_root_directory(dir_path)
        
        # 验证搜索关键字
        keyword = self._search_input.text().strip()
        if not keyword:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("提示")
            msg_box.setText("请输入正确的关键词")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setModal(True)  # 设置为模态
            msg_box.exec()
            return
        
        # 执行搜索
        self._viewmodel.search(keyword)

    def _on_search_results_changed(self, results: list):
        self._result_list.clear()
        self._checked_items = {}
        for index, item in enumerate(results):
            list_item = QListWidgetItem()
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            
            checkbox = QCheckBox()
            icon = "📁" if item.item_type == ItemType.FOLDER else "📄"
            checkbox.setText(f"{icon} {item.path}")
            checkbox.stateChanged.connect(lambda state, idx=index: self._on_item_checked(state, idx))
            
            self._result_list.addItem(list_item)
            self._result_list.setItemWidget(list_item, checkbox)
            self._checked_items[index] = False
        
        self._update_select_all_state()
        self._update_delete_button_state()
        self._update_selection_count()
    
    def _on_item_checked(self, state, index):
        print(f"_on_item_checked: state={state}, index={index}")
        self._checked_items[index] = (state != 0)
        print(f"  After update: {self._checked_items}")
        self._update_select_all_state()
        self._update_delete_button_state()
        self._update_selection_count()
    
    def _update_select_all_state(self):
        if not self._checked_items:
            self._select_all_checkbox.blockSignals(True)
            self._select_all_checkbox.setCheckState(Qt.CheckState.Unchecked)
            self._select_all_checkbox.blockSignals(False)
            return
        
        checked_count = sum(1 for checked in self._checked_items.values() if checked)
        total_count = len(self._checked_items)
        
        if checked_count == total_count:
            self._select_all_checkbox.blockSignals(True)
            self._select_all_checkbox.setCheckState(Qt.CheckState.Checked)
            self._select_all_checkbox.blockSignals(False)
        else:
            self._select_all_checkbox.blockSignals(True)
            self._select_all_checkbox.setCheckState(Qt.CheckState.Unchecked)
            self._select_all_checkbox.blockSignals(False)
    
    def _update_delete_button_state(self):
        has_selection = any(self._checked_items.values())
        self._delete_btn.setEnabled(has_selection)
    
    def _update_selection_count(self):
        count = sum(1 for checked in self._checked_items.values() if checked)
        self._selection_count_label.setText(f"({count})")
    
    def _on_delete_clicked(self):
        selected_indexes = [idx for idx, checked in self._checked_items.items() if checked]
        if not selected_indexes:
            return
        
        # 收集所有选中的项目
        selected_items = []
        for index in selected_indexes:
            list_item = self._result_list.item(index)
            item = list_item.data(Qt.ItemDataRole.UserRole)
            if item:
                selected_items.append(item)
        
        count = len(selected_items)
        if count == 0:
            return
        
        reply = QMessageBox.question(self, "确认删除", f"确定要删除选中的 {count} 个项目吗？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # 调用批量删除方法
            deleted_count = self._viewmodel.delete_items(selected_items)
            
            # 显示详细的删除结果
            import os
            permission_denied_count = 0
            other_failed_count = 0
            
            for item in selected_items:
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
                        permission_denied_count += 1
                    else:
                        # 有写权限但删除失败，是其他原因
                        other_failed_count += 1
            
            # 构建消息
            messages = []
            if deleted_count > 0:
                messages.append(f"已成功删除 {deleted_count} 个项目")
            if permission_denied_count > 0:
                messages.append(f"权限不足，无法删除 {permission_denied_count} 个项目")
            if other_failed_count > 0:
                messages.append(f"其他原因导致 {other_failed_count} 个项目删除失败")
            
            # 确保至少有一条消息
            if not messages:
                messages.append("删除操作完成")
            
            # 显示弹窗提示
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("删除结果")
            msg_box.setText('\n'.join(messages))
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setModal(True)
            msg_box.exec()
            
            # 更新状态栏
            self._status_label.setText('; '.join(messages))
    
    def _on_item_clicked(self, list_item):
        pass

    def _on_delete_confirm_requested(self, item: FileItem):
        type_str = "folder" if item.item_type == ItemType.FOLDER else "file"
        dialog = DeleteConfirmDialog(item.name, type_str, self)
        if dialog.exec():
            index = self._result_list.currentRow()
            self._viewmodel.confirm_delete(index)

    def _on_status_message_changed(self, message: str):
        self._status_label.setText(message)
    
    def _on_search_started(self):
        self._search_btn.setEnabled(False)
        self._search_btn.setText("搜索中...")
        # 以模态方式显示，确保点击非弹窗区域不会关闭
        self._loading_dialog.setModal(True)
        self._loading_dialog.show()
    
    def _on_search_finished(self):
        self._loading_dialog.hide()
        self._search_btn.setEnabled(True)
        self._search_btn.setText("搜索")
    
    def _on_search_canceled(self):
        self._loading_dialog.hide()
        self._search_btn.setEnabled(True)
        self._search_btn.setText("搜索")
        self._viewmodel.cancel_search()

    def closeEvent(self, event):
        if self._loading_dialog.isVisible():
            self._loading_dialog.hide()
        
        self._viewmodel.cleanup()
        self._loading_dialog.deleteLater()
        event.accept()