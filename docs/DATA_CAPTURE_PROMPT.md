# 競品資料收集任務說明

> 把這整份文件貼到新的 cowork 對話開頭，讓 AI 理解任務範圍。

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

- `gameId`：平台的遊戲 ID 或 URL 代碼（直接照抄）
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
| Red Tiger | REDTIGER、Red Tiger |
| FunTa Gaming | FTG |
| NetEnt | NETENT、NetEnt |
| OmniPlay | OP |
| Playstar | PLAYSTAR |
| KingMidas | KingMidas |
| YesBingo | YESBINGO |
| Lucky365 | LUCKY365 |

> 不在表中的廠家：`vendor` 填平台原始文字（等人工確認），`rawVendor` 也填一樣。

### 無法辨識的遊戲名稱

看得到 gameId 但看不到名稱時：
- `name` 填 `"(待辨識)"`
- `gameId` 照填
- `vendor` / `rawVendor` 如果看得到就填

---

## 流程建議（分兩批提供資料）

**第一批（PT + BP + CP）**
- 我會貼 PT 截圖 / HTML，你先辨識整理
- 再貼 BP HTML，整理
- 再貼 CP HTML，整理（記得套用 CP 廠家規則）

**第二批（TCG + BAJI）**
- 貼 TCG 排行 + NEW 分類 HTML
- 貼 BAJI 排行 + New-Old HTML

**全部資料確認後，輸出一份完整的 `raw_input.json`（代碼區塊）。**

---

## 輸出要求

- 最後輸出一個 JSON 代碼區塊，內容是完整的 `raw_input.json`
- 每個平台都要有 20 筆 rankings（不夠 20 筆要回報）
- TCG 和 BAJI 要有 newGames（沒有資料則填 `null`），**最多收錄 20 筆，超過只取前 20**
- 輸出後說「raw_input.json 整理完成，請存檔後執行 capture_week.py」，任務結束

---

## 不需要你做的事

- ❌ 不要執行任何 python 指令
- ❌ 不要修改 games.json / vendors.json 等主表
- ❌ 不要分析排名趨勢或提供洞察
- ❌ 不要問「需要我做什麼其他的嗎」
- ❌ 不要更新任何其他文件
