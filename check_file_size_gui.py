# -*- coding: utf-8 -*-

import wx
import os
import thread

import check_file_size

# http://d.hatena.ne.jp/Megumi221/20110308/1299571975

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):  #ファイルをドロップするときの処理
        for file in filenames:
            self.window.text.SetValue(file)
            if os.path.isdir(file):
                root = file
            else:
                root = os.path.dirname(file)
            thread.start_new_thread(check_file_size.main, (root, 0, 0, check_file_size.SIZE, self.window.result_text))
            #check_file_size.main(root = root, outbuf=self.window.result_text)

class MyFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, u"ファイルサイズチェッカ")

        root_pane = wx.Panel(self, wx.ID_ANY)

        layout = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(root_pane, -1, "File name:")
        self.text = wx.TextCtrl(root_pane, -1, "", size=(400,-1))
        sizer.Add(label, 0, wx.ALL, 5)
        sizer.Add(self.text, 0, wx.ALL, 5)

        self.result_text = wx.TextCtrl(root_pane, -1, "", style=wx.TE_MULTILINE)

        layout.Add(sizer, 0, wx.ALL, 5)
        layout.Add(self.result_text, 1, wx.ALL | wx.GROW, 5)
        root_pane.SetSizer(layout)

        dt = MyFileDropTarget(self)  #ドロップする対象をこのフレーム全体にする
        self.SetDropTarget(dt)

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()
