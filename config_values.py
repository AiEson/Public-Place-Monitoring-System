import cv2
from collections import deque


MOUSE_SENSITIVE = 2

color_set = [
    (83, 109, 254),
    (124, 77, 255),
    (255, 64, 129),
    (255, 82, 82),
    (83, 109, 254),
]
color_set_deep = [
    (197, 202, 233),
    (209, 196, 233),
    (225, 190, 231),
    (248, 187, 208),
    (255, 205, 210),
]
offset = -90 - 25
MODE_NAME = ["Do Nothing", "Move And Click", "PPT Printer", "AAA", "BBB"]

TITLE_MAP = {
    "people walking on a street": "人们走在街上",
    "buildings": "建筑物",
    "fight on a street": "街上打架",
    "fire on a street": "街上着火",
    "street violence": "街头暴力",
    "road": "道路",
    "car crash": "车祸",
    "cars on a road": "道路上的车辆",
    "car parking area": "停车场",
    "cars": "汽车",
    "office environment": "办公环境",
    "office corridor": "办公室走廊",
    "violence in office": "室内暴力",
    "fire in office": "室内着火",
    "people talking": "人们在交谈",
    "people walking in office": "室内行走的人们",
    "person walking in office": "室内行走的人",
    "group of people": "一群人",
    "unknown": "未知",
}

# Define Values
DO_NOTHING = 0
MOVE_AND_CLICK = 1
PPT_WRITE = 2
NOW_MODE = DO_NOTHING

NOW_MODE_COLOR = color_set[0]
pTime = 0
bef_clicked = 0
bef_selecting = 0
frameR = 100  # Frame Reduction
smoothening = 8

wCam, hCam = (0, 0)
wScr, hScr = 1920, 1080
plocX, plocY = 0, 0
clocX, clocY = 0, 0
leftDown = False
# Colors Set When Select Mode

# Floating Balls Settings
move_length = 120

# Points
mouse_points = deque(maxlen=smoothening)
app = None
window = None
