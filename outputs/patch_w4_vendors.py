import json
from pathlib import Path

ROOT = Path(r"D:\Claude Project\競品調研(排名)")
vendors_path = ROOT / "data/master/vendors.json"
games_path   = ROOT / "data/master/games.json"
w4_path      = ROOT / "data/weekly/W4_2026-05-28.json"

vendors = json.loads(vendors_path.read_text(encoding="utf-8"))
games   = json.loads(games_path.read_text(encoding="utf-8"))
w4      = json.loads(w4_path.read_text(encoding="utf-8"))

# 1. 新增 Spark Game 進 vendors.json
vendors["vendors"].append({
    "normalizedName": "Spark Game",
    "displayPerPlatform": {
        "PT": "Spark Game", "BP": None, "CP": None, "TCG": None, "BAJI": None
    },
    "note": "W4 新發現於 PT"
})
print("OK vendors.json 新增 Spark Game")

# 2. W4 CP #18 廠家補為 HACKSAW
cp_r = next(r for r in w4["platforms"]["CP"]["rankings"] if r["rank"] == 18)
cp_r["vendor"] = "HACKSAW"
cp_r["rawVendor"] = "HACKSAW"

# 3. games.json 裡的 Mines Dare2Win 補廠家
game = next((g for g in games["games"] if g["normalizedName"] == "Mines Dare2Win"), None)
if game:
    mid = game["masterId"]
    game["normalizedVendor"] = "HACKSAW"
    cp_r["masterId"] = mid
    print("OK games.json Mines Dare2Win -> HACKSAW (ID " + str(mid) + ")")
else:
    new_id = max(g["masterId"] for g in games["games"]) + 1
    games["games"].append({
        "masterId": new_id,
        "normalizedName": "Mines Dare2Win",
        "normalizedVendor": "HACKSAW",
        "platformAliases": {"PT": None, "BP": None, "CP": "Mines Dare2Win", "TCG": None, "BAJI": None},
        "firstSeen": "2026-05-28",
        "note": "W4 新發現於 CP"
    })
    cp_r["masterId"] = new_id
    print("OK games.json 新增 Mines Dare2Win / HACKSAW (ID " + str(new_id) + ")")

vendors_path.write_text(json.dumps(vendors, ensure_ascii=False, indent=2), encoding="utf-8")
games_path.write_text(json.dumps(games, ensure_ascii=False, indent=2), encoding="utf-8")
w4_path.write_text(json.dumps(w4, ensure_ascii=False, indent=2), encoding="utf-8")
print("完成")
