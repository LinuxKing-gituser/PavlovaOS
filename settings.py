import sys
import os
import shutil
import platform
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QStackedWidget, QListWidget, QLabel, QComboBox, 
                             QFrame, QPushButton, QFileDialog, QColorDialog)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class PavlovaSettings(QWidget):
    def __init__(self):
        super().__init__()
        # Frameless window matching your custom desktop interface behavior
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(750, 500)
        
        # Center the window on your 1366x768 display layout
        self.move((1366 - 750) // 2, (768 - 500) // 2)
        
        # Project assets directories mapping
        self.project_dir = os.path.expanduser("~/PavlovaOS")
        self.assets_dir = os.path.join(self.project_dir, "assets")
        self.lang_file = os.path.join(self.assets_dir, "lang.txt")
        
        self.read_saved_language()

        # --- STYLING: Strawberry Pink Glass Layout Architecture ---
        self.setStyleSheet("""
            QWidget { background-color: transparent; color: white; }
            QFrame#MainContainer {
                background-color: rgba(13, 13, 19, 235);
                border: 2px solid rgba(255, 102, 178, 60);
                border-radius: 20px;
            }
            QListWidget { 
                background-color: rgba(255, 255, 255, 10); 
                border: 1px solid rgba(255, 102, 178, 40); 
                border-radius: 12px; 
                font-size: 14px; 
            }
            QListWidget::item { padding: 12px; color: #e0e0e0; }
            QListWidget::item:hover { background-color: rgba(255, 102, 178, 25); border-radius: 8px; }
            QListWidget::item:selected { background-color: rgba(255, 102, 178, 50); color: #ff66b2; border-radius: 8px; font-weight: bold; }
            QFrame#ContentPanel { 
                background-color: rgba(255, 255, 255, 10); 
                border: 1px solid rgba(255, 102, 178, 40); 
                border-radius: 12px; 
            }
            QLabel { background: transparent; color: white; font-family: 'sans-serif'; }
            QComboBox { 
                background-color: #1a1a24; 
                color: white; 
                border: 1px solid rgba(255, 102, 178, 80); 
                border-radius: 8px; 
                padding: 6px; 
                min-width: 180px; 
                font-family: 'sans-serif';
            }
            QComboBox::drop-down { border: none; }
            QPushButton {
                background-color: rgba(255, 255, 255, 15);
                border: 1px solid rgba(255, 255, 255, 10);
                color: white;
                font-family: 'sans-serif';
                font-size: 13px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 102, 178, 45);
                border: 1px solid rgba(255, 102, 178, 120);
            }
            QPushButton:pressed {
                background-color: rgba(255, 102, 178, 80);
            }
        """)

        # Core outer translucent container shell setup
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 750, 500)
        self.container.setObjectName("MainContainer")

        outer_layout = QVBoxLayout(self.container)
        outer_layout.setContentsMargins(25, 20, 25, 25)

        # Upper Title Bar Row + Close Action
        title_bar_layout = QHBoxLayout()
        self.window_title_lbl = QLabel("⚙️ PavlovaOS Core Settings")
        self.window_title_lbl.setStyleSheet("color: #ff66b2; font-size: 18px; font-weight: bold;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: #aaaaaa; font-size: 16px; padding: 0px; }
            QPushButton:hover { color: #ff66b2; background: transparent; border: none; }
        """)
        close_btn.clicked.connect(self.close)
        
        title_bar_layout.addWidget(self.window_title_lbl)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(close_btn)
        outer_layout.addLayout(title_bar_layout)
        outer_layout.addSpacing(10)

        # Main Workspace Splitter Layout
        workspace_layout = QHBoxLayout()
        workspace_layout.setSpacing(20)
        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        workspace_layout.addWidget(self.sidebar)

        self.pages = QStackedWidget()
        self.content_container = QFrame()
        self.content_container.setObjectName("ContentPanel")
        container_layout = QVBoxLayout(self.content_container)
        container_layout.setContentsMargins(25, 25, 25, 25)
        container_layout.addWidget(self.pages)
        workspace_layout.addWidget(self.content_container)
        outer_layout.addLayout(workspace_layout)

        # ================= PAGE 1: ABOUT SYSTEM =================
        self.page_about = QWidget()
        self.about_layout = QVBoxLayout(self.page_about)
        self.about_layout.setContentsMargins(0, 0, 0, 0)
        self.about_layout.setSpacing(15)
        
        self.about_title = QLabel()
        self.about_title.setFont(QFont("sans-serif", 16, QFont.Weight.Bold))
        self.about_title.setStyleSheet("color: #ff66b2;")
        self.about_layout.addWidget(self.about_title)
        
        # Read board names directly from sysfs layers safely
        try:
            with open("/sys/class/dmi/id/board_name", "r") as f: mobo = f.read().strip()
            with open("/sys/class/dmi/id/board_vendor", "r") as f: vendor = f.read().strip()
            mobo_info = f"{vendor} {mobo}"
        except: 
            mobo_info = "Acer Aspire Baseboard"
            
        info = f"<p style='line-height:160%; font-size:14px;'><b>OS Name:</b> PavlovaOS alpha<br><b>Kernel Level:</b> Linux {platform.release()}<br><b>Machine Target:</b> {mobo_info}<br><b>UI Architecture:</b> PyQt6 / Native Graphics Pipeline</p>"
        self.info_lbl = QLabel(info)
        self.about_layout.addWidget(self.info_lbl)
        self.about_layout.addStretch()
        self.pages.addWidget(self.page_about)

        # ================= PAGE 2: PERSONALIZATION =================
        self.page_visuals = QWidget()
        self.visuals_layout = QVBoxLayout(self.page_visuals)
        self.visuals_layout.setContentsMargins(0, 0, 0, 0)
        self.visuals_layout.setSpacing(15)
        
        self.visuals_title = QLabel()
        self.visuals_title.setFont(QFont("sans-serif", 16, QFont.Weight.Bold))
        self.visuals_title.setStyleSheet("color: #ff66b2;")
        self.visuals_layout.addWidget(self.visuals_title)
        
        appearance_btn_layout = QHBoxLayout()
        self.wall_btn = QPushButton()
        self.color_btn = QPushButton()
        
        self.wall_btn.clicked.connect(self.change_wallpaper)
        self.color_btn.clicked.connect(self.change_background_color)
        
        appearance_btn_layout.addWidget(self.wall_btn)
        appearance_btn_layout.addWidget(self.color_btn)
        appearance_btn_layout.addStretch()
        
        self.visuals_layout.addLayout(appearance_btn_layout)
        self.visuals_layout.addStretch()
        self.pages.addWidget(self.page_visuals)

        # ================= PAGE 3: LANGUAGES =================
        self.page_lang = QWidget()
        self.lang_layout = QVBoxLayout(self.page_lang)
        self.lang_layout.setContentsMargins(0, 0, 0, 0)
        self.lang_layout.setSpacing(15)
        
        self.lang_title = QLabel()
        self.lang_title.setFont(QFont("sans-serif", 16, QFont.Weight.Bold))
        self.lang_title.setStyleSheet("color: #ff66b2;")
        self.lang_layout.addWidget(self.lang_title)
        
        self.combo = QComboBox()
        self.lang_map = ["en", "tl", "ja", "es", "ko"]
        self.combo.addItems(["English", "Filipino", "日本語 (Japanese)", "Español (Spanish)", "한국어 (Korean)"])
        
        if self.current_lang in self.lang_map:
            self.combo.setCurrentIndex(self.lang_map.index(self.current_lang))
        else:
            self.combo.setCurrentIndex(0)
            
        self.combo.currentIndexChanged.connect(self.write_language_selection)
        self.lang_layout.addWidget(self.combo)
        self.lang_layout.addStretch()
        self.pages.addWidget(self.page_lang)

        # Connect Sidebar to our Pages Core
        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)
        
        self.apply_ui_strings()
        self.sidebar.setCurrentRow(0)

    def read_saved_language(self):
        self.current_lang = "en"
        if os.path.exists(self.lang_file):
            try:
                with open(self.lang_file, "r") as f:
                    self.current_lang = f.read().strip()
            except: pass

    def change_wallpaper(self):
        file_filter = "Images (*.png *.jpg *.jpeg)"
        selected_file, _ = QFileDialog.getOpenFileName(self, "Select Wallpaper Image", "", file_filter)
        if selected_file:
            os.makedirs(self.assets_dir, exist_ok=True)
            destination = os.path.join(self.assets_dir, "Wallpaper.png")
            try:
                shutil.copy(selected_file, destination)
                print(f"Wallpaper redirection logged: {destination}")
            except Exception as e:
                print(f"Failed to copy wallpaper asset: {e}")

    def change_background_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            color_file = os.path.join(self.assets_dir, "bg_color.txt")
            os.makedirs(self.assets_dir, exist_ok=True)
            try:
                with open(color_file, "w") as f:
                    f.write(color_hex)
                wall_path = os.path.join(self.assets_dir, "Wallpaper.png")
                if os.path.exists(wall_path):
                    os.remove(wall_path)
                print(f"Solid color background state saved: {color_hex}")
            except Exception as e:
                print(f"Failed to write background color asset: {e}")

    def apply_ui_strings(self):
        # Save track index to prevent focus resets on language updates
        current_idx = self.sidebar.currentRow()
        self.sidebar.clear()
        
        # 5-Language Sidebar & Label Layout Engine Translation Router
        if self.current_lang == "tl":
            self.window_title_lbl.setText("⚙️ Mga Setting ng System")
            self.sidebar.addItems(["ℹ️ Tungkol sa System", "🎨 Anyo ng Desktop", "🗣️ Wika"])
            self.about_title.setText("Tungkol sa PavlovaOS")
            self.visuals_title.setText("I-personalize ang Iyong Interface")
            self.wall_btn.setText("Palitan ang Wallpaper")
            self.color_btn.setText("Kulay ng Background")
            self.lang_title.setText("Pumili ng wika ng system:")
        elif self.current_lang == "ja":
            self.window_title_lbl.setText("⚙️ システム設定")
            self.sidebar.addItems(["ℹ️ システムについて", "🎨 個人設定と外観", "🗣️ 言語選択"])
            self.about_title.setText("PavlovaOS について")
            self.visuals_title.setText("インターフェースのカスタマイズ")
            self.wall_btn.setText("壁紙の変更")
            self.color_btn.setText("単色背景の設定")
            self.lang_title.setText("システム言語を選択してください:")
        elif self.current_lang == "es":
            self.window_title_lbl.setText("⚙️ Configuración del Sistema")
            self.sidebar.addItems(["ℹ️ Sobre el Sistema", "🎨 Personalización", "🗣️ Idiomas"])
            self.about_title.setText("Sobre PavlovaOS")
            self.visuals_title.setText("Personaliza tu Interfaz")
            self.wall_btn.setText("Cambiar Fondo de Pantalla")
            self.color_btn.setText("Fondo de Color Sólido")
            self.lang_title.setText("Seleccione el idioma del sistema:")
        elif self.current_lang == "ko":
            self.window_title_lbl.setText("⚙️ 시스템 설정")
            self.sidebar.addItems(["ℹ️ 시스템 정보", "🎨 디자인 및 개인 설정", "🗣️ 언어 설정"])
            self.about_title.setText("PavlovaOS 정보")
            self.visuals_title.setText("인터페이스 개인 설정")
            self.wall_btn.setText("배경화면 변경")
            self.color_btn.setText("단색 배경 설정")
            self.lang_title.setText("시스템 표시 언어를 선택하세요:")
        else: # Default: English fallback
            self.window_title_lbl.setText("⚙️ System Settings")
            self.sidebar.addItems(["ℹ️ About System", "🎨 Appearance", "🗣️ Languages"])
            self.about_title.setText("About PavlovaOS")
            self.visuals_title.setText("Personalize Your Workspace")
            self.wall_btn.setText("Change Wallpaper")
            self.color_btn.setText("Solid Color Background")
            self.lang_title.setText("Select system display language:")

        if current_idx >= 0:
            self.sidebar.setCurrentRow(current_idx)
        else:
            self.sidebar.setCurrentRow(0)

    def write_language_selection(self, index):
        self.current_lang = self.lang_map[index]
        os.makedirs(self.assets_dir, exist_ok=True)
        try:
            with open(self.lang_file, "w") as f:
                f.write(self.current_lang)
        except Exception as e: 
            print(f"Write error: {e}")
        self.apply_ui_strings()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PavlovaSettings()
    ex.show()
    sys.exit(app.exec())
