import sys
import os
import json
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from LoginUi import Ui_LoginWindow
import data.resources_rc  # 导入编译的资源文件

class LoginApp(QMainWindow, Ui_LoginWindow):
    current_user = None  # 添加一个类变量来保存当前用户

    def __init__(self, parent=None):
        super(LoginApp, self).__init__(parent)
        self.setupUi(self)
        self.setup_connections()
        self.user_data_file = "users.json"
        self.load_user_data()
        self.face_login_window = None  # 添加一个类变量来跟踪人脸登录窗口

        # 设置背景图片
        self.backgroundLabel = QLabel(self)
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(QPixmap(":/Background_mainPage.jpg"))
        self.backgroundLabel.setScaledContents(True)
        self.backgroundLabel.lower()  # 确保背景在最底层

    def resizeEvent(self, event):
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(self.backgroundLabel.pixmap().scaled(self.backgroundLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        super(LoginApp, self).resizeEvent(event)

    def setup_connections(self):
        self.loginButton.clicked.connect(self.login)
        self.faceLoginButton.clicked.connect(self.open_face_login)
        self.registerButton.clicked.connect(self.register)

    def load_user_data(self):
        if os.path.exists(self.user_data_file):
            with open(self.user_data_file, 'r') as file:
                self.users = json.load(file)
        else:
            self.users = {}

    def save_user_data(self):
        with open(self.user_data_file, 'w') as file:
            json.dump(self.users, file)

    def validate_input(self, username, password):
        if not username or not password:
            QMessageBox.warning(self, "输入错误", "用户名和密码不能为空。")
            return False
        if not re.match("^[a-zA-Z0-9_]+$", username):
            QMessageBox.warning(self, "输入错误", "用户名只能包含字母、数字和下划线。")
            return False
        if len(password) < 6:
            QMessageBox.warning(self, "输入错误", "密码长度不能少于6个字符。")
            return False
        return True

    def login(self):
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        if not self.validate_input(username, password):
            return
        if username in self.users and self.users[username] == password:
            LoginApp.current_user = username  # 成功登录后保存用户名
            QMessageBox.information(self, "登录成功", "欢迎回来！")
            self.open_people_flow_monitoring(username)  # 登录成功后跳转到人流量监控页面并传递用户名
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误。")

    def open_face_login(self):
        if self.face_login_window == None or not self.face_login_window.isVisible():
            from FaceLoginFrame import FaceLoginApp  # 延迟导入以避免循环导入
            self.face_login_window = FaceLoginApp()
            self.face_login_window.show()
        else:
            print("Face login window is already opened.")

    def register(self):
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        if not self.validate_input(username, password):
            return
        if username in self.users:
            QMessageBox.warning(self, "注册失败", "用户名已存在。")
        else:
            self.users[username] = password
            self.save_user_data()
            LoginApp.current_user = username  # 成功注册后保存用户名
            QMessageBox.information(self, "注册成功", "用户注册成功。")

    def open_people_flow_monitoring(self, username):
        from PeopleFlowMonitorFrame import FlowMonitoringApp  # 确保正确导入
        self.people_flow_monitoring_page = FlowMonitoringApp(username)
        self.people_flow_monitoring_page.show()
        self.close()  # 关闭登录窗口

    def validate_old_password(self, username, old_password):
        is_valid = self.users.get(username) == old_password
        print(f"Validating old password for user {username}: {is_valid}")  # 调试信息
        return is_valid

    def update_password(self, username, new_password):
        self.users[username] = new_password
        self.save_user_data()
        print(f"Updated password for user {username}")  # 调试信息


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = LoginApp()
    mainWindow.show()
    sys.exit(app.exec_())
