"""
主表瀏覽升級 v4：
- 所有主要欄位可點擊排序（上市日期、RTP、波動度、名稱、廠家、跨台數、首見）
- 點同一欄切換升降序；點新欄重設方向（數字欄預設降序、文字欄預設升序）
- 排序在篩選之後，篩選結果上直接排序
"""
from pathlib import Path

INDEX_PATH = Path(r"D:\Claude Project\競品調研(排名)\index.html")
html = INDEX_PATH.read_text(encoding="utf-8")

# ── 1. JS state：加排序狀態 ──────────────────────────────────────
OLD_STATE = """let MASTER_SEARCH      = '';
let MASTER_PLAT_FILTER = new Set(['PT','BP','CP','TCG','BAJI']);
let MASTER_VOL         = '';
let MASTER_ATTR_KW     = '';
let MASTER_DATE_PRESET = '';
let MASTER_DATE_FROM   = '';
let MASTER_DATE_TO     = '';"""

NEW_STATE = """let MASTER_SEARCH      = '';
let MASTER_PLAT_FILTER = new Set(['PT','BP','CP','TCG','BAJI']);
let MASTER_VOL         = '';
let MASTER_ATTR_KW     = '';
let MASTER_DATE_PRESET = '';
let MASTER_DATE_FROM   = '';
let MASTER_DATE_TO     = '';
let MASTER_SORT_COL    = '';   // '' = 預設排序（跨台降序）
let MASTER_SORT_DIR    = 'asc';"""

assert OLD_STATE in html
html = html.replace(OLD_STATE, NEW_STATE, 1)

# ── 2. 在 renderMasterTable 之前插入排序相關 helpers ────────────
INSERT_BEFORE = "function renderAttrList(arr, limit) {"

SORT_HELPERS = r"""// ── 主表排序 helpers
const VOL_ORDER = {'Low':0,'Low-Med':1,'Med':2,'Med-High':3,'High':4,'N/A':5,'Adjusted':6};

function setSortCol(col) {
  if (MASTER_SORT_COL === col) {
    MASTER_SORT_DIR = MASTER_SORT_DIR === 'asc' ? 'desc' : 'asc';
  } else {
    MASTER_SORT_COL = col;
    // 數字欄/日期欄預設降序（最大/最新在前）；文字欄預設升序
    MASTER_SORT_DIR = ['count','rtp','releaseDate','firstSeen'].includes(col) ? 'desc' : 'asc';
  }
  renderMasterTable();
}

function sortTh(col, label, align) {
  const active = MASTER_SORT_COL === col;
  const ind = active ? (MASTER_SORT_DIR === 'asc' ? ' ▲' : ' ▼') : ' <span class="opacity-30">⇅</span>';
  const cls = (align === 'center' ? 'text-center' : 'text-left') +
    ' px-2 py-2 text-xs font-medium cursor-pointer select-none whitespace-nowrap ' +
    (active ? 'text-blue-600 hover:text-blue-700' : 'text-gray-500 hover:text-blue-500');
  return `<th class="${cls}" onclick="setSortCol('${col}')">${label}${ind}</th>`;
}

function masterCompareRows(a, b) {
  const col = MASTER_SORT_COL;
  const d = MASTER_SORT_DIR === 'asc' ? 1 : -1;
  let av, bv;
  switch (col) {
    case 'name':
      av = (a.normalizedName || '').toLowerCase();
      bv = (b.normalizedName || '').toLowerCase();
      return av < bv ? -d : av > bv ? d : 0;
    case 'vendor':
      av = (a.normalizedVendor || '').toLowerCase();
      bv = (b.normalizedVendor || '').toLowerCase();
      return av < bv ? -d : av > bv ? d : 0;
    case 'count':
      return (a._count - b._count) * d;
    case 'volatility':
      av = VOL_ORDER[(a._attr && a._attr.volatility) ?? ''] ?? 99;
      bv = VOL_ORDER[(b._attr && b._attr.volatility) ?? ''] ?? 99;
      return (av - bv) * d;
    case 'rtp':
      av = (a._attr && a._attr.rtp > 10) ? a._attr.rtp : -1;
      bv = (b._attr && b._attr.rtp > 10) ? b._attr.rtp : -1;
      return (av - bv) * d;
    case 'releaseDate':
      av = (a._attr && a._attr.releaseDate) || '';
      bv = (b._attr && b._attr.releaseDate) || '';
      return av < bv ? -d : av > bv ? d : 0;
    case 'firstSeen':
      av = a.firstSeen || '';
      bv = b.firstSeen || '';
      return av < bv ? -d : av > bv ? d : 0;
    default:
      return b._count - a._count || a.masterId - b.masterId;
  }
}

"""

assert INSERT_BEFORE in html
html = html.replace(INSERT_BEFORE, SORT_HELPERS + INSERT_BEFORE, 1)

# ── 3. 更新 filtered.sort 呼叫 ───────────────────────────────────
OLD_SORT = "  filtered.sort((a, b) => b._count - a._count || a.masterId - b.masterId);"
NEW_SORT = "  filtered.sort(masterCompareRows);"

assert OLD_SORT in html
html = html.replace(OLD_SORT, NEW_SORT, 1)

# ── 4. 更新 table header：可排序的欄位改用 sortTh() ─────────────
OLD_THEAD = """      <thead class="bg-gray-50 sticky top-0">
        <tr>
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium">ID</th>
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium">遊戲名稱</th>
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium">廠家</th>
          <th class="px-2 py-2 text-center text-gray-500 text-xs font-medium">跨台</th>
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium">上榜平台</th>
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium">波動度</th>
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium">RTP</th>
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium">上市</th>
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium">主題</th>
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium">玩法功能</th>
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium">首見</th>
        </tr>
      </thead>"""

# 使用 template literal 拼接（注意：這裡是 Python 字串，裡面有 JS template literal）
# sortTh() 呼叫本身就是 JS 程式，放進 template literal 裡用 ${ } 包住
NEW_THEAD = """      <thead class="bg-gray-50 sticky top-0">
        <tr>
          <th class="px-2 py-2 text-left text-gray-400 text-xs font-medium">ID</th>
          ${sortTh('name','遊戲名稱')}
          ${sortTh('vendor','廠家')}
          ${sortTh('count','跨台','center')}
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium whitespace-nowrap">上榜平台</th>
          ${sortTh('volatility','波動度')}
          ${sortTh('rtp','RTP')}
          ${sortTh('releaseDate','上市')}
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium">主題</th>
          <th class="px-2 py-2 text-left text-gray-500 text-xs font-medium">玩法功能</th>
          ${sortTh('firstSeen','首見')}
        </tr>
      </thead>"""

assert OLD_THEAD in html
html = html.replace(OLD_THEAD, NEW_THEAD, 1)

INDEX_PATH.write_text(html, encoding="utf-8")
print(f"✓ 主表排序升級完成（{len(html):,} chars）")
