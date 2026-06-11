"""
SlotCatalog 批次爬蟲
- 讀 data/master/games.json（175 款）
- 逐一抓取屬性，存入 data/master/attributes.json
- 支援中斷續跑：已有結果的 masterId 直接跳過
- 遇到 not_found 時嘗試備用 URL 格式
用法：python scripts/scrape_slotcatalog_batch.py
      python scripts/scrape_slotcatalog_batch.py --force  # 重新抓所有（含已有的）
"""

import re
import sys
import time
import json
import argparse
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent.parent
GAMES_JSON   = ROOT / "data" / "master" / "games.json"
ATTRS_JSON   = ROOT / "data" / "master" / "attributes.json"
DELAY        = 1.5   # 每次請求間隔（秒）
RETRY_DELAY  = 10    # 429/503 後等待（秒）
MAX_RETRIES  = 2

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


# ── URL slug 生成（多種格式輪流嘗試）────────────────────────────
def slugs_for(name: str, vendor: str):
    """回傳要嘗試的 slug 清單（由高到低可能性）"""
    def base(s):
        s = re.sub(r"[^\w\s-]", "", s)
        return re.sub(r"\s+", "-", s.strip())

    candidates = [base(name)]

    # 數字詞替換：1000→1000 / 100→100 等（通常 slotcatalog 保留數字）
    # 嘗試加廠家前綴
    if vendor:
        v_slug = base(vendor)
        candidates.append(f"{base(name)}-{v_slug}")

    # 移除尾端數字（Fortune Gems 3 → Fortune Gems）
    stripped = re.sub(r'\s+\d+$', '', name).strip()
    if stripped != name:
        candidates.append(base(stripped))

    # 去掉括弧部分（如 "Super Ace (Deluxe)"）
    no_paren = re.sub(r'\s*\(.*?\)', '', name).strip()
    if no_paren != name:
        candidates.append(base(no_paren))

    # 全小寫
    candidates.append(base(name).lower())

    return list(dict.fromkeys(candidates))  # 去重保序


# ── 解析單頁屬性 ────────────────────────────────────────────────
def parse_game_page(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    data = {"slotcatalogUrl": url}

    for th in soup.find_all("th", class_="propLeft"):
        label = th.get_text(strip=True).rstrip(":").replace("\U0001f517", "").strip()
        td = th.find_next_sibling("td", class_="propRight")
        if not td:
            continue
        links = [a.get_text(strip=True) for a in td.find_all("a")]

        if label == "RTP":
            m = re.search(r"[\d.]+", ", ".join(links) or td.get_text())
            data["rtp"] = float(m.group()) if m else None
        elif label == "Variance":
            data["volatility"] = (links[0] if links else td.get_text(strip=True)) or None
        elif label == "Betways":
            m = re.search(r"[\d,]+", td.get_text())
            data["ways"] = int(m.group().replace(",", "")) if m else None
            data.setdefault("lines", None)
        elif label == "Lines":
            m = re.search(r"[\d,]+", td.get_text())
            data["lines"] = int(m.group().replace(",", "")) if m else None
            data.setdefault("ways", None)
        elif label == "Layout":
            data["layout"] = (links[0] if links else td.get_text(strip=True)) or None
        elif label == "Max Win":
            m = re.search(r"[\d,]+\.?\d*", td.get_text())
            data["maxWin"] = float(m.group().replace(",", "")) if m else None
        elif label == "Release Date":
            raw = td.get_text(" ", strip=True)
            m = re.search(r"\d{4}-\d{2}-\d{2}", raw)
            data["releaseDate"] = m.group() if m else None

    for td in soup.find_all("td", class_="propRight", colspan="2"):
        text = td.get_text(" ", strip=True)
        links = [a.get_text(strip=True) for a in td.find_all("a")]
        if text.startswith("Theme:"):
            data["theme"] = links or None
        elif text.startswith("Features:"):
            data["features"] = links or None

    return data


# ── 單款抓取（含 retry）────────────────────────────────────────
def fetch_one(name: str, vendor: str) -> dict:
    for slug in slugs_for(name, vendor):
        url = f"https://slotcatalog.com/en/slots/{slug}"
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = requests.get(url, headers=HEADERS, timeout=12)
                if resp.status_code == 200 and "Variance" in resp.text:
                    result = parse_game_page(resp.text, url)
                    result["status"] = "found"
                    return result
                elif resp.status_code in (429, 503):
                    print(f"    [{resp.status_code}] 限速，等 {RETRY_DELAY}s ...")
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    break  # 404 等，換下一個 slug
            except requests.RequestException as e:
                if attempt < MAX_RETRIES:
                    time.sleep(3)
                else:
                    return {"status": "error", "error": str(e)}

    return {"status": "not_found", "triedSlugs": slugs_for(name, vendor)}


# ── 主流程 ───────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="重新抓所有（忽略已有結果）")
    args = parser.parse_args()

    games = json.loads(GAMES_JSON.read_text(encoding="utf-8"))["games"]

    # 載入既有結果
    if ATTRS_JSON.exists() and not args.force:
        existing = json.loads(ATTRS_JSON.read_text(encoding="utf-8"))
    else:
        existing = {}

    done_ids = set(int(k) for k in existing.keys()) if existing else set()
    total = len(games)
    new_count = 0

    print(f"共 {total} 款遊戲，已有 {len(done_ids)} 筆，待抓 {total - len(done_ids)} 筆\n")

    for i, game in enumerate(games, 1):
        mid  = game["masterId"]
        name = game["normalizedName"]
        vendor = game.get("normalizedVendor", "")

        if mid in done_ids:
            print(f"[{i:3}/{total}] ✓ skip  {name}")
            continue

        print(f"[{i:3}/{total}] → {name} ({vendor}) ...", end=" ", flush=True)
        result = fetch_one(name, vendor)
        existing[str(mid)] = {
            "masterId": mid,
            "name": name,
            "vendor": vendor,
            **result
        }
        new_count += 1

        status = result.get("status")
        if status == "found":
            vol = result.get("volatility", "?")
            rtp = result.get("rtp", "?")
            print(f"✓  vol={vol}  rtp={rtp}")
        else:
            print(f"✗  {status}")

        # 每抓 10 筆存一次（防中斷遺失）
        if new_count % 10 == 0:
            ATTRS_JSON.write_text(
                json.dumps(existing, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            print(f"  [中間存檔 {len(existing)} 筆]")

        time.sleep(DELAY)

    # 最終存檔
    ATTRS_JSON.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    found = sum(1 for v in existing.values() if v.get("status") == "found")
    not_found = sum(1 for v in existing.values() if v.get("status") == "not_found")
    errors = sum(1 for v in existing.values() if v.get("status") == "error")

    print(f"\n── 完成 ──")
    print(f"  found     : {found}")
    print(f"  not_found : {not_found}")
    print(f"  error     : {errors}")
    print(f"  輸出 → {ATTRS_JSON}")


if __name__ == "__main__":
    main()
