# coding:UTF-8
import tkinter as tk
from tkinter import *
from tkinter import ttk
import time
from datetime import datetime
from tkinter import messagebox
from tkinter import scrolledtext
import threading
from .RWjson import *

class StationConfigUI(tk.Toplevel):
     def __init__(self,master,logger,sendMsg):
         super(StationConfigUI,self).__init__()
         self.logger = logger
         self.master = master
         self.endCommand = sendMsg
         self.StationNum = StringVar()
         self.LineName = StringVar()
         self.SWName = StringVar()
         self.SWVersion = StringVar()
         self.setup()
         self.rootCfg = ''
         self.readCfg()

     def setup(self):
         self.logger.debug("this is setup...")
         self.transient(self.master)
         body = Frame(self, bg="#E6E6FA")
         self.initial_focus = self.loadUI(body)
         body.pack(padx=0, pady=0, fill='both')

         # 创建线程，如果函数里面有参数，args=()
         self.logger.info('StationConfigUI loadUI done')
         # 注册关闭窗口回调
         self.protocol("WM_DELETE_WINDOW", self.callback)

         self.grab_set()
         if not self.initial_focus:
             self.initial_focus = self
         # 前两个参数是窗口的大小，后两个参数是窗口的位置
         self.geometry("600x270+%d+%d" % (self.master.winfo_rootx() + 100,
                                          self.master.winfo_rooty() + 100))
         self.logger.info(
             'Password geometry is x:' + str(self.master.winfo_rootx()) + ' y:' + str(self.master.winfo_rooty()))
         # self.focus_set()
         # 宽不可变, 高不可变, 默认为True, 表明都可变化
         self.resizable(width=False, height=False)

     def loadUI(self,parent):
         self.logger.debug("this is setup...")
         spaceLable0 = Label(parent,
                             fg='black',
                             width=16,
                             font="Arial 12",
                             bg=parent['bg'])
         spaceLable0.grid(row=0)

         self.StationInfoLabel = Label(parent,
                                      text='Station Info',
                                      fg='black',
                                      width=16,
                                      font="Arial 16",
                                      bg=parent['bg'])
         # 使用place()设置该Label的大小和位置
         self.StationInfoLabel.grid(row=3, columnspan = '2')
         # 创建Label，设置背景色和前景色
         self.StationNumLabel = Label(parent,
                                      text='Station Number:',
                                      fg='black',
                                      width=16,
                                      font="Arial 12",
                                      bg=parent['bg'])
         # 使用place()设置该Label的大小和位置
         self.StationNumLabel.grid(row = 4)
         self.StationNumEntry = Entry(parent,
                              textvariable=self.LineName,
                              width=12,
                              bg=parent['bg'],
                              state='normal',
                              fg='black')
         self.StationNumEntry.grid(row = 4, column = 1)

         # 创建Label，设置背景色和前景色
         self.LineNameLabel = Label(parent,
                               text='Line Name:',
                               fg='black',
                               width=16,
                               font="Arial 12",
                               bg=parent['bg'])
         # 使用place()设置该Label的大小和位置
         self.LineNameLabel.grid(row = 5)
         self.LineNameEntry = Entry(parent,
                              textvariable=self.StationNum,
                              width=12,
                              bg=parent['bg'],
                              state='normal',
                              fg='black',)
         self.LineNameEntry.grid(row = 5, column = 1)

         spaceLable6 = Label(parent,
                            fg='black',
                            width=16,
                            font="Arial 12",
                            bg=parent['bg'])
         spaceLable6.grid(row=6)

         self.SWInfoLabel = Label(parent,
                                       text='Software Info',
                                       fg='black',
                                       width=16,
                                       font="Arial 16",
                                       bg=parent['bg'])
         # 使用place()设置该Label的大小和位置
         self.SWInfoLabel.grid(row=7, columnspan='2')
         # 创建Label，设置背景色和前景色
         self.SWNameLabel = Label(parent,
                                  text='Software Name:',
                                  fg='black',
                                  width=16,
                                  font="Arial 12",
                                  bg=parent['bg'])
         # 使用place()设置该Label的大小和位置
         self.SWNameLabel.grid(row = 8, column=0)
         self.SWNameEntry = Entry(parent,
                                    textvariable=self.SWName,
                                    width=20,
                                    bg=parent['bg'],
                                    state='normal',
                                    fg='black', )
         self.SWNameEntry.grid(row = 8, column=1)

         # 创建Label，设置背景色和前景色
         self.SWVersionLabel = Label(parent,
                                  text='Software Version:',
                                  fg='black',
                                  width=16,
                                  font="Arial 12",
                                  bg=parent['bg'])
         # 使用place()设置该Label的大小和位置
         self.SWVersionLabel.grid(row=9, column=0)
         self.SWVersionEntry = Entry(parent,
                                  textvariable=self.SWVersion,
                                  width=20,
                                  bg=parent['bg'],
                                  state='normal',
                                  fg='black', )
         self.SWVersionEntry.grid(row=9, column=1)

         spaceLable10 = Label(parent,
                             fg='black',
                             width=16,
                             font="Arial 12",
                             bg=parent['bg'])
         spaceLable10.grid(row=10)

         self.ok_btn = Button(parent,
                              text='OK',
                              command=self.clickOkBtn,
                              width=8)
         self.ok_btn.grid(row=11, columnspan = '2')

         spaceLable12 = Label(parent,
                              fg='black',
                              width=16,
                              font="Arial 12",
                              bg=parent['bg'])
         spaceLable12.grid(row=12)

         self.title("Station Config")

     def clickOkBtn(self):
         self.logger.debug("manual click Ok Button ...")
         print(self.rootCfg)
         self.saveCfg("StationID", self.StationNum.get())
         self.saveCfg("LineName", self.LineName.get())
         self.saveCfg("SoftwareName", self.SWName.get())
         self.saveCfg("Version",  self.SWVersion.get())
         print(self.rootCfg)
         result = self.rwJson.saveJson(self.rootCfg)
         if result:
             self.logger.debug('save json config successful')
             self.endCommand(1)
         else:
             self.logger.debug('save json config failure')
             messagebox.showinfo("Error","save json config failure")
             self.endCommand(0)
         self.master.grab_set()
         self.destroy()

     def readCfg(self):
         self.rwJson = RWjson('StationCfg.json')
         result, self.rootCfg = self.rwJson.loadJson()
         self.logger.debug(self.rootCfg)
         self.StationNum.set(self.loadCfg(("StationID")))
         self.LineName.set(self.loadCfg(("LineName")))
         self.SWName.set(self.loadCfg(("SoftwareName")))
         self.SWVersion.set(self.loadCfg(("Version")))

     def loadCfg(self, key_item):
         if key_item in (self.rootCfg):
             return self.rootCfg[key_item]
         else:
             return "Unkonw Value"

     def saveCfg(self,key_item,value_item):
         if key_item in (self.rootCfg):
             self.rootCfg[key_item] = value_item
         else:
             self.rootCfg.update(key_item=value_item)

     def callback(self):
         self.logger.warn("[warning]manual close password view...")
         # self.endCommand(0)
         self.master.grab_set()
         self.destroy()
