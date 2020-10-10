import os
import re
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import filetype

import Amusic


def show_file_path():
    if sys.platform[:3] == "win":
        subprocess.run(['explorer', '/n,downloads'])
    if sys.platform == "darwin":
        downloads_path = os.path.expanduser("~/Music/")
        subprocess.run(['open', downloads_path])


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.program_name = "自嗨音频下载器"
        self.show_screen = tk.StringVar()
        self.show_progress = tk.StringVar()
        self.lock = threading.Lock()
        self.createWidgets()

    def createWidgets(self):
        # 0
        self.title(self.program_name + " - 独居者")

        # 设置字体
        l_font = ("宋体", 30)
        m_font = ("宋体", 20)
        s_font = ("宋体", 15)

        # 设置窗口大小
        width = 500
        height = 310
        # 获取屏幕尺寸以计算布局参数，使窗口居于屏幕中央
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry_str = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 3)
        self.geometry(geometry_str)
        self.resizable(width=False, height=False)

        # 1
        self.show_screen.set(self.program_name)
        labScreen = tk.Label(self, textvariable=self.show_screen, bd=1, relief="solid", font=m_font)
        labScreen.place(x=100, y=20, width=300, height=50)

        # 2
        self.progressBar = ttk.Progressbar(self, length=100, mode="determinate")
        self.progressBar.place(x=50, y=85, width=400, height=10)

        # 3
        self.show_progress.set("")
        labProgress = tk.Label(self, textvariable=self.show_progress)
        labProgress.place(x=410, y=65, width=40, height=20)

        # 4
        self.entryUrl = tk.Entry(validate="focusin", validatecommand=self.del_url_show, font=s_font)
        self.entryUrl.place(x=50, y=125, width=293, height=50)
        self.entryUrl.insert(0, "请输入分享链接即可")

        # 5
        self.buttonDownload = tk.Button(self, text="下载", command=self.audio_down, font=s_font)
        self.buttonDownload.place(x=370, y=125, width=80, height=50)

        # 6
        buttonFile = tk.Button(self, text="浏览输出", command=show_file_path, font=l_font)
        buttonFile.place(x=50, y=200, width=400, height=80)

        # 7
        declare_str = "声明：仅供个人录制音频下载使用"
        labDeclare = tk.Label(self, text=declare_str, font=("宋体", 9), fg="red")
        labDeclare.place(x=0, y=285, width=500, height=25)

    def down_thread(self, music_url):
        self.lock.acquire()
        try:
            self.progressBar["value"] = 0
            self.show_progress.set("")
            self.show_screen.set(self.program_name)
            self.update()
            try:
                music_data = Amusic.get_all_music_parm(music_url)
                if music_data[0] == "null" and music_data[1] == "null":
                    print("不支持此分享链接或者链接格式错误")
                    messagebox.showwarning(title="警告", message="不支持此分享链接或者链接格式错误")
                    return
                if music_data[1] == "null":
                    music_name = music_data[0]
                    self.show_screen.set(music_name)
                    messagebox.showwarning(title="警告", message=music_name)
                    return
                music_name = music_data[0]
                music_play_url = music_data[1]
                self.show_screen.set(music_name)
                ###开始下载###
                try:
                    if sys.platform[:3] == "win":
                        down_path = "downloads/"
                    if sys.platform == "darwin":
                        down_path = os.path.expanduser("~/Music/")
                    down_name = music_name + ".temp"
                    str_out = ['./aria2c', '-x', '8', '-d', down_path, '-o', down_name, music_play_url]
                    print(str_out)
                    if sys.platform[:3] == "win":
                        si = subprocess.STARTUPINFO()
                        si.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
                        si.wShowWindow = subprocess.SW_HIDE
                        process = subprocess.Popen(str_out, shell=False, stdout=subprocess.PIPE,
                                                   stderr=subprocess.STDOUT,
                                                   encoding="utf-8",
                                                   text=True, startupinfo=si)
                    if sys.platform == "darwin":
                        process = subprocess.Popen(str_out, shell=False, stdout=subprocess.PIPE,
                                                   stderr=subprocess.STDOUT,
                                                   encoding="utf-8", text=True)
                    for line in process.stdout:
                        # print(line)

                        percent_res = re.search(r'\((?P<percent>[\s\S]*?)%\)', line)
                        if percent_res is not None:
                            progress = percent_res.groupdict()['percent']
                            print(progress)
                            self.progressBar["value"] = progress
                            self.show_progress.set(progress + "%")
                            self.update()
                    process.wait()
                    if process.poll() == 0:
                        self.progressBar["value"] = 100
                        self.show_progress.set("100%")
                        self.show_screen.set("下载完成")
                        self.update()
                        kind = filetype.guess(down_path + down_name)
                        if kind is None:
                            print("文件类型不支持")
                        else:
                            name_len = len(down_name) - 5
                            try:
                                os.rename(down_path + down_name,
                                          down_path + down_name[:name_len] + "." + kind.extension)
                            except Exception as e:
                                print(e)
                                messagebox.showwarning(title="警告", message=str(e))
                except Exception as e:
                    print("网络未连接，请检查连接后重试")
                    print(e)
                    messagebox.showwarning(title="警告", message="网络未连接，请检查连接后重试")
                ############
            except Exception as e:
                print("网络未连接，请检查连接后重试")
                print(e)
                messagebox.showwarning(title="警告", message="网络未连接，请检查连接后重试")
                return
        finally:
            self.lock.release()

    def audio_down(self):
        music_url = self.entryUrl.get().strip('\n')
        if music_url == "" or music_url == "请输入分享链接即可":
            messagebox.showwarning(title="警告", message="请输入分享链接后执行")
            return

        if not self.lock.locked():
            temp_thread = threading.Thread(target=self.down_thread, args=(music_url,))
            temp_thread.setDaemon(True)
            temp_thread.start()

    def del_url_show(self):
        self.entryUrl.delete(0, "end")


if __name__ == '__main__':
    app = Application()
    app.mainloop()
