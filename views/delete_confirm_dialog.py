from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt


class DeleteConfirmDialog(QDialog):
    def __init__(self, item_name: str, item_type: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("确认删除")
        self.setModal(True)
        self._setup_ui(item_name, item_type)

    def _setup_ui(self, item_name: str, item_type: str):
        layout = QVBoxLayout()

        type_text = "文件夹" if item_type == "folder" else "文件"
        message = QLabel(f"确定要删除该{type_text}吗？\n\n{item_name}\n\n此操作不可恢复！")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self._confirm_btn = QPushButton("确认删除")
        self._confirm_btn.setObjectName("dangerBtn")
        self._confirm_btn.clicked.connect(self.accept)
        button_layout.addWidget(self._confirm_btn)

        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)