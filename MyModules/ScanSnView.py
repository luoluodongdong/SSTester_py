# coding:UTF-8
import tkinter as tk
from tkinter import *
from tkinter import ttk
import time
from datetime import datetime
from tkinter import messagebox
from tkinter import scrolledtext
import threading
import logging

from .SnIsOk import *


class ScanSnUI(tk.Toplevel):
    """docstring for TestUI"""

    def __init__(self,master,firstSn,selectedArr,endCommand):
        super(ScanSnUI, self).__init__()
        self.logger=logging.getLogger('SSUI.scanSn')
        self.master = master
        self.endCommand = endCommand
        self.lock = threading.Lock()

        # SN
        self.sn = firstSn
        # 需要扫描的位置数组[1,0,1,1]
        self.selectedArr = selectedArr
        # 需要sn的统计
        self.snSum = len(selectedArr)
        # 下一个需要扫描的sn的索引
        self.nextSnIndex = 0
        # 已完成扫描sn的数量统计
        self.finishScanCount = 0
        # sn数组
        self.snArr = []
        # Check Sn is OK
        self.checkSn = CheckSn(self.logger)

        self.inputSn = StringVar()
        self.setup()
        # check first Sn
        # sn是否ok
        if self.checkSn.isOK(self.sn):
            if self.hasFinished():
                self.logger.info(self.snArr)
                self.endCommand(self.snArr)
                self.destroy()
                return
        else:
            messagebox.showerror(title='Error',message='Check sn result is failure!')

        self.snEntry.focus()

    def setup(self):
        self.transient(self.master)
        body = Frame(self)
        self.initial_focus = self.loadUI(body)
        body.pack(padx=0, pady=0,fill='both')
        # body.place(x=0,y=0,width=400,height=800)

        #---------just for test self--------
        # t = threading.Thread(target=self.testFunc)
        # t.start()
        #-----------------------------------

        # self.initStatus(self.statusArr,self.infoArr)
        # self.initLog(self.logArr)

        # self.update_UI()

        # 创建线程，如果函数里面有参数，args=()
        self.logger.info('ScanSn loadUI done')
        # 注册关闭窗口回调
        self.protocol("WM_DELETE_WINDOW", self.callback)

        # self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self

        self.geometry("+%d+%d" % (self.master.winfo_rootx() + 400,
                                  self.master.winfo_rooty() + 100))
        self.focus_set()
        self.resizable(width=False, height=False)  # 宽不可变, 高可变,默认为True

        # self.wait_window(self)

    # 窗体手动关闭时回调事件
    def callback(self):
        # messagebox.showwarning(title="警告",message='关闭提示窗口!')
        self.logger.warn("[warning]manual close scanSn view...")
        self.endCommand([])
        self.destroy()

    # 载入控件
    def loadUI(self,parent):
        # 新建一个输入框
        self.snEntry = Entry(parent, 
                             textvariable=self.inputSn,
                             width=30,
                             bg='white',
                             state='normal'
                             ) 
        self.snEntry.pack(side='top',padx=10,pady=10,fill='x')
        self.snEntry.bind('<Return>', self.inputSnEvent)

        # 滚动文本框
        scrolW = 30  # 设置文本框的长度
        scrolH = 20  # 设置文本框的高度
        self.scrText = scrolledtext.ScrolledText(parent, font="Arial 16",width=scrolW,height=scrolH, wrap=tk.WORD)    
        self.scrText.pack(side='left',fill='both',expand='yes')
        # self.scrText.place(x=10,y=40)

        self.title("ScanSn View")

    # 响应sn输入事件
    def inputSnEvent(self,event=None):
        # 启动线程锁
        self.lock.acquire()
        self.snEntry['bg'] = 'gray'
        self.sn = self.inputSn.get().upper()
        self.inputSn.set('')
        self.logger.info("scan sn:" + self.sn)
        if len(self.sn) == 0:
            self.snEntry['bg'] = 'white'
            # 激活窗体
            self.focus_force()
            # 获取焦点
            self.snEntry.focus()
            # 刷新UI
            self.update()
            # 线程锁释放
            self.lock.release()
            return

        # sn是否重复
        repeatFlag = False
        for item in self.snArr:
            if item == self.sn:
                repeatFlag = True
                break
        if repeatFlag:
            messagebox.showerror(title='Error',message='SN is repeat!')
        else:
            # sn是否ok
            if self.checkSn.isOK(self.sn):
                if self.hasFinished():
                    self.logger.debug(self.snArr)
                    self.endCommand(self.snArr)
                    self.lock.release()
                    self.destroy()
                    return
            else:
                messagebox.showerror(title='Error',message='Check sn result is failure!')
        # time.sleep(1.0)
        self.snEntry['bg'] = 'white'
        # 激活窗体
        self.focus_force()
        # 获取焦点
        self.snEntry.focus()
        # 刷新UI
        self.update()
        # 线程锁释放
        self.lock.release()
        self.logger.info("-->>scan sn done.")

    # 扫描SN是否结束？
    def hasFinished(self):
        self.logger.debug('this is hasFinished')
        # 当前sn存入数组的标记
        currentSnHasMark = 0
        for index in range(self.nextSnIndex,self.snSum):
            if self.selectedArr[index]:
                if not currentSnHasMark:
                    msg = "[{}]:{}\n".format(index,self.sn)
                    self.scrText.insert(tk.END, msg)
                    self.scrText.see(tk.END)
                    self.finishScanCount += 1

                    self.snArr.append(self.sn)
                    currentSnHasMark = 1
                else:
                    self.nextSnIndex = index
                    break
            else:
                msg = "[{}]:{}\n".format(index,'NA')
                self.scrText.insert(tk.END, msg)
                self.scrText.see(tk.END)
                self.finishScanCount += 1

                self.snArr.append('')
                pass

        if self.finishScanCount == self.snSum:
            self.logger.info("finish all scan sn")

            return True
        else:
            return False

#*------just for test self--------*#


def finishScan(msg):
    print("finish scan sn:\n" + str(msg))


if __name__ == '__main__':
    root = Tk()
    root.title("SS View")
    root.geometry('800x600')  # 是x 不是*
    root.resizable(width=False, height=False)  # 宽不可变, 高可变,默认为True
    firstSn = 'sn123'
    selectedArr = [0,1,0,0]
    scanSn = ScanSnUI(root,firstSn,selectedArr,finishScan)
    # scanSn.snEntry.focus()

    root.mainloop()








