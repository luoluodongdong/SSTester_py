import tkinter as tk
from  tkinter import *
from tkinter import ttk
from tkinter import scrolledtext        # 导入滚动文本框的模块

class CommunicationViewUI(tk.Toplevel):
    def __init__(self,master,key,logger,sendMsg):
        super(CommunicationViewUI, self).__init__()
        self.master = master
        self.key = key
        self.logger = logger
        self.sendMsg = sendMsg
        self.list_cmd = []

    def showUI(self):
        self.logger.debug("this is setup...")
        self.transient(self.master)
        body = Frame(self, bg=self.master.bg)
        self.initial_focus = self.loadUI(body)
        body.place(x = 0,y = 0, width = 400, height = 400)
        self.logger.info('ConfigUI loadUI done')
        # 注册关闭窗口回调
        self.protocol("WM_DELETE_WINDOW", self.callback)

        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self

        self.geometry("400x400+%d+%d" % (self.master.winfo_rootx() + 100,
                                         self.master.winfo_rooty() + 100))

        self.resizable(width=False, height=False)  # 宽不可变, 高可变,默认为True
        self.cb.focus()

    def loadUI(self,parent):
        self.DevCommunicationLog =  Label(parent,
                                          text = "Dev Communication Log:",
                                          fg='black',
                                          width=20,
                                          font="Arial 12",
                                          bg=parent['bg'],
                                          anchor="w")
        self.DevCommunicationLog.place(x=10,y=5)

        # 滚动文本框
        self.logText = scrolledtext.ScrolledText(parent,
                                                 width=380,
                                                 height=40,
                                                 wrap=tk.WORD)  # wrap=tk.WORD   这个值表示在行的末尾如果有一个单词跨行，会将该单词放到下一行显示,比如输入hello，he在第一行的行尾,llo在第二行的行首, 这时如果wrap=tk.WORD，则表示会将 hello 这个单词挪到下一行行首显示, wrap默认的值为tk.CHAR
        self.logText.place(x=10,y=28,width=380,height=320)

        # 创建Combobox组件
        self.cb = ttk.Combobox(parent,
                               postcommand=self.choose)  # 当用户单击下拉箭头时触发self.choose方法
        self.cb.place(x=10, y=360, width=180, height=20)
        # 为Combobox配置多个选项
        self.cb['values'] = ['']
        self.cb.bind("<<ComboboxSelected>>", self.selectFunc)

        # 新建一个按钮
        self.send_btn = Button(parent,
                               text='Send',
                               command=self.sendEvent)  # 背景色:蓝色
        self.send_btn.place(x=200, y=360, width=40, height=20)

        self.title(self.key + " Communication View")

    def choose(self):
        self.logger.debug('this is click combobox event')

    def selectFunc(self, event):
        self.logger.info('selected value:' + str(self.cb.get()))

    def sendEvent(self):
        self.logger.debug('this is click sendEvent '+ str(self.cb.get()))
        if not (str(self.cb.get()) in self.list_cmd):
            self.list_cmd.append(str(self.cb.get()))
        self.cb['values'] = self.list_cmd
        self.sendMsg(str(self.cb.get())+"\n")

    # 窗体手动关闭时回调事件
    def callback(self):
        self.logger.debug("[info]manual close config view...")
        # self.sendMsg(-1)
        self.master.grab_set()
        self.destroy()


