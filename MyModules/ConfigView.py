# coding:UTF-8
import tkinter as tk
from tkinter import *
from tkinter import ttk

from .SerialPort import *
from .Instruments import *
from .RWjson import *
import logging


class ConfigUI(tk.Toplevel):
    """docstring for TestUI"""

    def __init__(self,master,name,logger,sendMsg):
        super(ConfigUI, self).__init__()

        self.master = master
        self.name=name
        self.logger=logger
        self.sendMsg=sendMsg
        self.devices=None

    def showUI(self):
        self.transient(self.master)
        body = Frame(self)
        self.initial_focus = self.loadUI(body)
        # body.pack(padx=0, pady=0,fill='both')
        body.place(x=0,y=0,width=600,height=400)
        self.logger.info('ConfigUI loadUI done')
        # 注册关闭窗口回调
        self.protocol("WM_DELETE_WINDOW", self.callback)

        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self

        self.geometry("600x400+%d+%d" % (self.master.winfo_rootx() + 100,
                                         self.master.winfo_rooty() + 100))

        self.resizable(width=False, height=False)  # 宽不可变, 高可变,默认为True
        # self.focus_set()
        # self.wait_window(self)
    # 载入控件

    def loadUI(self,parent):
        print(self.devices)
        i=0
        for key in self.devices:
            self.devices[key].setup(parent,10,10 + 70 *i)
            i += 1
        self.title("%s Config View" %self.name)

    # 窗体手动关闭时回调事件
    def callback(self):
        # messagebox.showwarning(title="警告",message='关闭提示窗口!')
        self.logger.debug("[info]manual close config view...")
        self.sendMsg(-1)
        self.master.grab_set()
        self.destroy()

        # self.saveCfg()


class ConfigPanel(object):
    """docstring for ConfigView"""

    def __init__(self, master,devKey,sendMsg):
        super(ConfigPanel, self).__init__()
        self.master = master
        self.devKey=devKey
        self.logger=logging.getLogger('%s.cfg' %self.devKey)
        self.sendMsg=sendMsg
        self.errCount=0
        self.devices={}
        self.setup()

    def setup(self):
        self.logger.debug('this is setup func...')
        self.readCfg()
        print(self.devCfg)
        for dev in self.devCfg:
            cfg=self.devCfg[dev]
            devType=cfg['type']
            load=cfg['load']
            if not load:
                self.logger.warn('unload device:%s' %cfg['name'])
                continue
            # test serial port
            if devType == 'serial':
                print(str(cfg))
                serialDev=SerialDevice(dev,cfg,self.logger,self.saveEvent)

                self.devices[cfg['name']]=serialDev
                serialDev.bg='gray'
                if not serialDev.autoOpen():
                    self.errCount+=1
            elif devType == 'nivisa':
                instr=NivisaDev(dev,cfg,self.logger,self.saveEvent)
                self.devices[cfg['name']]=instr
                instr.bg='yellow'
                if not instr.autoOpen():
                    self.errCount+=1

    def loadUI(self):
        self.logger.debug('this is loadUI func...')
        self.cfgUI=ConfigUI(self.master,self.devKey,self.logger,self.receivedMsgFromCfgUI)
        self.cfgUI.devices=self.devices
        # self.readCfg()
        self.cfgUI.showUI()

    def readCfg(self):
        self.rwJson=RWjson('DevicesCfg.json')
        result,self.rootCfg=self.rwJson.loadJson()
        if result:
            self.logger.debug(self.rootCfg)
            self.devCfg=self.rootCfg[self.devKey]
        else:
            self.logger.error('load config json error')
            raise

    def saveCfg(self):
        result=self.rwJson.saveJson(self.rootCfg)
        if result:
            self.logger.debug('save json config successful')
        else:
            self.logger.error('save json config failure')
            raise
        self.errCount-=1
        self.sendMsg(self.errCount)

    def saveEvent(self,key,config):
        self.logger.debug("{}:{}".format(key,config))
        self.rootCfg[self.devKey][key]=config
        print('Slot Config View saveEvent:' +str(self.rootCfg))
        self.saveCfg()

    def receivedMsgFromCfgUI(self,msg):
        self.logger.debug('cfg ui msg:%s' %str(msg))
        self.sendMsg(msg)

    def closeDevices(self):
        for item in self.devices:
            if self.devices[item].opened:
                self.devices[item].close()


