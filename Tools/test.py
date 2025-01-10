import tkinter as tk
from tkinter import messagebox
import requests
import os
import sys
import time
import subprocess

# 當前版本
CURRENT_VERSION = "v1.0.4"

# GitHub 儲存庫資訊
REPO = "igs-jawenchen/LocalTest"

def is_online():
    """檢查網路連線"""
    try:
        requests.get("https://www.google.com", timeout=2)
        return True
    except requests.ConnectionError:
        return False

def get_latest_release_info(repo):
    """從 GitHub API 獲取最新版本資訊"""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "version": data["tag_name"],  # 最新版本號
                "name": data["name"],  # Release 標題
                "body": data["body"]  # Release 描述
            }
        else:
            return None
    except Exception as e:
        print(f"無法獲取最新版本資訊: {e}")
        return None

def download_update(latest_version):
    """下載最新版本"""
    download_url = f"https://github.com/{REPO}/releases/download/{latest_version}/update.exe"
    temp_file = "temp_update.exe"

    try:
        # 下載最新版本
        response = requests.get(download_url, stream=True)
        with open(temp_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"已下載最新版本：{temp_file}")
        return temp_file
    except Exception as e:
        messagebox.showerror("更新失敗", f"下載過程中出現錯誤：{e}")
        return None

def replace_and_restart(temp_file):
    """使用中繼程式替換執行檔並重新啟動"""
    updater_script = "updater.bat"

    # 建立批次檔案
    with open(updater_script, "w") as f:
        f.write(f"@echo off\n")
        f.write(f"timeout /t 3 > nul\n")  # 等待 3 秒，確保主程式退出
        f.write(f"move /y {temp_file} update.exe\n")  # 替換執行檔
        f.write(f"start update.exe\n")  # 啟動新的程式
        f.write(f"del \"%~f0\"\n")  # 刪除自身

    # 執行批次檔並退出主程式
    try:
        subprocess.Popen(["cmd", "/c", updater_script])
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("更新失敗", f"替換過程中出現錯誤：{e}")

def check_for_update():
    """檢查更新"""
    if not is_online():
        messagebox.showwarning("無網路連線", "目前處於離線狀態，無法檢查更新。")
        return

    release_info = get_latest_release_info(REPO)
    if release_info is None:
        messagebox.showerror("錯誤", "無法檢查最新版本，請稍後再試。")
        return

    latest_version = release_info["version"]
    release_name = release_info["name"]
    release_body = release_info["body"]

    if latest_version != CURRENT_VERSION:
        # 顯示更新資訊
        result = messagebox.askyesno(
            "有新版本可用",
            f"檢測到新版本：{latest_version}\n\n"
            f"更新內容：\n{release_name}\n\n{release_body}\n\n"
            "是否立即更新？"
        )
        if result:
            temp_file = download_update(latest_version)
            if temp_file:
                replace_and_restart(temp_file)
    else:
        messagebox.showinfo("已是最新版本", "目前已是最新版本，無需更新。")

# 建立 GUI 介面
def create_gui():
    root = tk.Tk()
    root.title("更新工具")
    root.geometry("300x150")

    # 更新按鈕
    update_button = tk.Button(root, text="檢查更新", font=("Arial", 14), command=check_for_update)
    update_button.pack(pady=50)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
