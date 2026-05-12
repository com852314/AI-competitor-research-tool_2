# 競品調研工具

每週追蹤 5 個 Slot 遊戲平台的 Top 20 熱門榜與新遊戲，做跨平台分析。

## 5 個平台

| 代號 | 平台 | 市場 |
|---|---|---|
| PT | PT Gaming | 菲律賓 |
| BP | BingoPlus | 菲律賓 |
| CP | Casino Plus | 菲律賓 |
| TCG | Luckyi | 菲律賓 |
| BAJI | Baji | 孟加拉 |

## 怎麼看資料

**最快方式**：

1. 把整個 repo 下載到本機
2. 雙擊 `scripts/viewer.html` 在 Chrome 開啟
3. 點「📂 選擇 data 資料夾」按鈕，選擇 repo 的 `data/` 資料夾
4. 看本週 Top 20、跨平台分析、主表瀏覽、廠家對照

## 資料結構

```
data/
├── weekly/        每週快照（JSON）
│   └── W1_2026-04-30.json
└── master/        主資料
    ├── games.json       遊戲主表
    ├── vendors.json     廠家對照
    └── platforms.json   平台對照
```

## 程式碼

- `scripts/viewer.html` - 全功能 HTML 檢視器（單檔 SPA）
- `scripts/capture_week.py` - 每週抓取資料寫入 JSON
- `scripts/migrate_w18.py` - 一次性遷移（已執行）

## 文件

- `docs/探勘總結報告_v2.docx` - 5 平台技術可行性報告
- `docs/週執行SOP.docx` - 標準作業程序 v4
- `專案規劃與架構.md` - 完整架構與決策記錄

## W1（第一週）跨平台亮點

5 款遊戲在 ≥3 平台 Top 20 上榜：

- **Super Ace**（JILI）- 4 平台（PT/CP/TCG/BAJI）
- **Super Ace Deluxe**（JILI）- 4 平台
- Wild Bounty Showdown（PG Soft）- 3 平台
- Golden Empire（JILI）- 3 平台
- Fortune Garuda 500（JILI）- 3 平台

詳細看 viewer.html 的「🌐 跨平台分析」頁籤。
