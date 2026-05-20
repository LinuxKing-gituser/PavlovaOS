import sys
import os
import pty
import subprocess
import fcntl
import pyte
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QApplication
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import QTimer, Qt

class PavlovaTerminal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PavlovaOS v1.1 - Dev Edition")
        self.resize(1000, 650)
        self.setStyleSheet("""
            QWidget { 
                background-color: rgba(5, 5, 8, 230); 
                border: 2px solid #00d9ff; 
                border-radius: 12px; 
            }
            QPlainTextEdit { background-color: transparent; border: none; color: #ffffff; }
            QScrollBar:vertical { border: none; background: rgba(0, 255, 255, 10); width: 8px; }
            QScrollBar::handle:vertical { background: #00d9ff; border-radius: 4px; }
        """)

        layout = QVBoxLayout(self)
        self.output = QPlainTextEdit(self)
        self.output.setFont(QFont("Monospace", 10))
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.output)

        self.screen = pyte.Screen(100, 35)
        self.stream = pyte.Stream(self.screen)
        self.last_display = []

        self.master_fd, self.slave_fd = pty.openpty()
        
        # Path logic for GitHub portability
        bin_dir = os.path.dirname(os.path.abspath(__file__))
        art_path = os.path.join(bin_dir, "ascii-art.txt")
        conf_path = os.path.join(bin_dir, "pear_fetch.conf")

        # The Custom Signal-Based Neofetch Config
        with open(conf_path, "w") as f:
            f.write('print_info() {\n')
            f.write('    info "CPU" cpu\n')
            f.write('    info "GPU" gpu\n')
            f.write('    info "Memory" memory\n')
            f.write('    prin "OS" "PavlovaOS v1.1"\n')
            f.write('}\n')

        # The command that makes your custom neofetch the default
        init_commands = f"alias neofetch='neofetch --config {conf_path} --ascii {art_path} --ascii_colors 6 4'; clear\n"
        
        custom_env = os.environ.copy()
        custom_env["TERM"] = "linux"
        
        self.process = subprocess.Popen(
            ["/bin/bash", "--norc", "--noprofile"], 
            stdin=self.slave_fd, stdout=self.slave_fd, stderr=self.slave_fd,
            preexec_fn=os.setsid,
            env=custom_env
        )

        os.write(self.master_fd, init_commands.encode())
        fcntl.fcntl(self.master_fd, fcntl.F_SETFL, os.O_NONBLOCK)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_output)
        self.timer.start(10)

    def update_output(self):
        try:
            raw_data = os.read(self.master_fd, 10240)
            if raw_data:
                self.stream.feed(raw_data.decode('utf-8', errors='ignore'))
                current_display = list(self.screen.display)
                if current_display != self.last_display:
                    full_text = "\n".join(current_display).rstrip()
                    self.output.setPlainText(full_text)
                    self.output.moveCursor(QTextCursor.MoveOperation.End)
                    self.last_display = current_display
        except OSError:
            pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            os.write(self.master_fd, b'\n')
        elif event.key() == Qt.Key.Key_Backspace:
            os.write(self.master_fd, b'\x7f')
        elif event.key() == Qt.Key.Key_Tab:
            os.write(self.master_fd, b'\t')
        else:
            os.write(self.master_fd, event.text().encode('utf-8'))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    term = PavlovaTerminal()
    term.show()
    sys.exit(app.exec())
