import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk
from tkinter import scrolledtext 
import tkinter.font as tk_font
import time
import threading
import queue


SKIP_NEXT_PAGE_INDEX=15


class TreeListBox:

    def __init__(self, master):
        self.master = master

        self.level = 0
        self.setup_widget_tree()
        # self.build_tree(self.root, '')
        self.ids_arr = []

    def setup_widget_tree(self):
        container_tree = tk.Frame(self.master, width=500, height=320)
        container_tree.propagate(False)
        container_tree.pack(side="top",fill='x')
        self.tree = ttk.Treeview(container_tree, show="tree", selectmode='browse')
        fr_y = tk.Frame(container_tree)
        fr_y.pack(side='right', fill='y')
        tk.Label(fr_y, borderwidth=1, relief='raised', font="Arial 8").pack(side='bottom', fill='x')
        sb_y = tk.Scrollbar(fr_y, orient="vertical", command=self.tree.yview)
        sb_y.pack(expand='yes', fill='y')
        fr_x = tk.Frame(container_tree)
        fr_x.pack(side='bottom', fill='x')
        sb_x = tk.Scrollbar(fr_x, orient="horizontal", command=self.tree.xview)
        sb_x.pack(expand='yes', fill='x')
        self.tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        self.tree.pack(fill='both', expand='yes')

    def build_tree(self, parent, id_stroki):
        self.level += 1
        id = self.tree.insert(id_stroki, 'end', text=parent)
        # -----------------
        col_w = tk_font.Font().measure(parent)
        if col_w > 1000:
            col_w -= 400
        elif col_w > 500:
            col_w -= 200
        elif col_w > 300:
            col_w -= 100
        col_w = col_w + 25 * self.level
        if col_w > self.tree.column('#0', 'width'):
            self.tree.column('#0', width=col_w)
        # -----------------
        for element in sorted(self.dict_group[parent]):
            self.build_tree(element, id)
        self.level -= 1

    def append_tree(self,parent,dict_group):
        self.dict_group = dict_group
        self.build_tree(parent,'')

    def brush_treeview(self, tv):
        # 改变treeview样式
        if not isinstance(tv, ttk.Treeview):
            raise Exception("argument tv of method bursh_treeview must be instance of ttk.TreeView")
        #=============给bom_lines设置样式=====
        items = tv.get_children()
        for i in range(len(items)):
            if i % 2 == 1:
                tv.item(items[i], tags=('oddrow'))
        tv.tag_configure('oddrow', background='#eeeeff')
        # tv.tag_configure('oddrow', background='#7FFFD4')

    def load_items(self,items_arr):
        id_stroki = ''
        self.level = 0
        self.ids_arr = []
        child_arr = self.tree.get_children()
        if len(child_arr) > 1:
            for item in child_arr:
                self.tree.delete(item)

        for i in range(0,len(items_arr)):

            parent = '-{}-{}'.format(str(i),items_arr[i])
            id_item = self.tree.insert(id_stroki, 'end', text=parent)
            self.ids_arr.append(id_item)

            # -----------------
            col_w = tk_font.Font().measure(parent)
            if col_w > 1000:
                col_w -= 400
            elif col_w > 500:
                col_w -= 200
            elif col_w > 300:
                col_w -= 100
            col_w = col_w + 25 * self.level
            if col_w > self.tree.column('#0', 'width'):
                self.tree.column('#0', width=col_w)

        # # -----------------
        # for element in sorted(self.dict_group[parent]):
        #     self.build_tree(element, id)
        # self.level -= 1
        self.brush_treeview(self.tree)
        self.tree.yview_moveto(0)

    def add_result_2item(self,index,info):

        id_stroki = self.ids_arr[index]
        parent = info
        self.level = 1
        id_item = self.tree.insert(id_stroki, 'end', text=parent)
        self.ids_arr.append(id_item)

        # -----------------
        col_w = tk_font.Font().measure(parent)
        col_w = col_w + 100 * self.level
        # print("col_w:" + str(col_w))
        col_w_0 = self.tree.column('#0', 'width')
        # print("col_w_0:" + str(col_w_0))
        if col_w > col_w_0:
            self.tree.column('#0', width=col_w)

    def change_row_color(self,index,col_v,scr=False):
        if not isinstance(self.tree, ttk.Treeview):
            raise Exception("argument tv of method bursh_treeview must be instance of ttk.TreeView")

        #=============给bom_lines设置样式=====
        items = self.tree.get_children()
        if index >= len(items):
            raise Exception("index number bigger list rows count")
        tag = 'row%s' % str(index)
        self.tree.item(items[index],tags=(tag))
        self.tree.tag_configure(tag, background=col_v)
        # self.tree.item(items[index])
        if scr and index > SKIP_NEXT_PAGE_INDEX -1 and \
                index % SKIP_NEXT_PAGE_INDEX == 0:
            self.tree.yview_moveto(index / len(items))
            # self.tree.update()
        # self.tree.item(items[index]).update()
        # self.tree.item(items[index],tags=(''))


class TextView(object):
    """docstring for TextView"""

    def __init__(self,master):
        super(TextView, self).__init__()
        self.master = master
        self.scrText = None

    def initUI(self):
        # 滚动文本框
        # scrolW = 70  # 设置文本框的长度
        scrolH = 10  # 设置文本框的高度
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


class DetialView(tk.Toplevel):
    """docstring for TestUI"""

    def __init__(self,config):
        super(DetialView, self).__init__()
        self.listView = None
        self.textView = None
        self.load_isOK = False
        self.items = config['items']
        self.index=config['index']
        self.notify_queue = config['queue']
        self.master = config['master']
        self.endCommand = config['closeEvent']
        self.refreshRow = None

        self.isShowView=False
        self.updateUIFlag=False
        self.updateIsBusy=False
        self.statusArr=[]
        self.infoArr=[]
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
        self.myPrint("detial view will close...")
        self.isShowView=False
        self.endCommand(0)
        self.withdraw()
        # self.destroy()

    def loadUI(self,parent):
        # self.win = tk.Toplevel()
        self.listView=TreeListBox(parent)
        # self.items = []
        # for i in range(0,30):
        #     self.items.append('item_%s' % str(i))
        self.listView.load_items(self.items)
        self.load_isOK=True
        self.textView=TextView(parent)
        self.textView.initUI()
        self.title("Slot-%d" %self.index)

    def initLoadData(self):
        self.refreshRow=0
        self.listView.load_items(self.items)
        for i in range(0,len(self.statusArr)):
            if i < len(self.infoArr):
                self.listView.add_result_2item(self.refreshRow,self.infoArr[i])
            self.refreshStatus(self.statusArr[i])
        self.textView.add_log_arr(self.logArr)

    def refreshStatus(self,status):
        if self.refreshRow > len(self.items) - 1:
            return
        if status == "testing":
            self.listView.change_row_color(self.refreshRow,'#FFFF00',True)
        elif status == "pass":
            self.listView.change_row_color(self.refreshRow,'#7CFC00')
            self.refreshRow += 1
        elif status == "fail":
            self.listView.change_row_color(self.refreshRow,'red')
            self.refreshRow += 1
        elif status == "skip":
            self.listView.change_row_color(self.refreshRow,'gray')
            self.refreshRow += 1

    def resetUI(self):

        if self.updateUIFlag:
            self.refreshRow=0
            self.listView.load_items(self.items)
            self.textView.clearAll()
        self.statusArr=[]
        self.infoArr=[]
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
                # 0,status
                if msg[0] == 0:
                    #'pass'/'fail'/'skip'
                    if msg[1].find('testing') == -1:
                        self.statusArr.append(msg[1])
                    if self.updateUIFlag:
                        self.refreshStatus(msg[1])

                # 1,test infomation
                elif msg[0] == 1:
                    self.infoArr.append(msg[1])
                    if self.updateUIFlag:
                        if self.refreshRow < len(self.items):
                            self.listView.add_result_2item(self.refreshRow,msg[1])
                # 2,log
                elif msg[0] == 2:
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
        print('[DetialView-{}]{}'.format(self.index,msg))

    #--------------just for test self--------------
    def testFunc(self):
        count=0
        while not self.load_isOK:
            print("wait load...")
            time.sleep(0.1)
            count += 0.1
            if count > 5:
                print("load timeout")
                return
        print('testing...')
        time.sleep(1.0)
        items=self.listView.tree.get_children()
        for i in range(len(items)):
            self.listView.change_row_color(i,'#FFFF00',scr=True)
            self.textView.add_log("testing...%s\n" % str(i))
            time.sleep(0.1)
            self.listView.add_result_2item(i,'result:pass value:10 up:20 low:5 unit:ohm duration:0.01s')
            self.textView.add_log('result:pass value:10 up:20 low:5 unit:ohm duration:0.01s\n')
            self.listView.change_row_color(i,'#7CFC00')

        print('change row done')

        time.sleep(2.0)

        # self.listView.load_items(self.items)
        # print('testing2...')
        # items = self.listView.tree.get_children()
        # for i in range(len(items)):
        #     self.listView.change_row_color(i,'#FFFF00',scr=True)
        #     time.sleep(0.1)
        #     self.listView.add_result_2item(i,'result:pass value:10 up:20 low:5 unit:ohm duration:0.01s')
        #     self.textView.add_log('result:pass value:10 up:20 low:5 unit:ohm duration:0.01s\n')
        #     self.listView.change_row_color(i,'#7CFC00')



