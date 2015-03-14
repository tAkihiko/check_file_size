# -*- coding: utf-8 -*-

import wx
import wx.grid as gridlib
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

# http://stackoverflow.com/questions/28509629/work-with-ctrl-c-and-ctrl-v-to-copy-and-paste-into-a-wx-grid-in-wxpython
class MyGrid(wx.grid.Grid):
    """ A Copy&Paste enabled grid class"""
    def __init__(self, parent, id, style):
        wx.grid.Grid.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, style)
        wx.EVT_KEY_DOWN(self, self.OnKey)
        self.data4undo = [0, 0, '']

    def OnKey(self, event):
        # If Ctrl+C is pressed...
        if event.ControlDown() and event.GetKeyCode() == 67:
            self.copy()
        # If Ctrl+V is pressed...
        if event.ControlDown() and event.GetKeyCode() == 86:
            self.paste('clip')
        # If Ctrl+Z is pressed...
        if event.ControlDown() and event.GetKeyCode() == 90:
            if self.data4undo[2] != '':
                self.paste('undo')
        # If del is pressed...
        if event.GetKeyCode() == 127:
            # Call delete method
            self.delete()
        # Skip other Key events
        if event.GetKeyCode():
            event.Skip()
            return

    def copy(self):
        # Number of rows and cols
        if self.GetSelectionBlockTopLeft() == []:
            rows = 1
            cols = 1
            iscell = True
        else:
            rows = self.GetSelectionBlockBottomRight()[0][0] - self.GetSelectionBlockTopLeft()[0][0] + 1
            cols = self.GetSelectionBlockBottomRight()[0][1] - self.GetSelectionBlockTopLeft()[0][1] + 1
            iscell = False
        # data variable contain text that must be set in the clipboard
        data = ''
        # For each cell in selected range append the cell value in the data variable
        # Tabs '\t' for cols and '\r' for rows
        for r in range(rows):
            for c in range(cols):
                if iscell:
                    data += str(self.GetCellValue(self.GetGridCursorRow() + r, self.GetGridCursorCol() + c))
                else:
                    data += str(self.GetCellValue(self.GetSelectionBlockTopLeft()[0][0] + r, self.GetSelectionBlockTopLeft()[0][1] + c))
                if c < cols - 1:
                    data += '\t'
            data += '\n'
        # Create text data object
        clipboard = wx.TextDataObject()
        # Set data object value
        clipboard.SetText(data)
        # Put the data in the clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(clipboard)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Error")

    def paste(self, stage):
        if stage == 'clip':
            clipboard = wx.TextDataObject()
            if wx.TheClipboard.Open():
                wx.TheClipboard.GetData(clipboard)
                wx.TheClipboard.Close()
            else:
                wx.MessageBox("Can't open the clipboard", "Error")
            data = clipboard.GetText()
            if self.GetSelectionBlockTopLeft() == []:
                rowstart = self.GetGridCursorRow()
                colstart = self.GetGridCursorCol()
            else:
                rowstart = self.GetSelectionBlockTopLeft()[0][0]
                colstart = self.GetSelectionBlockTopLeft()[0][1]
        elif stage == 'undo':
            data = self.data4undo[2]
            rowstart = self.data4undo[0]
            colstart = self.data4undo[1]
        else:
            wx.MessageBox("Paste method "+stage+" does not exist", "Error")
        text4undo = ''
        # Convert text in a array of lines
        for y, r in enumerate(data.splitlines()):
            # Convert c in a array of text separated by tab
            for x, c in enumerate(r.split('\t')):
                if y + rowstart < self.NumberRows and x + colstart < self.NumberCols :
                    text4undo += str(self.GetCellValue(rowstart + y, colstart + x)) + '\t'
                    self.SetCellValue(rowstart + y, colstart + x, c)
            text4undo = text4undo[:-1] + '\n'
        if stage == 'clip':
            self.data4undo = [rowstart, colstart, text4undo]
        else:
            self.data4undo = [0, 0, '']

    def delete(self):
        # print "Delete method"
        # Number of rows and cols
        if self.GetSelectionBlockTopLeft() == []:
            rows = 1
            cols = 1
        else:
            rows = self.GetSelectionBlockBottomRight()[0][0] - self.GetSelectionBlockTopLeft()[0][0] + 1
            cols = self.GetSelectionBlockBottomRight()[0][1] - self.GetSelectionBlockTopLeft()[0][1] + 1
        # Clear cells contents
        for r in range(rows):
            for c in range(cols):
                if self.GetSelectionBlockTopLeft() == []:
                    self.SetCellValue(self.GetGridCursorRow() + r, self.GetGridCursorCol() + c, '')
                else:
                    self.SetCellValue(self.GetSelectionBlockTopLeft()[0][0] + r, self.GetSelectionBlockTopLeft()[0][1] + c, '')

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
        self.result_text = MyGrid(root_pane, wx.ID_ANY, wx.ALL)
        self.result_text.CreateGrid(0,2)

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
                for key in sorted(size_dir.keys()):
                    self.result_text.AppendRows()
                    row = self.result_text.GetNumberRows() - 1
                    self.result_text.SetCellValue(row, 0, key)
                    self.result_text.SetCellValue(row, 1, str(size_dir[key]))

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()
