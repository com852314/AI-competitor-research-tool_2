#!/usr/bin/env python3
"""把 raw_input.json 的 TCG 資料重新套入 W3，重新計算排名變化。"""
import json
from pathlib import Path

ROOT = Path(r"D:\Claude Project\競品調研(排名)")
RAW_PATH   = ROOT / "raw_input.json"
W2_PATH    = ROOT / "data/weekly/W2_2026-05-11.json"
W3_PATH    = ROOT / "data/weekly/W3_2026-05-22.json"
GAMES_PATH = ROOT / "data/master/games.json"

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def save(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

raw   = load(RAW_PATH)
w2    = load(W2_PATH)
w3    = load(W3_PATH)
games = load(GAMES_PATH)

# ── 主表查詢 ──────────────────────────────────
def find_master(name, vendor):
    for g in games["games"]:
        if g["normalizedName"].lower() == name.lower() and \
           g["normalizedVendor"].lower() == vendor.lower():
            return g["masterId"]
    return None

def get_next_id():
    return max(g["masterId"] for g in games["games"]) + 1

# ── W2 TCG 排名 lookup ────────────────────────
prev_lookup = {}
for r in w2["platforms"]["TCG"]["rankings"]:
    key = (r["name"].lower(), r["vendor"].lower())
    prev_lookup[key] = r["rank"]

# ── 重建 TCG rankings ─────────────────────────
new_rankings = []
next_id = get_next_id()
new_games_added = []

for i, r in enumerate(raw["platforms"]["TCG"]["rankings"], start=1):
    name      = r.get("name", "").strip()
    vendor    = r.get("vendor", "").strip()
    raw_vend  = r.get("rawVendor", vendor).strip()
    note      = r.get("note", "")

    mid = find_master(name, vendor)
    if mid is None and name and vendor and "(待補)" not in vendor and "待辨識" not in name:
        mid = next_id
        next_id += 1
        games["games"].append({
            "masterId": mid,
            "normalizedName": name,
            "normalizedVendor": vendor,
            "platformAliases": {"PT":None,"BP":None,"CP":None,"TCG":name,"BAJI":None},
            "firstSeen": "2026-05-22",
            "note": "W3 TCG patch"
        })
        new_games_added.append(f"  + ID {mid}: {name} ({vendor})")

    key = (name.lower(), vendor.lower())
    last_rank   = prev_lookup.get(key)
    rank_change = (last_rank - i) if last_rank is not None else None
    is_new      = last_rank is None

    new_rankings.append({
        "rank": i,
        "name": name,
        "vendor": vendor,
        "rawVendor": raw_vend,
        "masterId": mid,
        "isNewToTop20": is_new,
        "lastWeekRank": last_rank,
        "rankChange": rank_change,
        "note": note
    })

# ── 重建 TCG newGames ─────────────────────────
new_ng = []
for i, g in enumerate(raw["platforms"]["TCG"].get("newGames") or [], start=1):
    new_ng.append({
        "order":      i,
        "name":       g.get("name","").strip(),
        "vendor":     g.get("vendor","").strip(),
        "rawVendor":  g.get("rawVendor", g.get("vendor","")).strip(),
        "gameId":     g.get("gameId","").strip(),
        "isFirstSeen": True,
        "note":       g.get("note","")
    })

# ── 寫回 W3 ──────────────────────────────────
w3["platforms"]["TCG"]["rankings"] = new_rankings
w3["platforms"]["TCG"]["newGames"] = new_ng

save(W3_PATH, w3)
save(GAMES_PATH, games)

print(f"✅ W3 TCG rankings 更新：{len(new_rankings)} 筆")
print(f"✅ W3 TCG newGames 更新：{len(new_ng)} 筆")
if new_games_added:
    print(f"✅ 主表新增 {len(new_games_added)} 款：")
    for line in new_games_added:
        print(line)
else:
    print("主表無新增")
print("完成")
