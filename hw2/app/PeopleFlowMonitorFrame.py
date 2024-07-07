import sys  # 导入系统模块
import cv2  # 导入OpenCV模块
import time  # 导入时间模块

from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage  # 导入PyQt5图形界面组件
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QCheckBox, QLabel  # 导入PyQt5窗口组件
from PyQt5.QtCore import pyqtSlot, QTimer, Qt, QThread, pyqtSignal  # 导入PyQt5核心模块
from PeopleFlowMonitorUi import Ui_FlowMonitoringWindow  # 导入自定义的UI类
from ai.people_flow_monitor import get_people_flow  # 导入人流量监测AI模块
import data.resources_rc  # 导入资源文件

# 定义图像处理线程类
class ImageProcessingThread(QThread):
    image_processed = pyqtSignal(int, object)  # 定义信号，用于传递处理后的图像信息

    def __init__(self, camera_number, frame):
        super().__init__()
        self.camera_number = camera_number  # 保存摄像头编号
        self.frame = frame  # 保存要处理的帧
        self.running = True  # 运行标志

    def run(self):
        try:
            while self.running:  # 循环处理图像帧
                success, encoded_image = cv2.imencode('.jpg', self.frame)  # 将图像编码为JPEG格式
                if success:
                    response = get_people_flow(encoded_image.tobytes())  # 发送图像数据进行人流量检测
                    self.image_processed.emit(self.camera_number, response)  # 发射处理结果信号
                else:
                    print("Failed to encode image")
                time.sleep(1)  # 间隔1秒进行检测
        except Exception as e:
            print(f"Error in ImageProcessingThread: {e}")

    def stop(self):
        self.running = False  # 停止线程

# 定义主应用程序类
class FlowMonitoringApp(QMainWindow, Ui_FlowMonitoringWindow):
    def __init__(self, username, parent=None):
        super(FlowMonitoringApp, self).__init__(parent)
        self.username = username  # 保存用户名
        try:
            self.setupUi(self)  # 初始化UI
            self.setup_connections()  # 设置信号和槽的连接
            self.init_cameras()  # 初始化摄像头
            self.threads = []  # 初始化线程列表
            self.last_request_time = time.time()  # 记录最后请求时间

            # 设置背景图片
            self.backgroundLabel = QLabel(self)
            self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
            self.backgroundLabel.setPixmap(QPixmap(":/op_bk.jpg"))
            self.backgroundLabel.setScaledContents(True)
            self.backgroundLabel.lower()  # 确保背景在最底层

        except Exception as e:
            print(f"Error during initialization: {e}")

    def resizeEvent(self, event):
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())  # 调整背景图片尺寸
        self.backgroundLabel.setPixmap(self.backgroundLabel.pixmap().scaled(self.backgroundLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        super(FlowMonitoringApp, self).resizeEvent(event)  # 调用父类的resizeEvent方法

    def setup_connections(self):
        # 连接信号和槽
        self.radioButton1_1.toggled.connect(lambda: self.change_camera_view(1, 0))
        self.radioButton1_2.toggled.connect(lambda: self.open_video_file(1, 1))
        self.radioButton1_3.toggled.connect(lambda: self.open_video_file(1, 2))

        self.radioButton2_1.toggled.connect(lambda: self.change_camera_view(2, 0))
        self.radioButton2_2.toggled.connect(lambda: self.open_video_file(2, 1))
        self.radioButton2_3.toggled.connect(lambda: self.open_video_file(2, 2))

        self.radioButton3_1.toggled.connect(lambda: self.change_camera_view(3, 0))
        self.radioButton3_2.toggled.connect(lambda: self.open_video_file(3, 1))
        self.radioButton3_3.toggled.connect(lambda: self.open_video_file(3, 2))

        self.exportButton.clicked.connect(self.export_data)
        self.abnormalBehaviorButton.clicked.connect(self.open_abnormal_behavior_monitoring)
        self.peopleFlowMonitorButton.clicked.connect(self.analyze_people_flow)

        # 添加人流量检测开关
        self.peopleFlowToggle = self.findChild(QCheckBox, 'peopleFlowToggle')
        self.peopleFlowToggle.stateChanged.connect(self.toggle_people_flow_detection)

    def init_cameras(self):
        try:
            self.cap1 = None  # 初始化摄像头1
            self.cap2 = None  # 初始化摄像头2
            self.cap3 = None  # 初始化摄像头3
            self.current_view1 = 0  # 初始化当前视图1
            self.current_view2 = 0  # 初始化当前视图2
            self.current_view3 = 0  # 初始化当前视图3

            self.timer = QTimer(self)  # 创建定时器
            self.timer.timeout.connect(self.update_frame)  # 连接定时器超时信号到更新帧的方法
            self.timer.start(20)  # 每20毫秒更新一次帧
            print("Cameras initialized and timer started.")
        except Exception as e:
            print(f"Error during camera initialization: {e}")

    def toggle_people_flow_detection(self, state):
        if state == Qt.Checked:
            self.start_people_flow_detection()  # 启动人流量检测
        else:
            self.stop_people_flow_detection()  # 停止人流量检测

    def start_people_flow_detection(self):
        self.last_request_time = time.time()  # 记录当前时间

    def stop_people_flow_detection(self):
        for thread in self.threads:
            thread.stop()  # 停止所有线程
        self.threads = []  # 清空线程列表

    def open_video_file(self, camera_number, source_number):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择视频文件", "", "Video Files (*.mp4 *.avi *.mov)")
        if file_path:
            self.close_camera(camera_number)  # 关闭摄像头
            if camera_number == 1:
                self.cap1 = cv2.VideoCapture(file_path)  # 打开视频文件
                self.current_view1 = source_number
            elif camera_number == 2:
                self.cap2 = cv2.VideoCapture(file_path)
                self.current_view2 = source_number
            elif camera_number == 3:
                self.cap3 = cv2.VideoCapture(file_path)
                self.current_view3 = source_number

    def change_camera_view(self, camera_number, view_index):
        try:
            self.close_camera(camera_number)  # 关闭摄像头
            if camera_number == 1:
                if view_index == 0:
                    self.cap1 = cv2.VideoCapture(0)  # 打开摄像头
                self.stackedWidget1.setCurrentIndex(view_index)  # 切换视图
                self.current_view1 = view_index
            elif camera_number == 2:
                if view_index == 0:
                    self.cap2 = cv2.VideoCapture(0)
                self.stackedWidget2.setCurrentIndex(view_index)
                self.current_view2 = view_index
            elif camera_number == 3:
                if view_index == 0:
                    self.cap3 = cv2.VideoCapture(0)
                self.stackedWidget3.setCurrentIndex(view_index)
                self.current_view3 = view_index
        except Exception as e:
            print(f"Error in change_camera_view: {e}")

    def close_camera(self, camera_number):
        if camera_number == 1 and self.cap1:
            self.cap1.release()  # 释放摄像头资源
            self.cap1 = None
        elif camera_number == 2 and self.cap2:
            self.cap2.release()
            self.cap2 = None
        elif camera_number == 3 and self.cap3:
            self.cap3.release()
            self.cap3 = None

    def update_frame(self):
        try:
            self.update_camera_frame(self.cap1, self.current_view1, 1, self.camera1View1, self.label_people_flow_1)  # 更新摄像头1的帧
            self.update_camera_frame(self.cap2, self.current_view2, 2, self.camera2View1, self.label_people_flow_2)  # 更新摄像头2的帧
            self.update_camera_frame(self.cap3, self.current_view3, 3, self.camera3View1, self.label_people_flow_3)  # 更新摄像头3的帧
        except Exception as e:
            print(f"Error in update_frame: {e}")

    def update_camera_frame(self, cap, current_view, camera_number, label_view, label_flow):
        try:
            if cap is not None:
                if current_view == 0 and not cap.isOpened():
                    cap.open(0)  # 打开摄像头
                ret, frame = cap.read()  # 读取帧
                if ret:
                    self.display_video(frame, label_view)  # 显示视频帧
                    if self.peopleFlowToggle.isChecked():
                        self.process_frame(camera_number, frame)  # 处理帧
                else:
                    print(f"Failed to read frame from camera {camera_number}")
            else:
                print(f"Camera {camera_number} is not initialized")
        except Exception as e:
            print(f"Error in update_camera_frame for camera {camera_number}: {e}")

    def process_frame(self, camera_number, frame):
        current_time = time.time()
        if current_time - self.last_request_time >= 1:
            thread = ImageProcessingThread(camera_number, frame)  # 创建图像处理线程
            thread.image_processed.connect(self.on_image_processed)  # 连接信号到槽
            thread.start()  # 启动线程
            self.threads.append(thread)  # 将线程加入列表
            self.last_request_time = current_time

    def on_image_processed(self, camera_number, response):
        try:
            if response and 'person_info' in response:
                self.process_frame_overlay(camera_number, response)  # 处理帧覆盖
                if camera_number == 1:
                    self.label_people_flow_1.setText(f"人流量：{len(response['person_info'])}")
                elif camera_number == 2:
                    self.label_people_flow_2.setText(f"人流量：{len(response['person_info'])}")
                elif camera_number == 3:
                    self.label_people_flow_3.setText(f"人流量：{len(response['person_info'])}")
            else:
                print(f"No valid response for camera {camera_number}")
        except Exception as e:
            print(f"Error in on_image_processed: {e}")

    def process_frame_overlay(self, camera_number, response):
        try:
            frame = self.get_frame_by_camera_number(camera_number)  # 获取帧
            if frame is not None:
                painter = QPainter()  # 创建QPainter对象
                painter.begin(frame)
                pen = QPen(Qt.red, 2)  # 创建画笔
                painter.setPen(pen)
                for person in response['person_info']:
                    location = person['location']
                    top = int(location['top'])
                    left = int(location['left'])
                    width = int(location['width'])
                    height = int(location['height'])
                    painter.drawRect(left, top, width, height)  # 绘制矩形
                painter.end()
            else:
                print(f"Frame for camera {camera_number} is None")
        except Exception as e:
            print(f"Error in process_frame_overlay: {e}")

    def get_frame_by_camera_number(self, camera_number):
        if camera_number == 1:
            return self.camera1View1.pixmap()
        elif camera_number == 2:
            return self.camera2View1.pixmap()
        elif camera_number == 3:
            return self.camera3View1.pixmap()
        else:
            return None

    def display_video(self, frame, label):
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 转换颜色空间
            height, width, channel = frame.shape
            step = channel * width
            qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)  # 创建QImage对象
            label.setPixmap(QPixmap.fromImage(qImg).scaled(label.size(), Qt.KeepAspectRatio))  # 显示图像
        else:
            print("Frame is None, cannot display video")

    def open_abnormal_behavior_monitoring(self):
        try:
            from AbnormalBehaviorMonitoringFrame import AbnormalBehaviorMonitoringPage
            if hasattr(self, 'abnormal_behavior_monitoring_page'):
                self.abnormal_behavior_monitoring_page.close()
            self.abnormal_behavior_monitoring_page = AbnormalBehaviorMonitoringPage(self.username)
            self.abnormal_behavior_monitoring_page.show()
            self.close()
        except Exception as e:
            print(f"Error in open_abnormal_behavior_monitoring: {e}")

    def open_face_registration(self):
        try:
            from FaceRegistrationFrame import FaceRegistrationApp
            self.face_registration_app = FaceRegistrationApp(self.username)
            self.face_registration_app.show()
        except Exception as e:
            print(f"Error in open_face_registration: {e}")

    def open_password_change(self):
        try:
            from passWordChangeFrame import PasswordChangeDialog
            self.password_change_dialog = PasswordChangeDialog(self.username)
            self.password_change_dialog.show()
        except Exception as e:
            print(f"Error in open_password_change: {e}")

    def open_login_dialog(self):
        try:
            from LoginFrame import LoginApp
            self.login_app = LoginApp()
            self.login_app.show()
            self.close()
        except Exception as e:
            print(f"Error in open_login_dialog: {e}")

    @pyqtSlot()
    def export_data(self):
        try:
            print("Data exported")
        except Exception as e:
            print(f"Error in export_data: {e}")

    @pyqtSlot()
    def analyze_people_flow(self):
        if not self.peopleFlowToggle.isChecked():
            QMessageBox.information(self, "提示", "人流量检测已禁用")
            return

        try:
            image_path, _ = QFileDialog.getOpenFileName(self, "选择图像文件", "", "Image Files (*.png *.jpg *.bmp)")
            if image_path:
                result = get_people_flow(image_path)
                if result:
                    self.display_people_flow_result(result)
                else:
                    QMessageBox.warning(self, "错误", "人流量监测失败。")
        except Exception as e:
            print(f"Error in analyze_people_flow: {e}")

    def display_people_flow_result(self, result):
        try:
            self.flowData.setTitle(f"人流量：{result['person_num']}")
        except Exception as e:
            print(f"Error in display_people_flow_result: {e}")

    def closeEvent(self, event):
        try:
            self.stop_people_flow_detection()  # 停止人流量检测
            self.timer.stop()  # 停止定时器
            if self.cap1 is not None:
                self.cap1.release()  # 释放摄像头资源
            if self.cap2 is not None:
                self.cap2.release()
            if self.cap3 is not None:
                self.cap3.release()
            super().closeEvent(event)
        except Exception as e:
            print(f"Error in closeEvent: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = FlowMonitoringApp("test_user")  # 传递测试用户名
    mainWindow.show()
    sys.exit(app.exec_())
