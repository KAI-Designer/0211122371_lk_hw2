from PyQt5.QtWidgets import QApplication
from LoginFrame import LoginApp
import sys

class IntelligentMonitorApp(QApplication):
    def __init__(self):
        super(IntelligentMonitorApp, self).__init__(sys.argv)
        self.md = LoginApp()
        self.md.show()
