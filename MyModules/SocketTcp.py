from socket import *
import os
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

BUFFERSIZE = 1024

class SocketTcpDevice(object):

    def __init__(self,key,config,logger,saveEvent):
        super(SocketTcpDevice,self).__init__()
        self.key = key
        self.config = config
        self.ip = self.config['ip']
        self.port = self.config['port']
        self.logger = logger
        self.saveEvent = saveEvent
        self.socket = None
        self.opened = False
        self.bg = 'green'
        self.title = 'Socket device of %s' % self.config['name']
        self.openBtnTitle = StringVar()
        self.openBtnTitle.set('Open')

    def setup(self, master, x, y):
        self.master = master
        self.x = x
        self.y = y

        frame1 = tk.Frame(self.master, bg=self.bg, relief=tk.SOLID,)
        frame1.place(x=self.x, y=self.y, width=390, height=60)

        # 创建title Label，设置背景色和前景色
        self.info_lb = Label(frame1,
                             text=self.title,
                             fg='Black',
                             font="Arial 14",
                             bg=self.bg)
        # 使用place()设置该Label的大小和位置
        self.info_lb.place(x=40, y=2, width=300, height=20)

        # 创建Label，设置背景色和前景色
        self.ipLabel = Label(frame1,
                              text='IP:  '+ self.ip,
                              fg='Black',
                              font="Arial 12",
                              bg=self.bg,
                              anchor = 'w')
        # 使用place()设置该Label的大小和位置
        self.ipLabel.place(x=5, y=32, width=120, height=20)

        # 创建Label，设置背景色和前景色
        self.portLabel = Label(frame1,
                             text='Port:  ' + self.port,
                             fg='Black',
                             font="Arial 12",
                             bg=self.bg,
                             anchor = 'w')
        self.portLabel.place(x=126, y=30, width=60, height=20)

        # 新建一个按钮
        self.open_btn = Button(frame1,
                               textvariable=self.openBtnTitle,
                               bg=self.bg,
                               command=self.openEvent)  # 背景色:蓝色
        self.open_btn.place(x=240, y=30, width=40, height=20)

        # 新建一个按钮
        self.more_btn = Button(frame1,
                               text='More+', )  # 背景色:蓝色
        self.more_btn.place(x=340, y=30, width=40, height=20)

        if self.opened:
            self.openBtnTitle.set('Close')
        else:
            self.more_btn['state'] = 'disabled'

    def openEvent(self):
        self.logger.debug('this is open/close event')
        if self.open_btn['text'] == 'Open':
            self.open()
            if self.opened:
                self.more_btn['state'] = 'normal'
        else:
            self.more_btn['state'] = 'disabled'

    def moreEvent(self):
        self.logger.debug('this is more event')

    def autoOpen(self):
        self.logger.debug("this is auto open func")
        return self.open()

    def open(self):
        ret = os.system("ping -c 1 -t 1 {0}".format(self.ip))
        print(ret)
        if ret == 0:
            try:
                self.socket = socket(AF_INET, SOCK_STREAM)  # Create TCP socket
                self.socket.connect((self.ip, int(self.port)))  # Connect to the server
                self.opened = True
                return True
            except Exception as e:
                self.opened = False
                self.logger.error(e)
                messagebox.showerror(title='Error', message='Open socket error!')
                self.master.grab_set()
                return False
        else:
            self.opened = False
            messagebox.showerror(title='Error', message='Can not ping to '+ self.ip)
            return False

    def close(self):
        self.socket.close()
        self.opened = False

    def writeFunc(self, cmd):
        self.logger.debug('this is writeFunc')
        self.logger.info('[Send data]%s' % cmd)

        if not self.opened():
            return False
        try:
            self.socket.send(cmd.encode('utf-8'))
            return True
        except Exception as e:
            self.logger.error(str(e))
        return False

    def readFunc(self, timeout = 2.0):
        self.logger.debug('this is readFunc')
        time.sleep(0.1)
        Response = ''
        startTime = time.time()

        while ((time.time() - startTime) < timeout):
            time.sleep(0.05)
            tempStr = self.socket.recv(BUFFERSIZE)
            Response += tempStr.decode('utf-8')
            if Response.find('\n') != -1:
                self.logger.info('[Recieve data]' + Response)
                return Response
        self.logger.info('[Recieve data]' + Response)
        self.logger.warn("Time out receving correct string")
        return Response

    def query(self, cmd, timeout=2.0):
        if self.writeFunc(cmd):
            resp = self.readFunc(timeout)
            return True, resp
        else:
            return False, ''


