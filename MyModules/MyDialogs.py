# coding:UTF-8
import tkinter as tk
from tkinter import *
from tkinter import ttk


class MyDialogOk(tk.Toplevel):
    """docstring for TestUI"""

    def __init__(self, master, msg):
        super(MyDialogOk, self).__init__()

        self.master = master
        self.msg = msg
        self.result = False

        # self.readCfg()

        # self.serial2=None
        self.showUI()

    def showUI(self):
        # self.resizable(width=False, height=False)  # 宽不可变, 高可变,默认为True
        self.geometry("300x200+%d+%d" % (self.master.winfo_rootx() + 100,
                                         self.master.winfo_rooty() + 100))
        self.master.update()
        self.transient(self.master)
        body = Frame(self,
                     bg='yellow')
        self.initial_focus = self.loadUI(body)
        # body.pack(padx=0, pady=0, fill='both')
        body.place(x=10, y=10, width=280, height=180)
        self.myPrint('MyDialogOk loadUI done')
        # 注册关闭窗口回调
        self.protocol("WM_DELETE_WINDOW", self.callback)

        if not self.initial_focus:
            self.initial_focus = self

        # self.focus_set()

        self.bind('<Return>', self.okBtnAction)
        self.title("Dialog")

        self.grab_set()
        self.ok_btn.focus()

        self.wait_window(self)
    # 载入控件

    def loadUI(self, parent):

        # 创建Label，设置背景色和前景色
        self.info_lb = Label(parent,
                             text=self.msg,
                             fg='Black',
                             font="Arial 16",
                             bg='white',
                             width=21,
                             height=5,
                             wraplength=260,
                             justify='left'
                             )
        # 使用place()设置该Label的大小和位置
        # self.info_lb.place(x=10, y=10, width=260, height=120)
        self.info_lb.place(x=10, y=10)
        # 新建一个按钮
        self.ok_btn = Button(parent,
                             text='OK',
                             highlightcolor='blue',
                             highlightthickness=2,
                             command=self.okBtnAction)  # 背景色:蓝色

        self.ok_btn.place(x=105, y=160, width=60, height=20)

        # self.serial2.setup(parent,10,80)

    def okBtnAction(self, event=None):
        self.master.grab_set()
        self.myPrint('click ok button')
        self.destroy()

    # 窗体手动关闭时回调事件
    def callback(self):
        # messagebox.showwarning(title="警告",message='关闭提示窗口!')
        self.myPrint("[info]manual close dialog view...")
        self.master.grab_set()
        self.destroy()

        # self.saveCfg()

    def myPrint(self, msg):
        print('[MyDialogOk]' + str(msg))


class MyDialogYESorNO(tk.Toplevel):
    """docstring for TestUI"""

    def __init__(self, master, msg):
        super(MyDialogYESorNO, self).__init__()

        self.master = master
        self.msg = msg
        self.focusIndex = 0
        # self.readCfg()

        # self.serial2=None
        self.showUI()

    def showUI(self):
        self.transient(self.master)
        body = Frame(self,
                     ba='yellow')
        self.initial_focus = self.loadUI(body)
        # body.pack(padx=0, pady=0,fill='both')
        body.place(x=10, y=10, width=280, height=180)
        self.myPrint('MyDialogYESorNO loadUI done')
        # 注册关闭窗口回调
        self.protocol("WM_DELETE_WINDOW", self.callback)

        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self

        self.geometry("300x200+%d+%d" % (self.master.winfo_rootx() + 100,
                                         self.master.winfo_rooty() + 100))

        self.resizable(width=False, height=False)  # 宽不可变, 高可变,默认为True
        # self.focus_set()

        self.bind('<Return>', self.returnAction)
        self.yes_btn.focus()
        self.wait_window(self)
    # 载入控件

    def loadUI(self, parent):

        # 创建Label，设置背景色和前景色
        self.info_lb = Label(parent,
                             text=self.msg,
                             fg='Black',
                             font="Arial 16",
                             bg='white',
                             width=20,
                             height=5,
                             wraplength=260,
                             justify='left'
                             )
        # 使用place()设置该Label的大小和位置
        self.info_lb.place(x=10, y=10)
        # 新建一个按钮
        self.yes_btn = Button(parent,
                              text='YES',
                              highlightcolor='blue',
                              highlightthickness=2,
                              command=self.yesBtnAction)  # 背景色:蓝色

        self.yes_btn.place(x=60, y=160, width=60, height=20)
        self.yes_btn.bind('<FocusIn>', self.yesBtnFocusIn)
        # 新建一个按钮
        self.no_btn = Button(parent,
                             text='NO',
                             highlightcolor='blue',
                             highlightthickness=2,
                             command=self.noBtnAction)  # 背景色:蓝色

        self.no_btn.place(x=140, y=160, width=60, height=20)
        self.no_btn.bind('<FocusIn>', self.noBtnFocusIn)
        # self.serial2.setup(parent,10,80)

        self.title("Dialog")

    def yesBtnAction(self, event=None):
        self.master.grab_set()
        self.myPrint('click yes button')
        self.result = True
        self.destroy()

    def noBtnAction(self, event=None):
        self.master.grab_set()
        self.myPrint('click no button')
        self.result = False
        self.destroy()

    def yesBtnFocusIn(self, event=None):
        self.focusIndex = 0

    def noBtnFocusIn(self, event=None):
        self.focusIndex = 1

    def returnAction(self, event=None):
        if self.focusIndex == 0:
            self.result = True
        else:
            self.result = False
        self.destroy()

    # 窗体手动关闭时回调事件
    def callback(self):
        # messagebox.showwarning(title="警告",message='关闭提示窗口!')
        self.myPrint("[info]manual close dialog view...")
        self.master.grab_set()
        self.result = False
        self.destroy()

        # self.saveCfg()

    def myPrint(self, msg):
        print('[MyDialogYESorNO]' + str(msg))
