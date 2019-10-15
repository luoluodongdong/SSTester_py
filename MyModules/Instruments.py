# coding:UTF-8
import tkinter as tk
from tkinter import *
from tkinter import ttk
import time
from tkinter import messagebox
#import threading

import sys
# get nivisa resources

sys.path.append(sys.path[0] +'/MyModules')
# print(sys.path[0])
import pyvisa as visa

# visa.log_to_screen()


class NivisaDev(object):
    """docstring for Nivisa Device"""

    def __init__(self,key,config,logger,saveEvent):
        super(NivisaDev, self).__init__()
        self.key = key
        self.logger=logger
        self.config=config
        self.title='Nivisa device of %s' %self.config['name']
        self.bg='yellow'
        self.portName=config['port']
        self.baudRate=config['baud']
        self.opened=False
        self.instr=None

        self.saveEvent=saveEvent

        self.openBtnTitle=StringVar()
        self.openBtnTitle.set('Open')
        self.rm=visa.ResourceManager()

        # self.rm.close()
        # self.setup()

    def setup(self,master,x,y):
        self.master=master
        self.x=x
        self.y=y

        frame1 = tk.Frame(self.master,bg=self.bg ,relief=tk.SOLID,)
        # frame1.pack(padx=10, pady=10)
        frame1.place(x=self.x, y=self.y, width=340, height=60)

        # 创建Label，设置背景色和前景色
        self.info_lb = Label(frame1,
                             text=self.title,
                             fg='Black',
                             font="Arial 14",
                             bg=self.bg)
        # 使用place()设置该Label的大小和位置
        self.info_lb.place(x=5, y=2, width=300, height=20)

        # 创建Label，设置背景色和前景色
        self.comLabel = Label(frame1,
                              text='COM:',
                              fg='Black',
                              font="Arial 12",
                              bg=self.bg)
        # 使用place()设置该Label的大小和位置
        self.comLabel.place(x=5, y=32, width=40, height=20)

        # 创建Combobox组件
        self.cb = ttk.Combobox(frame1,
                               state='readonly',
                               background='yellow',
                               postcommand=self.choose)  # 当用户单击下拉箭头时触发self.choose方法
        # self.cb.pack(side=TOP)
        self.cb.place(x=46,y=30,width=180,height=20)
        # 为Combobox配置多个选项
        self.cb['values'] = []
        # self.cb.current(0)
        self.cb.bind("<<ComboboxSelected>>",self.selectFunc)

        # 新建一个按钮
        self.open_btn = Button(frame1, 
                               textvariable=self.openBtnTitle,
                               bg=self.bg,
                               command=self.openEvent)  # 背景色:蓝色

        self.open_btn.place(x=240, y=30, width=40, height=20)

        # 新建一个按钮
        self.scan_btn = Button(frame1, 
                               text='Scan',
                               command=self.scanEvent)  # 背景色:蓝色

        self.scan_btn.place(x=290, y=30, width=40, height=20)

        if self.opened:
            self.cb['values']=[self.portName]
            self.cb.current(0)
            self.cb['state']='disabled'

            self.scan_btn['state']='disabled'
            self.openBtnTitle.set('Close')

    def choose(self):
        self.logger.debug('this is click combobox event')
        # 获取Combbox的当前值
        # messagebox.showinfo(title=None, message=str(self.cb.get()))

    def selectFunc(self,event):
        self.portName=str(self.cb.get())
        self.logger.info('selected value:' +self.portName)

    def openEvent(self):
        self.logger.debug('this is open/close event')
        if self.open_btn['text'] == 'Open':
            self.logger.info('will open nivisa dev...')
            try:
                self.opened=self.openInstr(self.portName,baud=self.baudRate,delay=0.1)
            except Exception as e:
                self.opened=False
                self.logger.error(e)
                messagebox.showerror(title='Error',message='Open nivisa device error!')
                self.master.grab_set()
            if not self.opened:
                return

            self.config['port'] = self.portName
            self.config['baud'] = self.baudRate
            self.saveEvent(self.key,self.config)

            self.cb['state']='disabled'
            self.scan_btn['state']='disabled'
            self.openBtnTitle.set('Close')
            messagebox.showinfo(title='Info',message='Open instr successful!')
            self.master.grab_set()
            self.logger.info('open instr successful')
        else:
            self.logger.debug('will close nivisa dev...')
            if self.opened:
                self.close()
            self.opened=False
            self.cb['state']='normal'
            self.cb['values']=['']
            port_list=self.getInstrList()
            if len(port_list) != 0:
                self.cb['values']=port_list
            self.cb.current(0)
            self.portName=self.cb.get()
            self.scan_btn['state']='normal'
            self.openBtnTitle.set('Open')

    def scanEvent(self):
        self.logger.debug('this is scan event')
        port_list=self.getInstrList()
        self.logger.debug(port_list)
        self.cb['values']=['']
        if len(port_list) ==0:
            messagebox.showwarning(title='Warning',message='Not any nivisa device plugin')
            self.master.grab_set()
        self.cb['values']=port_list
        self.cb.current(0)

    def autoOpen(self):
        self.logger.debug("this is auto open func")
        port_list=self.getInstrList()
        if self.portName in port_list:
            time.sleep(0.1)
            self.opened=self.openInstr(self.portName,delay=0.1)
        return self.opened

    def getInstrList(self):
        self.logger.debug('this is getInstrList func')
        port_list=[]
        port_list=self.rm.list_resources()
        self.logger.debug(port_list)
        return port_list

    def openInstr(self,port,baud=9600,timeout=2000,delay=3.0):
        self.instr=None
        if port.find('ASRL') != -1 or port.find('USB') != -1 \
                or port.find('GPIB') != -1 or port.find('TCPIP') != -1:
            try:

                self.instr=self.rm.open_resource(port,baud_rate=baud)
                self.instr.timeout=timeout
                time.sleep(delay)
            except Exception as e:
                self.logger.error(str(e))
                return False
            return True
        else:
            self.logger.error('port name error!')
            return False

    def close(self):
        self.instr.close()
        # self.rm.close()
        self.opened=False

    def query(self,cmd,timeout=2.0):
        self.logger.info('[TX]' +cmd)
        response=''
        opResult=True
        try:
            self.instr.timeout=timeout *1000
            response=self.instr.query(cmd)
        except Exception as e:
            self.logger.error(str(e))
            opResult=False
        self.logger.info('[RX]' +response)
        return opResult,response

    def writeInstr(self,cmd):
        self.logger.info('[TX]' +cmd)
        opResult=True
        try:
            self.instr.write(cmd)
        except Exception as e:
            self.logger.error(str(e))
            opResult=False
        return opResult

    def readInstr(self,timeout=2.0):
        response=''
        opResult=True
        try:
            self.instr.timeout=timeout *1000
            response=self.instr.read()
        except Exception as e:
            self.logger.error(str(e))
            opResult=False
        self.logger.info('[RX]' +response)
        return opResult,response

