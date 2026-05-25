# 競品調研（排名）專案交接文件

> 給接手的 AI agent：直接讀本文件即可上工，無須回看 chat history。

---

## 1. 專案目標

建立 Slot 遊戲跨平台競品追蹤系統，每週快照 5 個平台 Top 20 排名 + 新遊戲清單，產出可分享給內部團隊的可視化報表。

- **5 個平台**：PT / BP / CP / TCG（菲律賓 4 個）+ BAJI（孟加拉 1 個）
- **架構**：JSON-first + HTML SPA viewer（已從 Excel 全面遷移，省 30–40× token）
- **發佈**：GitHub Pages 自動讀 `data/manifest.json`，內部團隊可直接看
- **頻率**：每週一次資料快照

---

## 2. 目前完成進度

### 已完成
- ✅ JSON-first 架構（取代 Excel）
- ✅ 主表系統：games.json（106 款）/ vendors.json（36 個）/ platforms.json（5 個）
- ✅ `scripts/capture_week.py`：自動算下週次 + 配對主表 ID + 更新 manifest
- ✅ W1 快照（2026-04-30）
- ✅ W2 快照（2026-05-11）：5 平台 Top 20 + TCG/BAJI 新遊戲 + 18 款遊戲補名 + 10 新廠家
- ✅ W3 快照（2026-05-22）：5 平台 Top 20 + TCG 20 新遊戲 + BAJI 24 新遊戲 + 主表新增 25 款
- ✅ index.html viewer：snapshot / cross / newgames (2D) / master / vendors / **trend (2E)** 6 個頁籤
- ✅ GitHub Pages 部署、自動載入 manifest
- ✅ **Phase 2E 跨週趨勢頁籤**（2026-05-18 完成）：排名折線圖 + 常勝軍 + 進出榜 + 廠家市占 Stacked Bar
- ✅ 週執行 SOP v5（本文件第 10 節）
- ✅ 資料收集提示詞（`docs/DATA_CAPTURE_PROMPT.md`）：含頁面操作規則、新遊戲 20 筆上限

### 待辦
- ⏳ W4 抓取（下週執行）
- ⏳ 未來：SOP v5 流程累積更多週後，可考慮 Phase 3（自動排程、更多分析維度）

---

## 3. 未完成工作

無阻塞性問題。目前系統完整可運作。

下一步是 **W4 抓取**（按第 10 節 SOP v5 執行）。

---

## 4. 當前正在處理的問題

無。W3 已完工並 push（2026-05-25）。

---

## 5. 已確認規則

### 編輯 index.html / 大檔的規則（重要）
- ❌ **不要用 Edit 工具大段改 index.html**：Edit 多次截斷檔案，造成損毀
- ✅ **改用 Python 腳本**：在 `outputs/add_phaseXX.py` 寫腳本，read → 字串 replace → write 原子寫回
- ✅ 每段 replace 前先 `assert old_string in html` 防呆

### CP 廠家規則（master-first）
- CP 排行頁面沒有可靠廠家欄
- 規則：**先查主表**，主表沒有 → 廠家留空 / 標「(待補)」，**不猜**
- 已踩過坑：Sugar Bang Bang = FA CHAI（不是 OmniPlay）、Cloud Princess = HACKSAW（不是 PG Soft）

### 抓資料 SOP（v5）
分批進行，避免 token 爆掉：
1. 第一批：PT / BP / CP（3 個菲律賓 Top 20）
2. 第二批：TCG / BAJI（Top 20 + 新遊戲清單，**新遊戲最多 20 筆**）
3. 第三批：跑 `capture_week.py raw_input.json` + 補名 + 補廠家

### Cowork 資料收集規則（DATA_CAPTURE_PROMPT.md）
- **可在頁面內滾動**，但不可自行切換到其他分頁或分類
- 發現頁面內容與預期不符（分類錯誤、平台不對）→ 立即回報使用者，等確認後再繼續
- 任何不確定的情況先詢問，不自行判斷
- 新遊戲清單超過 20 筆只取前 20（腳本也有 `[:20]` 保護）

### 廠家命名
- `normalizedName`：主表標準名（如 `FA CHAI`）
- `rawVendor`：平台原樣（如 `FaChai`、`FACHAI`）
- 寫入時保留 raw 以便 debug，比對時用 normalized

### 「待辨識」處理
- 抓到只看到 gameId、沒有名稱的遊戲 → name 欄填 `(待辨識)`
- 用戶提供名稱對應表後，跑 `outputs/patch_wN.py` 批次補名 + 主表新增

---

## 6. 已知限制

- **Edit 工具會截斷大檔**：>500 行的 HTML/JS 不要用 Edit 改大段，要用 Python 腳本
- **OneDrive 同步鎖**：Excel 開著時 .xlsx 會變損毀 ZIP；已遷至 JSON 規避
- **LibreOffice 鎖檔**：`.~lock.xxx#` 殘留檔需手動刪
- **GitHub Pages CDN cache**：push 後可能需要 1–3 分鐘才看到 manifest 更新
- **W1 / platforms.json 都有 `platforms` 欄**：viewer 必須先用 `typeof json.week === 'number' && !Array.isArray(json.platforms)` 判斷是否為 weekly
- **CP 抓取無法看廠家**：永遠用 master-first 策略

---

## 7. 資料來源與取得方式

| 平台 | 市場 | 來源頁面類型 |
|---|---|---|
| PT | 菲律賓 | 後台排行頁 Top 20 |
| BP | 菲律賓 | 後台排行頁 Top 20 |
| CP | 菲律賓 | 後台排行頁 Top 20（無廠家資訊） |
| TCG | 菲律賓 | 排行頁 Top 20 + 「NEW」分類新遊戲 |
| BAJI | 孟加拉 | Recommend Top 20 + New-Old 新遊戲清單 |

抓法：由人類在自己電腦截圖/瀏覽，貼 raw 資料給 Claude，Claude 整理成 `raw_input.json` 後跑 `capture_week.py`。

---

## 8. JSON 資料格式

### `data/manifest.json`
```json
{ "weekly": ["W1_2026-04-30.json", "W2_2026-05-11.json"] }
```

### `data/weekly/W{N}_{YYYY-MM-DD}.json`
```json
{
  "week": 2,
  "captureDate": "2026-05-11",
  "platforms": {
    "PT": {
      "market": "菲律賓",
      "rankings": [
        {
          "rank": 1,
          "name": "Pinata Wins",
          "vendor": "JILI",
          "rawVendor": "JILI",
          "masterId": 12,
          "isNewToTop20": false,
          "lastWeekRank": 2,
          "rankChange": 1,
          "note": ""
        }
      ],
      "newGames": null
    },
    "TCG": {
      "market": "菲律賓",
      "rankings": [...],
      "newGames": [
        {
          "order": 1,
          "name": "Inca Queen",
          "vendor": "Pragmatic Play",
          "rawVendor": "PP",
          "gameId": "PP1014",
          "isFirstSeen": true,
          "note": ""
        }
      ]
    }
  }
}
```

### `data/master/games.json`
```json
{
  "games": [
    {
      "masterId": 1,
      "normalizedName": "Super Ace",
      "normalizedVendor": "JILI",
      "platformAliases": { "PT": "Super Ace", "BP": null, "CP": null, "TCG": "Super Ace", "BAJI": null },
      "firstSeen": "2026-04-30",
      "note": ""
    }
  ]
}
```

### `data/master/vendors.json`
```json
{
  "vendors": [
    {
      "normalizedName": "JILI",
      "displayPerPlatform": {
        "PT": "JILI",
        "BP": "JILI",
        "CP": null,
        "TCG": { "urlCode": "JL", "display": "Jili" },
        "BAJI": { "urlCode": "JILI", "display": "JILI" }
      },
      "note": ""
    }
  ]
}
```

### `data/master/platforms.json`
```json
{
  "platforms": [
    { "code": "PT", "name": "...", "market": "菲律賓", "lastCapture": "2026-05-11", "status": "active" }
  ]
}
```

---

## 9. 重要檔案路徑

工作根目錄：`D:\Claude Project\競品調研(排名)\`

### 程式
- `index.html` — viewer SPA（934 行，含 Phase 2D）
- `scripts/capture_week.py` — 每週抓取腳本
- `outputs/add_phase2d.py` — Phase 2D 注入腳本（範本）
- `outputs/patch_w2.py` — W2 補名+新增廠家腳本（範本）

### 資料
- `data/manifest.json`
- `data/weekly/W1_2026-04-30.json`
- `data/weekly/W2_2026-05-11.json`
- `data/master/games.json`（80 款）
- `data/master/vendors.json`（36 個）
- `data/master/platforms.json`（5 個）
- `data/incoming/raw_input.json` — 每週抓取暫存

### 文件
- `專案規劃與架構.md` — 含 Phase 2A–2E 規格
- `docs/週執行SOP.docx` — v4
- `HANDOVER.md` — 本文件

### Bash 路徑對照
- D:\Claude Project\競品調研(排名)\ → `/sessions/festive-serene-bell/mnt/競品調研(排名)/`
- outputs\ → `/sessions/festive-serene-bell/mnt/outputs/`

---

## 10. 每週執行流程（SOP v5）

> Phase 2E 完成後的新工作流程。資料收集改用獨立 cowork session，主 session 只做 viewer 開發。

### 步驟一：開新 cowork session 收資料

1. 開一個**全新的 cowork 對話**
2. 把 `docs/DATA_CAPTURE_PROMPT.md` **全文貼到第一則訊息**
3. 分兩批提供資料：
   - **第一批**：PT 截圖 → BP HTML → CP HTML（cowork 整理前三平台）
   - **第二批**：TCG 排行 + NEW 清單 HTML → BAJI 排行 + New-Old HTML
4. 確認所有平台都有 20 筆後，要求 cowork 輸出完整 `raw_input.json`

### 步驟二：存檔並執行腳本

```bash
# 1. 把 cowork 輸出的 JSON 存成：
data/incoming/raw_input.json

# 2. 在專案根目錄執行：
python scripts/capture_week.py data/incoming/raw_input.json
```

### 步驟三：處理腳本回報

腳本會印出：
- ✓ 各平台寫入筆數
- ⚠ 新廠家（需手動補進 `data/master/vendors.json`）
- ℹ (待補) 廠家數量（CP 未查到的，後續補）

若有 `(待辨識)` 遊戲 → 查明名稱後跑 `outputs/patch_wN.py` 批次補名

### 步驟四：git push

```bash
git add data/weekly/ data/master/ data/manifest.json
git commit -m "data: W{N} 快照 ({日期})"
git push origin main
```

### 步驟五：驗收

- GitHub Pages 約 1–2 分鐘更新
- 打開網址 → 確認本週快照、跨週趨勢更新
- 通知團隊

---

## 11. 需要避免的事項

- ❌ 用 Edit 對 index.html 做大段（>50 行）替換 → 會被截斷
- ❌ 猜 CP 廠家 → 永遠 master-first
- ❌ 修主表時直接 in-place 改 normalizedVendor → 會破壞已有 ranking 的 masterId 關聯
- ❌ 把 `raw_input.json` 提交到 git → 屬於暫存
- ❌ 在 Excel 開著時改 .xlsx → OneDrive 鎖檔損毀
- ❌ 在 viewer 載入邏輯裡先判斷 weekly 之前先判 platforms → W1 也有 platforms 欄，會被誤判
- ❌ 寫 docs 時忘了更新 SOP version 號 → 用戶會看出來

---

## 12. 若重新開始應先做什麼

1. **讀本文件全文**（你正在做）
2. **讀 `專案規劃與架構.md`** → 理解 Phase 路線圖
3. **確認週數**：`ls data/weekly/`
4. **不要重做已完成的事**：W1/W2 已抓、Phase 2D/2E 已完成
5. **跟用戶確認現在要做什麼**：下一週 W3 抓取？還是 viewer 新功能？

---

## 附：用戶習慣

- 中文溝通（繁中）
- 偏好簡短、結構化回答
- 完成 milestone 後會說「OK 往下一步」/ 「先往 2X 做」
- 看到紅字會說「F12 也沒有紅字錯誤」表示驗收 OK
- 會自己 git push、自己看 GitHub Pages
- 喜歡用 emoji 標示頁籤（🌐 📰 📋 📊）
