# coding:UTF-8
import tkinter as tk
from tkinter import *
from tkinter import ttk

# 引入字体模块
# import tkinter.font as tkFont

import time
from tkinter import messagebox
import threading
import queue
import sys
import platform
import os

from MyModules.MyDialogs import MyDialogOk

from MyModules.SlotView import SlotView
from MyModules.ScanSnView import ScanSnUI
from MyModules.PassWordView import PassWordUI
from MyModules.SSConfigView import SSConfigView
from MyModules.Logger import MyLogger
from MyModules.RWjson import RWjson
from MyModules.LogCsv import SaveLog
from MyModules.ProgressBars import MyProgressBar1, MyWelcomeBar
# 主框架SSView


class SSUI(object):
    """
    SS框架
    主测试框架，负责载入各个单元，载入station配置
    载入station级别的设备通讯，如治具
    开发环境：Mac os 10.14 
            python 3.6.8(Anaconda5.2.0)
    已适配Mac os/Windows10/Ubuntu18.04

    """

    def __init__(self):
        super(SSUI, self).__init__()
        self.myLogger = MyLogger(name='SSUI')
        # 获取运行平台的名称
        self.sysName = platform.system()  # "Windows"/"Darwin"/"Linux"
        # print(sys.path[0])
        # :/Users/weidongcao/Documents/PythonCode/SSTester

        self.master = Tk()
        self.master.geometry('800x600')  # 是x 不是*
        self.master.resizable(width=False, height=False)  # 宽不可变, 高可变,默认为True
        self.load_0()
        self.load_1()
        self.master.update()
        self.updateUIQueue.put((4, 'load_2'))
        self.updateUIQueue.put((5, 'load_3'))
        # self.load_2()
        # self.load_3()
        self.master.mainloop()

    def load_0(self):

        # 读取配置信息
        self.readCfg()
        self.modeValue = IntVar()
        self.create_menu(self.master)
        self.master['background'] = 'white'
        self.master.title("SS View")

        self.resousePath = sys.path[0] + '/Resources'
        if sys.platform.startswith('win'):
            appIcon = self.resousePath + '/AppBitmap/App.ico'
            self.master.iconbitmap(appIcon)
        else:
            appIcon = self.resousePath + '/AppBitmap/App.png'
            img = PhotoImage(file=appIcon)
            self.master.tk.call('wm', 'iconphoto', self.master._w, img)

        # 注册关闭窗口回调
        self.master.protocol("WM_DELETE_WINDOW", self.closeWinCallback)

        self.loopCountStr = StringVar()
        self.finishLoopStr = StringVar()
        self.loopCountStr.set('1')
        self.finishLoopStr.set('finished:0')
        self.loopCountInt = int(self.loopCountStr.get())
        self.finishLoopCount = 0
        self.abortLoopFlag = False

        self.firstSn = StringVar()
        self.isTesting = False
        self.exitFlag = False
        self.lock = threading.Lock()
        self.updateUIQueue = queue.Queue()
        self.receivedMsgQueue = queue.Queue()
        self.exitProgressQueue = queue.Queue()

        # self.master.update()
        # self.welcomeBar.deiconify()

    def load_1(self):
        # 启动主线程UI刷新队列loop
        self.updateUIloop()

        # 子线程开启消息处理队列
        thTest = threading.Thread(target=self.startMsgQueue, name='msgThread_SSUI')
        thTest.setDaemon(True)
        thTest.start()

        # SlotView数组
        self.slotArr = []
        # SlotView是否选中的数组
        self.selectedArr = []
        # SlotView数量
        #self.slotCount = 1
        # SlotView选中的数量统计
        self.selectedSlotCount = self.slotCount
        # SlotView完成测试的数量统计
        self.endTestCount = 0
        # slot同步顺序执行的虚拟钥匙
        self.SSKey = True
        # slot同步信号统计
        self.syncSignaCount = 0
        self.syncSignaCheckSUM = 0

        self.exitOkCount = 0

        # yield Panel
        self.inputInfo = StringVar()
        self.passInfo = StringVar()
        self.yieldInfo = StringVar()

        self.snArr = []
        self.snIsReady = False

        self.setup()

    def load_2(self):
        # --------------------------
        # 载入SS view配置
        # 如:治具（串口通讯serial）/34970数据采集器（nivisa接口）
        #   self.cfgView.devices['Fixture']
        #   self.cfgView.devices['34970']
        # -------------------------
        self.cfgView = SSConfigView(self.master, -1, self.receivedMsgFromConfig)
        if self.cfgView.errCount != 0:
            self.myLogger.logger.error('config error,please check!')
            messagebox.showerror(title='Error', message='SS Config error,please check!')

        # 刷新良率统计panel
        self.updateYieldPanel(save=False)
        # ------------------------------
        # 载入所有的Slot view
        # ------------------------------
        slotParams={}
        slotParams['master']=self.master
        slotParams['swName']=self.swName
        slotParams['swVersion']=self.swVersion
        slotParams['sendEvent']=self.receivedMsgFromSlot
        for i in range(0, self.slotCount):
            slotParams['index']=i
            if i < 2:            
                slotParams['x']=20 +280 *i
                slotParams['y']=80
                slot = SlotView(slotParams)
            else:
                slotParams['x']=20 +280 *(i -2)
                slotParams['y']=80 +200
                slot = SlotView(slotParams)
            self.slotArr.append(slot)
            self.selectedArr.append(1)
            self.master.update()

        # self.firstSn.set("")

    def load_3(self):
        self.csvHelper = SaveLog(path=sys.path[0], swName=self.swName)
        self.setupCsvHelper()
        self.allCsvData = ''

        self.snEntry.focus()
        if self.sysName.find("Windows") == -1:
            # 载入自定义主题
            combostyle = ttk.Style()
            combostyle.theme_create('combostyle',
                                    parent='alt',
                                    settings={'BW.TCombobox':
                                              {'configure':
                                               {'foreground': 'black',
                                                'selectbackground': '#403c40',
                                                'fieldbackground': 'white',
                                                'background': 'yellow'
                                                }
                                               }
                                              }
                                    )
            combostyle.theme_use('combostyle')
        self.myLogger.logger.info('start SS view done.')
        self.myLogger.logger.warn('SSUI:' + str(threading.current_thread()))

        # 启动主循环
        # self.master.mainloop()
        #print('mainloop done')

    # -------------------
    # 载入程序菜单选项
    # -------------------

    def create_menu(self, root):
        # 创建菜单栏
        self.menu = Menu(root)

        setting_menu = Menu(self.menu, tearoff=0)
        # 创建二级菜单

        setting_menu.add_radiobutton(label="Debug", value=1, variable=self.modeValue, command=self.clickDebugMenu)
        setting_menu.add_radiobutton(label="Normal", value=2, variable=self.modeValue, command=self.clickNorMenu)
        self.modeValue.set(2)
        # setting_menu.add_separator()
        # setting_menu.add_command(label="Config",command=self.clickCfgMenu)

        about_menu = Menu(self.menu, tearoff=0)
        about_menu.add_command(label="version:1.0")

        # 在菜单栏中添加菜单
        self.menu.add_cascade(label="Setting", menu=setting_menu)
        self.menu.add_cascade(label="About", menu=about_menu)

        root['menu'] = self.menu

    # 载入SS view 的所有元素
    def setup(self):
        frame1 = tk.Frame(self.master, bg="yellow", relief=tk.SOLID,)
        #self.lf.pack(expand=NO, padx=self.x, pady=self.y)
        frame1.place(x=5, y=5, width=600, height=50)

        # 指定字体名称、大小、样式
        #ft = tkFont.Font(family='Fixdsys', size=28, weight=tkFont.NORMAL)

        # 创建Label，设置背景色和前景色
        self.swLabel = Label(frame1,
                             text=self.swName,
                             fg='Black',
                             font="Arial 28",  # ft
                             bg="white")
        # 使用place()设置该Label的大小和位置
        self.swLabel.place(x=10, y=10, width=400, height=30)

        # 创建Label，设置背景色和前景色
        self.verLabel = Label(frame1,
                              text=self.swVersion,
                              fg='Black',
                              font="Arial 16",
                              bg="white")
        # 使用place()设置该Label的大小和位置
        self.verLabel.place(x=460, y=15, width=100, height=30)

        frame2 = tk.Frame(self.master, bg="green", relief=tk.SOLID)
        frame2.place(x=600, y=80, width=180, height=60)

        # 新建一个输入框
        self.snEntry = Entry(frame2,
                             textvariable=self.firstSn,
                             width=17,
                             bg='white'
                             )

        self.snEntry.place(x=0, y=0, height=20)
        self.snEntry.bind('<Return>', self.inputSnEvent)
        # 新建一个按钮
        self.startAll_btn = Button(frame2,
                                   text='TestAll',
                                   command=self.clickStartAllBtn)  # 背景色:蓝色

        self.startAll_btn.place(x=30, y=30, width=100, height=30)
        # yield panel frame
        frame3 = tk.Frame(self.master, bg="#E6E6FA", relief=tk.SOLID)
        frame3.place(x=600, y=160, width=180, height=120)
        self.inputLabel = Label(frame3,
                                textvariable=self.inputInfo,
                                fg='black',
                                anchor=W,
                                font="Arial 12",
                                bg="#D3D3D3")
        # 使用place()设置该Label的大小和位置
        self.inputLabel.place(x=10, y=10, width=140, height=20)
        self.passLabel = Label(frame3,
                               textvariable=self.passInfo,
                               fg='black',
                               anchor=W,
                               font="Arial 12",
                               bg="#7FFFD4")
        # 使用place()设置该Label的大小和位置
        self.passLabel.place(x=10, y=32, width=140, height=20)
        self.yieldLabel = Label(frame3,
                                textvariable=self.yieldInfo,
                                fg='black',
                                anchor=W,
                                font="Arial 12",
                                bg="#D2B48C")
        # 使用place()设置该Label的大小和位置
        self.yieldLabel.place(x=10, y=54, width=140, height=20)
        # 新建一个按钮
        self.clear_btn = Button(frame3,
                                text='Clear',
                                command=self.clearYield)  # 背景色:蓝色

        self.clear_btn.place(x=30, y=80, width=60, height=20)

        # debug panel frame
        self.debugFrame = tk.Frame(self.master, bg="#E6E6FA", relief=tk.SOLID)
        # self.debugFrame.place(x=600,y=300,width=180,height=120)
        self.debugLabel = Label(self.debugFrame,
                                text='Debug',
                                fg='red',
                                anchor=W,
                                font="Arial 26",
                                bg="#D3D3D3")
        # 使用place()设置该Label的大小和位置
        self.debugLabel.place(x=10, y=10, width=140, height=40)
        # 新建一个按钮
        self.ssCfg_btn = Button(self.debugFrame,
                                text='Config',
                                command=self.ssCfgClick)  # 背景色:蓝色

        self.ssCfg_btn.place(x=10, y=60, width=100, height=30)
        # loop operater panel
        loopLabel = Label(self.debugFrame,
                          text='loop:',
                          fg='black',
                          anchor=W,
                          font="Arial 11",
                          bg="#D3D3D3")
        # 使用place()设置该Label的大小和位置
        loopLabel.place(x=10, y=120, width=40, height=20)

        self.loopCountEntry = Entry(self.debugFrame,
                                    textvariable=self.loopCountStr,
                                    width=6,
                                    bg='white'
                                    )

        self.loopCountEntry.place(x=60, y=120, height=20)
        finishLoopLabel = Label(self.debugFrame,
                                textvariable=self.finishLoopStr,
                                fg='black',
                                anchor=W,
                                font="Arial 11",
                                bg="#D3D3D3")
        # 使用place()设置该Label的大小和位置
        finishLoopLabel.place(x=10, y=145, width=140, height=20)
        # 新建一个按钮
        self.abortLoop_btn = Button(self.debugFrame,
                                    text='Abort',
                                    command=self.abortLoopAction)  # 背景色:蓝色

        self.abortLoop_btn.place(x=10, y=172, width=70, height=20)
        self.abortLoop_btn['state'] = DISABLED

    # ---------------------------
    # 界面点击事件
    # ---------------------------
    # 点击菜单栏‘Debug’按钮
    def clickDebugMenu(self):
        self.myLogger.logger.debug('click debug mode menu')
        pwUI = PassWordUI(self.master, self.myLogger.logger, self.passwordCallBack)
        pwUI.rawKey = self.password
        # self.modeValue.set(1)

    # 点击菜单栏‘Normal’按钮
    def clickNorMenu(self):
        self.myLogger.logger.debug('click normal mode menu')
        self.master['bg'] = 'white'
        self.modeValue.set(2)
        self.debugFrame.place_forget()
        self.sendMsg2Slot("mode:normal", allSend=True)

    # 点击SS view ‘StartAll’按钮
    def clickStartAllBtn(self):
        self.myLogger.logger.debug("start all test...")

        if not self.snIsReady:
            messagebox.showerror(title='Error', message='Please scan sn first!')
            self.master.focus_force()
            self.snEntry.focus()
            return
        # debug mode
        if self.modeValue.get() == 1:
            self.finishLoopCount = 0
            self.loopCountInt = int(self.loopCountStr.get())
            self.finishLoopStr.set('finished:0')
            self.abortLoopFlag = False
            self.abortLoop_btn['state'] = NORMAL
            self.loopCountEntry['state'] = DISABLED
            self.ssCfg_btn['state'] = DISABLED
        # 调用开始Slot测试的方法
        self.startAllTestAction()

    # 点击SS view的配置按钮
    def ssCfgClick(self):
        self.myLogger.logger.debug('ss view config btn click')
        self.cfgView.loadUI()

    # 点击良率‘clear’按钮
    def clearYield(self):
        self.inputCount = 0
        self.passCount = 0
        self.updateYieldPanel()

    # 点击loop测试的‘abort’按钮
    def abortLoopAction(self):
        self.myLogger.logger.debug('this is abortLoopAction func')
        self.abortLoopFlag = True
        self.abortLoop_btn['state'] = DISABLED

    # ----------------------------------
    # 回调事件
    # ----------------------------------
    # 密码认证view回调
    def passwordCallBack(self, msg):
        if msg == 1:
            self.myLogger.logger.info('password is right')
            self.modeValue.set(1)
            self.master['bg'] = '#FFC0CB'
            self.debugFrame.place(x=600, y=300, width=180, height=200)
            self.sendMsg2Slot("mode:debug", allSend=True)
        else:
            self.myLogger.logger.warn('password is wrong')
            self.modeValue.set(2)

    # 从Scan sn view接收消息
    def receivedMsgFromScanSn(self, msg):
        self.myLogger.logger.info("msg form scan sn:" + str(msg))
        self.snArr = msg
        if len(self.snArr) == 0:
            self.snIsReady = False
            return
        for i in range(0, self.slotCount):
            if self.selectedArr[i]:
                msg = 'sn:%s' % self.snArr[i]
                self.slotArr[i].receiveMsgFromSS(msg)
        self.snIsReady = True
        self.clickStartAllBtn()

    # 从SS view的config view接收消息
    def receivedMsgFromConfig(self, msg):
        self.myLogger.logger.debug("msg form config:" + str(msg))
        # self.master.grab_set()

    # 从Slot view接收消息
    def receivedMsgFromSlot(self, index, msg):
        # 线程加锁
        self.lock.acquire()
        self.myLogger.logger.info("index:{} msg:{}".format(str(index), msg))
        self.receivedMsgQueue.put((index, msg))
        # 线程释放锁
        self.lock.release()
        self.myLogger.logger.info('SS lock release now')

    # 点击SS view关闭按钮的回调事件
    def closeWinCallback(self):
        if messagebox.askokcancel("Warning", "Exit ？"):
            exitProgBar = MyProgressBar1(self.master, self.exitProgressFinish, self.exitProgressQueue, title='Waiting...')
            self.exitProgressQueue.put((10, 'Init exit...OK'))
            self.abortLoopFlag = True
            # 关闭主框架打开的设备
            # self.cfgView.closeDevices()
            # 通知Slot，退出程序
            self.sendMsg2Slot('exit', allSend=True)
            self.exitProgressQueue.put((15, 'Send exit msg to slots...OK'))
            # 停留0.5s
            # time.sleep(0.5)
            # 关闭主窗体
            # self.master.destroy()

            # kill python progress
            # if self.sysName == "Windows":  # Winsows os
            #     os.system('taskkill /f /im python.exe')
            # else:  # Mac os / Linux os
            #     os.system('killall python')
            # return True
            return False
        else:

            self.myLogger.logger.debug('cancel close app!')
            return False

    # 响应输入SN回车事件
    def inputSnEvent(self, event=None):
        if self.isTesting:
            return
        sn = self.firstSn.get().upper()
        if len(sn) == 0:
            return
        self.myLogger.logger.debug("first scan sn:" + sn)
        self.firstSn.set('')
        if self.selectedSlotCount == 0:
            messagebox.showerror(title='Error', message='Not any slot is selected!')
        else:
            self.sendMsg2Slot('idle')
            self.snIsReady = False
            scanSn = ScanSnUI(self.master, sn, self.selectedArr, self.receivedMsgFromScanSn)

    # ----------------------------------
    # 其他方法
    # ----------------------------------
    def setupCsvHelper(self):
        items_Arr = self.slotArr[0].testplan['TestItems']
        up_Arr = self.slotArr[0].testplan['Up']
        low_Arr = self.slotArr[0].testplan['Low']
        unit_Arr = self.slotArr[0].testplan['Unit']
        csvTitle = {
            "firstLine": '',
            "upLimitLine": '',
            "lowLimitLine": '',
            "unitLine": ''
        }
        # csv title: SN,result,slot id,error code,fail list,start time,end time,item1,tiem2...
        csvTitle['firstLine'] = 'SN,Result,Slot ID,Error code,Fail list,Start time,End time,'
        csvTitle['upLimitLine'] = 'Up--->,,,,,,,'
        csvTitle['lowLimitLine'] = 'Low--->,,,,,,,'
        csvTitle['unitLine'] = 'Unit--->,,,,,,,'
        for i in range(0, len(items_Arr)):
            csvTitle['firstLine'] = csvTitle['firstLine'] + items_Arr[i] + ','
            csvTitle['upLimitLine'] = csvTitle['upLimitLine'] + up_Arr[i] + ','
            csvTitle['lowLimitLine'] = csvTitle['lowLimitLine'] + low_Arr[i] + ','
            csvTitle['unitLine'] = csvTitle['unitLine'] + unit_Arr[i] + ','
        self.csvTitleStr = csvTitle['firstLine'] + '\n' + \
            csvTitle['upLimitLine'] + '\n' + \
            csvTitle['lowLimitLine'] + '\n' + \
            csvTitle['unitLine'] + '\n'

    # 主线程刷新UI队列，周期200ms

    def updateUIloop(self):
        # self.myLogger.logger.warn(threading.currentThread().getName())
        # print('update ui loop...%d',self.index)
        while self.updateUIQueue.qsize():
            try:
                msg = self.updateUIQueue.get(0)
                # 0,'finishTest'
                if msg[0] == 0:
                    self.sendMsg2Slot("finish", allSend=True)
                    self.snEntry['state'] = NORMAL
                    self.startAll_btn['state'] = NORMAL
                    self.clear_btn['state'] = NORMAL
                    self.snIsReady = False
                    self.menu.entryconfig('Setting', state=NORMAL)
                    self.updateYieldPanel()
                    # normal mode
                    if self.modeValue.get() == 2:
                        self.isTesting = False

                # 1,close cfg view
                elif msg[0] == 1:
                    self.snEntry['state'] = NORMAL
                    self.snEntry.focus()
                # 2,'start all test' ---for loop test next test
                elif msg[0] == 2:
                    self.startAllTestAction()
                # 3,'finishAllLoop' ---for loop test finish all test
                elif msg[0] == 3:
                    self.loopCountStr.set('1')
                    self.abortLoop_btn['state'] = DISABLED
                    self.loopCountEntry['state'] = NORMAL
                    self.ssCfg_btn['state'] = NORMAL
                    self.isTesting = False
                # 4,load_2
                elif msg[0] == 4:
                    self.load_2()
                # 5,load_3
                elif msg[0] == 5:
                    self.load_3()

            except Exception as e:
                self.myLogger.logger.error(str(e))

        self.master.after(200, self.updateUIloop)

    # 载入SS view配置文件
    def readCfg(self):
        self.rwJson = RWjson('StationCfg.json')
        result, self.rootCfg = self.rwJson.loadJson()
        if result:
            self.inputCount = self.rootCfg['input']
            self.passCount = self.rootCfg['pass']
            self.slotCount = self.rootCfg['SlotCount']
            self.swName = self.rootCfg['SoftwareName']
            self.swVersion = self.rootCfg['Version']
            self.password = self.rootCfg['PassWord']

        else:
            self.myLogger.logger.error('load config json error')
            raise

    # 刷新良率统计
    def updateYieldPanel(self, save=True):
        self.inputInfo.set('Input:' + str(self.inputCount))
        self.passInfo.set('Pass:' + str(self.passCount))
        if self.inputCount == 0:
            yieldVal = 0.0
        else:
            yieldVal = self.passCount / self.inputCount * 100
        self.yieldInfo.set('Yield:{:.2f}%'.format(yieldVal))
        if save:
            self.rootCfg['input'] = self.inputCount
            self.rootCfg['pass'] = self.passCount
            result = self.rwJson.saveJson(self.rootCfg)
            if result:
                self.myLogger.logger.debug('save json config successful')
            else:
                self.myLogger.logger.error('save json config failure')
                # raise

    # 开始所有单元的测试
    def startAllTestAction(self):
        self.isTesting = True
        self.SSKey = True
        self.syncSignaCount = 0
        self.allCsvData = ''
        self.syncSignaCheckSUM = self.selectedSlotCount
        self.menu.entryconfig('Setting', state=DISABLED)
        self.endTestCount = 0
        self.sendMsg2Slot("start", allSend=True)
        self.snEntry['state'] = DISABLED
        self.startAll_btn['state'] = DISABLED
        self.clear_btn['state'] = DISABLED

    # 向SlotView发送信息
    def sendMsg2Slot(self, msg, allSend=False):
        for i in range(0, self.slotCount):
            # time.sleep(0.1)
            if allSend:
                self.slotArr[i].receiveMsgFromSS(msg)
            else:
                if self.selectedArr[i]:
                    self.slotArr[i].receiveMsgFromSS(msg)

    # 开启消息处理队列（子线程运行）
    def startMsgQueue(self):
        while not self.exitFlag:
            while self.receivedMsgQueue.qsize():
                try:
                    ls = self.receivedMsgQueue.get(0)
                    index = ls[0]
                    msg = ls[1]
                    if msg.startswith("selected"):
                        value = int(msg.split(':')[1])
                        self.selectedArr[index] = value
                        if value:
                            self.selectedSlotCount += 1
                        else:
                            self.selectedSlotCount -= 1
                        # 没有选择任何位置
                        if self.selectedSlotCount == 0:
                            messagebox.showerror(title='Error', message='Not any slot is selected!')

                    elif msg.startswith("endTest"):
                        self.endTestCount += 1
                        self.syncSignaCheckSUM -= 1
                        resultVal = int(msg.split('#')[1])
                        self.allCsvData = self.allCsvData + msg.split('#')[2] + '\n'
                        self.inputCount += 1
                        self.passCount += resultVal
                        if self.endTestCount == self.selectedSlotCount:
                            self.myLogger.logger.info("find all test task!")
                            # save all slots csv data
                            modeStr = 'Normal'
                            if self.modeValue.get() == 1:
                                modeStr = 'Debug'
                            self.csvHelper.InitCsv(modeStr)
                            self.csvHelper.CreatCsv(self.csvTitleStr)
                            self.csvHelper.SaveCsv(self.allCsvData)

                            self.updateUIQueue.put((0, 'finishTest'))
                            # debug mode
                            if self.modeValue.get() == 1:
                                self.finishLoopCount += 1
                                self.finishLoopStr.set('finished:%d' % self.finishLoopCount)
                                if self.finishLoopCount < self.loopCountInt and not self.abortLoopFlag:
                                    time.sleep(0.5)
                                    self.updateUIQueue.put((2, 'startLoopTest'))
                                else:
                                    self.myLogger.logger.debug('finish all loop test')
                                    self.updateUIQueue.put((3, 'finishAllLoop'))

                    elif msg.find("closeCfgView") != -1:
                        self.updateUIQueue.put((1, 'closeCfgView'))

                    elif msg.find('exitOK') != -1:
                        self.exitOkCount += 1
                        if self.exitOkCount == self.slotCount:
                            self.myLogger.logger.info('all slot exit OK!')
                            t = threading.Thread(target=self.closeSelf)
                            t.setDaemon(True)
                            t.start()

                    # ---------------------------------------------------------------
                    # Slot异步请求，多个Slot同步执行各自的弹窗任务-->>async dialog
                    # 1.Slot发出请求，取用SS view的虚拟Key
                    # 2.SS view异步处理请求，有Key应答OK，无Key应答NG
                    # 3.若无Key,Slot循环发出请求，直到取到Key的OK信号
                    # 4.Slot拿到Key后执行同步任务（例如弹窗)
                    # 5.Slot执行完毕归还Key（self.sendEvent(self.index,"returnKey"))
                    # ---------------------------------------------------------------
                    elif msg.find("asyncQuery:") != -1:
                        cmd = msg.split(':')[1]
                        reReply = 'NG'
                        if cmd == 'asyncKey':
                            if self.SSKey:
                                self.SSKey = False
                                reReply = 'OK'
                        # 应答回复Key的状态
                        t = threading.Thread(target=self.asyncReplySlotFunc,
                                             name='asyncQueryThread_Slot-%d' % index, args=(index, cmd, reReply))
                        t.setDaemon(True)
                        t.start()
                        self.myLogger.logger.debug('start async reply done.')
                    elif msg.find("returnKey") != -1:
                        self.SSKey = True
                    # ------------------------------------------------------------
                    # Slot同步请求，多个Slot同步后执行同一个弹窗任务-->>syncDialog
                    # 1.Slot发出请求，SS view 同步信号计数器累加1
                    # 2.Slot发出请求后，进入等待SS view应答循环状态
                    # 3.SS view接收请求，当同步信号累加值等于激活的Slot数量，
                    #   代表多个Slot进度达到同步状态，全部进入等待应答状态
                    # 4.此时SS view执行需要执行的同步任务（弹窗syncDialog）
                    # 5.任务结束后，SS view向发出请求的Slot回应OK应答信号
                    # ------------------------------------------------------------
                    elif msg.find("syncQuery:") != -1:
                        cmd = msg.split(':')[1]
                        # 同步信号累加
                        self.syncSignaCount += 1
                        # 同步信号累加值达到激活的Slot数量
                        if self.syncSignaCount == self.syncSignaCheckSUM:
                            self.syncSignaCount = 0
                            reReply = 'OK'
                            # 触发执行同步任务
                            t = threading.Thread(target=self.syncReplySlotFunc,
                                                 name='syncQueryThread_Slot-%d' % index, args=(index, cmd, reReply))
                            t.setDaemon(True)
                            t.start()
                        self.myLogger.logger.debug('start sync reply done.')
                except Exception as e:
                    self.myLogger.logger.error(str(e))
            time.sleep(0.05)

    # -----------------------------
    # 异步应答Slot发出的异步执行请求
    # 不阻塞SS view当前线程
    # 在子线程中执行，不可调用UI资源
    # -----------------------------
    def asyncReplySlotFunc(self, index, cmd, reReply):
        self.myLogger.logger.info('async question:{} from slot:{}'.format(cmd, index))
        response = 'NA'
        if cmd.find('asyncKey') != -1:
            response = reReply

        reply = "asyncReply:" + response
        self.slotArr[index].receiveMsgFromSS(reply)

    # -----------------------------
    # 异步应答Slot发出的同步执行请求
    # 不阻塞SS view当前线程
    # 在子线程中执行，不可调用UI资源
    # -----------------------------
    def syncReplySlotFunc(self, index, cmd, reReply):
        self.myLogger.logger.info('sync question:{} from slot:{}'.format(cmd, index))
        response = reReply
        if cmd.find('dialog#') != -1:
            # MyDialogOk(self.master, msg=cmd.split('#')[1])
            self.myLogger.logger.info('sync task print log!!!')

        reply = "syncReply:" + response
        self.sendMsg2Slot(reply)

    def closeSelf(self):
        while self.isTesting:
            time.sleep(0.2)
        self.exitFlag = True
        self.exitProgressQueue.put((60, 'All slot exit...OK'))
        self.cfgView.closeDevices()
        time.sleep(0.2)
        self.exitProgressQueue.put((90, 'SS close devices...OK'))
        self.myLogger.logger.info('will exit the app...')
        time.sleep(0.5)
        self.exitProgressQueue.put((100, 'Finish exit progress...OK'))

    def exitProgressFinish(self, msg):
        self.myLogger.logger.info("message from exit bar:" + str(msg))
        self.master.destroy()


if __name__ == '__main__':
    # print(sys.path[0])
    # startPDCAserver='python2.7 ' +sys.path[0] +'/MyModules/PDCApy27Server.py'
    # output=os.popen(startPDCAserver)
    # print('output:' + str(output.readlines()))
    # 实例化主框架应用
    app = SSUI()
