# -*- coding: utf-8 -*-

import wx
import os
import thread
import threading

import check_file_size

# http://d.hatena.ne.jp/Megumi221/20110308/1299571975

class MyThreadKanshi(threading.Thread):
    def __init__(self, window, filenames):
        threading.Thread.__init__(self)
        self.window = window
        self.filenames = filenames
        self.t_list = []

    def run(self):
        with self.window.status_update_lock:
            self.window.status.SetValue(u"処理中")
        for f in self.filenames:
            if os.path.isdir(f):
                root = f
            else:
                root = os.path.dirname(f)
            self.window.text.SetValue(root)
            main_arg = {
                    'root' : root,
                    'human_readble' : False,
                    'outbuf' : self.window.result_text,
                    }
            thread = threading.Thread(target=check_file_size.main, kwargs=(main_arg))
            self.t_list.append(thread)
            thread.start()
        for t in self.t_list:
            t.join()
        with self.window.status_update_lock:
            #self.window.status.SetValue(" ".join(map(str,threading.enumerate())))
            self.window.status.SetValue(u"未処理")
            self.window.drop_ctrl_event.clear()

class MyThread(threading.Thread):
    def __init__(self, window, **argk):
        threading.Thread.__init__(self)
        self.argk = argk
        self.window = window

    def run(self):
        with self.window.status_update_lock:
            self.window.status.SetValue(u"処理中")
        check_file_size.main(**self.argk)
        with self.window.status_update_lock:
            self.window.status.SetValue(" ".join(map(str,threading.enumerate())))

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.window.drop_ctrl_event = threading.Event()
        self.result_text_list = []

    def OnDropFiles(self, x, y, filenames):  #ファイルをドロップするときの処理
        if not self.window.drop_ctrl_event.is_set():
            self.window.drop_ctrl_event.set()
            th = MyThreadKanshi(self.window, filenames)
            th.start()
        """
        for file in filenames:
            self.window.text.SetValue(file)
            if os.path.isdir(file):
                root = file
            else:
                root = os.path.dirname(file)
            main_arg = {
                    'root' : root,
                    'human_readble' : False,
                    'outbuf' : self.window.result_text,
                    }
            #thread.start_new_thread(check_file_size.main, (root, 0, 0, False, self.window.result_text))
            #self.window.thread.run(**main_arg)
            thread = MyThread(self.window, **main_arg)
            thread.start()
            #check_file_size.main(root = root, outbuf=self.window.result_text)
        #"""

class MyFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, u"ファイルサイズチェッカ", size=(500,-1))

        root_pane = wx.Panel(self, wx.ID_ANY)

        layout = wx.BoxSizer(wx.VERTICAL)

        # 1段目
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(root_pane, -1, u"File name:")
        self.text = wx.TextCtrl(root_pane, -1, "", size=(400,-1))
        sizer.Add(label, 0, wx.ALL, 5)
        sizer.Add(self.text, 0, wx.ALL | wx.GROW, 5)

        # 2段目
        self.status = wx.TextCtrl(root_pane, -1, u"未処理")
        self.status_update_lock = threading.Lock()
        # 3段目
        self.result_text = wx.TextCtrl(root_pane, -1, "", style=wx.TE_MULTILINE)

        # 縦組み
        layout.Add(sizer, 0, wx.ALL, 5)
        layout.Add(self.status, 0, wx.ALL, 5)
        layout.Add(self.result_text, 1, wx.ALL | wx.GROW, 5)
        root_pane.SetSizer(layout)

        # ファイルドロップの設定
        dt = MyFileDropTarget(self)  #対象はこのフレーム全体
        self.SetDropTarget(dt)

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()
