# coding:UTF-8
import tkinter as tk
from tkinter import *
from tkinter import ttk
import time
from datetime import datetime
from tkinter import messagebox
import threading
import queue


class GressBar():

    def start(self):
        top = Toplevel()
        self.master = top
        # top.overrideredirect(True)
        top.title("进度条")
        Label(top, text="任务正在运行中,请稍等……", fg="green").pack(pady=2)
        #prog = ttk.Progressbar(top, mode='indeterminate', length=200)
        prog = ttk.Progressbar(top, length=200)
        prog.pack(pady=10, padx=35)
        prog.start()

        top.resizable(False, False)

        curWidth = top.winfo_width()
        curHeight = top.winfo_height()
        scnWidth, scnHeight = top.maxsize()
        tmpcnf = '+%d+%d' % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        top.geometry(tmpcnf)
        top.update()
        # top.mainloop()

    def quit(self):
        if self.master:
            self.master.destroy()


class AppUI():

    def __init__(self):
        # 创建一个消息队列
        self.notify_queue = queue.Queue()
        root = Tk()
        self.master = root
        self.create_menu(root)
        self.create_content(root)
        root.title("磁盘文件搜索工具")

        # ………省略………
        self.search_key = "key"
        # 创建一个进度条对话框实例
        self.gress_bar = GressBar()
        # 在UI线程启动消息队列循环
        self.process_msg()

        root.mainloop()

    def create_menu(self, root):
        # 创建菜单栏
        menu = Menu(root)
        file_menu = Menu(menu, tearoff=0)
        # 创建二级菜单
        file_menu.add_command(label="设置路径", command=self.open_dir)
        file_menu.add_separator()
        file_menu.add_command(label="扫描", command=self.execute_asyn)
        about_menu = Menu(menu, tearoff=0)
        about_menu.add_command(label="version:1.0")
        # 在菜单栏中添加菜单
        menu.add_cascade(label="文件", menu=file_menu)
        menu.add_cascade(label="关于", menu=about_menu)
        root['menu'] = menu

    def create_content(self, root):
        lf = ttk.LabelFrame(root, text="文件搜索")
        lf.pack(fill=X, padx=15, pady=8)
        top_frame = Frame(lf)
        top_frame.pack(fill=X, expand=YES, side=TOP, padx=15, pady=8)
        self.search_key = StringVar()
        ttk.Entry(top_frame, textvariable=self.search_key, width=50).pack(fill=X, expand=YES, side=LEFT)
        ttk.Button(top_frame, text="搜索", command=self.search_file).pack(padx=15, fill=X, expand=YES)
        bottom_frame = Frame(lf)
        bottom_frame.pack(fill=BOTH, expand=YES, side=TOP, padx=15, pady=8)
        band = Frame(bottom_frame)
        band.pack(fill=BOTH, expand=YES, side=TOP)
        self.list_val = StringVar()
        listbox = Listbox(band, listvariable=self.list_val, height=18)
        listbox.pack(side=LEFT, fill=X, expand=YES)
        vertical_bar = ttk.Scrollbar(band, orient=VERTICAL, command=listbox.yview)
        vertical_bar.pack(side=RIGHT, fill=Y)
        listbox['yscrollcommand'] = vertical_bar.set
        horizontal_bar = ttk.Scrollbar(bottom_frame, orient=HORIZONTAL, command=listbox.xview)
        horizontal_bar.pack(side=BOTTOM, fill=X)
        listbox['xscrollcommand'] = horizontal_bar.set
        # 给list动态设置数据，set方法传入一个元组，注意此处是设置，
        # 不是插入数据，此方法调用后，list之前的数据会被清除
        self.list_val.set(('jioj', 124, "fjoweghpw", 1, 2, 3, 4, 5, 6))

    def open_dir(self):
        print('this is open_dir...')

    def search_file(self):
        print('this is search_file...')

    def process_msg(self):
        self.master.after(400, self.process_msg)
        print('check queue...')
        while not self.notify_queue.empty():
            try:
                msg = self.notify_queue.get()
                if msg[0] == 1:
                    self.gress_bar.quit()
            except queue.Empty:
                pass

    def execute_asyn(self):
        # 定义一个scan函数，放入线程中去执行耗时扫描
        def scan(_queue):
            time.sleep(2)  # 让线程睡眠2秒
            _queue.put((1,))

        th = threading.Thread(target=scan, args=(self.notify_queue,))
        th.setDaemon(True)
        th.start()
        # 启动进度条
        self.gress_bar.start()


app = AppUI()
