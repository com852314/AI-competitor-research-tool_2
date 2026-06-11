"""
升級主表瀏覽頁籤：
1. STATE.master 加 attributes: null
2. loadFiles 加 attributes.json 識別
3. 自動載入加 attributes
4. 主表 HTML：filter bar 加波動度 + 屬性搜尋
5. renderMasterTable：平台欄改 icon、加屬性欄位（波動度/RTP/上市/主題/功能）
"""
import re
from pathlib import Path

INDEX_PATH = Path(r"D:\Claude Project\競品調研(排名)\index.html")
html = INDEX_PATH.read_text(encoding="utf-8")

# ── 1. STATE.master ─────────────────────────────────────────────
html = html.replace(
    """  master: {
    games: null,
    vendors: null,
    platforms: null
  },""",
    """  master: {
    games: null,
    vendors: null,
    platforms: null,
    attributes: null
  },"""
)

# ── 2. loadFiles：加 attributes.json 識別 ───────────────────────
html = html.replace(
    """      } else if (f.name === 'platforms.json' || (Array.isArray(json.platforms))) {
        STATE.master.platforms = json; parsedCount++;
        console.log(`[viewer] ✓ 主表 platforms:`, f.name);
      } else {""",
    """      } else if (f.name === 'platforms.json' || (Array.isArray(json.platforms))) {
        STATE.master.platforms = json; parsedCount++;
        console.log(`[viewer] ✓ 主表 platforms:`, f.name);
      } else if (f.name === 'attributes.json') {
        STATE.master.attributes = json; parsedCount++;
        console.log(`[viewer] ✓ 主表 attributes:`, f.name);
      } else {"""
)

# ── 3. 自動載入：加 attributes ───────────────────────────────────
html = html.replace(
    "    for (const name of ['games', 'vendors', 'platforms']) {",
    "    for (const name of ['games', 'vendors', 'platforms', 'attributes']) {"
)

# ── 4. 主表 HTML：filter bar 加波動度 + 屬性關鍵字篩選 ────────────
OLD_FILTER_BAR = """    <div class="flex items-center gap-3 mb-3 flex-wrap">
      <h2 class="text-xl font-bold">遊戲主表</h2>
      <span id="master-count" class="text-sm text-gray-500"></span>
      <div class="flex-1"></div>
      <input id="master-search" type="text" placeholder="搜尋遊戲名稱 / 廠家..." class="px-3 py-2 text-sm border border-gray-300 rounded w-64">
      <select id="master-filter-platforms" class="px-3 py-2 text-sm border border-gray-300 rounded">
        <option value="0">全部（不分跨平台數）</option>
        <option value="2">≥2 平台</option>
        <option value="3">≥3 平台</option>
        <option value="4">≥4 平台</option>
        <option value="5">5 平台</option>
      </select>
    </div>"""

NEW_FILTER_BAR = """    <div class="space-y-2 mb-3">
      <div class="flex items-center gap-3 flex-wrap">
        <h2 class="text-xl font-bold">遊戲主表</h2>
        <span id="master-count" class="text-sm text-gray-500"></span>
      </div>
      <div class="flex gap-2 flex-wrap items-center">
        <input id="master-search" type="text" placeholder="搜尋名稱 / 廠家..." class="px-3 py-2 text-sm border border-gray-300 rounded w-52">
        <select id="master-filter-platforms" class="px-2 py-2 text-sm border border-gray-300 rounded">
          <option value="0">全部平台</option>
          <option value="2">≥2 平台</option>
          <option value="3">≥3 平台</option>
          <option value="4">≥4 平台</option>
          <option value="5">5 平台</option>
        </select>
        <select id="master-filter-vol" class="px-2 py-2 text-sm border border-gray-300 rounded">
          <option value="">全部波動度</option>
          <option value="Low">Low（低）</option>
          <option value="Low-Med">Low-Med</option>
          <option value="Med">Med（中）</option>
          <option value="Med-High">Med-High</option>
          <option value="High">High（高）</option>
          <option value="N/A">N/A</option>
          <option value="__none">未收錄</option>
        </select>
        <input id="master-filter-attr" type="text" placeholder="篩主題/功能（如 Asian、Wild）..." class="px-3 py-2 text-sm border border-gray-300 rounded w-56">
        <label class="text-xs text-gray-400 ml-auto">共 <span id="master-count-inline"></span></label>
      </div>
    </div>"""

assert OLD_FILTER_BAR in html, "找不到舊的 filter bar"
html = html.replace(OLD_FILTER_BAR, NEW_FILTER_BAR, 1)

# ── 5. renderMaster JS：綁定新的篩選器 + renderMasterTable ────────
OLD_RENDER_MASTER = """function renderMaster() {
  if (!STATE.master.games) {
    document.getElementById('master-table-wrap').innerHTML = '<div class="text-gray-400 text-sm py-8 text-center">尚未載入遊戲主表</div>';
    return;
  }

  // 綁定搜尋與篩選（只綁一次）
  const searchEl = document.getElementById('master-search');
  const filterEl = document.getElementById('master-filter-platforms');
  if (!searchEl.dataset.bound) {
    searchEl.addEventListener('input', e => { MASTER_SEARCH = e.target.value.toLowerCase(); renderMasterTable(); });
    filterEl.addEventListener('change', e => { MASTER_FILTER = parseInt(e.target.value) || 0; renderMasterTable(); });
    searchEl.dataset.bound = '1';
  }
  searchEl.value = MASTER_SEARCH;
  filterEl.value = MASTER_FILTER;
  renderMasterTable();
}"""

NEW_RENDER_MASTER = """function renderMaster() {
  if (!STATE.master.games) {
    document.getElementById('master-table-wrap').innerHTML = '<div class="text-gray-400 text-sm py-8 text-center">尚未載入遊戲主表</div>';
    return;
  }

  const searchEl  = document.getElementById('master-search');
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
  attrEl.value   = MASTER_ATTR_KW;
  renderMasterTable();
}"""

assert OLD_RENDER_MASTER in html, "找不到 renderMaster 函式"
html = html.replace(OLD_RENDER_MASTER, NEW_RENDER_MASTER, 1)

# ── 6. 主表狀態變數：加 VOL / ATTR_KW ───────────────────────────
html = html.replace(
    "// ===== Render: 主表瀏覽 =====\nlet MASTER_SEARCH = '';\nlet MASTER_FILTER = 0;",
    "// ===== Render: 主表瀏覽 =====\nlet MASTER_SEARCH  = '';\nlet MASTER_FILTER  = 0;\nlet MASTER_VOL     = '';\nlet MASTER_ATTR_KW = '';"
)

# ── 7. renderMasterTable：重寫（加屬性 join + 新欄位 + 新篩選）──
OLD_RENDER_TABLE = """function renderMasterTable() {
  const allGames = STATE.master.games.games || [];
  // 計算每款的跨平台數
  const augmented = allGames.map(g => {
    const aliases = g.platformAliases || {};
    const platforms = Object.entries(aliases).filter(([_, v]) => v).map(([k]) => k);
    return { ...g, _platforms: platforms, _count: platforms.length };
  });
  // 篩選
  let filtered = augmented;
  if (MASTER_FILTER > 0) {
    filtered = filtered.filter(g => g._count >= MASTER_FILTER);
  }
  if (MASTER_SEARCH) {
    filtered = filtered.filter(g =>
      (g.normalizedName || '').toLowerCase().includes(MASTER_SEARCH) ||
      (g.normalizedVendor || '').toLowerCase().includes(MASTER_SEARCH) ||
      Object.values(g.platformAliases || {}).some(v => v && String(v).toLowerCase().includes(MASTER_SEARCH))
    );
  }
  // 排序：平台數降 → 主表ID升
  filtered.sort((a, b) => b._count - a._count || a.masterId - b.masterId);

  document.getElementById('master-count').textContent = `共 ${allGames.length} 款，顯示 ${filtered.length} 款`;

  if (!filtered.length) {
    document.getElementById('master-table-wrap').innerHTML = '<div class="text-gray-400 text-sm py-8 text-center">沒有符合條件的遊戲</div>';
    return;
  }

  const html = `
    <table class="w-full text-sm">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-3 py-2 text-left text-gray-600">ID</th>
          <th class="px-3 py-2 text-left text-gray-600">正規化名稱</th>
          <th class="px-3 py-2 text-left text-gray-600">廠家</th>
          <th class="px-3 py-2 text-center text-gray-600">平台數</th>
          ${PLATFORM_ORDER.map(c => `<th class="px-3 py-2 text-left text-gray-600">${c} 名稱/ID</th>`).join('')}
          <th class="px-3 py-2 text-left text-gray-600">首次發現</th>
          <th class="px-3 py-2 text-left text-gray-600">備註</th>
        </tr>
      </thead>
      <tbody>
        ${filtered.map(g => {
          const star = g._count >= 3 ? '<span class="text-orange-500">★</span> ' : '';
          const countCls = g._count >= 3 ? 'text-orange-600 font-bold' : (g._count === 2 ? 'text-blue-600 font-semibold' : 'text-gray-500');
          return `
            <tr class="border-t border-gray-100 hover:bg-blue-50">
              <td class="px-3 py-2 text-gray-500">${g.masterId}</td>
              <td class="px-3 py-2 font-medium">${star}${escapeHtml(g.normalizedName)}</td>
              <td class="px-3 py-2"><span class="vendor-tag ${vendorClass(g.normalizedVendor)}">${escapeHtml(g.normalizedVendor)}</span></td>
              <td class="px-3 py-2 text-center ${countCls}">${g._count}</td>
              ${PLATFORM_ORDER.map(c => `<td class="px-3 py-2 text-gray-600 text-xs">${escapeHtml(g.platformAliases?.[c] || '—')}</td>`).join('')}
              <td class="px-3 py-2 text-xs text-gray-500">${escapeHtml(g.firstSeen || '')}</td>
              <td class="px-3 py-2 text-xs text-gray-500">${escapeHtml(g.note || '')}</td>
            </tr>`;
        }).join('')}
      </tbody>
    </table>
  `;
  document.getElementById('master-table-wrap').innerHTML = html;
}"""

NEW_RENDER_TABLE = r"""function renderMasterTable() {
  const allGames = STATE.master.games.games || [];

  // 建立屬性 Map（masterId → attr）
  const attrsMap = {};
  if (STATE.master.attributes) {
    Object.values(STATE.master.attributes).forEach(a => {
      if (a.masterId != null) attrsMap[a.masterId] = a;
    });
  }

  const VOL_COLOR = {
    'High':'bg-red-100 text-red-700','Med-High':'bg-orange-100 text-orange-700',
    'Med':'bg-yellow-100 text-yellow-700','Low-Med':'bg-green-100 text-green-700',
    'Low':'bg-blue-100 text-blue-700','N/A':'bg-gray-100 text-gray-500',
    'Adjusted':'bg-purple-100 text-purple-600'
  };
  const PLAT_COLOR = { PT:'bg-blue-100 text-blue-700', BP:'bg-green-100 text-green-700',
    CP:'bg-yellow-100 text-yellow-700', TCG:'bg-purple-100 text-purple-700',
    BAJI:'bg-pink-100 text-pink-700' };

  const augmented = allGames.map(g => {
    const aliases = g.platformAliases || {};
    const platforms = Object.entries(aliases).filter(([_, v]) => v).map(([k]) => k);
    const attr = attrsMap[g.masterId] || null;
    return { ...g, _platforms: platforms, _count: platforms.length, _attr: attr };
  });

  // 篩選
  let filtered = augmented;
  if (MASTER_FILTER > 0)
    filtered = filtered.filter(g => g._count >= MASTER_FILTER);
  if (MASTER_SEARCH)
    filtered = filtered.filter(g =>
      (g.normalizedName || '').toLowerCase().includes(MASTER_SEARCH) ||
      (g.normalizedVendor || '').toLowerCase().includes(MASTER_SEARCH) ||
      Object.values(g.platformAliases || {}).some(v => v && String(v).toLowerCase().includes(MASTER_SEARCH))
    );
  if (MASTER_VOL) {
    if (MASTER_VOL === '__none')
      filtered = filtered.filter(g => !g._attr || !g._attr.volatility);
    else
      filtered = filtered.filter(g => g._attr && g._attr.volatility === MASTER_VOL);
  }
  if (MASTER_ATTR_KW) {
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

  filtered.sort((a, b) => b._count - a._count || a.masterId - b.masterId);

  const summary = `共 ${allGames.length} 款，顯示 ${filtered.length} 款`;
  document.getElementById('master-count').textContent = summary;
  const ci = document.getElementById('master-count-inline');
  if (ci) ci.textContent = `${filtered.length} / ${allGames.length} 款`;

  if (!filtered.length) {
    document.getElementById('master-table-wrap').innerHTML = '<div class="text-gray-400 text-sm py-8 text-center">沒有符合條件的遊戲</div>';
    return;
  }

  const rows = filtered.map(g => {
    const a = g._attr;
    const star = g._count >= 3 ? '<span class="text-orange-500">★</span> ' : '';
    const countCls = g._count >= 3 ? 'text-orange-600 font-bold' : (g._count === 2 ? 'text-blue-600 font-semibold' : 'text-gray-400');

    // 平台 icon
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

    return `<tr class="border-t border-gray-100 hover:bg-blue-50" title="${escapeHtml((a && a.theme ? 'Theme: ' + a.theme.join(', ') + '\n' : '') + (a && a.features ? 'Features: ' + a.features.join(', ') : ''))}">
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
    </tr>`;
  }).join('');

  const tableHtml = `
    <table class="w-full text-sm">
      <thead class="bg-gray-50 sticky top-0">
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
      </thead>
      <tbody>${rows}</tbody>
    </table>`;

  document.getElementById('master-table-wrap').innerHTML = tableHtml;
}"""

assert OLD_RENDER_TABLE in html, "找不到 renderMasterTable 函式"
html = html.replace(OLD_RENDER_TABLE, NEW_RENDER_TABLE, 1)

INDEX_PATH.write_text(html, encoding="utf-8")
print(f"✓ 主表瀏覽升級完成（{len(html):,} chars）")
