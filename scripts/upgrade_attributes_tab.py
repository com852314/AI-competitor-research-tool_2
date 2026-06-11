"""
遊戲屬性頁籤全面升級：
- 平台篩選改為 checkbox（與主表瀏覽一致）
- 週次按鈕動態產生（對應實際載入的週次，顯示日期 tooltip）
- computeAgg 改用真實資料（STATE.weekly × STATE.master.attributes）
- 新增廠家上榜次數圖（不需屬性資料）
- 新增屬性覆蓋率摘要卡片
- 移除 Mock 資料常數
"""
import re
from pathlib import Path

INDEX_PATH = Path(r"D:\Claude Project\競品調研(排名)\index.html")
html = INDEX_PATH.read_text(encoding="utf-8")

# ════════════════════════════════════════════════════
# 1. 替換 JS IIFE
# ════════════════════════════════════════════════════
NEW_IIFE = r"""
// ===== 遊戲屬性分析 Tab =====
(function () {

const VOL_COLORS = { High:"#ef4444","Med-High":"#f97316",Med:"#eab308","Low-Med":"#22c55e",Low:"#3b82f6","N/A":"#d1d5db",Adjusted:"#a855f7" };
let _charts = {};
let _attrRendered = false;

// ── 遊戲名稱 → 屬性 Map（從 STATE 建立）
function buildAttrsByName() {
  if (!STATE.master.games || !STATE.master.attributes) return {};
  const map = {};
  for (const game of (STATE.master.games.games || [])) {
    const attr = STATE.master.attributes[String(game.masterId)];
    if (attr && attr.status === 'found') map[game.normalizedName] = attr;
  }
  return map;
}

// ── 取篩選狀態
function getSelectedWeekKeys() {
  return [...document.querySelectorAll('.attr-week-btn.selected')]
    .map(b => b.dataset.key).filter(Boolean);
}
function getSelectedPlatforms() {
  return [...document.querySelectorAll('.attr-plat-cb:checked')].map(c => c.value);
}

// ── 主計算（真實資料）
function computeAgg(selPlats, weekKeys) {
  const attrsByName = buildAttrsByName();
  const allPlats = selPlats.length ? selPlats : ['PT','BP','CP','TCG','BAJI'];
  const volMap={}, themeMap={}, featMap={}, yearMap={}, vendorMap={};
  let rtpTotal=0, rtpCount=0, withAttr=0, totalApps=0;
  const uniq=new Set();

  for (const key of weekKeys) {
    const wk = STATE.weekly[key];
    if (!wk) continue;
    for (const plat of allPlats) {
      for (const r of (wk.platforms?.[plat]?.rankings || [])) {
        totalApps++;
        uniq.add(r.name);
        const v = r.vendor || r.rawVendor || '(未知)';
        vendorMap[v] = (vendorMap[v]||0) + 1;
        const attr = attrsByName[r.name];
        if (!attr) continue;
        withAttr++;
        const vol = attr.volatility || 'N/A';
        volMap[vol] = (volMap[vol]||0) + 1;
        if (attr.rtp && attr.rtp > 10) { rtpTotal += attr.rtp; rtpCount++; }
        (attr.theme    || []).forEach(t => { themeMap[t]  = (themeMap[t] ||0)+1; });
        (attr.features || []).forEach(f => { featMap[f]   = (featMap[f]  ||0)+1; });
        if (attr.releaseDate) {
          const yr = attr.releaseDate.slice(0,4);
          yearMap[yr] = (yearMap[yr]||0)+1;
        }
      }
    }
  }

  const curY = new Date().getFullYear();
  const recentCnt = Object.entries(yearMap).filter(([y])=>parseInt(y)>=curY-1).reduce((s,[,v])=>s+v,0);
  const totalDated = Object.values(yearMap).reduce((s,v)=>s+v,0);

  return {
    appearances: totalApps,
    unique:      uniq.size,
    coverage:    totalApps > 0 ? withAttr/totalApps : 0,
    rtp:         rtpCount  > 0 ? rtpTotal/rtpCount  : null,
    newRatio:    totalDated > 0 ? recentCnt/totalDated : null,
    vol:     volMap,
    themes:  Object.entries(themeMap).sort((a,b)=>b[1]-a[1]).slice(0,12),
    features:Object.entries(featMap).sort((a,b)=>b[1]-a[1]).slice(0,12),
    years:   Object.entries(yearMap).sort((a,b)=>a[0]>b[0]?1:-1),
    vendors: Object.entries(vendorMap).sort((a,b)=>b[1]-a[1]).slice(0,15),
  };
}

// ── 波動度週次趨勢
function computeTrend(selPlats, allWeekKeys) {
  const attrsByName = buildAttrsByName();
  const allPlats = selPlats.length ? selPlats : ['PT','BP','CP','TCG','BAJI'];
  return allWeekKeys.map(key => {
    const wk = STATE.weekly[key];
    if (!wk) return { label: key, high:0, med:0, low:0 };
    const cnt={};  let total=0;
    for (const plat of allPlats)
      for (const r of (wk.platforms?.[plat]?.rankings || [])) {
        const attr = attrsByName[r.name];
        if (!attr) continue;
        const vol = attr.volatility || 'N/A';
        cnt[vol] = (cnt[vol]||0)+1;  total++;
      }
    const pct = (...vs) => total>0 ? Math.round(vs.reduce((s,v)=>(s+(cnt[v]||0)),0)/total*100) : 0;
    return {
      label: `W${wk.week} (${(wk.captureDate||'').slice(5,10)})`,
      high:  pct('High','Med-High'),
      med:   pct('Med'),
      low:   pct('Low','Low-Med'),
    };
  });
}

function destroyChart(id) { if (_charts[id]) { _charts[id].destroy(); _charts[id]=null; } }
function rebuildCanvas(id) {
  const wrap = document.getElementById(id).parentElement;
  destroyChart(id);
  wrap.innerHTML = `<canvas id="${id}"></canvas>`;
}

function renderAll() {
  const plats    = getSelectedPlatforms();
  const weekKeys = getSelectedWeekKeys();
  if (!weekKeys.length || !plats.length) return;

  const d = computeAgg(plats, weekKeys);

  // 摘要
  document.getElementById("attr-stat-appearances").textContent = d.appearances.toLocaleString();
  document.getElementById("attr-stat-unique").textContent      = d.unique + " 款";
  document.getElementById("attr-stat-rtp").textContent         = d.rtp    ? d.rtp.toFixed(1)+"%" : "—";
  document.getElementById("attr-stat-new-ratio").textContent   = d.newRatio ? Math.round(d.newRatio*100)+"%" : "—";
  document.getElementById("attr-stat-coverage").textContent    = Math.round(d.coverage*100) + "%";
  document.getElementById("attr-filter-label").textContent     =
    `${plats.length===5?"全平台":plats.join("/")} × ${weekKeys.length} 週`;

  // 廠家
  rebuildCanvas("attr-vendor-canvas");
  const vtop = d.vendors;
  _charts["attr-vendor-canvas"] = new Chart(document.getElementById("attr-vendor-canvas"), {
    type:"bar",
    data:{ labels:vtop.map(v=>v[0]),
      datasets:[{ label:"上榜次數", data:vtop.map(v=>v[1]), backgroundColor:"#6366f1", borderRadius:3 }] },
    options:{ indexAxis:"y", responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false} },
      scales:{ x:{beginAtZero:true}, y:{ticks:{font:{size:11}}} } }
  });

  // 波動度
  rebuildCanvas("attr-vol-canvas");
  const volLabels = Object.keys(d.vol);
  _charts["attr-vol-canvas"] = new Chart(document.getElementById("attr-vol-canvas"), {
    type:"pie",
    data:{ labels:volLabels,
      datasets:[{ data:Object.values(d.vol),
        backgroundColor:volLabels.map(k=>VOL_COLORS[k]||"#d1d5db"), borderWidth:1 }] },
    options:{ responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ position:"right", labels:{ font:{size:11} } } } }
  });

  // 上市年份
  rebuildCanvas("attr-year-canvas");
  _charts["attr-year-canvas"] = new Chart(document.getElementById("attr-year-canvas"), {
    type:"bar",
    data:{ labels:d.years.map(y=>y[0]),
      datasets:[{ data:d.years.map(y=>y[1]),
        backgroundColor:d.years.map(y=>parseInt(y[0])>=2024?"#6366f1":"#93c5fd"), borderRadius:3 }] },
    options:{ responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false}, tooltip:{ callbacks:{ label:ctx=>ctx.raw+" 次" } } },
      scales:{ x:{grid:{display:false}}, y:{beginAtZero:true,ticks:{font:{size:10}}} } }
  });

  // 主題
  const thSorted = [...d.themes].sort((a,b)=>a[1]-b[1]);
  rebuildCanvas("attr-theme-canvas");
  _charts["attr-theme-canvas"] = new Chart(document.getElementById("attr-theme-canvas"), {
    type:"bar",
    data:{ labels:thSorted.map(t=>t[0]),
      datasets:[{ label:"上榜次數", data:thSorted.map(t=>t[1]), backgroundColor:"#f59e0b", borderRadius:3 }] },
    options:{ indexAxis:"y", responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false} },
      scales:{ x:{beginAtZero:true}, y:{ticks:{font:{size:11}}} } }
  });

  // 玩法功能
  const ftSorted = [...d.features].sort((a,b)=>a[1]-b[1]);
  rebuildCanvas("attr-feature-canvas");
  _charts["attr-feature-canvas"] = new Chart(document.getElementById("attr-feature-canvas"), {
    type:"bar",
    data:{ labels:ftSorted.map(f=>f[0]),
      datasets:[{ label:"上榜次數", data:ftSorted.map(f=>f[1]), backgroundColor:"#10b981", borderRadius:3 }] },
    options:{ indexAxis:"y", responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false} },
      scales:{ x:{beginAtZero:true}, y:{ticks:{font:{size:11}}} } }
  });

  // 波動度趨勢（對所有週次，不受週次 checkbox 影響 → 讓折線圖始終完整）
  const allWeekKeys = Object.keys(STATE.weekly).sort();
  const trendData   = computeTrend(plats, allWeekKeys);
  rebuildCanvas("attr-trend-canvas");
  _charts["attr-trend-canvas"] = new Chart(document.getElementById("attr-trend-canvas"), {
    type:"line",
    data:{
      labels: trendData.map(t=>t.label),
      datasets:[
        { label:"High+Med-High %", data:trendData.map(t=>t.high),
          borderColor:"#ef4444", backgroundColor:"rgba(239,68,68,0.08)", tension:0.3, fill:false, pointRadius:4 },
        { label:"Med %", data:trendData.map(t=>t.med),
          borderColor:"#eab308", backgroundColor:"rgba(234,179,8,0.08)",  tension:0.3, fill:false, pointRadius:4 },
        { label:"Low+Low-Med %", data:trendData.map(t=>t.low),
          borderColor:"#3b82f6", backgroundColor:"rgba(59,130,246,0.08)", tension:0.3, fill:false, pointRadius:4 },
      ]
    },
    options:{ responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ position:"bottom", labels:{font:{size:11}} },
        tooltip:{ callbacks:{ label:ctx=>ctx.dataset.label+": "+ctx.raw+"%" } } },
      scales:{ y:{ min:0, max:100, ticks:{ callback:v=>v+"%" } },
               x:{ grid:{display:false} } } }
  });
}

function toggleWeekBtn(btn, on) {
  btn.classList.toggle("selected",          on);
  btn.classList.toggle("border-blue-500",   on);
  btn.classList.toggle("bg-blue-50",        on);
  btn.classList.toggle("text-blue-700",     on);
  btn.classList.toggle("border-gray-300",  !on);
  btn.classList.toggle("text-gray-400",    !on);
}

function initAttributesTab() {
  if (_attrRendered) return;
  _attrRendered = true;

  // ── 動態週次按鈕
  const weekKeys   = Object.keys(STATE.weekly).sort();
  const weekBtnDiv = document.getElementById("attr-week-btns");
  if (weekKeys.length) {
    weekBtnDiv.innerHTML = weekKeys.map(k => {
      const wk = STATE.weekly[k];
      return `<button class="attr-week-btn selected px-2 py-1 text-xs rounded border border-blue-500 bg-blue-50 text-blue-700" data-key="${k}" title="${wk.captureDate||''}">W${wk.week}<span class="opacity-60 text-xs ml-0.5">(${(wk.captureDate||'').slice(5,10)})</span></button>`;
    }).join('');
    weekBtnDiv.querySelectorAll('.attr-week-btn').forEach(btn =>
      btn.addEventListener('click', () => { toggleWeekBtn(btn, !btn.classList.contains('selected')); renderAll(); })
    );
  } else {
    weekBtnDiv.innerHTML = '<span class="text-xs text-gray-400">尚未載入資料</span>';
  }

  // 週次全選/全消
  document.getElementById("attr-week-all").addEventListener("click", () => {
    const btns = [...document.querySelectorAll(".attr-week-btn")];
    const allOn = btns.every(b => b.classList.contains("selected"));
    btns.forEach(b => toggleWeekBtn(b, !allOn));
    renderAll();
  });

  // ── 平台 checkbox
  const platAllCb = document.getElementById("attr-plat-all");
  const platCbs   = document.querySelectorAll(".attr-plat-cb");
  const syncAll   = () => {
    platAllCb.checked       = [...platCbs].every(c => c.checked);
    platAllCb.indeterminate = !platAllCb.checked && [...platCbs].some(c => c.checked);
  };
  platAllCb.addEventListener("change", () => { platCbs.forEach(c => c.checked = platAllCb.checked); renderAll(); });
  platCbs.forEach(cb => cb.addEventListener("change", () => { syncAll(); renderAll(); }));

  renderAll();
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => { if (btn.dataset.tab === "attributes") initAttributesTab(); });
  });
});

})();
"""

# ════════════════════════════════════════════════════
# 2. 新 HTML 區塊
# ════════════════════════════════════════════════════
NEW_HTML = """
  <!-- Attributes Tab -->
  <section id="tab-attributes" class="tab-content hidden">
    <div class="max-w-6xl mx-auto space-y-5">

      <!-- 篩選列 -->
      <div class="bg-white rounded border border-gray-200 p-3 flex flex-wrap gap-3 items-center">
        <div class="flex items-center gap-1.5 border border-gray-200 rounded px-2.5 py-1.5 flex-wrap">
          <span class="text-xs text-gray-500 font-medium">平台：</span>
          <label class="flex items-center gap-1 cursor-pointer select-none">
            <input type="checkbox" id="attr-plat-all" class="accent-gray-500" checked>
            <span class="text-xs text-gray-600 font-medium">全選</span>
          </label>
          <span class="text-gray-200">|</span>
          <label class="flex items-center gap-0.5 cursor-pointer select-none"><input type="checkbox" class="attr-plat-cb accent-blue-500"   value="PT"   checked> <span class="text-xs px-1 rounded bg-blue-100 text-blue-700">PT</span></label>
          <label class="flex items-center gap-0.5 cursor-pointer select-none"><input type="checkbox" class="attr-plat-cb accent-green-500"  value="BP"   checked> <span class="text-xs px-1 rounded bg-green-100 text-green-700">BP</span></label>
          <label class="flex items-center gap-0.5 cursor-pointer select-none"><input type="checkbox" class="attr-plat-cb accent-yellow-500" value="CP"   checked> <span class="text-xs px-1 rounded bg-yellow-100 text-yellow-700">CP</span></label>
          <label class="flex items-center gap-0.5 cursor-pointer select-none"><input type="checkbox" class="attr-plat-cb accent-purple-500" value="TCG"  checked> <span class="text-xs px-1 rounded bg-purple-100 text-purple-700">TCG</span></label>
          <label class="flex items-center gap-0.5 cursor-pointer select-none"><input type="checkbox" class="attr-plat-cb accent-pink-500"   value="BAJI" checked> <span class="text-xs px-1 rounded bg-pink-100 text-pink-700">BAJI</span></label>
        </div>
        <div class="flex items-center gap-1.5 flex-wrap">
          <span class="text-xs text-gray-500 font-medium">週次：</span>
          <button id="attr-week-all" class="px-2 py-1 text-xs rounded border border-gray-300 text-gray-500 hover:border-blue-400 hover:text-blue-600">全選/全消</button>
          <div id="attr-week-btns" class="flex gap-1 flex-wrap"></div>
        </div>
        <span id="attr-filter-label" class="text-xs text-gray-400 ml-auto"></span>
      </div>

      <!-- 摘要卡片 -->
      <div class="grid grid-cols-5 gap-3">
        <div class="bg-white rounded border border-gray-200 p-3 text-center">
          <div class="text-2xl font-bold text-blue-600" id="attr-stat-appearances">—</div>
          <div class="text-xs text-gray-500 mt-1">上榜次數（含重複）</div>
        </div>
        <div class="bg-white rounded border border-gray-200 p-3 text-center">
          <div class="text-2xl font-bold text-indigo-600" id="attr-stat-unique">—</div>
          <div class="text-xs text-gray-500 mt-1">不重複遊戲款數</div>
        </div>
        <div class="bg-white rounded border border-gray-200 p-3 text-center">
          <div class="text-2xl font-bold text-green-600" id="attr-stat-rtp">—</div>
          <div class="text-xs text-gray-500 mt-1">有屬性款平均 RTP</div>
        </div>
        <div class="bg-white rounded border border-gray-200 p-3 text-center">
          <div class="text-2xl font-bold text-orange-500" id="attr-stat-new-ratio">—</div>
          <div class="text-xs text-gray-500 mt-1">近 2 年新遊戲佔比</div>
        </div>
        <div class="bg-white rounded border border-gray-200 p-3 text-center">
          <div class="text-2xl font-bold text-gray-500" id="attr-stat-coverage">—</div>
          <div class="text-xs text-gray-500 mt-1">屬性覆蓋率</div>
        </div>
      </div>

      <!-- 廠家 + 波動度/年份 -->
      <div class="grid grid-cols-2 gap-4">
        <div class="bg-white rounded border border-gray-200 p-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3">廠家上榜次數 Top 15</h3>
          <div style="position:relative;height:340px;"><canvas id="attr-vendor-canvas"></canvas></div>
        </div>
        <div class="bg-white rounded border border-gray-200 p-4 flex flex-col gap-4">
          <div>
            <h3 class="text-sm font-semibold text-gray-700 mb-2">波動度分布</h3>
            <div style="position:relative;height:190px;"><canvas id="attr-vol-canvas"></canvas></div>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-gray-700 mb-2">上市年份分布</h3>
            <div style="position:relative;height:110px;"><canvas id="attr-year-canvas"></canvas></div>
          </div>
        </div>
      </div>

      <!-- 主題 -->
      <div class="bg-white rounded border border-gray-200 p-4">
        <h3 class="text-sm font-semibold text-gray-700 mb-3">熱門主題 Top 12（上榜遊戲屬性）</h3>
        <div style="position:relative;height:300px;"><canvas id="attr-theme-canvas"></canvas></div>
      </div>

      <!-- 玩法功能 -->
      <div class="bg-white rounded border border-gray-200 p-4">
        <h3 class="text-sm font-semibold text-gray-700 mb-3">熱門玩法功能 Top 12（上榜遊戲屬性）</h3>
        <div style="position:relative;height:300px;"><canvas id="attr-feature-canvas"></canvas></div>
      </div>

      <!-- 波動度趨勢 -->
      <div class="bg-white rounded border border-gray-200 p-4">
        <h3 class="text-sm font-semibold text-gray-700 mb-1">波動度趨勢（週次）</h3>
        <p class="text-xs text-gray-400 mb-3">全週次趨勢；週次篩選影響左側圖表，趨勢線始終顯示全部週次以便觀察走向</p>
        <div style="position:relative;height:240px;"><canvas id="attr-trend-canvas"></canvas></div>
      </div>
    </div>
  </section>
"""

# ════════════════════════════════════════════════════
# 執行替換
# ════════════════════════════════════════════════════

# 找 IIFE 起始
iife_start = html.find("\n// ===== 遊戲屬性分析 Tab（Mock v2）=====\n(function () {")
assert iife_start != -1, "找不到 IIFE 起始"

# 找 IIFE 結尾 })(); 之後
iife_end_marker = "})();\n"
iife_end = html.find(iife_end_marker, iife_start) + len(iife_end_marker)
assert iife_end > iife_start, "找不到 IIFE 結尾"

html = html[:iife_start] + NEW_IIFE + html[iife_end:]

# 找 HTML 區塊
html_start = html.find("\n  <!-- Attributes Tab (mock) -->\n  <section id=\"tab-attributes\"")
assert html_start != -1, "找不到 Attributes HTML 起始"

# 找對應的 </section>
html_end_search = html.find("</section>\n", html_start) + len("</section>\n")
assert html_end_search > html_start, "找不到 Attributes HTML 結尾"

html = html[:html_start] + NEW_HTML + html[html_end_search:]

INDEX_PATH.write_text(html, encoding="utf-8")
print(f"✓ 遊戲屬性頁籤升級完成（{len(html):,} chars）")
