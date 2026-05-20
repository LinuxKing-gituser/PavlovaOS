import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout, 
                             QFrame, QPushButton)
from PyQt6.QtGui import QPixmap, QPainter, QIcon, QColor, QFont
from PyQt6.QtCore import Qt, QTimer, QTime, QSize

# Hardware acceleration optimizations for Intel HD graphics
os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"
os.environ["LIBVA_DRIVER_NAME"] = "i965"

class PavlovaTaskbar(QFrame):
    def __init__(self, parent_shell):
        super().__init__()
        self.shell = parent_shell
        self.menu_process = None
        self.current_lang = "en"
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 0, 1366, 45) 
        
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 1366, 45)
        self.container.setStyleSheet("background-color: rgba(0, 0, 0, 160); border: none;")

        self.layout = QHBoxLayout(self.container)
        self.layout.setContentsMargins(15, 0, 15, 0)
        self.layout.setSpacing(15)

        self.setup_icons()
        self.layout.addStretch()

        self.clock = QLabel()
        self.clock.setStyleSheet("color: white; border: none; background: transparent;")
        self.layout.addWidget(self.clock)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        self.lang_timer = QTimer(self)
        self.lang_timer.timeout.connect(self.check_system_language)
        self.lang_timer.start(1000)
        
        self.check_system_language()
        self.update_time()

    def check_system_language(self):
        lang_file = os.path.expanduser("~/PavlovaOS/assets/lang.txt")
        if os.path.exists(lang_file):
            try:
                with open(lang_file, "r") as f:
                    latest_lang = f.read().strip()
                if latest_lang != self.current_lang:
                    self.current_lang = latest_lang
                    self.apply_live_translation()
            except: pass

    def apply_live_translation(self):
        if self.current_lang == "tl":
            self.clock.setFont(QFont("sans-serif", 12, QFont.Weight.Bold))
        else:
            self.clock.setFont(QFont("Comic Sans MS", 12, QFont.Weight.Bold))

    def setup_icons(self):
        icon_map = [
            ("super.png", "menu"),
            ("terminal-removebg-preview.png", "terminal"),
            ("chromium.png", "browser"),
            ("files.png", "explorer"),
            ("github.png", "github")
        ]

        for filename, target in icon_map:
            path = self.shell.find_file(filename)
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # --- FIXED: Taskbar hover set to Strawberry Pink Glow ---
            btn.setStyleSheet("""
                QPushButton { background: transparent; border: none; border-radius: 8px; } 
                QPushButton:hover { background-color: rgba(255, 102, 178, 60); }
            """)
            
            if path:
                btn.setIcon(QIcon(path))
                btn.setIconSize(QSize(28, 28))
            btn.clicked.connect(lambda checked, t=target: self.launch_app(t))
            self.layout.addWidget(btn)

    def launch_app(self, target):
        python_exe = sys.executable
        bin_dir = os.path.join(self.shell.project_dir, "bin")
        
        if target == "menu":
            if self.menu_process and self.menu_process.poll() is None:
                self.menu_process.terminate()
                self.menu_process = None
            else:
                path = os.path.join(bin_dir, "menu.py")
                if os.path.exists(path):
                    self.menu_process = subprocess.Popen([python_exe, path], start_new_session=True)
            return

        targets = {"terminal": "terminal.py", "browser": "browser.py", "explorer": "files.py"}
        script_name = targets.get(target, "browser.py")
        path = os.path.join(bin_dir, script_name)
        if os.path.exists(path):
            subprocess.Popen([python_exe, path], start_new_session=True)

    def update_time(self):
        self.clock.setText(QTime.currentTime().toString("hh:mm AP"))

class PavlovaShell(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        self.project_dir = os.path.join(os.path.expanduser("~"), "PavlovaOS")
        wall_path = self.find_file("Wallpaper.png")
        self.pixmap = QPixmap(wall_path) if wall_path else QPixmap()

    def find_file(self, target):
        if os.path.exists(self.project_dir):
            for root, dirs, files in os.walk(self.project_dir):
                if target in files: return os.path.join(root, target)
        return None

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.pixmap.isNull(): painter.drawPixmap(self.rect(), self.pixmap)
        else: painter.fillRect(self.rect(), QColor(10, 10, 15))

    def mousePressEvent(self, event):
        if hasattr(self, 'taskbar_ref'): self.taskbar_ref.raise_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    shell = PavlovaShell()
    shell.show()
    taskbar = PavlovaTaskbar(shell)
    shell.taskbar_ref = taskbar
    taskbar.show()
    sys.exit(app.exec())
