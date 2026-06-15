"""
合併 YELLOW BAT 回 YesBingo（確認為同一廠家）
- vendors.json：移除 YELLOW BAT entry，YesBingo 加入 PT/BAJI 顯示別名
- games.json：YELLOW BAT 遊戲改回 YesBingo
- W6 weekly + raw_input：vendor 改回 YesBingo，同步補上 gameId
"""
import json
from pathlib import Path

ROOT = Path(r"D:\Claude Project\競品調研(排名)")

g_data  = json.loads((ROOT / "data/master/games.json").read_text(encoding="utf-8"))
v_data  = json.loads((ROOT / "data/master/vendors.json").read_text(encoding="utf-8"))
w6_path = ROOT / "data/weekly/W6_2026-06-15.json"
w6_data = json.loads(w6_path.read_text(encoding="utf-8"))
raw_data = json.loads((ROOT / "W6_raw_input.json").read_text(encoding="utf-8"))

# ── 1. vendors.json：移除 YELLOW BAT，YesBingo 補齊顯示名稱
v_data["vendors"] = [v for v in v_data["vendors"] if v["normalizedName"] != "YELLOW BAT"]
for v in v_data["vendors"]:
    if v["normalizedName"] == "YesBingo":
        v["displayPerPlatform"]["PT"]   = {"urlCode": "YB", "display": "YB"}
        v["displayPerPlatform"]["BAJI"] = {"urlCode": "YesBingo", "display": "YELLOW BAT"}
        v["note"] = "PT顯示YB、BAJI顯示YELLOW BAT，gameId前綴為YesBingo-SLOT-"
        print("YesBingo vendor 更新完成")

# ── 2. games.json：YELLOW BAT → YesBingo
updated = []
for g in g_data["games"]:
    if g.get("normalizedVendor") == "YELLOW BAT":
        g["normalizedVendor"] = "YesBingo"
        updated.append(f'ID {g["masterId"]}: {g["normalizedName"]}')
print(f"games.json 更新 {len(updated)} 筆: {updated}")

# ── 3. W6 weekly：vendor 改回 YesBingo + 從 raw_input 同步 gameId
# 建立 raw newGames 的 gameId 查找表（by name+vendor）
raw_new_lookup = {}
for plat, pdata in raw_data.get("platforms", {}).items():
    for r in (pdata.get("newGames") or []):
        key = (r["name"], plat)
        raw_new_lookup[key] = r.get("gameId", "")

fixed_vendor = 0
synced_gid   = 0
for plat, pdata in w6_data.get("platforms", {}).items():
    for r in pdata.get("rankings", []):
        if r.get("vendor") == "YELLOW BAT":
            r["vendor"] = "YesBingo"; fixed_vendor += 1
    for r in (pdata.get("newGames") or []):
        if r.get("vendor") == "YELLOW BAT":
            r["vendor"] = "YesBingo"; fixed_vendor += 1
        # 同步 gameId
        key = (r["name"], plat)
        if key in raw_new_lookup and not r.get("gameId"):
            r["gameId"] = raw_new_lookup[key]; synced_gid += 1

print(f"W6 weekly：vendor 修正 {fixed_vendor} 筆，gameId 同步 {synced_gid} 筆")

# ── 4. W6 raw_input：vendor 改回 YesBingo
fixed_raw = 0
for plat, pdata in raw_data.get("platforms", {}).items():
    for r in pdata.get("rankings", []):
        if r.get("vendor") == "YELLOW BAT":
            r["vendor"] = "YesBingo"; fixed_raw += 1
    for r in (pdata.get("newGames") or []):
        if r.get("vendor") == "YELLOW BAT":
            r["vendor"] = "YesBingo"; fixed_raw += 1
print(f"W6 raw_input：vendor 修正 {fixed_raw} 筆")

# ── 儲存
(ROOT / "data/master/vendors.json").write_text(
    json.dumps(v_data, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "data/master/games.json").write_text(
    json.dumps(g_data, ensure_ascii=False, indent=2), encoding="utf-8")
w6_path.write_text(json.dumps(w6_data, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "W6_raw_input.json").write_text(
    json.dumps(raw_data, ensure_ascii=False, indent=2), encoding="utf-8")

print("\n全部儲存完成")
