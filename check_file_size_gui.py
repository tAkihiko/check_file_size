# -*- coding: utf-8 -*-

import wx
import os
import threading

import check_file_size

# http://d.hatena.ne.jp/Megumi221/20110308/1299571975

class MyThreadKanshi(threading.Thread):
    def __init__(self, window, filenames):
        threading.Thread.__init__(self)
        self.window = window
        self.filenames = filenames
        self.t_list = []

    def proc(self, root):
        size_dir, skip_files = check_file_size.check_file_size(root=root)
        with self.window.result_list_write_lock:
            self.window.result_list.append((root, size_dir, skip_files))

    def run(self):
        with self.window.status_update_lock:
            self.window.status.SetValue(u"処理中")
        for f in self.filenames:
            if os.path.isdir(f):
                root = f
            else:
                root = os.path.dirname(f)
            self.window.text.SetValue(root)
            thread = threading.Thread(target=MyThreadKanshi.proc, args=(self, root))
            self.t_list.append(thread)
            thread.start()
        for t in self.t_list:
            t.join()
        with self.window.status_update_lock:

            root_list = []
            for root, size_dir, skip_files in self.window.result_list[:]:
                root_list.append(root)

            self.window.file_list.SetItems(root_list)
            self.window.status.SetValue(u"未処理")
            self.window.drop_ctrl_event.clear()

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

class MyFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, u"ファイルサイズチェッカ", size=(500,-1))

        root_pane = wx.Panel(self, wx.ID_ANY)

        layout = wx.BoxSizer(wx.VERTICAL)

        self.result_list = []
        self.result_list_write_lock = threading.Lock()

        # 1段目
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(root_pane, -1, u"File name:")
        self.text = wx.TextCtrl(root_pane, -1, "", size=(400,-1))
        sizer_1.Add(label, 0, wx.ALL, 5)
        sizer_1.Add(self.text, 0, wx.ALL | wx.GROW, 5)

        # 2段目
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.status_update_lock = threading.Lock()
        self.status = wx.TextCtrl(root_pane, -1, u"未処理")
        self.file_list = wx.ComboBox(root_pane, wx.ID_ANY, style=wx.CB_DROPDOWN)
        self.file_list.Bind(wx.EVT_COMBOBOX, self.OnComboBoxSelect)
        sizer_2.Add(self.status, 0, wx.ALL, 5)
        sizer_2.Add(self.file_list, 0, wx.ALL, 5)

        # 3段目
        self.result_text_update_lock = threading.Lock()
        self.result_text = wx.TextCtrl(root_pane, -1, "", style=wx.TE_MULTILINE)

        # 縦組み
        layout.Add(sizer_1, 0, wx.ALL, 5)
        layout.Add(sizer_2, 0, wx.ALL, 5)
        layout.Add(self.result_text, 1, wx.ALL | wx.GROW, 5)
        root_pane.SetSizer(layout)

        # ファイルドロップの設定
        dt = MyFileDropTarget(self)  #対象はこのフレーム全体
        self.SetDropTarget(dt)

    def OnComboBoxSelect(self, event):
        selected = self.file_list.GetValue()
        with self.result_text_update_lock:
            for root, size_dir, skip_files in self.result_list[:]:
                if root != selected:
                    continue
                self.result_text.write(root + "\n")
                for key in sorted(size_dir.keys()):
                    self.result_text.write("\t".join([key, str(size_dir[key])]) + "\n")
                self.result_text.write("\n")

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()
