from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QSize


class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("搜索中")
        self.setModal(True)
        self.setFixedSize(QSize(350, 120))
        # 设置窗口标志：对话框 | 标题栏 | 关闭按钮 | 自定义窗口提示
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowTitleHint | 
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.CustomizeWindowHint
        )
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        self._message = QLabel("正在搜索文件...")
        self._message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._message.setStyleSheet("font-size: 14px; font-weight: 500;")
        layout.addWidget(self._message)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # 不确定进度
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: #f5f5f5;
                height: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self._progress)

        self.setLayout(layout)