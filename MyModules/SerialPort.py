# coding:UTF-8
import tkinter as tk
from tkinter import *
from tkinter import ttk
import time
from tkinter import messagebox
import threading
import os
import glob
import re
import platform
import sys

sys.path.append(sys.path[0] + '/MyModules')

import serial.tools.list_ports_linux
import serial.tools.list_ports
import serial


class SerialDevice(object):
    """docstring for SerialDevice"""

    def __init__(self, key, config, logger, saveEvent):
        super(SerialDevice, self).__init__()
        self.key = key
        self.logger = logger
        self.config = config
        self.title = 'Serial device of %s' % self.config['name']
        self.bg = 'yellow'
        self.serialName = config['port']
        self.baudRate = config['baud']
        self.opened = False
        self.serial = None

        self.saveEvent = saveEvent

        self.openBtnTitle = StringVar()
        self.openBtnTitle.set('Open')

        # self.setup()

    def setup(self, master, x, y):
        self.master = master
        self.x = x
        self.y = y

        frame1 = tk.Frame(self.master, bg=self.bg, relief=tk.SOLID,)
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
        self.cb.place(x=46, y=30, width=180, height=20)
        # 为Combobox配置多个选项
        self.cb['values'] = []
        # self.cb.current(0)
        self.cb.bind("<<ComboboxSelected>>", self.selectFunc)

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
            self.cb['values'] = [self.serialName]
            self.cb.current(0)
            self.cb['state'] = 'disabled'

            self.scan_btn['state'] = 'disabled'
            self.openBtnTitle.set('Close')

    def choose(self):
        self.logger.debug('this is click combobox event')
        # 获取Combbox的当前值
        # messagebox.showinfo(title=None, message=str(self.cb.get()))

    def selectFunc(self, event):
        self.serialName = str(self.cb.get())
        self.logger.info('selected value:' + self.serialName)

    def openEvent(self):
        self.logger.debug('this is open/close event')
        if self.open_btn['text'] == 'Open':
            self.logger.info('will open serial...')
            try:
                self.serial = serial.Serial(self.serialName, self.baudRate, timeout=0.1)
                if self.serial.isOpen():
                    self.opened = True
            except Exception as e:
                self.opened = False
                self.logger.error(e)
                messagebox.showerror(title='Error', message='Open serial error!')
                self.master.grab_set()
            if not self.opened:
                return

            self.config['port'] = self.serialName
            self.config['baud'] = self.baudRate

            self.saveEvent(self.key, self.config)

            self.cb['state'] = 'disabled'
            self.scan_btn['state'] = 'disabled'
            self.openBtnTitle.set('Close')
            messagebox.showinfo(title='Info', message='Open serial successful!')
            self.master.grab_set()
            self.logger.info('open serial successful')
        else:
            self.logger.debug('will close serial...')
            if self.serial.isOpen():
                self.serial.close()
            self.opened = False
            self.cb['state'] = 'normal'
            self.cb['values'] = ['']
            port_list = self.scanSerilPort()
            if len(port_list) != 0:
                self.cb['values'] = port_list
            self.cb.current(0)
            self.serialName = self.cb.get()
            self.scan_btn['state'] = 'normal'
            self.openBtnTitle.set('Open')

    def scanEvent(self):
        self.logger.debug('this is scan event')
        port_list = self.scanSerilPort()
        self.cb['values'] = ['']
        if len(port_list) == 0:
            messagebox.showwarning(title='Warning', message='Not any serial device plugin')
            self.master.grab_set()
        else:
            self.cb['values'] = port_list
            self.cb.current(0)

    def scanSerilPort(self):
        port_list = []
        # window or Mac OS
        if platform.system() == "Windows" or platform.system() == "Darwin":
            ports_comports = serial.tools.list_ports.comports()
            for i in range(0, len(ports_comports)):
                temp_list = list(ports_comports[i])
                # print(temp_list)
                port_list.append(temp_list[0])
            self.logger.debug(port_list)
            return port_list
        elif platform.system() == "Linux":
            return self.find_usb_tty()
        else:
            self.logger.error('not match platform:%s' % str(platform.system()))
            return []

    def find_usb_tty(self, vendor_id=None, product_id=None):
        '''
        查找Linux下的串口设备
        '''
        tty_list = []
        try:
            ports_comports = serial.tools.list_ports_linux.comports()
            for i in range(0, len(ports_comports)):
                temp_list = list(ports_comports[i])
                # print(temp_list)
                tty_list.append(temp_list[0])
            # print(tty_list)
        except Exception as e:
            self.logger.error(e)

        return tty_list

    def writeFunc(self, cmd):
        self.logger.debug('this is writeFunc')
        self.logger.info('[TX]%s' % cmd)

        if not self.serial.isOpen():
            return False
        try:
            self.serial.write(cmd.encode('utf-8'))
            return True
        except Exception as e:
            self.logger.error(str(e))
        return False

    def readFunc(self, timeout=2.0):
        self.logger.debug('this is readFunc')
        time.sleep(0.1)
        Response = ''
        startTime = time.time()

        if self.serial.inWaiting == 0:
            self.logger.error("\nError: Record start command failed.")
            return ''
            # sys.exit()
        while ((time.time() - startTime) < timeout):
            time.sleep(0.05)
            tempStr = self.serial.read(24)            # 24 chosen arbitrarily
            Response += tempStr.decode('utf-8')
            if Response.find('\n') != -1:
                self.logger.info('[RX]' + Response)
                return Response
        self.logger.info('[RX]' + Response)
        self.logger.warn("Time out receving correct string")
        return Response

    def query(self, cmd, timeout=2.0):
        if self.writeFunc(cmd):
            resp = self.readFunc(timeout)
            return True, resp
        else:
            return False, ''

    def autoOpen(self):
        self.logger.debug("this is auto open func")
        port_list = self.scanSerilPort()
        if self.serialName in port_list:
            try:
                self.serial = serial.Serial(self.serialName, self.baudRate, timeout=0.1)
                if self.serial.isOpen():
                    self.opened = True
            except Exception as e:
                self.opened = False
                self.logger.error(str(e))
                raise

        return self.opened

    def close(self):
        self.serial.flushInput()
        self.serial.flushOutput()
        self.serial.close()
        self.opened = False
