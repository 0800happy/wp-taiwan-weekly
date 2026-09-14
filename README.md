# WP 台灣週報

依提供的兩張圖片與 https://oberonlai.github.io/wp-taiwan-weekly/issues/003.html 製作的獨立靜態週報版型。

- 目錄：`dist/index.html`
- 內頁示範：`dist/issues/demo.html`
- 每一則消息獨立一张卡片，分類有獨立外框，桌面左側有本期目錄，手機改為單欄。
- 示範刊是來源導覽，不是當週新聞；首期正式內容提交後會自動隱藏示範刊。
- 不需要 WordPress、資料庫、npm 套件或 API 金鑰。

## 目前狀態

版型、內容產生器、Pages 部署工作流程與出刊規則已準備。尚未連到目標 GitHub 儲存庫，尚未部署，GPT 排程尚未啟用。

## 首次發布

1. 在你自己的 GitHub 帳號建立 `wp-taiwan-weekly` 公開儲存庫（可換名稱），預設分支 main，並授權 ChatGPT GitHub 連線存取。
2. 將本資料夾內容提交到儲存庫根目錄，包含 `.github/workflows/pages.yml`。
3. 在 Settings → Pages → Build and deployment 將 Source 設為 GitHub Actions。
4. 執行 Publish weekly site 工作流程，或推送一次更新。完成後以部署結果回傳的網址為準。
5. GPT 讀寫測試與首次 Pages 部署確認成功後，依 AUTOMATION.md 建立每週一台灣時間早晨排程。

## 本機建置與查看

```sh
python3 scripts/build.py
```

直接打開 `dist/index.html` 即可閱讀，所有頁面都是靜態 HTML，關閉 JavaScript 仍可使用。中文字型優先載入 Google Fonts；離線時回退系統中文字型。

## 新一期

以 `content/issues/demo.json` 與 `AUTOMATION.md` 的 schema 為參考新增一個 JSON。每則消息對應 sections[].items[] 中的一個物件；不可把多個標題混進同一則。正式刊設定 demo=false，期數由 1 開始，出刊日期以當週一為準。

`scripts/build.py` 檢查重複日期、重複期數、日期格式、來源欄位、安全連結與章節錨點，將文字 HTML escape。此檢查不代表內容事實已查證；查證由出刊任務完成。已刊來源整理至 dist/published.json。

GitHub Actions 在 main 更新時建置並部署，沒有另設第二個自動撰稿排程。
