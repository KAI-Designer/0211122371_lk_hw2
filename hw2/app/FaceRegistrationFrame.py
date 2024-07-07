import sys
import cv2
import base64
import os
import json
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel
from FaceRegistrationUi import Ui_FaceRegistrationWindow
from ai.face_recognition import register_face
import data.resources_rc  # 导入编译的资源文件

class FaceRegistrationApp(QMainWindow, Ui_FaceRegistrationWindow):
    def __init__(self, username, parent=None):
        super(FaceRegistrationApp, self).__init__(parent)
        self.setupUi(self)
        self.username = username  # 保存用户名

        # 设置背景图片
        self.backgroundLabel = QLabel(self)
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(QPixmap(":/op_bk.jpg"))  # 确保路径正确
        self.backgroundLabel.setScaledContents(True)
        self.backgroundLabel.lower()  # 确保背景在最底层

        self.setup_connections()
        self.load_user_data()

        # 初始化摄像头
        self.init_camera()

    def resizeEvent(self, event):
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(self.backgroundLabel.pixmap().scaled(self.backgroundLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        super(FaceRegistrationApp, self).resizeEvent(event)

    def setup_connections(self):
        self.submitButton.clicked.connect(self.submit_data)
        self.cancelButton.clicked.connect(self.cancel_registration)

    def load_user_data(self):
        user_data_file = "users.json"
        if os.path.exists(user_data_file):
            with open(user_data_file, 'r') as file:
                self.users = json.load(file)
        else:
            self.users = {}

    def validate_credentials(self, username, password):
        return self.users.get(username) == password

    def init_camera(self):
        print("Initializing camera...")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Failed to open camera.")
            QMessageBox.warning(self, "错误", "无法打开摄像头")
            return
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)
        print("Camera initialized successfully.")

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            step = channel * width
            qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            self.cameraLabel.setPixmap(QPixmap.fromImage(qImg))
        else:
            print("Failed to read frame from camera.")

    def submit_data(self):
        username = self.usernameLineEdit.text().strip()
        password = self.passwordLineEdit.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "输入错误", "用户名和密码不能为空。")
            return

        if not self.validate_credentials(username, password):
            QMessageBox.warning(self, "验证失败", "用户名或密码错误。")
            return

        img_str = self.capture_face_image()
        if img_str:
            result = register_face(username, img_str)
            if result['error_code'] == 0:
                QMessageBox.information(self, "成功", "人脸数据捕捉并保存成功！")
            else:
                QMessageBox.warning(self, "错误", f"人脸录入失败：{result['error_msg']}")
        else:
            QMessageBox.warning(self, "错误", "无法捕获人脸图像")

    def capture_face_image(self):
        ret, frame = self.cap.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            img_str = base64.b64encode(buffer).decode()
            return img_str
        else:
            print("Failed to capture image from camera.")
            return None

    def cancel_registration(self):
        self.timer.stop()
        self.cap.release()
        self.close()

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = FaceRegistrationApp("test_user")  # 传递测试用户名
    mainWindow.show()
    sys.exit(app.exec_())
