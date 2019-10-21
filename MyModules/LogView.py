import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk
from tkinter import scrolledtext 
import tkinter.font as tk_font
import time
import threading
import queue


SKIP_NEXT_PAGE_INDEX=15


class TextView(object):
    """docstring for TextView"""

    def __init__(self,master):
        super(TextView, self).__init__()
        self.master = master
        self.scrText = None

    def initUI(self):
        # 滚动文本框
        # scrolW = 70  # 设置文本框的长度
        scrolH = 30  # 设置文本框的高度
        # wrap=tk.WORD   这个值表示在行的末尾如果有一个单词跨行，会将该单词放到下一行显示,
        # 比如输入hello，he在第一行的行尾,llo在第二行的行首, 这时如果wrap=tk.WORD，则表示会
        # 将 hello 这个单词挪到下一行行首显示, wrap默认的值为tk.CHAR
        self.scrText = scrolledtext.ScrolledText(self.master, height=scrolH, wrap=tk.WORD)  
        # self.scrText = scrolledtext.ScrolledText(self.master, wrap=tk.WORD) 
        # columnspan 个人理解是将3列合并成一列   也可以通过 sticky=tk.W  来控制该文本框的对齐方式   
        # scr.grid(column=0, row=1)   
        self.scrText.pack(side='left',fill='x',expand='yes')

    def add_log(self,msg):
        self.scrText.insert(tk.END, msg)
        self.scrText.see(tk.END)

    def add_log_arr(self,logArr):
        self.clearAll()
        str_data = ''.join([str(i) for i in logArr[::1]])
        self.scrText.insert(tk.END, str_data)
        self.scrText.see(tk.END)

    def clearAll(self):
        self.scrText.delete(1.0, tk.END)  # 使用 delete


class LogView(tk.Toplevel):
    """docstring for TestUI"""

    def __init__(self,config):
        super(LogView, self).__init__()
        self.textView = None
        self.load_isOK = False
        self.items = config['items']
        self.index=config['index']
        self.notify_queue = config['queue']
        self.master = config['master']
        self.endCommand = config['closeEvent']

        self.isShowView=False
        self.updateUIFlag=False
        self.updateIsBusy=False

        self.logArr=[]

        self.setup()

    def setup(self):
        self.transient(self.master)
        body = Frame(self)
        self.initial_focus = self.loadUI(body)
        body.pack(padx=0, pady=0,fill='both')

        # 创建线程，如果函数里面有参数，args=()
        self.myPrint('loadUI done')
        # 注册关闭窗口回调
        self.protocol("WM_DELETE_WINDOW", self.callback)

        if not self.initial_focus:
            self.initial_focus = self

        # self.geometry("+%d+%d" % (self.master.winfo_rootx() + 50,
        #                         self.master.winfo_rooty() + 50))
        # self.master.update()
        # self.grab_set()
        self.periodicCall()
        self.withdraw()

    def showUI(self):
        self.geometry("+%d+%d" % (self.master.winfo_rootx() + 50,
                                  self.master.winfo_rooty() + 50))
        self.isShowView=True
        self.initLoadData()
        self.deiconify()
        self.master.update()
        self.grab_set()

    def callback(self):
        # messagebox.showwarning(title="警告",message='关闭提示窗口!')
        self.myPrint("log view will close...")
        self.isShowView=False
        self.endCommand(0)
        self.withdraw()
        # self.destroy()

    def loadUI(self,parent):
        self.load_isOK=True
        self.textView=TextView(parent)
        self.textView.initUI()
        self.title("SSUI-LogView")

    def initLoadData(self):
        self.textView.add_log_arr(self.logArr)

    def resetUI(self):
        if self.updateUIFlag:
            self.textView.clearAll()

        self.logArr=[]

    # detialView窗口定时刷新进度
    def periodicCall(self):
        if not self.updateIsBusy:
            self.update_UI()
        self.master.after(200,self.periodicCall)
        # self.master.destroy()

    def update_UI(self):
        self.updateIsBusy=True
        if self.isShowView:
            self.updateUIFlag=True
        else:
            self.updateUIFlag=False
        # self.myPrint("update ui...")
        while not self.notify_queue.empty(): 

            try: 
                msg=self.notify_queue.get(0) 
                # self.myPrint(msg)
                # 2,log
                if msg[0] == 2:
                    self.logArr.append(msg[1])
                    if self.updateUIFlag:
                        self.textView.add_log(msg[1])
                # 3,reset UI
                elif msg[0] == 3:
                    self.resetUI()
                    self.myPrint('reset UI')
                    # if msg[0] == 1: 
                    # self.gress_bar.quit() 

            except queue.Empty: 
                self.myPrint("queue empty")
                pass
        self.updateIsBusy=False

    def myPrint(self,msg):
        print('[LogView-{}]{}'.format(self.index,msg))


