# import math
import sys
import threading
import time
from collections import deque

import cv2

# import numpy as np
# import torch
# import torch.nn as nn
# from pynput.mouse import Button
from PySide6.QtCore import QObject, Signal

sys.path.append("./librarys")

from widgets import *  # noqa

import config_values as cfg  # noqa
from fall_infer_utils import get_fall_down_result, draw
from fight_infer_utils import get_fight_img
from smoke_infer_utils import get_is_smoke_img

global widgets


class Identify(QObject):
    control_ball_open_and_close = Signal(bool)

    def __init__(self, win):
        super().__init__()
        self.prin_time = None
        self.h_t = None
        self.win = win
        self.isEnd = False
        self.in_dim_stack = deque(maxlen=30)
        
        self.smoke_num = 0

    def start(self):
        if not hasattr(self, "cap") or not self.cap.isOpened():
            threading.Thread(target=self.run).start()

    def run(self):
        self.cap = cv2.VideoCapture(0)  # 摄像头图像采集
        S = 0  # 每帧的处理时间

        self.prin_time = time.time()  # 初始化输出时间

        ratio = self.cap.get(4) / self.cap.get(3)  # 高宽比

        start_time = time.time()  # 初始化当前帧帧起始时间

        opened = self.cap.isOpened()

        while opened:
            if self.isEnd:
                break
            self.win.eventRunning.wait()
            # 判断是否满足当前帧率
            wait_time = S - (time.time() - start_time)
            if wait_time > 0:
                time.sleep(wait_time)
            start_time = time.time()  # 重置起始时间

            success, image = self.cap.read()  # 获取摄像头输出
            success, image = self.cap.read()  # 获取摄像头输出
            
            if not success:
                break
            size = (
                int(self.win.ui.label_img.width()),
                int(self.win.ui.label_img.width() * ratio),
            )
            cfg.wCam = size[0] // 1.5
            cfg.hCam = size[1] // 1.5
            image = cv2.resize(image, size)
            label_title = get_fight_img(image)
            is_smoke = get_is_smoke_img(image, conf=0.85)

            fall_down_ret = get_fall_down_result(image)
            fall_down_bbox_results = fall_down_ret[-1]

            if len(fall_down_bbox_results):
                self.win.set_log("有人跌倒了！")

            image = draw(*fall_down_ret)

            
            if is_smoke:
                self.smoke_num += 2 if self.smoke_num < 10 else 0
            
            if self.smoke_num > 3:
                self.win.ui.label_res.setText("有人在吸烟！")
                self.smoke_num -= 1
            else:
                self.win.ui.label_res.setText(cfg.TITLE_MAP[label_title.lower()])
                self.smoke_num -= 1 if self.smoke_num > 0 else 0
                
            print(self.smoke_num)
            
            if self.win.eventRunning.isSet():
                self.win.flash_img(image)

            # cv2.waitKey(1)

        self.cap.release()
        del self.cap

    def break_loop(self):
        self.isEnd = True
