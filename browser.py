import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QLineEdit, QHBoxLayout, QPushButton, QTabWidget, QMenu)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QAction

# --- HARDWARE FIXES FOR INTEL GRAPHICS ---
os.environ["LIBVA_DRIVER_NAME"] = "i965"
os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"

class PavlovaBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pavlova Chromium")
        
        # Dimensions optimized for Acer 1366x768 workspace canvas
        window_width = 950
        window_height = 650
        self.resize(window_width, window_height)
        
        # --- FEATURE: PERFECT CENTER SPAWNING PIPELINE ---
        # Grabs screen geometry to calculate absolute center points
        screen = QApplication.primaryScreen().geometry()
        center_x = int((screen.width() - window_width) / 2)
        center_y = int((screen.height() - window_height) / 2)
        self.move(center_x, center_y) # Moves window safely away from taskbar lock zone

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint)

        # Neon Blue Cyber Theme styles
        self.setStyleSheet("""
            QMainWindow { background-color: #050508; border: 1px solid #00d9ff; }
            QWidget { background-color: #050508; }
            
            QTabWidget::pane { border: 1px solid #101015; background: #050508; }
            QTabBar::tab {
                background: #101015;
                color: #888888;
                border: 1px solid #202025;
                border-bottom-color: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 6px 15px;
                min-width: 100px;
                font-family: sans-serif;
                font-size: 11px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #151520;
                color: #00d9ff;
                border: 1px solid #00d9ff;
                border-bottom-color: none;
            }
            
            QPushButton {
                background: #101015;
                border: 1px solid #00d9ff;
                color: #00d9ff;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
                min-width: 30px;
                min-height: 28px;
            }
            QPushButton:hover {
                background: rgba(0, 217, 255, 30);
            }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(6)

        # Navigation Bar
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(6)

        self.btn_back = QPushButton("←")
        self.btn_back.clicked.connect(lambda: self.get_current_browser().back() if self.get_current_browser() else None)
        
        self.btn_forward = QPushButton("→")
        self.btn_forward.clicked.connect(lambda: self.get_current_browser().forward() if self.get_current_browser() else None)
        
        self.btn_refresh = QPushButton("⟳")
        self.btn_refresh.clicked.connect(lambda: self.get_current_browser().reload() if self.get_current_browser() else None)
        
        self.btn_new_tab = QPushButton("+")
        self.btn_new_tab.clicked.connect(lambda: self.add_new_tab())

        self.nav_layout.addWidget(self.btn_back)
        self.nav_layout.addWidget(self.btn_forward)
        self.nav_layout.addWidget(self.btn_refresh)
        self.nav_layout.addWidget(self.btn_new_tab)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search Google or type a URL...")
        self.url_bar.setStyleSheet("""
            QLineEdit { 
                background: #101015; border: 1px solid #00d9ff; 
                color: white; border-radius: 6px; padding: 5px 10px;
                font-family: sans-serif; font-size: 13px;
            }
        """)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.nav_layout.addWidget(self.url_bar)

        self.layout.addLayout(self.nav_layout)

        # Tab Engine
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        
        self.layout.addWidget(self.tabs)

        # Track devtools window instance to prevent it from getting garbage collected
        self.devtools_window = None

        # Boot initial tab
        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")
        
        self.show()
        self.raise_()

    def add_new_tab(self, qurl=None, title="New Tab"):
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        # --- FEATURE: CUSTOM RIGHT-CLICK CONTEXT INTERCEPTOR ---
        browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        browser.customContextMenuRequested.connect(lambda pos: self.handle_custom_context_menu(pos, browser))
        
        index = self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(index)

        browser.urlChanged.connect(lambda url, b=browser: self.sync_url_text(url, b))
        browser.titleChanged.connect(lambda t: self.tabs.setTabText(self.tabs.indexOf(browser), t[:15] + "..." if len(t) > 15 else t))

    # --- FEATURE: INSPECT ELEMENT MENU CONSTRUCT ---
    def handle_custom_context_menu(self, pos, browser_instance):
        context_menu = QMenu(self)
        context_menu.setStyleSheet("""
            QMenu {
                background-color: #0c0c12;
                color: #00d9ff;
                border: 1px solid #00d9ff;
                border-radius: 6px;
                padding: 4px;
                font-family: sans-serif;
            }
            QMenu::item {
                padding: 6px 25px;
                background: transparent;
            }
            QMenu::item:selected {
                background-color: rgba(0, 217, 255, 40);
                color: white;
                border-radius: 4px;
            }
        """)

        # Standard navigation actions inside the right click menu
        act_back = QAction("Back", self)
        act_back.triggered.connect(browser_instance.back)
        act_back.setEnabled(browser_instance.history().canGoBack())

        act_forward = QAction("Forward", self)
        act_forward.triggered.connect(browser_instance.forward)
        act_forward.setEnabled(browser_instance.history().canGoForward())

        act_reload = QAction("Reload", self)
        act_reload.triggered.connect(browser_instance.reload)

        # Inspect Element Trigger Action
        act_inspect = QAction("Inspect Element", self)
        act_inspect.triggered.connect(lambda: self.open_dev_tools(browser_instance))

        # Compile options list structure
        context_menu.addAction(act_back)
        context_menu.addAction(act_forward)
        context_menu.addAction(act_reload)
        context_menu.addSeparator()
        context_menu.addAction(act_inspect)
        
        # Display menu tracking mouse position coordinates
        context_menu.exec(browser_instance.mapToGlobal(pos))

    def open_dev_tools(self, browser_instance):
        # Create a fresh independent floating window container frame for the DevTools console
        if self.devtools_window is None or not self.devtools_window.isVisible():
            self.devtools_window = QMainWindow()
            self.devtools_window.setWindowTitle("Pavlova Developer Tool Panel")
            self.devtools_window.resize(850, 500)
            
            # Center devtools view frame layout
            screen = QApplication.primaryScreen().geometry()
            dt_x = int((screen.width() - 850) / 2)
            dt_y = int((screen.height() - 500) / 2) + 40
            self.devtools_window.move(dt_x, dt_y)

            self.devtools_view = QWebEngineView()
            self.devtools_window.setCentralWidget(self.devtools_view)
        
        # Link devtools view profile layout to target page engine inspected segment
        browser_instance.page().setDevToolsPage(self.devtools_view.page())
        
        # Execute action command call to trigger console panel view rendering
        browser_instance.page().triggerAction(QWebEnginePage.WebAction.InspectElement)
        
        self.devtools_window.show()
        self.devtools_window.raise_()

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.widget(index).deleteLater()
            self.tabs.removeTab(index)
        else:
            self.get_current_browser().setUrl(QUrl("https://www.google.com"))

    def get_current_browser(self):
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, QWebEngineView):
            return current_widget
        return None

    def tab_changed(self, index):
        browser = self.get_current_browser()
        if browser:
            self.url_bar.setText(browser.url().toString())

    def sync_url_text(self, url, browser_source):
        if browser_source == self.get_current_browser():
            self.url_bar.setText(url.toString())

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url: return

        if not url.startswith("http"):
            url = "https://www.google.com/search?q=" + url if "." not in url else "https://" + url
            
        current_browser = self.get_current_browser()
        if current_browser:
            current_browser.setUrl(QUrl(url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PavlovaBrowser()
    sys.exit(app.exec())
