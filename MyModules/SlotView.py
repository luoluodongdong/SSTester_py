# coding:UTF-8
import tkinter as tk
from tkinter import *
from tkinter import ttk
import time
from datetime import datetime
from tkinter import messagebox
import threading
import queue
import re
import logging
import os
import sys

from .DetialView import DetialView
from .MyDialogs import MyDialogOk
from .ConfigView import ConfigPanel
from .Logger import MyLogger
from .LoadTestplan import LoadTestPlan
import zmq


class SlotView(object):
    """docstring for SlotView"""

    def __init__(self, params):
        super(SlotView, self).__init__()
        self.master = params['master']
        self.index = params['index']
        self.swName=params['swName']
        self.swVersion=params['swVersion']
        self.myLogger = MyLogger(name='Slot-%d' % self.index)
        self.x = params['x']
        self.y = params['y']

        self.bg = '#E0FFFF'
        self.sn = StringVar()
        self.sn.set("SN12345678901234567")
        self.status = StringVar()
        self.timer = StringVar()
        self.status.set("idle")
        self.timer.set("0s")
        self.sendEvent = params['sendEvent']
        self.exitNow = False
        self.selectedFlag = True
        self.isTesting = False
        self.mode = 'normal'
        # query SS
        self.replyFormSSFlag = False
        self.replyMsgFromSS = StringVar()

        self.printDetialQueue = queue.Queue()
        self.updateUIQueue = queue.Queue()
        self.receivedSSmsgQueue = queue.Queue()
        self.detialView = None

        self.lock = threading.Lock()
        self.uiIsBusy = False
        self.startTime = None
        # for collection csv datas
        self.csvData = {
            "sn": "",
            "result": "",
            "errorCode": "",
            "failList": "",
            "startTime": "",
            "endTime": "",
            "slotID": "",
            "values": ""
        }

        self.initWidgets()
        # 加载设备
        self.cfgView = ConfigPanel(self.master, "Slot-%d" %self.index, self.receivedMsgFromConfig)
        if self.cfgView.errCount != 0:
            self.myLogger.logger.error('Slot-%d config error,please check!' %self.index)
            messagebox.showerror(title='Error', message='Slot-%d Config error,please check!' %self.index)
            self.changeStatus('error')
        # 加载TestPlan
        testPlanFile = self.cfgView.rwJson.resourceFolder + '/TestPlan.csv'
        ltp=LoadTestPlan(testPlanFile)
        self.testplan=ltp.context
        # print(self.testplan)
        # 更新test mode
        self.updateMode()
        # 开启UI刷新loop(主线程运行)
        self.updateUIloop()
        self.initDetialView()

        # 开启消息接收处理子线程
        t = threading.Thread(target=self.startMsgQueue, name='msgThread_slot-%d' % self.index)
        t.setDaemon(True)
        t.start()

        self.myLogger.logger.info('start Slot-%d view done.' % self.index)
        self.myLogger.logger.warn('Slot-%d init' % self.index + str(threading.currentThread()))

    # 初始化各组件
    def initWidgets(self):
        # 创建Labelframe容器
        self.title = 'Slot-%d' % self.index
        self.fram = tk.Frame(self.master, bg=self.bg,)  # relief=tk.SOLID,)
        # self.lf.pack(expand=NO, padx=self.x, pady=self.y)
        # self.fram.bind("<Button-1>", self.callDetialView)
        self.fram.place(x=self.x, y=self.y, width=260, height=180)

        self.selected_val = IntVar()
        self.selected_val.set(1)
        self.selected_btn = Checkbutton(self.fram,
                                        bg=self.bg,
                                        text=self.title,
                                        variable=self.selected_val,
                                        command=self.selectClick,
                                        )
        self.selected_btn.place(x=5, y=5)

        # 创建Label，设置背景色和前景色
        self.sn_lb = Label(self.fram,
                           textvariable=self.sn,
                           fg='Black',
                           font="Arial 16",
                           bg=self.bg)
        # 使用place()设置该Label的大小和位置
        self.sn_lb.place(x=10, y=30, width=240, height=30)

        # status label
        # 创建Label，设置背景色和前景色
        self.status_lb = Label(self.fram,
                               textvariable=self.status,
                               fg='Black',
                               font="Arial 36",
                               bg=self.bg)
        # 使用place()设置该Label的大小和位置
        self.status_lb.bind("<Button-1>", self.callDetialView)
        self.status_lb.place(x=40, y=60, width=180, height=60)

        # 新建一个按钮
        self.call_cfg_btn = tk.Button(self.fram,
                                      bg=self.bg,
                                      relief='flat',
                                      text='Config',
                                      activebackground='blue',
                                      command=self.callConfigView)  # 背景色:蓝色

        self.call_cfg_btn.place(x=10, y=140, width=60, height=30)
        # self.call_detial_btn.pack()

        # timer label
        # 创建Label，设置背景色和前景色
        self.timer_lb = Label(self.fram,
                              textvariable=self.timer,
                              fg='Black',
                              font="Arial 18",
                              bg=self.bg)
        # 使用place()设置该Label的大小和位置
        self.timer_lb.place(x=170, y=140, width=80, height=40)

        # 新建一个按钮
        # self.start_btn = Button(self.fram,
        #                         text='Test',
        #                         command=self.startTest)  # 背景色:蓝色

        # self.start_btn.place(x=140, y=140, width=60, height=20)
        # self.call_detial_btn.pack()

        self.myLogger.logger.info('initWidgets done.')

    def initDetialView(self):

        config = {
            "index": self.index,
            "master": self.master,
            "queue": self.printDetialQueue,
            "closeEvent": self.closeDetialEvent,
            "items": self.testplan['TestItems']
        }

        self.detialView = DetialView(config)

    # 打开detialview
    def callDetialView(self, event=None):
        self.myLogger.logger.debug("click call detial view button...")
        self.detialView.showUI()

    # detialView 窗口关闭时回调
    def closeDetialEvent(self, msg):
        self.myLogger.logger.debug("close detial event")
        self.myLogger.logger.debug(msg)
        self.master.grab_set()
        # self.detialIsShow = False

        # self.detialView.update_UI()

    def callConfigView(self):
        self.myLogger.logger.debug('click call config view button...')

        self.cfgView.loadUI()
        self.myLogger.logger.info('show config view done.')

    def receivedMsgFromConfig(self, msg):
        self.myLogger.logger.debug('config msg:%s' % str(msg))
        # config view close event
        if str(msg) == '-1':
            self.sendEvent(self.index, 'closeCfgView')
        # config view devices all ready
        elif str(msg) == '0':
            self.changeStatus('ready')

    def updateMode(self):
        if self.mode == 'debug':
            self.call_cfg_btn.place(x=10, y=140, width=60, height=30)
        else:
            self.call_cfg_btn.place_forget()
            status = self.status.get().lower()
            self.changeStatus(status)

    # 输出Log
    def detialPrintLog(self, log):
        self.myLogger.logger.info(log)
        nowTime = datetime.now()
        tStr = nowTime.strftime('%H:%M:%S')
        msStr = nowTime.microsecond
        tStr = '[{}.{}]'.format(tStr, msStr)
        log = tStr + log
        self.printDetialQueue.put((2, '\n' + log))
        # self.detialView.textView.add_log('\n' + log)

    # 刷新UI队列loop(主线程)
    def updateUIloop(self):
        # self.myLogger.logger.warn(threading.currentThread().getName())
        if self.exitNow:
            return
        # print('update ui loop...%d',self.index)
        while self.updateUIQueue.qsize():
            try:
                msg = self.updateUIQueue.get(0)
                if msg[0] == 0:
                    self.changeStatus(msg[1])
                elif msg[0] == 1:
                    self.timer.set(msg[1])
                # start test
                elif msg[0] == 2:
                    self.selected_btn['state'] = DISABLED
                    if self.selectedFlag:
                        self.call_cfg_btn['state'] = DISABLED
                        # self.startTest()
                # finish
                elif msg[0] == 3:
                    self.selected_btn['state'] = NORMAL
                    self.call_cfg_btn['state'] = NORMAL
                # update mode
                elif msg[0] == 4:
                    self.updateMode()

            except Exception as e:
                self.myLogger.logger.error(str(e))

        self.master.after(200, self.updateUIloop)

    # ----------------------------------------------
    # 主测试任务(子线程进行)
    # 与SS UI界面交互借助于updateUIQueue
    # 与Detial View UI界面交互借助于printDetialQueue
    # ----------------------------------------------
    def testTask(self):
        # for i in range(0,20):
        #     print('item test...%d' % i)
        #     time.sleep(0.2)
        # self.changeStatus("testing")

        # result,response=self.cfgView.serial1.query('set LED on\r\n')

        self.updateUIQueue.put((1, '0s'))
        self.updateUIQueue.put((0, 'testing'))

        testResult = 'fail'
        saveData = ''

        for i in range(0, len(self.testplan['TestItems'])):
            t1 = time.time()
            thisItem = self.testplan['TestItems'][i]
            thisFunc = self.testplan['Function'][i]
            thisCommand = self.testplan['Command'][i]
            thisTimeout = self.testplan['TimeOut'][i]
            thisValueType = self.testplan['ValueType'][i]
            thisLow = self.testplan['Low'][i]
            thisReferVal = self.testplan['ReferValue'][i]
            thisUp = self.testplan['Up'][i]
            thisUnit = self.testplan['Unit'][i]
            thisSkip = self.testplan['Skip'][i]
            thisExitEnable = self.testplan['ExitEnable'][i]
            thisDelay = self.testplan['Delay'][i]

            # mark测试项开始时黄色状态
            self.printDetialQueue.put((0, 'testing'))
            # detialview log记录输出
            self.detialPrintLog("-----------------------------------")
            self.detialPrintLog("item:%s" % thisItem)
            # 初始化测试值和测试项状态
            thisValue = ''
            thisStatus = ''

            if thisSkip == 1:
                thisValue = 'NA'
                thisStatus = 'skip'
            else:
                # connectFIX
                if thisFunc == 'connectFIX':
                    result, response = self.cfgView.devices['DUT'].query(thisCommand, thisTimeout)
                    if result:
                        thisValue = response.strip()
                        if thisValueType == 'string':
                            if thisValue.find(thisReferVal) != -1:
                                thisStatus = 'pass'
                            else:
                                thisStatus = 'fail'
                        else:
                            saveData = thisValue
                            thisStatus = 'pass'

                    else:
                        thisValue = ''
                        thisStatus = 'fail'
                # connectREAD
                elif thisFunc == 'connectREAD':
                    result, response = self.cfgView.devices['DUT'].query(thisCommand, thisTimeout)
                    if result:
                        thisValue = response.strip()
                        if thisCommand == 'readStep':
                            thisValue = thisValue[:-3]
                        elif thisCommand == 'readTmp':
                            thisValue = thisValue[:-4]
                        elif thisCommand == 'readVolt1':
                            thisValue = thisValue[:-4]

                        if self.judgeValue(thisValue, thisLow, thisUp):
                            thisStatus = 'pass'
                        else:
                            thisStatus = 'fail'
                    else:
                        thisValue = ''
                        thisStatus = 'fail'
                # feedback
                elif thisFunc == 'feedback':
                    dataArray = saveData.split(',')
                    valueIndex = int(thisCommand) - 1
                    if valueIndex < len(dataArray):
                        thisValue = dataArray[valueIndex]
                        print(thisValue)
                        # convertOK,convertValue=self.ConvertELogStrToValue(thisValue)
                        # thisValue=str(thisValue)
                        if self.judgeValue(thisValue, thisLow, thisUp):
                            thisStatus = 'pass'
                        else:
                            thisStatus = 'fail'
                        pass
                    else:
                        thisValue = 'NA'
                        thisStatus = 'fail'
                # ---------------------------------------------------------------
                # Slot异步请求，多个Slot同步执行各自的子任务-->>async task
                # 1.Slot发出请求，取用SS view的虚拟Key
                # 2.SS view异步处理请求，有Key应答OK，无Key应答NG
                # 3.若无Key,Slot循环发出请求，直到取到Key的OK信号
                # 4.Slot拿到Key后执行同步任务（例如弹窗)
                # 5.Slot执行完毕归还Key（self.sendEvent(self.index,"returnKey"))
                # ---------------------------------------------------------------
                elif thisFunc == 'asyncTask':
                    result, reply = self.asyncQuerySS('asyncKey')
                    count = 0
                    while reply != 'OK':
                        time.sleep(0.5)
                        count += 0.5
                        result, reply = self.asyncQuerySS('asyncKey')
                        # 视情况而定timeOut 此处为50s
                        if count > 100:
                            break
                    if reply == 'OK':
                        #myDialog = MyDialogOk(self.master, msg='[Slot-{}]:\n{}'.format(self.index, thisCommand))
                        self.myLogger.logger.info('Async task print log!!!')
                        thisStatus = 'pass'
                        self.sendEvent(self.index, "returnKey")
                    else:
                        thisStatus = 'fail'
                    thisValue = reply

                # ------------------------------------------------------------
                # Slot同步请求，多个Slot同步后执行同一个任务-->>sync task
                # 1.Slot发出请求，SS view 同步信号计数器累加1
                # 2.Slot发出请求后，进入等待SS view应答循环状态
                # 3.SS view接收请求，当同步信号累加值等于激活的Slot数量，
                #   代表多个Slot进度达到同步状态，全部进入等待应答状态
                # 4.此时SS view执行需要执行的同步任务（弹窗syncDialog）
                # 5.任务结束后，SS view向发出请求的Slot回应OK应答信号
                # ------------------------------------------------------------
                elif thisFunc == 'syncTask':
                    result, reply = self.syncQuerySS('dialog#%s' % thisCommand)
                    if result:
                        thisStatus = 'pass'
                    else:
                        thisStatus = 'fail'
                    thisValue = reply

                # expection
                else:
                    self.myLogger.logger.error('error:unknown function:%s' % thisFunc)
                    thisValue = 'NA'
                    thisStatus = 'pass'

            detialT = time.time() - t1

            thisInfo = 'result:{} val:{} low:{} ref:{} up:{} unit:{} duration:{:.2f}s'.format(
                thisStatus, thisValue, thisLow, thisReferVal, thisUp, thisUnit, detialT)

            thisValue = thisValue.replace(',', ';')
            thisValue = thisValue.replace('\r', '')
            thisValue = thisValue.replace('\n', ' ')
            thisValue = thisValue.replace('#', '@')
            self.csvData['values'] = self.csvData['values'] + thisValue + ','

            # 输出测试log
            self.detialPrintLog(thisInfo)
            # 输出测试项详细结果
            self.printDetialQueue.put((1, thisInfo))
            # 输出测试项状态
            self.printDetialQueue.put((0, thisStatus))

            if thisStatus == 'fail':
                testResult = 'fail'
                self.csvData['failList'] = self.csvData['failList'] + thisItem + ';'
                if self.csvData['errorCode'] == '':
                    self.csvData['errorCode'] = 'ER_' + str(i)
            if thisStatus == 'fail' and thisExitEnable == 1:
                self.myLogger.logger.warn('error:exit this testing now!')
                break
            if self.exitNow:
                break

            time.sleep(thisDelay)

        # self.changeStatus("pass")
        if self.csvData['failList'] == '':
            testResult = 'pass'
        self.updateUIQueue.put((0, testResult))
        if testResult == 'pass':
            resultFlag = '1'
        else:
            resultFlag = '0'
        self.csvData['result'] = testResult.upper()
        self.csvData['endTime'] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

        # csv title: SN,result,slot id,error code,fail list,start time,end time,item1,tiem2...
        # self.myLogger.logger.info(self.csvData)
        csvDataStr = self.csvData['sn'] + ',' + \
            self.csvData['result'] + ',' + \
            self.csvData['slotID'] + ',' + \
            self.csvData['errorCode'] + ',' + \
            self.csvData['failList'] + ',' + \
            self.csvData['startTime'] + ',' + \
            self.csvData['endTime'] + ',' + \
            self.csvData['values']
        # print(csvDataStr)

        self.sendEvent(self.index, "endTest#" + resultFlag + "#" + csvDataStr)
        self.isTesting = False

    # 检查数组类型是否符合limit
    def judgeValue(self, val, low, up):
        try:
            if low == '' and up != '':
                if float(val) <= float(up):
                    return True
                else:
                    return False
            elif low != '' and up == '':
                if float(val) >= float(low):
                    return True
                else:
                    return False
            elif low != '' and up != '':
                if float(val) >= float(low) and float(val) <= float(up):
                    return True
                else:
                    return False
            else:
                self.myLogger.logger.warn('warning:no limit!')
                return True
        except Exception as e:
            self.myLogger.logger.error(str(e))
            return False

    # 开启主测试任务---子线程
    def startTest(self):
        self.myLogger.logger.debug("this is startTest...")
        self.myLogger.logger.warn('start Test func:' + str(threading.currentThread()))

        if self.isTesting:
            self.myLogger.logger.warn('Error,test task is going on!')
            return

        # reset detial view
        self.printDetialQueue.put((3, 'resetUI'))

        if not self.cfgView.devices['DUT'].opened:
            self.myLogger.logger.error('Error,devices not ready!')
            self.detialPrintLog('Devices not ready,please check!')
            self.sendEvent(self.index, "endTest:0")
            self.updateUIQueue.put((0, 'error'))
            self.isTesting = False
            return

        # init csv datas
        self.csvData = {
            "sn": "",
            "result": "",
            "errorCode": "",
            "failList": "",
            "startTime": "",
            "endTime": "",
            "slotID": "",
            "values": ""
        }
        self.startTime = time.time()
        self.csvData['sn'] = self.sn.get()
        self.csvData['slotID'] = 'Slot-%d' % self.index
        self.csvData['startTime'] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        self.isTesting = True
        # 开启计时线程
        t = threading.Thread(target=self.timerThread)
        t.setDaemon(True)
        t.start()

        self.testTask()

    # -----------------------------------------------------------------
    # just test for my dialogs
    def testDialogThread(self):

        self.closeDialog = MyDialogYESorNO(self.master, msg="Question:\nPlease close power,ok?")
        # self.closeDialog.wait_window()
        if self.closeDialog.result:
            print('result is true')
        else:
            print('result is false')

        print('MyDialogYESorNO test done.')
    # -----------------------------------------------------------------

    # 计时线程
    def timerThread(self):
        while self.isTesting:
            detaT = time.time() - self.startTime
            self.timer.set('%.2fs' % detaT)
            time.sleep(0.2)

    # 改变slotView状态
    def changeStatus(self, status):
        if status == "ready":
            self.status.set("Ready")
            self.changeBg("#E0FFFF")
        elif status == "testing":
            self.status.set("Testing")
            self.changeBg("#FFFF00")
        elif status == "pass":
            self.status.set("Pass")
            self.changeBg("#7CFC00")
        elif status == "fail":
            self.status.set("Fail")
            self.changeBg("red")
        elif status == "error":
            self.status.set("Error")
            self.changeBg("red")
        elif status == 'idle':
            self.status.set("Idle")
            self.changeBg("#00FFFF")

            self.timer.set('')

    # 改变slotview背景色
    def changeBg(self, color):
        self.fram.config(bg=color)
        self.sn_lb.config(bg=color)
        self.status_lb.config(bg=color)
        self.selected_btn.config(bg=color)
        self.timer_lb.config(bg=color)

    # slotView选中按钮点击事件
    def selectClick(self):
        self.selectedFlag = self.selected_val.get()
        self.myLogger.logger.debug("selectedFlag:%d" % self.selectedFlag)
        msg = "selected:%d" % self.selectedFlag
        self.sendEvent(self.index, msg)

        if self.selectedFlag:
            self.changeBg("#E0FFFF")
            self.sn.set("SN12345678901234567")
            self.status.set("Ready")
            # self.call_detial_btn.place(x=10, y=140, width=60, height=20)
        else:
            # self.call_detial_btn.place_forget()
            self.changeBg("#708090")
            self.sn.set("")
            self.status.set("")
            self.timer.set('')

    # 来自SS view的消息处理,周期50ms(子线程运行)
    def startMsgQueue(self):
        while not self.exitNow:
            while self.receivedSSmsgQueue.qsize():
                try:
                    msg = self.receivedSSmsgQueue.get(0)[1]
                    # 开始测试信息
                    if msg.find("start") != -1:
                        self.updateUIQueue.put((2, 'start'))
                        if self.selectedFlag:
                            thTimer = threading.Thread(target=self.startTest, name='startThread_Slot-%d' % self.index)
                            thTimer.setDaemon(True)
                            thTimer.start()
                    # 所有Slot测试结束信息
                    elif msg.find("finish") != -1:
                        self.updateUIQueue.put((3, 'finish'))
                        # self.selected_btn['state'] = NORMAL
                    # 接收sn信息
                    elif msg.find('sn:') != -1:
                        snStr = msg.split(':')[1]
                        self.sn.set(snStr)
                        self.updateUIQueue.put((0, 'ready'))
                    # 闲置状态信息
                    elif msg.find('idle') != -1:
                        self.sn.set("")
                        if self.selectedFlag:
                            self.updateUIQueue.put((0, 'idle'))
                        # self.changeStatus('idle')
                    # 程序退出信息
                    elif msg.find('exit') != -1:
                        self.exitNow = True
                        closeThread = threading.Thread(target=self.closeSelf)
                        closeThread.setDaemon(True)
                        closeThread.start()
                        # self.closeSelf()
                        # time.sleep(0.5)
                    # 模式信息
                    elif msg.find('mode:') != -1:
                        self.mode = msg.split(':')[1]
                        if self.selectedFlag:
                            self.updateUIQueue.put((4, 'updateMode'))
                    # 异步应答信息
                    elif msg.find('asyncReply:') != -1:
                        self.replyMsgFromSS.set(msg.split(':')[1])
                        self.replyFormSSFlag = True
                    # 同步请求应答信息
                    elif msg.find('syncReply:') != -1:
                        self.replyMsgFromSS.set(msg.split(':')[1])
                        self.replyFormSSFlag = True

                except Exception as e:
                    self.myLogger.logger.error(str(e))
            time.sleep(0.05)

    # 接收SSView发过来的消息
    def receiveMsgFromSS(self, msg):
        # 开启线程锁
        self.lock.acquire()
        self.myLogger.logger.info("slot_id:{} msg:{}".format(self.index, msg))
        self.myLogger.logger.warn("Slot-%d:receiveMsgFromSS" % self.index + str(threading.currentThread()))
        # 将消息添加到消息处理队列
        self.receivedSSmsgQueue.put((0, msg))
        # 关闭线程锁
        self.lock.release()

    # ---------------------------------------------
    # Async query SS View
    # 同步请求异步应答
    # 向主框架SS发出请求
    # 阻塞当前线程,不阻塞主框架线程
    # 此方法必须在任务线程（子线程）中执行
    # ---------------------------------------------
    def asyncQuerySS(self, cmd, timeout=2.0):
        self.replyMsgFromSS.set('')
        self.replyFormSSFlag = False
        self.sendEvent(self.index, 'asyncQuery:' + cmd)
        count = 0
        while count < timeout:
            time.sleep(0.05)
            count += 0.05
            if self.replyFormSSFlag:
                return True, self.replyMsgFromSS.get()
                break
        return False, ''

    # ---------------------------------------------
    # Sync query SS View
    # 同步多个Slot进度
    # 向主框架SS发出请求
    # 阻塞当前线程,不阻塞主框架线程
    # 此方法必须在任务线程（子线程）中执行
    # ---------------------------------------------
    def syncQuerySS(self, cmd, timeout=60.0):
        self.replyMsgFromSS.set('')
        self.replyFormSSFlag = False
        self.sendEvent(self.index, 'syncQuery:' + cmd)
        count = 0
        while count < timeout:
            time.sleep(0.05)
            count += 0.05
            if self.replyFormSSFlag:
                return True, self.replyMsgFromSS.get()
                break
        return False, ''

    def closeSelf(self):
        while self.isTesting:
            time.sleep(0.2)
        self.cfgView.closeDevices()

        self.sendEvent(self.index, 'exitOK')
        self.myLogger.logger.info('close self done.')
