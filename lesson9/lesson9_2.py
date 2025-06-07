import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font # 修正: 匯入 font 模組
from tkinter.constants import BOTH, END, LEFT, RIGHT, SINGLE, VERTICAL, X, Y
import os

APP_TITLE = "姓名搜尋器"
NAMES_FILE = "names.txt"

class NameSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("450x400")

        # --- Style ---
        self.style = ttk.Style(self.root)
        # 可嘗試的主題: 'clam', 'alt', 'default', 'vista' (Windows), 'aqua' (macOS)
        available_themes = self.style.theme_names()
        # print(f"Available themes: {available_themes}")
        if 'vista' in available_themes:
            self.style.theme_use('vista')
        elif 'clam' in available_themes:
            self.style.theme_use('clam')

        # --- Font ---
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Microsoft JhengHei UI", size=10) # 微軟正黑體
        self.root.option_add("*Font", default_font)

        self.all_names = self._load_names()

        # --- UI Elements ---
        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.pack(fill=BOTH, expand=True)

        # Search Frame
        search_frame = ttk.Frame(main_frame, padding="0 0 0 10") # 下方增加間距
        search_frame.pack(fill=X)

        ttk.Label(search_frame, text="搜尋姓名:").pack(side=LEFT, padx=(0, 10))
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=LEFT, expand=True, fill=X, padx=(0,10))
        self.search_entry.focus()

        search_button = ttk.Button(search_frame, text="搜尋", command=self._perform_search)
        search_button.pack(side=LEFT)

        # Results Frame
        results_frame = ttk.Frame(main_frame, padding="0 10 0 0") # 上方增加間距
        results_frame.pack(fill=BOTH, expand=True)

        self.results_listbox = tk.Listbox(results_frame, height=10, selectmode=SINGLE, relief=tk.SOLID, borderwidth=1)
        self.results_listbox.pack(fill=BOTH, expand=True, side=LEFT)

        scrollbar = ttk.Scrollbar(results_frame, orient=VERTICAL, command=self.results_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.results_listbox.config(yscrollcommand=scrollbar.set)

        # Status Label
        self.status_label = ttk.Label(main_frame, text="請輸入姓名進行搜尋", padding="5 0 0 0") # 上方增加間距
        self.status_label.pack(fill=X, side=tk.BOTTOM)

        # Bind Enter key to search
        self.root.bind('<Return>', lambda event: self._perform_search())

        # Initial status update based on file loading
        if not os.path.exists(NAMES_FILE):
            self.status_label.config(text=f"錯誤: \"{NAMES_FILE}\" 檔案不存在。", foreground="red")
        elif not self.all_names and os.path.exists(NAMES_FILE): # File exists but might be empty or unreadable
            self.status_label.config(text=f"\"{NAMES_FILE}\" 為空或無法讀取有效姓名。", foreground="orange")


    def _load_names(self):
        """載入 names.txt 檔案中的姓名列表"""
        names = []
        try:
            with open(NAMES_FILE, "r", encoding="utf-8") as f:
                names = [line.strip() for line in f if line.strip()]
            if not names and os.path.exists(NAMES_FILE): # File exists but is empty
                pass # Handled by initial status_label
        except FileNotFoundError:
            messagebox.showerror("檔案錯誤", f"找不到檔案: {NAMES_FILE}\n請確認檔案是否存在於程式目錄。")
        except Exception as e:
            messagebox.showerror("讀取錯誤", f"讀取 {NAMES_FILE} 時發生錯誤: {e}")
        return names

    def _perform_search(self):
        """執行搜尋並更新結果列表"""
        search_term = self.search_entry.get().strip()
        self.results_listbox.delete(0, END)  # 清除先前的結果
        self.status_label.config(foreground="black") # Reset color

        if not self.all_names:
            self.status_label.config(text="姓名列表未載入或為空。")
            self.results_listbox.insert(END, "姓名列表未載入或為空")
            return

        if not search_term:
            self.status_label.config(text="請輸入搜尋關鍵字。")
            # 可以選擇顯示所有姓名或保持空白
            # for name in self.all_names:
            #     self.results_listbox.insert(END, name)
            # self.status_label.config(text=f"顯示所有 {len(self.all_names)} 筆姓名")
            return

        found_names = [name for name in self.all_names if search_term.lower() in name.lower()]
        
        if found_names:
            for name in found_names:
                self.results_listbox.insert(END, name)
            self.status_label.config(text=f"找到 {len(found_names)} 個結果。")
        else:
            self.results_listbox.insert(END, "無此人")
            self.status_label.config(text="查無此人。")

if __name__ == "__main__":
    root = tk.Tk()
    app = NameSearchApp(root)
    root.mainloop()