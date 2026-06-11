"""
主表瀏覽升級 v3：
1. 上市時間維度篩選（今年/本季/本月/自訂範圍）
2. 複合搜尋（逗號分隔 = OR）+ 模糊比對（忽略空格/連字號/特殊符號）
3. 主搜尋擴展覆蓋主題/功能欄位
"""
from pathlib import Path

INDEX_PATH = Path(r"D:\Claude Project\競品調研(排名)\index.html")
html = INDEX_PATH.read_text(encoding="utf-8")

# ── 1. HTML：更新搜尋 placeholder + 加上市日期篩選 ───────────────
OLD_SEARCH_AND_ATTR = """        <input id="master-search" type="text" placeholder="搜尋名稱 / 廠家..." class="px-3 py-2 text-sm border border-gray-300 rounded w-52">"""

NEW_SEARCH_AND_ATTR = """        <input id="master-search" type="text" placeholder="搜尋名稱 / 廠家 / 主題（逗號=多詞OR）" class="px-3 py-2 text-sm border border-gray-300 rounded w-72">"""

assert OLD_SEARCH_AND_ATTR in html, "找不到 search input"
html = html.replace(OLD_SEARCH_AND_ATTR, NEW_SEARCH_AND_ATTR, 1)

# 在 attr 篩選後、count label 前插入日期篩選
OLD_ATTR_AND_COUNT = """        <input id="master-filter-attr" type="text" placeholder="篩主題/功能（如 Asian、Wild）..." class="px-3 py-2 text-sm border border-gray-300 rounded w-56">
        <label class="text-xs text-gray-400 ml-auto">共 <span id="master-count-inline"></span></label>"""

NEW_ATTR_AND_COUNT = """        <input id="master-filter-attr" type="text" placeholder="篩主題/功能（如 Asian、Wild）..." class="px-3 py-2 text-sm border border-gray-300 rounded w-56">
        <div class="flex items-center gap-1">
          <select id="master-filter-date" class="px-2 py-2 text-sm border border-gray-300 rounded">
            <option value="">全部上市時間</option>
            <option value="year">今年（2026）</option>
            <option value="quarter">本季</option>
            <option value="month">本月</option>
            <option value="custom">自訂區間</option>
          </select>
          <span id="master-date-custom" class="hidden items-center gap-1">
            <input type="date" id="master-date-from" class="px-2 py-1 text-xs border border-gray-300 rounded">
            <span class="text-xs text-gray-400">—</span>
            <input type="date" id="master-date-to" class="px-2 py-1 text-xs border border-gray-300 rounded">
          </span>
        </div>
        <label class="text-xs text-gray-400 ml-auto">共 <span id="master-count-inline"></span></label>"""

assert OLD_ATTR_AND_COUNT in html, "找不到 attr/count 區段"
html = html.replace(OLD_ATTR_AND_COUNT, NEW_ATTR_AND_COUNT, 1)

# ── 2. JS state：加上 MASTER_DATE_PRESET / FROM / TO ─────────────
OLD_STATE_VARS = """let MASTER_SEARCH  = '';
let MASTER_PLAT_FILTER = new Set(['PT','BP','CP','TCG','BAJI']);
let MASTER_VOL     = '';
let MASTER_ATTR_KW = '';"""

NEW_STATE_VARS = """let MASTER_SEARCH      = '';
let MASTER_PLAT_FILTER = new Set(['PT','BP','CP','TCG','BAJI']);
let MASTER_VOL         = '';
let MASTER_ATTR_KW     = '';
let MASTER_DATE_PRESET = '';
let MASTER_DATE_FROM   = '';
let MASTER_DATE_TO     = '';"""

assert OLD_STATE_VARS in html, "找不到 state vars"
html = html.replace(OLD_STATE_VARS, NEW_STATE_VARS, 1)

# ── 3. renderMaster：加日期篩選器的綁定 ─────────────────────────
OLD_BINDINGS_TAIL = """    searchEl.addEventListener('input',  e => { MASTER_SEARCH  = e.target.value.toLowerCase(); renderMasterTable(); });
    volEl.addEventListener('change',    e => { MASTER_VOL     = e.target.value; renderMasterTable(); });
    attrEl.addEventListener('input',    e => { MASTER_ATTR_KW = e.target.value.toLowerCase(); renderMasterTable(); });"""

NEW_BINDINGS_TAIL = """    searchEl.addEventListener('input',  e => { MASTER_SEARCH  = e.target.value.toLowerCase(); renderMasterTable(); });
    volEl.addEventListener('change',    e => { MASTER_VOL     = e.target.value; renderMasterTable(); });
    attrEl.addEventListener('input',    e => { MASTER_ATTR_KW = e.target.value.toLowerCase(); renderMasterTable(); });

    // 日期篩選
    const dateEl    = document.getElementById('master-filter-date');
    const dateFrEl  = document.getElementById('master-date-from');
    const dateToEl  = document.getElementById('master-date-to');
    const customBox = document.getElementById('master-date-custom');
    dateEl.addEventListener('change', e => {
      MASTER_DATE_PRESET = e.target.value;
      customBox.style.display = MASTER_DATE_PRESET === 'custom' ? 'flex' : 'none';
      renderMasterTable();
    });
    dateFrEl.addEventListener('change', e => { MASTER_DATE_FROM = e.target.value; renderMasterTable(); });
    dateToEl.addEventListener('change', e => { MASTER_DATE_TO   = e.target.value; renderMasterTable(); });"""

assert OLD_BINDINGS_TAIL in html, "找不到 bindings tail"
html = html.replace(OLD_BINDINGS_TAIL, NEW_BINDINGS_TAIL, 1)

# ── 4. renderMaster：sync 日期 input 值 ─────────────────────────
OLD_SYNC_VALS = """  searchEl.value = MASTER_SEARCH;
  volEl.value    = MASTER_VOL;
  attrEl.value   = MASTER_ATTR_KW;"""

NEW_SYNC_VALS = """  searchEl.value = MASTER_SEARCH;
  volEl.value    = MASTER_VOL;
  attrEl.value   = MASTER_ATTR_KW;
  const _dateEl = document.getElementById('master-filter-date');
  if (_dateEl) _dateEl.value = MASTER_DATE_PRESET;"""

assert OLD_SYNC_VALS in html, "找不到 sync vals"
html = html.replace(OLD_SYNC_VALS, NEW_SYNC_VALS, 1)

# ── 5. renderMasterTable：加 helper + 升級搜尋 + 加日期篩選 ──────
# 在 renderAttrList 之前插入新 helpers
HELPER_INSERT_BEFORE = "function renderAttrList(arr, limit) {"

NEW_HELPERS = """// ── 搜尋正規化（模糊：忽略空格/連字號/特殊符號）
function normSearch(s) {
  return String(s).toLowerCase().replace(/[\s\-_#.'\/\\\\,]/g, '');
}
function matchesTerm(rawTerm, g, a) {
  const term = normSearch(rawTerm);
  if (!term) return true;
  const fields = [
    g.normalizedName || '',
    g.normalizedVendor || '',
    ...Object.values(g.platformAliases || {}).filter(Boolean).map(String),
    ...((a && a.theme) || []),
    ...((a && a.features) || []),
  ];
  return fields.some(f => normSearch(f).includes(term));
}

// ── 上市日期範圍計算
function getDateRange(preset, from, to) {
  const now = new Date();
  const y = now.getFullYear();
  const m = now.getMonth();       // 0-indexed
  const q = Math.floor(m / 3);
  const pad = n => String(n).padStart(2, '0');
  if (preset === 'year')    return [`${y}-01-01`, `${y}-12-31`];
  if (preset === 'quarter') return [`${y}-${pad(q*3+1)}-01`, `${y}-${pad((q+1)*3)}-31`];
  if (preset === 'month')   return [`${y}-${pad(m+1)}-01`, `${y}-${pad(m+1)}-31`];
  if (preset === 'custom')  return [from || '', to || ''];
  return ['', ''];
}

"""

assert HELPER_INSERT_BEFORE in html, "找不到 renderAttrList"
html = html.replace(HELPER_INSERT_BEFORE, NEW_HELPERS + HELPER_INSERT_BEFORE, 1)

# ── 6. 更新搜尋篩選邏輯（替換舊的 MASTER_SEARCH if block）────────
OLD_SEARCH_FILTER = """  if (MASTER_SEARCH)
    filtered = filtered.filter(g =>
      (g.normalizedName || '').toLowerCase().includes(MASTER_SEARCH) ||
      (g.normalizedVendor || '').toLowerCase().includes(MASTER_SEARCH) ||
      Object.values(g.platformAliases || {}).some(v => v && String(v).toLowerCase().includes(MASTER_SEARCH))
    );"""

NEW_SEARCH_FILTER = """  if (MASTER_SEARCH.trim()) {
    const terms = MASTER_SEARCH.split(',').map(t => t.trim()).filter(Boolean);
    filtered = filtered.filter(g => terms.some(term => matchesTerm(term, g, g._attr)));
  }"""

assert OLD_SEARCH_FILTER in html, "找不到舊搜尋邏輯"
html = html.replace(OLD_SEARCH_FILTER, NEW_SEARCH_FILTER, 1)

# ── 7. 在波動度篩選後插入日期篩選邏輯 ───────────────────────────
OLD_VOL_FILTER_END = """  if (MASTER_ATTR_KW) {
    filtered = filtered.filter(g => {
      const a = g._attr;
      if (!a) return false;
      const haystack = [
        ...(a.theme || []), ...(a.features || []),
        a.volatility || '', a.layout || ''
      ].join(' ').toLowerCase();
      return haystack.includes(MASTER_ATTR_KW);
    });
  }"""

NEW_VOL_FILTER_END = """  if (MASTER_ATTR_KW) {
    filtered = filtered.filter(g => {
      const a = g._attr;
      if (!a) return false;
      const haystack = [
        ...(a.theme || []), ...(a.features || []),
        a.volatility || '', a.layout || ''
      ].join(' ').toLowerCase();
      return haystack.includes(MASTER_ATTR_KW);
    });
  }
  if (MASTER_DATE_PRESET) {
    const [from, to] = getDateRange(MASTER_DATE_PRESET, MASTER_DATE_FROM, MASTER_DATE_TO);
    filtered = filtered.filter(g => {
      const d = g._attr && g._attr.releaseDate;
      if (!d) return false;
      if (from && d < from) return false;
      if (to   && d > to)   return false;
      return true;
    });
  }"""

assert OLD_VOL_FILTER_END in html, "找不到 ATTR_KW 篩選結尾"
html = html.replace(OLD_VOL_FILTER_END, NEW_VOL_FILTER_END, 1)

INDEX_PATH.write_text(html, encoding="utf-8")
print(f"✓ 主表瀏覽 v3 升級完成（{len(html):,} chars）")
