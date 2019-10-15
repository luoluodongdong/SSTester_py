
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
import queue
import sys


class MyProgressBar1(tk.Toplevel):
    """docstring for TestUI"""

    def __init__(self, master, endCommand, queue, title='ProgressBar1', interval=50):
        super(MyProgressBar1, self).__init__()

        self.master = master
        self.endCommand = endCommand
        self.titleStr = title
        self.interval = interval
        self.barValue = IntVar()
        self.barValue.set(0)
        self.barInfo = StringVar()
        self.barInfo.set('')
        self.isRunning = True
        self.updateQueue = queue
        self.setup()
        self.updateProgress()

    def setup(self):
        self.transient(self.master)
        body = Frame(self)
        self.initial_focus = self.loadUI(body)
        # body.pack(padx=0, pady=0, fill='both')
        body.place(x=0, y=0, width=300, height=100)

        # 注册关闭窗口回调
        self.protocol("WM_DELETE_WINDOW", self.callback)

        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self

        self.geometry("300x100+%d+%d" % (self.master.winfo_rootx() + 100,
                                         self.master.winfo_rooty() + 100))
        # self.focus_set()
        self.resizable(width=False, height=False)  # 宽不可变, 高可变,默认为True
        self.initial_focus.focus_set()
        # self.wait_window(self)

    # 窗体手动关闭时回调事件
    def callback(self):
        # messagebox.showwarning(title="警告",message='关闭提示窗口!')
        self.isRunning = False
        self.endCommand(0)
        self.master.grab_set()
        self.destroy()

    # 载入控件
    def loadUI(self, parent):
        # 创建Label，设置背景色和前景色
        self.info_lb = Label(parent,
                             textvariable=self.barInfo,
                             anchor='w',
                             fg='Black',
                             font="Arial 10",
                             height=1,
                             )
        self.info_lb.grid(row=1, column=0, sticky="s", padx=10, pady=5)
        # progressbar
        bar = ttk.Progressbar(parent,
                              maximum=100, length=280, variable=self.barValue)
        bar.grid(row=2, column=0, sticky="s", padx=10)
        self.title(self.titleStr)

    def updateProgress(self):
        if not self.isRunning:
            return
        while not self.updateQueue.empty():
            msg = self.updateQueue.get(0)
            self.barValue.set(msg[0])
            self.barInfo.set(msg[1])
            if msg[0] >= 100:
                t = threading.Thread(target=self.closeSelf)
                t.setDaemon(True)
                t.start()
                return

        self.master.after(self.interval, self.updateProgress)

    def closeSelf(self):
        time.sleep(0.5)
        self.endCommand(0)
        self.master.grab_set()
        self.destroy()


class MyWelcomeBar(tk.Toplevel):
    """docstring for TestUI"""

    def __init__(self, master, endCommand, queue, title='MyWelcomeBar', interval=50):
        super(MyWelcomeBar, self).__init__()

        self.master = master
        self.endCommand = endCommand
        self.titleStr = title
        self.interval = interval
        self.barValue = IntVar()
        self.barValue.set(0)
        self.barInfo = StringVar()
        self.barInfo.set('')
        self.isRunning = True
        self.updateQueue = queue
        self.setup()
        self.master.update()
        t = threading.Thread(target=self.updateProgress)
        t.setDaemon(True)
        t.start()
        # self.updateProgress()

    def setup(self):
        self.transient(self.master)
        print(self.wm_attributes())
        # self.wm_attributes('-toolwindow', 1)
        # self.wm_attributes('-transparentcolor', 'yellow')
        # self.wm_attributes('-alpha', 0.5)
        print(self.wm_attributes())
        body = Frame(self)
        self.initial_focus = self.loadUI(body)
        # body.pack(padx=0, pady=0, fill='both')

        body.place(x=0, y=0, width=600, height=400)

        # 注册关闭窗口回调
        self.protocol("WM_DELETE_WINDOW", self.callback)

        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self

        self.geometry("600x400")
        # self.geometry("600x400+%d+%d" % (self.master.winfo_rootx() + 100,
        #                                 self.master.winfo_rooty() + 100))
        # self.focus_set()
        self.resizable(width=False, height=False)  # 宽不可变, 高可变,默认为True
        self.initial_focus.focus_set()
        # self.wait_window(self)

    # 窗体手动关闭时回调事件
    def callback(self):
        pass
        # messagebox.showwarning(title="警告",message='关闭提示窗口!')
        self.isRunning = False
        self.endCommand(0)
        self.master.grab_set()
        self.destroy()

    # 载入控件
    def loadUI(self, parent):
        bgFile = sys.path[0] + '/MyModules/medias/bg600x400.png'
        self.photo = tk.PhotoImage(file=bgFile)
        # 创建Label，设置背景色和前景色
        self.bgPic = Label(parent,
                           text='Welcome',
                           fg='white',
                           font="Arial 28",
                           image=self.photo,
                           compound=tk.CENTER
                           )
        # self.bgPic.pack()
        self.bgPic.place(x=0, y=0)
        parent.update()
        # self.bgPic.grid(row=0, column=0, padx=0, pady=0)
        # 创建Label，设置背景色和前景色
        self.info_lb = Label(parent,
                             textvariable=self.barInfo,
                             anchor='w',
                             fg='white',
                             font="Arial 12",
                             background='green',
                             height=1,
                             )
        self.info_lb.place(x=10, y=330)
        # progressbar
        bar = ttk.Progressbar(parent,
                              maximum=100, length=580, variable=self.barValue)
        bar.place(x=10, y=360)
        self.title(self.titleStr)

    def updateProgress(self):
        while self.isRunning:
            while not self.updateQueue.empty():
                msg = self.updateQueue.get(0)
                self.barValue.set(msg[0])
                self.barInfo.set(msg[1])
                self.master.update()
                if msg[0] >= 100:
                    t = threading.Thread(target=self.closeSelf)
                    t.setDaemon(True)
                    t.start()
                    return
            time.sleep(0.05)

    def closeSelf(self):
        time.sleep(1)
        self.destroy()
        self.endCommand(0)
        self.master.grab_set()


class App(object):
    """docstring for App"""

    def __init__(self):
        super(App, self).__init__()
        self.master = Tk()

        self.initWidgets()
        self.master.title("SS View")
        self.master.geometry('800x600')  # 是x 不是*
        self.master.resizable(width=False, height=False)  # 宽不可变, 高可变,默认为True
        # scanSn.snEntry.focus()
        self.updateProgressQueue = queue.Queue()

        self.master.mainloop()

    def initWidgets(self):
        # 新建一个按钮
        self.ok_btn = Button(self.master,
                             text='OK',
                             highlightcolor='blue',
                             highlightthickness=2,
                             command=self.okBtnAction)  # 背景色:蓝色

        self.ok_btn.place(x=10, y=10, width=60, height=20)

    def finishProgress(self, msg):
        print('finishProgress msg:' + str(msg))

    def okBtnAction(self):
        progBar1 = MyWelcomeBar(self.master, self.finishProgress, self.updateProgressQueue)
        print('load progress bar done')
        testT = threading.Thread(target=self.testProgressBarThread)
        testT.setDaemon(True)
        testT.start()

    def testProgressBarThread(self):
        for i in range(0, 11):
            self.updateProgressQueue.put((i * 10, 'progressing_%d' % (i * 10)))
            time.sleep(0.5)


if __name__ == '__main__':
    myApp = App()
