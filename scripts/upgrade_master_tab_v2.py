"""
主表瀏覽升級 v2：
1. 平台篩選改成勾選 checkbox（PT / BP / CP / TCG / BAJI）
2. 主題/功能欄位加收合展開按鈕
3. 遊戲名稱加 SlotCatalog 外連結（有收錄的才顯示）
"""
from pathlib import Path

INDEX_PATH = Path(r"D:\Claude Project\競品調研(排名)\index.html")
html = INDEX_PATH.read_text(encoding="utf-8")

# ── 1. HTML：平台 select → checkbox group ───────────────────────
OLD_PLAT_SELECT = """        <select id="master-filter-platforms" class="px-2 py-2 text-sm border border-gray-300 rounded">
          <option value="0">全部平台</option>
          <option value="2">≥2 平台</option>
          <option value="3">≥3 平台</option>
          <option value="4">≥4 平台</option>
          <option value="5">5 平台</option>
        </select>"""

NEW_PLAT_CB = """        <div class="flex items-center gap-1.5 border border-gray-300 rounded px-2.5 py-1.5 bg-white flex-wrap">
          <span class="text-xs text-gray-500 font-medium">平台：</span>
          <label class="flex items-center gap-1 cursor-pointer select-none">
            <input type="checkbox" id="master-plat-all" class="accent-gray-500"> <span class="text-xs text-gray-600 font-medium">全選</span>
          </label>
          <span class="text-gray-200">|</span>
          <label class="flex items-center gap-0.5 cursor-pointer select-none"><input type="checkbox" class="master-plat-cb accent-blue-500" value="PT" checked> <span class="text-xs px-1 rounded bg-blue-100 text-blue-700">PT</span></label>
          <label class="flex items-center gap-0.5 cursor-pointer select-none"><input type="checkbox" class="master-plat-cb accent-green-500" value="BP" checked> <span class="text-xs px-1 rounded bg-green-100 text-green-700">BP</span></label>
          <label class="flex items-center gap-0.5 cursor-pointer select-none"><input type="checkbox" class="master-plat-cb accent-yellow-500" value="CP" checked> <span class="text-xs px-1 rounded bg-yellow-100 text-yellow-700">CP</span></label>
          <label class="flex items-center gap-0.5 cursor-pointer select-none"><input type="checkbox" class="master-plat-cb accent-purple-500" value="TCG" checked> <span class="text-xs px-1 rounded bg-purple-100 text-purple-700">TCG</span></label>
          <label class="flex items-center gap-0.5 cursor-pointer select-none"><input type="checkbox" class="master-plat-cb accent-pink-500" value="BAJI" checked> <span class="text-xs px-1 rounded bg-pink-100 text-pink-700">BAJI</span></label>
        </div>"""

assert OLD_PLAT_SELECT in html, "找不到平台 select"
html = html.replace(OLD_PLAT_SELECT, NEW_PLAT_CB, 1)

# ── 2. JS state：MASTER_FILTER → MASTER_PLAT_FILTER ─────────────
html = html.replace(
    "let MASTER_FILTER  = 0;",
    "let MASTER_PLAT_FILTER = new Set(['PT','BP','CP','TCG','BAJI']);"
)

# ── 3. renderMaster：改綁 checkbox + 全選聯動 ────────────────────
OLD_BINDINGS = """  const searchEl  = document.getElementById('master-search');
  const filterEl  = document.getElementById('master-filter-platforms');
  const volEl     = document.getElementById('master-filter-vol');
  const attrEl    = document.getElementById('master-filter-attr');
  if (!searchEl.dataset.bound) {
    searchEl.addEventListener('input',  e => { MASTER_SEARCH   = e.target.value.toLowerCase(); renderMasterTable(); });
    filterEl.addEventListener('change', e => { MASTER_FILTER   = parseInt(e.target.value) || 0; renderMasterTable(); });
    volEl.addEventListener('change',    e => { MASTER_VOL      = e.target.value; renderMasterTable(); });
    attrEl.addEventListener('input',    e => { MASTER_ATTR_KW  = e.target.value.toLowerCase(); renderMasterTable(); });
    searchEl.dataset.bound = '1';
  }
  searchEl.value = MASTER_SEARCH;
  filterEl.value = MASTER_FILTER;
  volEl.value    = MASTER_VOL;
  attrEl.value   = MASTER_ATTR_KW;"""

NEW_BINDINGS = """  const searchEl  = document.getElementById('master-search');
  const volEl     = document.getElementById('master-filter-vol');
  const attrEl    = document.getElementById('master-filter-attr');
  if (!searchEl.dataset.bound) {
    searchEl.addEventListener('input',  e => { MASTER_SEARCH  = e.target.value.toLowerCase(); renderMasterTable(); });
    volEl.addEventListener('change',    e => { MASTER_VOL     = e.target.value; renderMasterTable(); });
    attrEl.addEventListener('input',    e => { MASTER_ATTR_KW = e.target.value.toLowerCase(); renderMasterTable(); });

    // 平台 checkbox 群組
    const allCb = document.getElementById('master-plat-all');
    const platCbs = document.querySelectorAll('.master-plat-cb');
    function syncAllCb() {
      allCb.checked = [...platCbs].every(c => c.checked);
      allCb.indeterminate = !allCb.checked && [...platCbs].some(c => c.checked);
    }
    allCb.addEventListener('change', () => {
      platCbs.forEach(c => c.checked = allCb.checked);
      MASTER_PLAT_FILTER = allCb.checked ? new Set(['PT','BP','CP','TCG','BAJI']) : new Set();
      renderMasterTable();
    });
    platCbs.forEach(cb => cb.addEventListener('change', () => {
      MASTER_PLAT_FILTER = new Set([...platCbs].filter(c => c.checked).map(c => c.value));
      syncAllCb();
      renderMasterTable();
    }));
    allCb.checked = true;

    searchEl.dataset.bound = '1';
  }
  searchEl.value = MASTER_SEARCH;
  volEl.value    = MASTER_VOL;
  attrEl.value   = MASTER_ATTR_KW;"""

assert OLD_BINDINGS in html, "找不到 renderMaster bindings"
html = html.replace(OLD_BINDINGS, NEW_BINDINGS, 1)

# ── 4. renderMasterTable：改平台篩選邏輯 ────────────────────────
OLD_PLAT_FILTER = """  if (MASTER_FILTER > 0)
    filtered = filtered.filter(g => g._count >= MASTER_FILTER);"""

NEW_PLAT_FILTER = """  if (MASTER_PLAT_FILTER.size > 0 && MASTER_PLAT_FILTER.size < 5)
    filtered = filtered.filter(g => g._platforms.some(p => MASTER_PLAT_FILTER.has(p)));"""

assert OLD_PLAT_FILTER in html, "找不到平台篩選邏輯"
html = html.replace(OLD_PLAT_FILTER, NEW_PLAT_FILTER, 1)

# ── 5. 加入 renderAttrList helper（在 renderMasterTable 之前）────
HELPER_JS = """function renderAttrList(arr, limit) {
  if (!arr || !arr.length) return '<span class="text-gray-300">—</span>';
  const safe = arr.map(s => escapeHtml(String(s)));
  if (arr.length <= limit) return '<span class="text-xs">' + safe.join(', ') + '</span>';
  const preview = safe.slice(0, limit).join(', ');
  const rest = safe.slice(limit).join(', ');
  const more = arr.length - limit;
  return `<span class="text-xs">${preview}</span><button class="text-blue-400 text-xs ml-1 hover:text-blue-600 font-medium align-middle" onclick="var s=this.nextElementSibling;var shown=s.style.display==='inline';s.style.display=shown?'none':'inline';this.textContent=shown?'+${more}':'▲'">+${more}</button><span class="text-xs text-gray-500" style="display:none">, ${rest}</span>`;
}

"""

assert "function renderMasterTable()" in html
html = html.replace("function renderMasterTable()", HELPER_JS + "function renderMasterTable()", 1)

# ── 6. 在 renderMasterTable 內：加 SC 連結、改用 renderAttrList ──
OLD_SC_AND_CELLS = """    // 平台 icon
    const platIcons = PLATFORM_ORDER.map(p =>
      g._platforms.includes(p)
        ? `<span class="inline-block text-xs px-1 rounded ${PLAT_COLOR[p]||'bg-gray-100 text-gray-600'}">${p}</span>`
        : `<span class="inline-block text-xs px-1 rounded bg-gray-50 text-gray-300">${p}</span>`
    ).join(' ');

    // 波動度 badge
    const vol = a && a.status === 'found' ? (a.volatility || 'N/A') : '—';
    const volBadge = vol !== '—'
      ? `<span class="text-xs px-1.5 py-0.5 rounded ${VOL_COLOR[vol]||'bg-gray-100 text-gray-500'}">${vol}</span>`
      : '<span class="text-xs text-gray-300">—</span>';

    // RTP
    const rtp = a && a.rtp && a.rtp > 50 ? a.rtp.toFixed(1) + '%' : '—';

    // 上市年份
    const releaseDate = a && a.releaseDate ? a.releaseDate.slice(0, 7) : '—';

    // 主題（最多 2 個）
    const themes = a && a.theme ? a.theme.slice(0, 2).join(', ') : '—';

    // 玩法功能（最多 2 個）
    const feats = a && a.features ? a.features.slice(0, 2).join(', ') : '—';

    return `<tr class="border-t border-gray-100 hover:bg-blue-50" title="${escapeHtml((a && a.theme ? 'Theme: ' + a.theme.join(', ') + '\\n' : '') + (a && a.features ? 'Features: ' + a.features.join(', ') : ''))}">
      <td class="px-2 py-2 text-gray-400 text-xs">${g.masterId}</td>
      <td class="px-2 py-2 font-medium text-sm">${star}${escapeHtml(g.normalizedName)}</td>
      <td class="px-2 py-2"><span class="vendor-tag ${vendorClass(g.normalizedVendor)}">${escapeHtml(g.normalizedVendor)}</span></td>
      <td class="px-2 py-2 text-center ${countCls} text-sm">${g._count}</td>
      <td class="px-2 py-2">${platIcons}</td>
      <td class="px-2 py-2">${volBadge}</td>
      <td class="px-2 py-2 text-xs text-gray-600">${escapeHtml(rtp)}</td>
      <td class="px-2 py-2 text-xs text-gray-500">${escapeHtml(releaseDate)}</td>
      <td class="px-2 py-2 text-xs text-gray-600 max-w-xs truncate" title="${escapeHtml(a && a.theme ? a.theme.join(', ') : '')}">${escapeHtml(themes)}</td>
      <td class="px-2 py-2 text-xs text-gray-600 max-w-xs truncate" title="${escapeHtml(a && a.features ? a.features.join(', ') : '')}">${escapeHtml(feats)}</td>
      <td class="px-2 py-2 text-xs text-gray-400">${escapeHtml(g.firstSeen || '')}</td>
    </tr>`;"""

NEW_SC_AND_CELLS = """    // 平台 icon
    const platIcons = PLATFORM_ORDER.map(p =>
      g._platforms.includes(p)
        ? `<span class="inline-block text-xs px-1 rounded ${PLAT_COLOR[p]||'bg-gray-100 text-gray-600'}">${p}</span>`
        : `<span class="inline-block text-xs px-1 rounded bg-gray-50 text-gray-300">${p}</span>`
    ).join(' ');

    // 波動度 badge
    const vol = a && a.status === 'found' ? (a.volatility || 'N/A') : '—';
    const volBadge = vol !== '—'
      ? `<span class="text-xs px-1.5 py-0.5 rounded ${VOL_COLOR[vol]||'bg-gray-100 text-gray-500'}">${vol}</span>`
      : '<span class="text-xs text-gray-300">—</span>';

    // RTP
    const rtp = a && a.rtp && a.rtp > 50 ? a.rtp.toFixed(1) + '%' : '—';

    // 上市年月
    const releaseDate = a && a.releaseDate ? a.releaseDate.slice(0, 7) : '—';

    // SlotCatalog 連結
    const scLink = a && a.status === 'found' && a.slotcatalogUrl
      ? `<a href="${escapeHtml(a.slotcatalogUrl)}" target="_blank" rel="noopener noreferrer" class="ml-1 text-gray-300 hover:text-blue-500" title="SlotCatalog">↗</a>`
      : '';

    // 主題、功能（展開收合）
    const themeCell  = renderAttrList(a && a.theme, 2);
    const featCell   = renderAttrList(a && a.features, 2);

    return `<tr class="border-t border-gray-100 hover:bg-blue-50">
      <td class="px-2 py-2 text-gray-400 text-xs">${g.masterId}</td>
      <td class="px-2 py-2 font-medium text-sm whitespace-nowrap">${star}${escapeHtml(g.normalizedName)}${scLink}</td>
      <td class="px-2 py-2"><span class="vendor-tag ${vendorClass(g.normalizedVendor)}">${escapeHtml(g.normalizedVendor)}</span></td>
      <td class="px-2 py-2 text-center ${countCls} text-sm">${g._count}</td>
      <td class="px-2 py-2 whitespace-nowrap">${platIcons}</td>
      <td class="px-2 py-2">${volBadge}</td>
      <td class="px-2 py-2 text-xs text-gray-600">${escapeHtml(rtp)}</td>
      <td class="px-2 py-2 text-xs text-gray-500 whitespace-nowrap">${escapeHtml(releaseDate)}</td>
      <td class="px-2 py-2">${themeCell}</td>
      <td class="px-2 py-2">${featCell}</td>
      <td class="px-2 py-2 text-xs text-gray-400 whitespace-nowrap">${escapeHtml(g.firstSeen || '')}</td>
    </tr>`;"""

assert OLD_SC_AND_CELLS in html, "找不到 SC/cell 區段"
html = html.replace(OLD_SC_AND_CELLS, NEW_SC_AND_CELLS, 1)

INDEX_PATH.write_text(html, encoding="utf-8")
print(f"✓ 主表瀏覽 v2 升級完成（{len(html):,} chars）")
