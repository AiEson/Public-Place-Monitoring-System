# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

import sys
import os
import platform
import time
from PySide6 import QtCore, QtGui
from threading import Event, Thread

import cv2
from process import Identify

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.bef_log_time = time.time()

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "基于目标检测的公共场所监测系统"
        description = ""
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        ## LEFT MENUS
        # widgets.btn_home.clicked.connect(self.buttonClick)
        # widgets.btn_widgets.clicked.connect(self.buttonClick)
        # widgets.btn_new.clicked.connect(self.buttonClick)
        # widgets.btn_save.clicked.connect(self.buttonClick)
        widgets.btn_app.clicked.connect(self.buttonClick)

        widgets.btn_home.setVisible(False)
        widgets.btn_widgets.setVisible(False)
        widgets.btn_save.setVisible(False)

        # 设置LeftBox上面的那个Left Box为中文
        widgets.extraLabel.setText("关于软件")

        widgets.btn_share.setText("分享本软件")
        widgets.btn_more.setVisible(False)
        widgets.btn_adjustments.setVisible(False)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)

        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)

        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        themeFile = "themes\py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        widgets.stackedWidget.setCurrentWidget(widgets.mainPage)
        widgets.btn_app.setStyleSheet(
            UIFunctions.selectMenu(widgets.btn_app.styleSheet())
        )

        widgets.btn_start.clicked.connect(self.select_file_and_open)

        self.identify = Identify(self)
        self.eventRunning = Event()

    def select_file_and_open(self):
        if not self.eventRunning.is_set():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mkv)"
            )
            if file_path:
                cap = cv2.VideoCapture(file_path)
                # self.run(cap)
                self.identify.cap = cap
                if self.eventRunning.is_set():
                    widgets.label_img.setText("识别准备已就绪\n正在等待视频讯号输入...")
                    widgets.btn_start.setText("开启识别")
                    self.eventRunning.clear()
                else:
                    self.eventRunning.set()
                    widgets.btn_start.setText("停止识别")
        else:
            self.eventRunning.clear()
            widgets.btn_start.setText("开启识别")
            widgets.label_img.setText("识别准备已就绪\n正在等待视频讯号输入...")
            self.run()

    def set_log(self, msg):
        if time.time() - self.bef_log_time > 3:
            widgets.textBrowser.append(
                time.strftime("(%H:%M:%S)", time.localtime()) + " " + msg
            )
            self.bef_log_time = time.time()
        else:
            pass

    def flash_img(self, image):
        # # cv2.imshow('img', shrink)
        shrink = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.QtImg = QtGui.QImage(
            shrink.data,
            shrink.shape[1],
            shrink.shape[0],
            shrink.shape[1] * 3,
            QtGui.QImage.Format_RGB888,
        )
        self.ui.label_img.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))

    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        # if btnName == "btn_home":
        #     widgets.stackedWidget.setCurrentWidget(widgets.home)
        #     UIFunctions.resetStyle(self, btnName)
        #     btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        # if btnName == "btn_widgets":
        #     widgets.stackedWidget.setCurrentWidget(widgets.widgets)
        #     UIFunctions.resetStyle(self, btnName)
        #     btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_app":
            widgets.stackedWidget.setCurrentWidget(widgets.mainPage)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

        # if btnName == "btn_save":
        #     print("Save BTN clicked!")

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print("Mouse click: LEFT CLICK")
        if event.buttons() == Qt.RightButton:
            print("Mouse click: RIGHT CLICK")

    def run(self):
        self.identify.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    window.run()
    sys.exit(app.exec())
