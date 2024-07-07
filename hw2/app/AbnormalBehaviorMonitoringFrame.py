import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QVBoxLayout, QCheckBox, QLabel, QTextEdit
from PyQt5.QtCore import QTimer, Qt, QDateTime
from PyQt5.QtGui import QImage, QPixmap
import cv2
from AbnormalBehaviorMonitoringUi import Ui_MainWindow
from passWordChangeFrame import PasswordChangeDialog
from FaceRegistrationFrame import FaceRegistrationApp
import ai.abnormal_behavior as baidu_ai
import winsound
import data.resources_rc  # 导入编译的资源文件
import os  # 新增导入os库

class AbnormalBehaviorMonitoringPage(QMainWindow, Ui_MainWindow):
    def __init__(self, username, parent=None):
        super(AbnormalBehaviorMonitoringPage, self).__init__(parent)
        self.setupUi(self)
        self.username = username  # 保存用户名

        # 设置背景图片
        self.backgroundLabel = QLabel(self)
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(QPixmap(":/op_bk.jpg"))  # 确保路径正确
        self.backgroundLabel.setScaledContents(True)
        self.backgroundLabel.lower()  # 确保背景在最底层

        self.abnormalBehaviorButton.clicked.connect(self.detect_abnormal_behavior)
        self.mainPageButton.clicked.connect(self.open_face_registration)
        self.peopleFlowMonitorButton.clicked.connect(self.open_people_flow_monitor)
        self.modifyInfoButton.clicked.connect(self.open_password_change_dialog)
        self.logoutButton.clicked.connect(self.open_login_dialog)

        # 添加异常行为检测开关
        self.abnormalBehaviorToggle = self.findChild(QCheckBox, 'abnormalBehaviorToggle')

        # 添加 QTextEdit 组件
        self.alertTextEdit = self.findChild(QTextEdit, 'alertTextEdit')
        self.historyTextEdit = self.findChild(QTextEdit, 'historyTextEdit')
        self.alertTextEdit.setStyleSheet("color: black;")
        self.historyTextEdit.setStyleSheet("color: black;")

        # 摄像头和视频源的信号连接
        self.radioButton1_1.toggled.connect(lambda: self.toggle_source(1, 1))
        self.radioButton1_2.toggled.connect(lambda: self.toggle_source(1, 2))
        self.radioButton1_3.toggled.connect(lambda: self.toggle_source(1, 3))
        self.radioButton2_1.toggled.connect(lambda: self.toggle_source(2, 1))
        self.radioButton2_2.toggled.connect(lambda: self.toggle_source(2, 2))
        self.radioButton2_3.toggled.connect(lambda: self.toggle_source(2, 3))
        self.radioButton3_1.toggled.connect(lambda: self.toggle_source(3, 1))
        self.radioButton3_2.toggled.connect(lambda: self.toggle_source(3, 2))
        self.radioButton3_3.toggled.connect(lambda: self.toggle_source(3, 3))

        self.cameras = [None, None, None]
        self.video_paths = [None, None, None]
        self.timers = [None, None, None]
        self.video_widgets = [self.camera1View1, self.camera2View1, self.camera3View1]
        self.frame_counter = [0, 0, 0]
        self.frame_interval = 10

        self.is_transitioning = False  # 防止重复触发

        # 添加导出按钮的点击事件
        self.exportButton.clicked.connect(self.export_data)

    def resizeEvent(self, event):
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(self.backgroundLabel.pixmap().scaled(self.backgroundLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        super(AbnormalBehaviorMonitoringPage, self).resizeEvent(event)

    def open_people_flow_monitor(self):
        if self.is_transitioning:
            return
        self.is_transitioning = True
        try:
            from PeopleFlowMonitorFrame import FlowMonitoringApp
            print("Releasing all resources...")
            self.release_all_resources()
            print("All resources released.")
            print("Initializing FlowMonitoringApp...")
            self.flow_monitoring_app = FlowMonitoringApp(self.username)  # 传递用户名
            print("FlowMonitoringApp initialized.")
            self.flow_monitoring_app.show()
            print("FlowMonitoringApp shown.")
            self.hide()
            print("Current window hidden.")
        except Exception as e:
            print(f"Error while opening PeopleFlowMonitorFrame: {e}")
            self.is_transitioning = False

    def open_password_change_dialog(self):
        self.password_change_dialog = PasswordChangeDialog(self.username)  # 传递用户名
        self.password_change_dialog.exec_()

    def open_login_dialog(self):
        if self.is_transitioning:
            return
        self.is_transitioning = True
        try:
            print("Releasing all resources before login...")
            self.release_all_resources()
            print("All resources released.")
            from LoginFrame import LoginApp
            print("Initializing LoginApp...")
            self.login_app = LoginApp()
            print("LoginApp initialized.")
            self.login_app.show()
            print("LoginApp shown.")
            self.close()
            print("Current window closed.")
        except Exception as e:
            print(f"Error while opening LoginFrame: {e}")
            self.is_transitioning = False

    def open_face_registration(self):
        if self.is_transitioning:
            return
        self.is_transitioning = True
        self.release_all_resources()
        self.face_registration_app = FaceRegistrationApp(self.username)  # 传递用户名
        self.face_registration_app.show()
        self.close()

    def detect_abnormal_behavior(self):
        if not self.abnormalBehaviorToggle.isChecked():
            QMessageBox.information(self, "提示", "异常行为检测已禁用")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "选择要检测的图片", "", "所有文件 (*);;图片文件 (*.png;*.jpg)", options=options)
        if file_name:
            image = cv2.imread(file_name)
            if image is None:
                QMessageBox.critical(self, "错误", "无法读取图片文件")
                return

            keyword, score, location = baidu_ai.detect_abnormal_behavior(image)
            print(f"Keyword: {keyword}, Score: {score}, Location: {location}")
            if keyword:
                self.draw_rectangle(image, location)
                cv2.imshow("Detected Image", image)
                self.raise_alarm(keyword, score, "文件")
            else:
                QMessageBox.information(self, "检测结果", "未检测到异常行为")

    def draw_rectangle(self, image, location):
        print(f"Drawing rectangle at location: {location}")
        x, y, w, h = location.get('left'), location.get('top'), location.get('width'), location.get('height')
        if x is not None and y is not None and w is not None and h is not None:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

    def raise_alarm(self, keyword, score, camera_source):
        alarm_message = f"检测到异常行为: {keyword} (置信度: {score})，来源: {camera_source}"
        print(f"Alarm: {alarm_message}")
        if keyword == '吸烟':
            winsound.Beep(1000, 500)
            self.add_record(alarm_message, camera_source)

        QMessageBox.critical(self, "异常行为警报", alarm_message)

    def add_record(self, message, camera_source):
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        record = f"{current_time} - {message} - 摄像头: {camera_source}"
        self.alertTextEdit.append(record)  # 添加到警报列表
        self.historyTextEdit.append(record)  # 添加到历史记录

    def toggle_source(self, camera_index, source_index):
        try:
            if self.cameras[camera_index - 1] and self.cameras[camera_index - 1].isOpened():
                self.cameras[camera_index - 1].release()
            if self.timers[camera_index - 1]:
                self.timers[camera_index - 1].stop()

            if source_index == 1:
                self.start_camera(camera_index)
            else:
                self.open_video_file(camera_index)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"切换视频源时发生错误：{e}")

    def start_camera(self, camera_index):
        try:
            self.cameras[camera_index - 1] = cv2.VideoCapture(0)
            self.timers[camera_index - 1] = QTimer(self)
            self.timers[camera_index - 1].timeout.connect(lambda: self.update_frame(camera_index))
            self.timers[camera_index - 1].start(30)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法启动摄像头：{e}")

    def open_video_file(self, camera_index):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(self, "选择视频文件", "", "视频文件 (*.mp4;*.avi)", options=options)
            if file_name:
                self.video_paths[camera_index - 1] = file_name
                self.cameras[camera_index - 1] = cv2.VideoCapture(file_name)
                self.timers[camera_index - 1] = QTimer(self)
                self.timers[camera_index - 1].timeout.connect(lambda: self.update_frame(camera_index))
                self.timers[camera_index - 1].start(30)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开视频文件：{e}")

    def update_frame(self, camera_index):
        try:
            ret, frame = self.cameras[camera_index - 1].read()
            if ret:
                if self.frame_counter[camera_index - 1] % self.frame_interval == 0:
                    if self.abnormalBehaviorToggle.isChecked():
                        keyword, score, location = baidu_ai.detect_abnormal_behavior(frame)
                        print(f"Frame {self.frame_counter[camera_index - 1]}: Keyword: {keyword}, Score: {score}, Location: {location}")
                        if keyword:
                            self.draw_rectangle(frame, location)
                            self.raise_alarm(keyword, score, f"摄像头 {camera_index}")
                self.frame_counter[camera_index - 1] += 1

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(image)

                widget = self.video_widgets[camera_index - 1]
                widget.setPixmap(pixmap)
                widget.setScaledContents(True)
                widget.setAlignment(Qt.AlignCenter)

                layout = widget.layout()
                if layout is not None:
                    layout.setContentsMargins(0, 0, 0, 0)
                else:
                    layout = QVBoxLayout()
                    layout.setContentsMargins(0, 0, 0, 0)
                    widget.setLayout(layout)
                layout.addWidget(widget)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新帧时发生错误：{e}")

    def release_all_resources(self):
        try:
            for camera in self.cameras:
                if camera and camera.isOpened():
                    print(f"Releasing camera {camera}")
                    camera.release()
            for timer in self.timers:
                if timer:
                    print(f"Stopping timer {timer}")
                    timer.stop()
            self.cameras = [None, None, None]
            self.timers = [None, None, None]
        except Exception as e:
            print(f"Error releasing resources: {e}")

    def closeEvent(self, event):
        self.release_all_resources()
        super().closeEvent(event)

    # 新增导出数据的方法
    def export_data(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "选择保存路径", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write("异常行为警报列表:\n")
                    file.write(self.alertTextEdit.toPlainText() + "\n\n")
                    file.write("异常行为历史记录:\n")
                    file.write(self.historyTextEdit.toPlainText())
                QMessageBox.information(self, "成功", "数据导出成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存文件: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AbnormalBehaviorMonitoringPage("test_user")  # 传递测试用户名
    window.show()
    sys.exit(app.exec_())
