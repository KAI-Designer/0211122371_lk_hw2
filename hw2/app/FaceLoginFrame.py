import sys
import cv2
import base64
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel
from FaceLoginUi import Ui_FaceLoginWindow
from ai.face_recognition import recognize_face
from AbnormalBehaviorMonitoringFrame import AbnormalBehaviorMonitoringPage  # 确保导入正确的监控页面类
import data.resources_rc  # 导入编译的资源文件

class FaceLoginApp(QMainWindow, Ui_FaceLoginWindow):
    def __init__(self, parent=None):
        super(FaceLoginApp, self).__init__(parent)
        self.setupUi(self)

        # 设置背景图片
        self.backgroundLabel = QLabel(self)
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(QPixmap(":/op_bk.jpg"))  # 确保路径正确
        self.backgroundLabel.setScaledContents(True)
        self.backgroundLabel.lower()  # 确保背景在最底层

        self.setup_connections()
        self.init_camera()

    def resizeEvent(self, event):
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(self.backgroundLabel.pixmap().scaled(self.backgroundLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        super(FaceLoginApp, self).resizeEvent(event)

    def setup_connections(self):
        self.faceLoginButton.clicked.connect(self.face_login)

    def init_camera(self):
        print("Initializing camera...")
        self.release_camera()  # 先释放可能占用的摄像头资源
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Failed to open camera.")
            QMessageBox.warning(self, "错误", "无法打开摄像头")
            return
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)
        print("Camera initialized successfully.")

    def release_camera(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
            print("Released camera resource.")

    def update_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                print("Frame read successfully.")
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                step = channel * width
                qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
                self.cameraLabel.setPixmap(QPixmap.fromImage(qImg))
                print("Frame updated.")
            else:
                print("Failed to read frame from camera.")
                # Add a delay before the next frame read attempt to avoid busy waiting
                self.timer.stop()
                self.timer.start(1000)  # Retry reading frame after 1 second
        else:
            print("Camera is not opened.")
            # Attempt to reopen the camera
            self.init_camera()

    def face_login(self):
        print("Attempting face login...")
        img_str = self.capture_face_image()
        if img_str:
            result = recognize_face(img_str)
            if result['error_code'] == 0:
                user_list = result['result']['user_list']
                if user_list and user_list[0]['score'] > 80:  # 设置匹配度阈值
                    username = user_list[0]['user_id']
                    QMessageBox.information(self, "登录成功", f"欢迎回来，{username}！")
                    self.timer.stop()
                    self.release_camera()
                    self.open_abnormal_behavior_monitoring(username)  # 登录成功后跳转到异常行为监控页面并传递用户名
                    return
                else:
                    QMessageBox.warning(self, "登录失败", "人脸识别失败。")
            else:
                QMessageBox.warning(self, "错误", f"人脸识别失败：{result['error_msg']}")
        else:
            QMessageBox.warning(self, "错误", "无法捕获人脸图像")

    def capture_face_image(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                img_str = base64.b64encode(buffer).decode()
                return img_str
            else:
                print("Failed to capture image from camera.")
        return None

    def open_abnormal_behavior_monitoring(self, username):
        print("Opening abnormal behavior monitoring page...")
        self.abnormal_behavior_monitoring_page = AbnormalBehaviorMonitoringPage(username)
        self.abnormal_behavior_monitoring_page.show()
        self.close()  # 关闭当前登录窗口
        print("Abnormal behavior monitoring page opened.")

    def closeEvent(self, event):
        print("Closing face login window...")
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.release_camera()
        super().closeEvent(event)
        print("Face login window closed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = FaceLoginApp()
    mainWindow.show()
    sys.exit(app.exec_())
