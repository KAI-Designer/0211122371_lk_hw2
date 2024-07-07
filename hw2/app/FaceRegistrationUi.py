from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FaceRegistrationWindow(object):
    def setupUi(self, FaceRegistrationWindow):
        FaceRegistrationWindow.setObjectName("FaceRegistrationWindow")
        FaceRegistrationWindow.resize(1200, 1000)
        self.centralwidget = QtWidgets.QWidget(FaceRegistrationWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.cameraLabel = QtWidgets.QLabel(self.centralwidget)
        self.cameraLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.cameraLabel.setStyleSheet("background-color: #c0c0c0; border: 5px solid #000;")
        self.cameraLabel.setMinimumSize(QtCore.QSize(600, 400))
        self.cameraLabel.setMaximumSize(QtCore.QSize(600, 400))
        self.cameraLabel.setObjectName("cameraLabel")

        self.horizontalLayout.addStretch()
        self.horizontalLayout.addWidget(self.cameraLabel)
        self.horizontalLayout.addStretch()

        self.usernameLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.usernameLineEdit.setObjectName("usernameLineEdit")
        self.verticalLayout.addWidget(self.usernameLineEdit)

        self.passwordLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.verticalLayout.addWidget(self.passwordLineEdit)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.submitButton = QtWidgets.QPushButton(self.centralwidget)
        self.submitButton.setStyleSheet("font: bold 14px; color: white; background-color: #4CAF50; border: none; padding: 10px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 16px;")
        self.submitButton.setObjectName("submitButton")
        self.horizontalLayout_2.addWidget(self.submitButton)
        self.cancelButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancelButton.setStyleSheet("font: bold 14px; color: white; background-color: #f44336; border: none; padding: 10px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 16px;")
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_2.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        FaceRegistrationWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(FaceRegistrationWindow)
        self.menubar.setObjectName("menubar")
        FaceRegistrationWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(FaceRegistrationWindow)
        self.statusbar.setObjectName("statusbar")
        FaceRegistrationWindow.setStatusBar(self.statusbar)

        self.retranslateUi(FaceRegistrationWindow)
        QtCore.QMetaObject.connectSlotsByName(FaceRegistrationWindow)

    def retranslateUi(self, FaceRegistrationWindow):
        _translate = QtCore.QCoreApplication.translate
        FaceRegistrationWindow.setWindowTitle(_translate("FaceRegistrationWindow", "人脸注册"))
        self.cameraLabel.setText(_translate("FaceRegistrationWindow", "摄像头画面"))
        self.usernameLineEdit.setPlaceholderText(_translate("FaceRegistrationWindow", "输入用户名"))
        self.passwordLineEdit.setPlaceholderText(_translate("FaceRegistrationWindow", "输入密码"))
        self.submitButton.setText(_translate("FaceRegistrationWindow", "提交"))
        self.cancelButton.setText(_translate("FaceRegistrationWindow", "取消"))
