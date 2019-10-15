# coding:UTF-8
import tkinter as tk
from tkinter import *
from tkinter import ttk
import time
from datetime import datetime
from tkinter import messagebox
from tkinter import scrolledtext
import threading


class PassWordUI(tk.Toplevel):
    """docstring for TestUI"""

    def __init__(self,master,logger,sendMsg):
        super(PassWordUI, self).__init__()
        self.logger=logger
        self.master = master
        self.endCommand = sendMsg
        self.rawKey=None
        self.keyStr = StringVar()
        self.keyStr.set('')
        self.setup()

        self.keyEntry.focus()

    def setup(self):
        self.transient(self.master)
        body = Frame(self)
        self.initial_focus = self.loadUI(body)
        body.pack()

        # 创建线程，如果函数里面有参数，args=()
        self.logger.info('Password loadUI done')
        # 注册关闭窗口回调
        self.protocol("WM_DELETE_WINDOW", self.callback)

        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self

        self.geometry("300x100+%d+%d" % (self.master.winfo_rootx() + 100,
                                         self.master.winfo_rooty() + 100))
        # self.focus_set()
        self.resizable(width=False, height=False)  # 宽不可变, 高可变,默认为True

        # self.wait_window(self)

    # 窗体手动关闭时回调事件
    def callback(self):
        # messagebox.showwarning(title="警告",message='关闭提示窗口!')
        self.logger.warn("[warning]manual close password view...")
        self.endCommand(0)
        self.master.grab_set()
        self.destroy()

    # 载入控件
    def loadUI(self,parent):
        # 创建Label，设置背景色和前景色
        infoLabel = Label(parent,
                          text='Key:',
                          fg='Black',
                          width=4,
                          font="Arial 16",
                          bg=parent['bg'])
        # 使用place()设置该Label的大小和位置
        infoLabel.pack(side='left',ipady=10,padx=0,pady=20)
        # 新建一个输入框
        self.keyEntry = Entry(parent, 
                              textvariable=self.keyStr,
                              show='*',
                              width=12,
                              bg=parent['bg'],
                              state='normal'
                              ) 
        self.keyEntry.pack(side='left',padx=0,pady=10)
        self.keyEntry.bind('<Return>', self.inputKeyEvent)

        self.title("Password View")

    # 响应key输入事件
    def inputKeyEvent(self,event=None):
        if not self.rawKey:
            self.rawKey='luxshare'
        if self.keyStr.get() == self.rawKey:
            self.logger.info('key match')
            self.endCommand(1)
            self.master.grab_set()
            self.destroy()
        else:
            self.logger.warn('key not match')
            self.keyEntry['bg'] = 'red'
            self.keyStr.set('')






