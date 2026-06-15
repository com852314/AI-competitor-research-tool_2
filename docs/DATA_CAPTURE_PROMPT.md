# 競品資料收集任務說明

> 把這整份文件貼到新的 cowork 對話開頭，讓 AI 理解任務範圍。

---

## 步驟零：用 MCP browser 工具開啟瀏覽器

收到此提示詞後，**第一件事**：使用瀏覽器 MCP 工具開啟一個瀏覽器視窗（保留空白新分頁即可，不需導覽至任何網址）。

瀏覽器就緒後回報，等待使用者說「可以開始」。所有頁面由使用者自行依序開啟。

---

## ⚠️ 瀏覽器操作限制

> - ✅ **只可導覽到上方表格中明確列出的網址**
> - ❌ **不可點擊任何連結跳轉到其他頁面**
> - ❌ **不可自行切換分頁或分類**（例如從 Recommend 切到 New、從 Slot 切到其他）
> - ❌ **不可自行搜尋或探索其他網址**
>
> 若頁面顯示內容與預期不符，或需要登入 → **立即回報使用者，等待指示**，絕不自行處理。

---

## 你的任務（只做這件事）

**收集本週 5 個競品平台的 Slot 排行資料，整理成 `raw_input.json`，輸出後任務結束。**

你不需要：
- 執行任何腳本或指令
- 修改任何現有檔案
- 分析資料、做觀察、產出報表
- 建議任何改進

---

## 5 個平台

| 代號 | 平台 | 市場 | 收集項目 |
|---|---|---|---|
| PT | PT Gaming | 菲律賓 | Top 20 排行（截圖辨識） |
| BP | BingoPlus | 菲律賓 | Top 20 排行 |
| CP | Casino Plus | 菲律賓 | Top 20 排行（**無廠家資訊，見下方規則**） |
| TCG | Luckyi | 菲律賓 | Top 20 排行 ＋ NEW 分類新遊戲清單（**最多 20 筆**） |
| BAJI | Baji | 孟加拉 | Top 20 排行 ＋ New-Old 排序新遊戲清單（**最多 20 筆**） |

---

## 輸出格式：`raw_input.json`

### 完整結構

```json
{
  "captureDate": "YYYY-MM-DD",
  "platforms": {
    "PT":   { "rankings": [ ...20 筆... ] },
    "BP":   { "rankings": [ ...20 筆... ] },
    "CP":   { "rankings": [ ...20 筆... ] },
    "TCG":  { "rankings": [ ...20 筆... ], "newGames": [ ...最多 20 筆... ] },
    "BAJI": { "rankings": [ ...20 筆... ], "newGames": [ ...最多 20 筆... ] }
  }
}
```

### rankings 每一筆

```json
{
  "name": "Super Ace",
  "vendor": "JILI",
  "rawVendor": "JILI",
  "note": ""
}
```

- `name`：遊戲正式名稱（英文，注意大小寫）
- `vendor`：廠家正規化名稱（見下方廠家命名規則）
- `rawVendor`：平台畫面上的原始顯示文字（直接照抄）
- `note`：有備註才填，沒有留空字串

### newGames 每一筆（TCG / BAJI 限定）

```json
{
  "name": "LUCKY JAGUAR 500",
  "vendor": "JILI",
  "rawVendor": "Jili",
  "gameId": "664",
  "note": ""
}
```

- `gameId`：平台的遊戲 ID 或 URL 代碼（直接照抄）。**必填，不可留空**；看不到 ID 才填空字串並在 note 說明
- 其他欄位同 rankings

---

## 重要規則

### CP 廠家：絕對不猜

CP 平台的排行頁面沒有廠家資訊。處理方式：

1. 先查下方「已知 CP 遊戲廠家對照表」
2. 表中有 → 填入對應廠家
3. 表中沒有 → `vendor` 填 `"(待補)"`，`rawVendor` 留空字串

**已知 CP 遊戲廠家對照表**（持續累積中，不在表中就填待補）：

| 遊戲名稱 | vendor |
|---|---|
| Super Ace | JILI |
| Super Ace 2 / Super Ace II | JILI |
| Super Ace Deluxe | JILI |
| Super Ace Jackpot | JILI |
| Fortune Gems | JILI |
| Fortune Gems 2 | JILI |
| Fortune Gems 500 | JILI |
| Fortune Coins | JILI |
| Fortune Coins 2 | JILI |
| Golden Empire | JILI |
| Boxing King | JILI |
| Money Coming | JILI |
| Jackpot Fishing | JILI |
| Mines | JILI |
| Fortune Garuda 500 | JILI |
| Sugar Bang Bang | FA CHAI |
| Sugar Bang Bang 2 | FA CHAI |
| Sugar Bang Bang Plus | FA CHAI |
| Poker Win | FA CHAI |
| Lucky Fortunes | FA CHAI |
| Super Elements | FA CHAI |
| Sweet Bonanza 1000 | Pragmatic Play |
| Sweet Bonanza 2500 | Pragmatic Play |
| Sweet Bonanza Xmas | Pragmatic Play |
| Sugar Rush 1000 | Pragmatic Play |
| Gates of Olympus Super Scatter | Pragmatic Play |
| Wild Ape #3258 | PG Soft |
| Pinata Wins | PG Soft |
| Wild Bounty Showdown | PG Soft |
| Fortune Gems 3 | JILI |
| Wanted Dead Or A Wild | HACKSAW |
| Cloud Princess | HACKSAW |
| Rise Of Ymir | HACKSAW |
| Mines (2) | HACKSAW |
| Le Pharaoh | HACKSAW |
| Ze Zeus | HACKSAW |
| Mines Dare2Win | HACKSAW |

### 廠家正規化名稱

平台顯示千變萬化，`vendor` 欄位統一用以下正規名稱：

| 正規名稱 | 平台可能的原始顯示 |
|---|---|
| JILI | JILI、Jili、JL、JL JACKPOT |
| PG Soft | PG、Pocket Games Soft、PG SOFT |
| Pragmatic Play | PP、PRAGMATIC PLAY、Pragmatic Play |
| FA CHAI | FC、FaChai、FACHAI、FA CHAI Gaming |
| HACKSAW | HACKSAW、Hacksaw Gaming |
| Habanero | HBN、Habanero |
| JDB | JDB |
| BNG | BNG |
| Red Tiger | REDTIGER、Red Tiger、RED TIGER |
| FunTa Gaming | FTG |
| NetEnt | NETENT、NetEnt |
| OmniPlay | OP |
| Playstar | PLAYSTAR |
| KingMidas | KingMidas、KINGMIDAS |
| YesBingo | YESBINGO |
| YELLOW BAT | YELLOW BAT、YB |
| Lucky365 | LUCKY365 |
| SPADEGAMING | SPADEGAMING |
| RICH88 | RICH88 |
| NOLIMIT CITY | NOLIMIT CITY |
| YGGDRASIL | YGGDRASIL |
| 5G Games | 5G |
| Victory Ark | Victory Ark |
| CREATIVE GAMING | CREATIVE GAMING |
| ACEWIN | ACEWIN |
| WORLD MATCH | WORLD MATCH |
| MICROGAMING | MICROGAMING |
| DRAGOONSOFT | DRAGOONSOFT |
| COMBO | COMBO |
| PLAY'N GO | PLAY'N GO |

> 不在表中的廠家：`vendor` 填平台原始文字（等人工確認），`rawVendor` 也填一樣。

### TCG NEW 遊戲：圖片載入失敗時用 DOM 抓取

若截圖看不清遊戲名稱，請使用者在 DevTools console 執行：

```javascript
Array.from(document.querySelectorAll('img'))
  .filter(img => img.src.includes('TCG_GAME_ICONS'))
  .slice(0, 20)
  .map(img => img.src)
```

URL 中 `{gameCode}` 即為 gameId，廠家從路徑推斷（PP=Pragmatic Play、PG=PG Soft、BNG=BNG、FC=FA CHAI、JL=JILI、PT=Playtech）。看不到名稱時 `name` 填 `(待辨識)`。

**gameId 填寫規則：**
- 字母型 ID（如 `vswaysplnk3p`、`PH-rainbowjackpots0`）→ 直接填，不加前綴
- 純數字 ID → **加廠家 URL 代碼前綴**，避免不同廠家撞號：
  - PG Soft → `PG` + 數字（如 `PG2058347`）
  - BNG → `BNG` + 數字（如 `BNG856`）
  - Victory Ark → `VA` + 數字（如 `VA1008`）
  - 其他純數字廠家 → 用 URL 路徑中的廠家代碼 + 數字

### 只看當前頁面，不自行切換（重申）

你沒有瀏覽器。你只能讀取使用者貼給你的內容。

- ✅ 可以在使用者貼的 HTML / 截圖 / 文字中滾動閱讀
- ❌ **不可自行導覽網址、點連結、切換分頁或分類**
- 收到資料後先確認內容與預期相符（例如：要收 TCG NEW 分類，確認是 NEW 而非 Recommend 或 Popular）
- **內容與預期不符**（分類錯誤、平台不對、資料量明顯異常）→ 立即回報，說明發現什麼，**等使用者確認後再繼續**
- 任何不確定 → 先詢問，不自行判斷

### 無法辨識的遊戲名稱

看得到 gameId 但看不到名稱時：
- `name` 填 `"(待辨識)"`
- `gameId` 照填
- `vendor` / `rawVendor` 如果看得到就填

---

## 流程：逐平台收集，每完成一個即確認

**不分批次，一個平台收完就回報一次。**

收集順序（依使用者開啟頁面的順序為準）：

1. **PT** → 整理完貼出 20 筆清單，等確認
2. **BP** → 整理完貼出 20 筆清單，等確認
3. **CP** → 整理完貼出 20 筆清單（套用 CP 廠家規則），等確認
4. **TCG 排行** → 整理完貼出 20 筆清單，等確認
5. **TCG NEW** → 整理完貼出最多 20 筆清單，等確認
6. **BAJI Recommend** → 整理完貼出 20 筆清單，等確認
7. **BAJI New-Old** → 整理完貼出最多 20 筆清單，等確認
8. **全部確認後** → 輸出完整 `raw_input.json`（代碼區塊）

---

## 輸出要求

- 最後輸出一個 JSON 代碼區塊，內容是完整的 `raw_input.json`
- 每個平台都要有 20 筆 rankings（不夠 20 筆要回報）
- TCG 和 BAJI 要有 newGames（沒有資料則填 `null`），**最多收錄 20 筆，超過只取前 20**
- 輸出後說「raw_input.json 整理完成，請存檔後執行 capture_week.py」，任務結束

---

## 不需要你做的事

- ❌ 不要自行導覽網址或切換分頁（**你沒有瀏覽器**）
- ❌ 不要執行任何 python 指令
- ❌ 不要修改 games.json / vendors.json 等主表
- ❌ 不要分析排名趨勢或提供洞察
- ❌ 不要問「需要我做什麼其他的嗎」
- ❌ 不要更新任何其他文件
