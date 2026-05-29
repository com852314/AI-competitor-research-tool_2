#!/usr/bin/env python3
# 修正 renderNewGamesTrend：gameId 為空時改用遊戲名稱做比對 key

HTML_PATH = r"D:\Claude Project\競品調研(排名)\index.html"

with open(HTML_PATH, encoding='utf-8') as f:
    html = f.read()

OLD = (
    "    const prevSet = new Set(prevGames.map(g => g.gameId).filter(Boolean));\n"
    "    const curSet = new Set(curGames.map(g => g.gameId).filter(Boolean));\n"
    "    const prevNames = new Map(prevGames.filter(g => g.gameId).map(g => [g.gameId, g.name]));\n"
    "    const curNames = new Map(curGames.filter(g => g.gameId).map(g => [g.gameId, g.name]));"
)

NEW = (
    "    // gameId 優先；若為空則用名稱小寫作為比對 key\n"
    "    const gameKey = g => (g.gameId && g.gameId.trim()) || (g.name || '').toLowerCase().trim();\n"
    "    const prevSet = new Set(prevGames.map(gameKey).filter(Boolean));\n"
    "    const curSet = new Set(curGames.map(gameKey).filter(Boolean));\n"
    "    const prevNames = new Map(prevGames.map(g => [gameKey(g), g.name]).filter(([k]) => k));\n"
    "    const curNames = new Map(curGames.map(g => [gameKey(g), g.name]).filter(([k]) => k));"
)

assert OLD in html, '[FAIL] sentinel not found'
html = html.replace(OLD, NEW, 1)
print('OK renderNewGamesTrend 比對邏輯更新（gameId 空時改用名稱）')

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)
print('完成')
