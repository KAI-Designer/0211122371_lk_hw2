import sys
import re
from PyQt5 import QtWidgets
from app.PassWordChangeUi import Ui_PasswordChangeDialog  # 绝对导入生成的 UI 类
from app.LoginFrame import LoginApp  # 导入 LoginApp 类
import data.resources_rc  # 导入编译的资源文件

class PasswordChangeDialog(QtWidgets.QDialog, Ui_PasswordChangeDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.username = username  # 保存用户名
        self.pushButtonConfirm.clicked.connect(self.confirm_password_change)
        self.pushButtonCancel.clicked.connect(self.cancel_password_change)
        self.login_app = LoginApp()  # 初始化 LoginApp 类以访问用户数据

    def validate_input(self, username, password):
        print(f"Validating Input - Username: {username}, Password: {password}")  # 调试信息
        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "输入错误", "密码不能为空。")
            return False
        if not re.match("^[a-zA-Z0-9_]+$", username):
            QtWidgets.QMessageBox.warning(self, "输入错误", "密码只能包含字母、数字和下划线。")
            return False
        if len(password) < 6:
            QtWidgets.QMessageBox.warning(self, "输入错误", "密码长度不能少于6个字符。")
            return False
        return True

    def confirm_password_change(self):
        old_password = self.lineEditOldPassword.text().strip()
        new_password = self.lineEditNewPassword.text().strip()
        confirm_password = self.lineEditConfirmNewPassword.text().strip()
        username = self.username  # 直接使用传递过来的用户名

        # 调试信息
        print(f"Old Password: {old_password}")
        print(f"New Password: {new_password}")
        print(f"Confirm Password: {confirm_password}")
        print(f"Username: {username}")

        if not self.validate_input(username, old_password):  # 验证旧密码输入
            return
        if not self.validate_input(username, new_password):  # 验证新密码输入
            return

        if new_password != confirm_password:
            QtWidgets.QMessageBox.warning(self, "错误", "新密码和确认新密码不匹配！")
        else:
            if self.login_app.validate_old_password(username, old_password):
                self.login_app.update_password(username, new_password)
                QtWidgets.QMessageBox.information(self, "成功", "密码修改成功！")
                self.accept()
            else:
                QtWidgets.QMessageBox.warning(self, "错误", "旧密码不正确！")

    def cancel_password_change(self):
        self.reject()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = PasswordChangeDialog("test_user")  # 传递测试用户名
    dialog.show()
    sys.exit(app.exec_())
