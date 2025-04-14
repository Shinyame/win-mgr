import tkinter as tk
from tkinter import messagebox
import subprocess
import datetime
import psutil
import os
import json
import locale

locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')  # 日本語ロケール（Windowsでは影響しないが念のため）

CONFIG_PATH = "shutdown_info.json"

def format_datetime_jp(dt):
    weekdays = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
    weekday_jp = weekdays[dt.weekday()]
    return f"{dt.year}年{dt.month}月{dt.day}日 {dt.hour}時{dt.minute}分 {weekday_jp}"


def load_last_shutdown_time():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            ts = data.get("last_shutdown_time")
            if ts:
                try:
                    dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    return format_datetime_jp(dt)
                except:
                    return "不明"
    return "不明"

def save_shutdown_time():
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"last_shutdown_time": now_str}, f, ensure_ascii=False)

def get_uptime():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    return format_datetime_jp(boot_time)

def get_elapsed_time():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    now = datetime.datetime.now()
    delta = now - boot_time
    hours, remainder = divmod(delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}時間{int(minutes)}分{int(seconds)}秒 稼働中"

def shutdown():
    save_shutdown_time()
    subprocess.run("shutdown /s /f /t 0", shell=True)

def reboot():
    subprocess.run("shutdown /r /f /t 0", shell=True)
    
def create_gui():
    root = tk.Tk()
    root.title("Windows 完全シャットダウン管理")
    root.geometry("520x550")
    root.configure(bg="white")
    root.resizable(False, False)

    # 共通スタイル
    accent_color = "#0a84ff"
    text_color = "#333333"
    font_main = ("MS Gothic", 16)
    font_button = ("MS Gothic", 14, "bold")

    # タイトル
    title = tk.Label(root, text="管理項目一覧", font=("MS Gothic", 16, "bold"),
                     bg="white", fg=accent_color)
    title.pack(pady=(20, 10))

    # 稼働時間表示
    uptime_str = get_uptime()
    uptime_label_var = tk.StringVar(value=f"起動時間：{uptime_str}")
    uptime_label = tk.Label(root, textvariable=uptime_label_var, font=font_main, bg="white", fg=text_color)
    uptime_label.pack(pady=(5, 10))

    # 稼働時間
    elapsed_label_var = tk.StringVar(value="")
    elapsed_button = tk.Button(root, text="稼働時間を表示", font=font_button,
                                bg="#007aff", fg="white", relief="flat",
                                command=lambda: elapsed_label_var.set(get_elapsed_time()))
    elapsed_button.pack(pady=(0, 5))

    elapsed_label = tk.Label(root, textvariable=elapsed_label_var, font=font_main,
                             bg="white", fg=text_color)
    elapsed_label.pack(pady=(0, 10))

    # 最後の完全シャットダウン
    last_shutdown = load_last_shutdown_time()
    last_label = tk.Label(root, text=f"最後の完全シャットダウン：\n{last_shutdown}",
                          font=font_main, bg="white", fg=text_color)
    last_label.pack(pady=(5, 15))

    # シャットダウン
    def confirm_shutdown():
        if messagebox.askyesno("確認", "本当に完全シャットダウンしますか？"):
            shutdown()

    shutdown_button = tk.Button(root, text="完全シャットダウン", font=font_button,
                                 bg=accent_color, fg="white", relief="flat",
                                 command=confirm_shutdown)
    shutdown_button.pack(pady=5)

    # 再起動
    def confirm_reboot():
        if messagebox.askyesno("確認", "本当に再起動しますか？"):
            reboot()

    reboot_button = tk.Button(root, text="再起動", font=font_button,
                              bg="#007aff", fg="white", relief="flat",
                              command=confirm_reboot)
    reboot_button.pack(pady=(5, 20))

    # 指定時間後シャットダウン
    timer_frame = tk.Frame(root, bg="white")
    timer_frame.pack(pady=(10, 5))

    tk.Label(timer_frame, text="n分後にシャットダウン：", font=font_main, bg="white", fg=text_color).grid(row=0, column=0, padx=5, pady=5)
    minutes_entry = tk.Entry(timer_frame, width=6, font=font_main)
    minutes_entry.grid(row=0, column=1, padx=5)

    is_force_shutdown = tk.BooleanVar()
    force_checkbox = tk.Checkbutton(timer_frame, text="完全にする", variable=is_force_shutdown,
                                    bg="white", font=("MS Gothic", 10))
    force_checkbox.grid(row=0, column=2, padx=10)

    def start_shutdown_timer():
        try:
            mins = int(minutes_entry.get())
            if mins <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("エラー", "正しい分数を入力してください。")
            return

        t_seconds = mins * 60
        if is_force_shutdown.get():
            save_shutdown_time()
            cmd = f"shutdown /s /f /t {t_seconds}"
        else:
            cmd = f"shutdown /s /t {t_seconds}"

        subprocess.run(cmd, shell=True)
        messagebox.showinfo("予約完了", f"{mins}分後に{'完全' if is_force_shutdown.get() else '通常'}シャットダウンします。")

    # タイマー中止
    def cancel_shutdown_timer():
        result = subprocess.run("shutdown /a", shell=True, capture_output=True, text=True)
        if "取り消されました" in result.stdout or result.returncode == 0:
            messagebox.showinfo("キャンセル成功", "シャットダウン予約をキャンセルしました。")
        else:
            messagebox.showwarning("キャンセル失敗", "キャンセルできる予約が存在しません。")

    timer_button = tk.Button(root, text="タイマー開始", font=font_button,
                             bg="#ff9500", fg="white", relief="flat",
                             command=start_shutdown_timer)
    timer_button.pack(pady=(0, 20))

    cancel_button = tk.Button(root, text="タイマー中止", font=font_button,
                              bg="#ff3b30", fg="white", relief="flat",
                              command=cancel_shutdown_timer)
    cancel_button.pack(pady=(5, 20))


    root.mainloop()

if __name__ == "__main__":
    create_gui()