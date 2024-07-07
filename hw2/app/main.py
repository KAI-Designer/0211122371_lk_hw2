import sys
from app.intelligentMonitorApp import IntelligentMonitorApp
if __name__ == '__main__':
    app = IntelligentMonitorApp()
    sys.exit(app.exec())