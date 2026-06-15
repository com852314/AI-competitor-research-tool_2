"""
修正 YELLOW BAT 與 YesBingo 分離：
- YesBingo 是獨立廠家（YESBINGO 顯示）
- YELLOW BAT 是獨立廠家（YB 在 PT、YELLOW BAT 在 BAJI）
- 所有目前誤標為 YesBingo 但實際是 YELLOW BAT 的遊戲需更新
"""
import json
from pathlib import Path

ROOT = Path(r"D:\Claude Project\競品調研(排名)")

g_data = json.loads((ROOT / "data/master/games.json").read_text(encoding="utf-8"))
v_data = json.loads((ROOT / "data/master/vendors.json").read_text(encoding="utf-8"))
w6_path = ROOT / "data/weekly/W6_2026-06-15.json"
w6_data = json.loads(w6_path.read_text(encoding="utf-8"))
raw_path = ROOT / "W6_raw_input.json"
raw_data = json.loads(raw_path.read_text(encoding="utf-8"))

# 哪些遊戲是 YELLOW BAT（不是 YesBingo）
# 判斷依據：rawVendor 為 YELLOW BAT 或 YB
YELLOWBAT_GAMES = {"Diva's Ace", "Happy Dragon", "Super Tiger"}

# ── 1. vendors.json：YesBingo 移除 YELLOW BAT 別名，新增 YELLOW BAT entry
for vv in v_data["vendors"]:
    if vv["normalizedName"] == "YesBingo":
        vv["displayPerPlatform"]["PT"] = None  # YesBingo 不在 PT
        vv["note"] = ""
        print("YesBingo vendor 清理完成")

# 新增 YELLOW BAT（若不存在）
if not any(vv["normalizedName"] == "YELLOW BAT" for vv in v_data["vendors"]):
    v_data["vendors"].append({
        "normalizedName": "YELLOW BAT",
        "displayPerPlatform": {
            "PT":   {"urlCode": "YB", "display": "YB"},
            "BP":   None,
            "CP":   None,
            "TCG":  None,
            "BAJI": {"urlCode": "YELLOWBAT", "display": "YELLOW BAT"}
        },
        "note": "W6 確認：PT 顯示 YB，BAJI 顯示 YELLOW BAT"
    })
    print("新增 YELLOW BAT vendor")

# ── 2. games.json：把 YELLOW BAT 遊戲的 normalizedVendor 改過來
updated_games = []
for x in g_data["games"]:
    if x["normalizedName"] in YELLOWBAT_GAMES and x.get("normalizedVendor") == "YesBingo":
        x["normalizedVendor"] = "YELLOW BAT"
        updated_games.append(f'ID {x["masterId"]}: {x["normalizedName"]}')
print(f"games.json 更新 {len(updated_games)} 筆:")
for s in updated_games:
    print(f"  {s}")

# ── 3. W6 weekly：修正 rankings/newGames 裡的 vendor
def fix_vendor(entry):
    if entry.get("rawVendor") in ("YELLOW BAT", "YB") and entry.get("vendor") == "YesBingo":
        entry["vendor"] = "YELLOW BAT"
        return True
    return False

fixed_w6 = 0
for plat, pdata in w6_data.get("platforms", {}).items():
    for r in pdata.get("rankings", []):
        if fix_vendor(r):
            fixed_w6 += 1
    for r in (pdata.get("newGames") or []):
        if fix_vendor(r):
            fixed_w6 += 1
print(f"W6 weekly 修正 {fixed_w6} 筆")

# ── 4. W6 raw_input：同上
fixed_raw = 0
for plat, pdata in raw_data.get("platforms", {}).items():
    for r in pdata.get("rankings", []):
        if fix_vendor(r):
            fixed_raw += 1
    for r in (pdata.get("newGames") or []):
        if fix_vendor(r):
            fixed_raw += 1
print(f"W6 raw_input 修正 {fixed_raw} 筆")

# ── 儲存
(ROOT / "data/master/vendors.json").write_text(
    json.dumps(v_data, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "data/master/games.json").write_text(
    json.dumps(g_data, ensure_ascii=False, indent=2), encoding="utf-8")
w6_path.write_text(json.dumps(w6_data, ensure_ascii=False, indent=2), encoding="utf-8")
raw_path.write_text(json.dumps(raw_data, ensure_ascii=False, indent=2), encoding="utf-8")

print("\n全部儲存完成")
