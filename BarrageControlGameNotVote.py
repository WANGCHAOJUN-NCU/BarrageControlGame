# -*-coding:utf-8-*-
import socket
import ctypes  # 加载动态链接库
import time
import requests
from bs4 import BeautifulSoup
import re, threading
from queue import Queue

OrdList = Queue(maxsize=50)  # 指令序列

Corder = {'up_arrow': '往前走',
          'up_arrow4': '往前走4步',
          'down_arrow': '往后走',
          'down_arrow4': '往后走4步',
          'left_arrow': '往左走',
          'left_arrow4': '往左走4步',
          'right_arrow': '往右走',
          'right_arrow4': '往右走4步',
          'enter': '确定',
          'esc': '返回',
          'saveGame': '保存游戏',
          'lookBag': '查看背包',
          'useSkill': '使用技能',
          'skip': '跳过',
          'fight': '攻击',
          'protect': '防御'}

SendInput = ctypes.windll.user32.SendInput  # ctypes调用windll.user32.SendInput实现按键控制
# 模拟键盘按键
keyCodeDec = {'backspace': 0x08,
              'tab': 0x09,
              'enter': 0x0D,
              'esc': 0x1B,
              'left_arrow': 0x25,
              'up_arrow': 0x26,
              'right_arrow': 0x27,
              'down_arrow': 0x28,
              '0': 0x30,
              '1': 0x31,
              '2': 0x32,
              '3': 0x33,
              '4': 0x34,
              '5': 0x35,
              '6': 0x36,
              '7': 0x37,
              '8': 0x38,
              '9': 0x39,
              'a': 0x41,
              'b': 0x42,
              'c': 0x43,
              'd': 0x44,
              'e': 0x45,
              'f': 0x46,
              'g': 0x47,
              'h': 0x48,
              'i': 0x49,
              'j': 0x4A,
              'k': 0x4B,
              'l': 0x4C,
              'm': 0x4D,
              'n': 0x4E,
              'o': 0x4F,
              'p': 0x50,
              'q': 0x51,
              'r': 0x52,
              's': 0x53,
              't': 0x54,
              'u': 0x55,
              'v': 0x56,
              'w': 0x57,
              'x': 0x58,
              'y': 0x59,
              'z': 0x5A
              }
keyCodeHex = {
    0x08: 0x0E,
    0x09: 0x0F,
    0x0D: 0x1C,
    0x1B: 0x01,
    0x25: 0x4B,
    0x26: 0x48,
    0x27: 0x4D,
    0x28: 0x50,
    0x30: 0x0B,
    0x31: 0x02,
    0x32: 0x03,
    0x33: 0x04,
    0x34: 0x05,
    0x35: 0x06,
    0x36: 0x07,
    0x37: 0x08,
    0x38: 0x09,
    0x39: 0x0A,
    0x41: 0x1E,
    0x42: 0x30,
    0x43: 0x2E,
    0x44: 0x20,
    0x45: 0x12,
    0x46: 0x21,
    0x47: 0x22,
    0x48: 0x23,
    0x49: 0x17,
    0x4A: 0x24,
    0x4B: 0x25,
    0x4C: 0x26,
    0x4D: 0x32,
    0x4E: 0x31,
    0x4F: 0x18,
    0x50: 0x19,
    0x51: 0x10,
    0x52: 0x13,
    0x53: 0x1F,
    0x54: 0x14,
    0x55: 0x16,
    0x56: 0x2F,
    0x57: 0x11,
    0x58: 0x2D,
    0x59: 0x15,
    0x5A: 0x2C
}
# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


# Actuals Functions
def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(hexKeyCode, keyCodeHex[hexKeyCode], 0, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(hexKeyCode, keyCodeHex[hexKeyCode], 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def sendInput(s_input):
    if (s_input in keyCodeDec.keys()):
        k = 0.1
        PressKey(keyCodeDec[s_input])
        time.sleep(k)
        ReleaseKey(keyCodeDec[s_input])


def LookMyStatus():  # 查看状态
    sendInput('s')


def UseSkill():  # 使用技能
    sendInput('esc')
    time.sleep(0.05)
    sendInput('down_arrow')
    time.sleep(0.05)
    sendInput('enter')


def LookBag():  # 查看背包
    sendInput('esc')
    time.sleep(0.05)
    sendInput('down_arrow')
    time.sleep(0.05)
    sendInput('down_arrow')
    time.sleep(0.05)
    sendInput('enter')


def SaveGame():  # 保存游戏
    sendInput('esc')
    time.sleep(0.05)
    sendInput('up_arrow')
    time.sleep(0.05)
    sendInput('enter')
    time.sleep(0.05)
    sendInput('enter')
    time.sleep(0.05)
    sendInput('enter')


def Esc():  # 返回
    sendInput('esc')


def Enter():  # 确认
    sendInput('enter')


def Up():  # 上
    sendInput('up_arrow')


def Down():  # 下
    sendInput('down_arrow')


def Right():  # 右
    sendInput('right_arrow')


def Left():  # 左
    sendInput('left_arrow')


def Fight():  # 攻击战斗状态下，自动普通攻击直至结束
    sendInput('a')


def Protect():  # 战斗状态下，防御
    sendInput('d')


def Skip():
    for i in range(10):
        Enter()
        time.sleep(0.01)


def Move(i):  # 移动
    if (i == 'w' or i == 'W'):
        Up()
    elif (i == 's' or i == 'S'):
        Down()
    elif (i == 'a' or i == 'A'):
        Left()
    elif (i == 'd' or i == 'D'):
        Right()


def handle():
    global OrdList  # 指令列表
    move = re.compile(r'^[WwAaSsDd]([1-9][0-9]?)?$')  # 匹配方向键指令
    while (True):
        while (OrdList != None):  # 判断指令列表是否为空
            # if (OrdList.empty()):
            #     print("当前指令队列为空！")
            inst = OrdList.get()  # 取出队列头部指令
            grd = move.match(inst)  # 判断取出的指令是否是方向键指令
            if (grd == None):  # 不是方向键
                if (inst == 'c' or inst == 'C'):  # 确认游戏
                    Enter()
                elif (inst == 'e' or inst == 'E'):  # 返回
                    Esc()
                elif (inst == 'k' or inst == 'K'):  # 保存游戏
                    SaveGame()
                elif (inst == 'b' or inst == 'B'):  # 查看背包
                    LookBag()
                elif (inst == 'u' or inst == 'U'):  # 使用技能
                    UseSkill()
                elif (inst == 't' or inst == 'T'):  # 跳过
                    Skip()
                elif (inst == 'f' or inst == 'F'):  # 攻击
                    Fight()
                elif (inst == 'p' or inst == 'P'):  # 防御
                    Protect()
                else:  # 非法指令处理
                    print("非法指令！")
                    continue
            else:
                s = grd.group()  # 取出方向键指令
                totalCount = re.sub("\D", "", s)  # 替换除十进制以外的任意字符
                if (totalCount == ''):  # 单纯移动
                    Move(s)
                else:  # 移动加数字
                    m = re.compile(r'([WwAaSsDd])')
                    m = m.match(s)
                    for j in range(int(totalCount)):
                        Move(m.group())


# 连接初始化，配置Socket的IP和端口
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname("openbarrage.douyutv.com")  # 第三方接入弹幕服务器列表IP地址
port = 8601  # 第三方接入弹幕服务器列表端口
client.connect((host, port))

# 正则表达式预编译
danmu_path = re.compile(b'txt@=(.+?)/cid@')  # 匹配用户发送的弹幕消息
uid_path = re.compile(b'uid@=(.+?)/nn@')  # 匹配用户ID
nickname_path = re.compile(b'nn@=(.+?)/txt@')  # 匹配用户昵称
level_path = re.compile(b'level@=([1-9][0-9]?)/sahf@')  # 匹配用户等级
col_path = re.compile(b'col@=([1-9][0-9]?)/rg')  # 匹配用户弹幕颜色


# 客户端向服务器发送请求
def sendmsg(msgstr):
    msg = msgstr.encode('utf-8')
    data_length = len(msg) + 8
    code = 689  # 客户端发送给弹幕服务器的文本格式数据
    # 发送数据前的协议头，消息长度的两倍，包含消息类型、加密字段、保留字段
    msgHead = int.to_bytes(data_length, 4, 'little') \
              + int.to_bytes(data_length, 4, 'little') + int.to_bytes(code, 4, 'little')
    client.send(msgHead)
    sent = 0
    while sent < len(msg):  # 发送具体数据，保证数据都发送出去
        tn = client.send(msg[sent:])
        sent = sent + tn


# 客户端向弹幕服务器发送登录请求
# 斗鱼独创序列化文本数据，结尾必须为'\0'
# 分组号，第三方平台固定选择-9999
def login(roomid):
    msg = 'type@=loginreq/roomid@={}/\0'.format(roomid)  # 登录请求消息
    sendmsg(msg)
    msg_more = 'type@=joingroup/rid@={}/gid@=-9999/\0'.format(roomid)  # 入组消息
    sendmsg(msg_more)
    print('***************连接到{}的直播间***************'.format(get_name(roomid)))


# 获取弹幕
def start(roomid):
    global OrdList  # 指令队列
    while True:
        data = client.recv(1024)  # 服务器返回的弹幕信息
        uid_more = uid_path.findall(data)  # 用户ID
        nickname_more = nickname_path.findall(data)  # 用户昵称
        level_more = level_path.findall(data)  # 用户等级
        danmu_more = danmu_path.findall(data)  # 弹幕内容
        if (not level_more):  # 没有获取到用户等级，用户默认0级
            level_more = b'0'
        if (not data):
            continue
        else:
            for i in range(0, len(danmu_more)):
                try:
                    product = {
                        'uid': uid_more[0].decode(encoding='utf-8'),  # 获取用户ID
                        'nickname': nickname_more[0].decode(encoding='utf-8'),  # 获取用户昵称
                        'level': level_more[0].decode(encoding='utf-8'),  # 获取用户等级
                        'danmu': danmu_more[0].decode(encoding='utf-8')  # 获取用户发送的弹幕
                    }
                    print("Barrage：", product['danmu'])  # 输出弹幕
                    OrdList.put(product['danmu'])
                    f = open('Testdata4.txt', 'a+')  # 打开文件，定位到文件末尾写入弹幕
                    f.write(str(product) + '\n')
                    f.close()
                except Exception as e:  # 异常处理
                    print(e)


# 发送心跳消息，维持TCP长连接
def keeplive():
    while (True):
        msg = 'type@=mrkl/' + '/\0'  # 心跳消息末尾加入\0
        sendmsg(msg)
        time.sleep(15)


def get_name(roomid):
    r = requests.get("http://www.douyu.com/" + roomid)
    soup = BeautifulSoup(r.text, 'lxml')
    return soup.find('a', {'class', 'Title-anchorName'}).string


if __name__ == '__main__':
    dic = {}
    # room_id = input("请输入房间号(roomid)：")
    room_id = "7505377"  # 直播间房间号
    login(room_id)
    p1 = threading.Thread(target=start, args=(room_id,))
    p2 = threading.Thread(target=keeplive)
    p3 = threading.Thread(target=start, args=(room_id,))
    p1.daemon = False  # 主进程运行完先检查子进程的状态，子进程执行完后，直接结束进程
    p2.daemon = False
    p3.daemon = False
    p1.start()
    p2.start()
    p3.start()
    handle()
    p1.join()
    p2.join()
    p3.join()
