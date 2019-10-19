from socket import *
import os
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import threading

BUFFERSIZE = 1024


class SocketDevice(object):

    def __init__(self,key,config,logger,saveEvent):
        super(SocketDevice,self).__init__()
        self.key = key
        self.config = config
        self.mode = self.config['mode']
        self.ip = self.config['ip']
        self.port = self.config['port']
        self.logger = logger
        self.saveEvent = saveEvent
        self.socket_client = None
        self.socket_server = None
        self.opened = False
        self.bg = 'green'
        self.title = 'Socket device of %s' % self.config['name']
        self.openBtnTitle = StringVar()
        self.openBtnTitle.set('Open')

        self.ipStr=StringVar()
        self.portStr=StringVar()

        self.ipStr.set(self.ip)
        self.portStr.set(str(self.port))

    def setup(self, master, x, y):
        self.master = master
        self.x = x
        self.y = y

        frame1 = tk.Frame(self.master, bg=self.bg, relief=tk.SOLID,)
        frame1.place(x=self.x, y=self.y, width=420, height=60)

        # 创建title Label，设置背景色和前景色
        self.info_lb = Label(frame1,
                             text=self.title,
                             fg='Black',
                             font="Arial 14",
                             bg=self.bg)
        # 使用place()设置该Label的大小和位置
        self.info_lb.place(x=5, y=2, width=300, height=20)

        # 创建Label，设置背景色和前景色
        self.ipLabel = Label(frame1,
                             text='Mode:',
                             fg='Black',
                             font="Arial 12",
                             bg=self.bg,
                             anchor='w')
        # 使用place()设置该Label的大小和位置
        self.ipLabel.place(x=5, y=32, width=35, height=20)

        # 创建Combobox组件
        self.cbMode = ttk.Combobox(frame1,
                                   state='readonly',
                                   background=self.bg,
                                   # postcommand=self.choose
                                   )  # 当用户单击下拉箭头时触发self.choose方法
        # self.cb.pack(side=TOP)
        self.cbMode.place(x=45, y=32, width=60, height=20)
        # 为Combobox配置多个选项
        self.cbMode['values'] = ['client','server']
        # self.cb.current(0)
        self.cbMode.bind("<<ComboboxSelected>>", self.selectModeFunc)

        # 创建Label，设置背景色和前景色
        self.ipLabel = Label(frame1,
                             text='IP:',
                             fg='Black',
                             font="Arial 12",
                             bg=self.bg,
                             anchor='w')
        # 使用place()设置该Label的大小和位置
        self.ipLabel.place(x=110, y=32, width=15, height=20)

        # 新建一个输入框
        self.ipEntry = Entry(frame1,
                             textvariable=self.ipStr,
                             width=17,
                             bg='white'
                             )

        self.ipEntry.place(x=130, y=32, width=120,height=20)

        # 创建Label，设置背景色和前景色
        self.portLabel = Label(frame1,
                               text='Port:',
                               fg='Black',
                               font="Arial 12",
                               bg=self.bg,
                               anchor='w')
        self.portLabel.place(x=255, y=32, width=30, height=20)

        # 新建一个输入框
        self.portEntry = Entry(frame1,
                               textvariable=self.portStr,
                               width=17,
                               bg='white'
                               )

        self.portEntry.place(x=290, y=32, width=60,height=20)

        # 新建一个按钮
        self.open_btn = Button(frame1,
                               textvariable=self.openBtnTitle,
                               bg=self.bg,
                               command=self.openEvent)  # 背景色:蓝色
        self.open_btn.place(x=365, y=32, width=40, height=20)

        if 'client' == self.mode:
            self.cbMode.current(0)
        else:
            self.cbMode.current(1)

        if self.opened:
            self.openBtnTitle.set('Close')
            self.cbMode['state']='disabled'
            self.ipEntry['state']='disabled'
            self.portEntry['state'] ='disabled'

    def selectModeFunc(self, event):
        self.mode = self.cbMode.get()
        self.logger.info('selected mode:' + self.mode)

    def openEvent(self):
        self.logger.debug('this is open/close event')
        if self.open_btn['text'] == 'Open':
            self.ip=self.ipStr.get()
            self.port=int(self.portStr.get())
            self.open()
            if self.opened:
                self.openBtnTitle.set('Close')
                self.cbMode['state']='disabled'
                self.ipEntry['state']='disabled'
                self.portEntry['state'] ='disabled'

                self.config['mode']=self.mode
                self.config['ip']=self.ip
                self.config['port']=self.port
                self.saveEvent(self.key,self.config)
        else:
            self.close()
            self.openBtnTitle.set('Open')
            self.cbMode['state']='normal'
            self.ipEntry['state']='normal'
            self.portEntry['state'] ='normal'

    def autoOpen(self):
        self.logger.debug("this is auto open func")
        return self.open()

    def open(self):
        self.opened = False
        ret = os.system("ping -c 1 -t 1 {0}".format(self.ip))
        print(ret)
        if ret == 0:
            try:
                if 'client' == self.mode:
                    self.socket_client = socket(AF_INET, SOCK_STREAM)  # Create TCP socket
                    self.socket_client.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 重用地址端口
                    self.socket_client.connect((self.ip, self.port))  # Connect to the server
                    self.opened = True
                    return True
                elif 'server' == self.mode:
                    self.socket_server = socket(AF_INET, SOCK_STREAM)  # Create TCP socket
                    self.socket_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 重用地址端口
                    self.socket_server.bind((self.ip, self.port))
                    self.socket_server.listen(1)  # 开始监听，1代表在允许有一个连接排队，更多的新连接连进来时就会被拒绝
                    self.opened = True
                    # 新开一个线程运行服务端
                    server_thread = threading.Thread(target=self.wait_client_connect)
                    server_thread.daemon = True
                    server_thread.start()
                    return True
                else:
                    self.logger.error('Unknown mode:%s ,please check cfg file!' %self.mode)
                    return False
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

    def wait_client_connect(self):
        print("waiting for client......")
        self.socket_client,client_addr=self.socket_server.accept()
        print("client ip:%s connect successful!" %str(client_addr))
        # just for testing server mode
        # Response = self.socket_client.recv(BUFFERSIZE).decode('utf-8')
        # self.logger.info('[Recieve data]' + Response)
        # self.socket_client.send(Response.encode('utf-8'))

    def close(self):
        if 'client' == self.mode:
            if self.socket_client == None:
                return
            self.socket_client.close()
        elif 'server' == self.mode:
            if self.socket_server == None:
                return
            self.socket_server.close()
            if self.socket_client == None:
                return
            self.socket_client.close()
        self.opened = False

    def writeFunc(self, cmd):
        self.logger.debug('this is writeFunc')
        self.logger.info('[Send data]%s' % cmd)

        if not self.opened:
            return False
        try:
            self.socket_client.send(cmd.encode('utf-8'))
            return True
        except Exception as e:
            self.logger.error(str(e))
        return False

    def readFunc(self, timeout=2.0):
        self.logger.debug('this is readFunc')
        time.sleep(0.1)
        Response = ''
        self.socket_client.settimeout(timeout)
        Response = self.socket_client.recv(BUFFERSIZE).decode('utf-8')
        self.logger.info('[Recieve data]' + Response)
        return Response

    def query(self, cmd, timeout=2.0):
        if self.writeFunc(cmd):
            resp = self.readFunc(timeout)
            return True, resp
        else:
            return False, ''


