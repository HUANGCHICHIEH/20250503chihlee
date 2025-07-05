# 任務清單 (Todolist)

- [ ] **步驟 1: 建立 CLI 應用程式基礎結構**
    - 建立 `app.py` 檔案。
    - 使用 `argparse` 模組設定命令列參數，需包含：
        - `--csv`: 用於指定輸入的 CSV 檔案路徑。
        - `--excel`: 用於指定輸出的 Excel 檔案路徑。

- [ ] **步驟 2: 實作檔案讀取與樞紐分析**
    - 在 `app.py` 中，使用 `pandas` 讀取由 `--csv` 參數指定的檔案。
    - 根據讀取的 DataFrame 建立樞紐分析表。

- [ ] **步驟 3: 實作檔案輸出與程式碼註解**
    - 將產生的樞紐分析表 DataFrame 儲存至由 `--excel` 參數指定的 Excel 檔案。
    - 根據 `WORKSPACE.md` 的要求，為 `app.py` 中所有的函式 (function) 加上清晰的 docstring 說明。