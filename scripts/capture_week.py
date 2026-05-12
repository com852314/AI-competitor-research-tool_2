"""
capture_week.py - 每週抓取資料寫入 JSON-first 架構

用法：
  python capture_week.py <raw_input.json>

輸入 JSON 範例（raw_input.json）：
{
  "captureDate": "2026-05-07",
  "platforms": {
    "PT": {
      "rankings": [
        {"name": "Super Ace", "vendor": "JILI", "rawVendor": "JILI", "note": ""},
        ...共 20 筆
      ]
    },
    "BP": {"rankings": [...]},
    "CP": {"rankings": [...]},
    "TCG": {
      "rankings": [...],
      "newGames": [
        {"name": "FORTUNE GARUDA 500", "vendor": "JILI", "rawVendor": "Jili", "gameId": "696", "note": ""}
      ]
    },
    "BAJI": {
      "rankings": [...],
      "newGames": [...]
    }
  }
}

腳本動作：
  1. 從 data/weekly/ 找最大週次 + 1 作為本週 N
  2. 從 master/games.json 找已知遊戲的主表 ID（用 name + vendor 配對）
  3. 新遊戲（主表沒有）→ 自動加進 games.json、給新主表 ID
  4. 新廠家（vendors.json 沒有）→ 報告給用戶手動補
  5. 對比 W{N-1} 計算 lastWeekRank、rankChange、isNewToTop20
  6. 寫 data/weekly/W{N}_{date}.json
  7. 更新 platforms.json 的 lastCapture
"""
import json
import sys
from pathlib import Path
from datetime import date

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
WEEKLY_DIR = DATA_DIR / "weekly"
MASTER_DIR = DATA_DIR / "master"

PLATFORM_ORDER = ["PT", "BP", "CP", "TCG", "BAJI"]


def load_json(p, default=None):
    if not p.exists():
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_json(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def get_next_week_number():
    max_w = 0
    for f in WEEKLY_DIR.glob("W*.json"):
        try:
            data = load_json(f, {})
            if isinstance(data.get("week"), int):
                max_w = max(max_w, data["week"])
        except Exception:
            pass
    return max_w + 1


def find_master_id(games_data, name, vendor):
    """name+vendor 都匹配（不分大小寫）→ 回傳 masterId"""
    if not games_data:
        return None
    name_lc = (name or "").lower()
    vendor_lc = (vendor or "").lower()
    for g in games_data.get("games", []):
        if (g.get("normalizedName") or "").lower() == name_lc and \
           (g.get("normalizedVendor") or "").lower() == vendor_lc:
            return g["masterId"]
    return None


def get_max_master_id(games_data):
    if not games_data or not games_data.get("games"):
        return 0
    return max(g["masterId"] for g in games_data["games"])


def load_prev_week_snapshot(current_week):
    prev_week = current_week - 1
    if prev_week <= 0:
        return None
    for f in WEEKLY_DIR.glob(f"W{prev_week}_*.json"):
        return load_json(f)
    return None


def build_prev_rank_lookup(prev_snapshot, plat_code):
    """{ (name_lc, vendor_lc): rank }"""
    lookup = {}
    if not prev_snapshot:
        return lookup
    rankings = prev_snapshot.get("platforms", {}).get(plat_code, {}).get("rankings", [])
    for r in rankings:
        key = ((r.get("name") or "").lower(), (r.get("vendor") or "").lower())
        lookup[key] = r["rank"]
    return lookup


def main():
    if len(sys.argv) < 2:
        print("用法: python capture_week.py <raw_input.json>")
        print("\n用 --help 看詳細格式")
        sys.exit(1)

    if sys.argv[1] in ("--help", "-h"):
        print(__doc__)
        sys.exit(0)

    raw_path = Path(sys.argv[1])
    if not raw_path.exists():
        print(f"找不到輸入檔: {raw_path}")
        sys.exit(1)

    raw = load_json(raw_path)
    if not raw or "platforms" not in raw:
        print("輸入 JSON 必須含 platforms 欄位")
        sys.exit(1)

    # 載入 master
    games = load_json(MASTER_DIR / "games.json", {"games": []})
    vendors = load_json(MASTER_DIR / "vendors.json", {"vendors": []})
    platforms = load_json(MASTER_DIR / "platforms.json", {"platforms": []})

    # 算下週次
    week_no = get_next_week_number()
    capture_date = raw.get("captureDate") or date.today().isoformat()
    print(f"\n=== 建立 W{week_no} ({capture_date}) ===\n")

    prev_snapshot = load_prev_week_snapshot(week_no)
    if prev_snapshot:
        print(f"找到上週快照 W{prev_snapshot.get('week')}，將計算排名變化")
    else:
        print("沒有上週快照（第一週），所有遊戲都不算「新進榜」")

    market_map = {p["code"]: p["market"] for p in platforms.get("platforms", [])}
    known_vendor_names = {v["normalizedName"] for v in vendors.get("vendors", [])}

    output_platforms = {}
    next_master_id = get_max_master_id(games) + 1
    new_games_added = []
    new_vendors_found = set()
    pending_vendors = 0  # 待補廠家統計

    for code in PLATFORM_ORDER:
        plat_raw = raw["platforms"].get(code)
        if not plat_raw:
            print(f"  ⚠ {code} 無資料、跳過")
            continue

        prev_lookup = build_prev_rank_lookup(prev_snapshot, code)
        has_prev = bool(prev_lookup)

        rankings = []
        for i, r in enumerate(plat_raw.get("rankings", []), start=1):
            name = (r.get("name") or "").strip()
            vendor = (r.get("vendor") or "").strip()
            raw_vendor = (r.get("rawVendor") or vendor).strip()
            note = r.get("note", "")

            # 查/建主表
            mid = find_master_id(games, name, vendor)
            should_add_master = (
                mid is None
                and name
                and vendor
                and "(待補)" not in vendor
                and "待辨識" not in name
            )
            if should_add_master:
                mid = next_master_id
                next_master_id += 1
                games["games"].append({
                    "masterId": mid,
                    "normalizedName": name,
                    "normalizedVendor": vendor,
                    "platformAliases": {c: (name if c == code else None) for c in PLATFORM_ORDER},
                    "firstSeen": capture_date,
                    "note": f"W{week_no} 新發現於 {code}"
                })
                new_games_added.append(f"  + ID {mid:3d}: {name} ({vendor}) @ {code}")

            # 廠家追蹤
            if vendor and "(待補)" in vendor:
                pending_vendors += 1
            elif vendor and vendor not in known_vendor_names:
                new_vendors_found.add(vendor)

            # 排名變化
            key = (name.lower(), vendor.lower())
            last_rank = prev_lookup.get(key)
            rank_change = (last_rank - i) if last_rank is not None else None
            is_new = (last_rank is None) and has_prev

            rankings.append({
                "rank": i,
                "name": name,
                "vendor": vendor,
                "rawVendor": raw_vendor,
                "masterId": mid,
                "isNewToTop20": is_new,
                "lastWeekRank": last_rank,
                "rankChange": rank_change,
                "note": note
            })

        # newGames（TCG / BAJI）
        new_games_section = None
        if "newGames" in plat_raw and plat_raw["newGames"] is not None:
            new_games_section = []
            for i, g in enumerate(plat_raw["newGames"], start=1):
                name = (g.get("name") or "").strip()
                vendor = (g.get("vendor") or "").strip()
                new_games_section.append({
                    "order": i,
                    "name": name,
                    "vendor": vendor,
                    "rawVendor": (g.get("rawVendor") or vendor).strip(),
                    "gameId": (g.get("gameId") or "").strip(),
                    "isFirstSeen": True,
                    "note": g.get("note", "")
                })

        output_platforms[code] = {
            "market": market_map.get(code, "菲律賓"),
            "rankings": rankings,
            "newGames": new_games_section
        }
        print(f"  ✓ {code:5} {len(rankings):2d} 筆 Top 20" +
              (f" + {len(new_games_section)} 新遊戲" if new_games_section else ""))

    # === 寫快照 ===
    snapshot = {
        "week": week_no,
        "captureDate": capture_date,
        "platforms": output_platforms
    }
    out_path = WEEKLY_DIR / f"W{week_no}_{capture_date}.json"
    save_json(out_path, snapshot)
    print(f"\n✓ 寫入 {out_path.relative_to(PROJECT_DIR)}")

    # === 更新 platforms.json lastCapture ===
    for p in platforms["platforms"]:
        if p["code"] in raw["platforms"]:
            p["lastCapture"] = capture_date
            p["status"] = "active"
    save_json(MASTER_DIR / "platforms.json", platforms)

    # === 更新 games.json（如有新增）===
    if new_games_added:
        save_json(MASTER_DIR / "games.json", games)
        print(f"\n✓ 主表新增 {len(new_games_added)} 款：")
        for line in new_games_added[:15]:
            print(line)
        if len(new_games_added) > 15:
            print(f"  ... 還有 {len(new_games_added) - 15} 款（完整列表在 games.json）")

    # === 報告新廠家 ===
    if new_vendors_found:
        print(f"\n⚠ 發現 {len(new_vendors_found)} 個新廠家（需手動補進 vendors.json）：")
        for v in sorted(new_vendors_found):
            print(f"   - {v}")

    if pending_vendors:
        print(f"\nℹ {pending_vendors} 個排名項目的廠家為「(待補)」，請後續用網路查證或人工確認後補回")

    # === 跨平台統計 ===
    cross_count = sum(
        1 for g in games["games"]
        if sum(1 for v in (g.get("platformAliases") or {}).values() if v) >= 3
    )
    print(f"\n📊 主表現況：{len(games['games'])} 款遊戲、{cross_count} 款 ≥3 平台")
    print(f"\n=== W{week_no} 抓取完成 ===")


if __name__ == "__main__":
    main()
