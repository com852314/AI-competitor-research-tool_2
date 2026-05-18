#!/usr/bin/env python3
# Phase 2E-A: 排名折線圖 + 常勝軍 + 進出榜

HTML_PATH = r"D:\Claude Project\競品調研(排名)\index.html"

with open(HTML_PATH, encoding='utf-8') as f:
    html = f.read()

# ──────────────────────────────────────────────
# 1. 加 Chart.js CDN
# ──────────────────────────────────────────────
OLD_HEAD = '</head>\n<body class="bg-gray-50 text-gray-900">'
NEW_HEAD = '  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>\n</head>\n<body class="bg-gray-50 text-gray-900">'
assert OLD_HEAD in html, '[FAIL] head sentinel not found'
html = html.replace(OLD_HEAD, NEW_HEAD, 1)
print('✅ 1. Chart.js CDN 加入')

# ──────────────────────────────────────────────
# 2. 移除 trend tab 的 disabled
# ──────────────────────────────────────────────
OLD_BTN = 'data-tab="trend" disabled title="Phase 2D 將實作">📈 跨週趨勢</button>'
NEW_BTN = 'data-tab="trend">📈 跨週趨勢</button>'
assert OLD_BTN in html, '[FAIL] trend btn sentinel not found'
html = html.replace(OLD_BTN, NEW_BTN, 1)
print('✅ 2. trend tab disabled 移除')

# ──────────────────────────────────────────────
# 3. 換掉 trend section placeholder
# ──────────────────────────────────────────────
OLD_SEC = '<section id="tab-trend" class="tab-content hidden"><div class="text-gray-400 text-center py-12">Phase 2D 將實作（需累積 2 週以上資料）</div></section>'
NEW_SEC = '''<section id="tab-trend" class="tab-content hidden">
  <div class="max-w-6xl mx-auto px-4 py-6 space-y-8">

    <!-- 排名折線圖 -->
    <div>
      <h2 class="text-xl font-bold mb-3">📈 排名變動折線圖</h2>
      <div class="bg-white border border-gray-200 rounded p-4">
        <div class="flex flex-wrap items-center gap-3 mb-4">
          <label class="text-sm text-gray-600 font-medium">平台：</label>
          <select id="trend-platform-sel" class="border border-gray-300 rounded px-2 py-1 text-sm">
            <option value="PT">PT</option>
            <option value="BP">BP</option>
            <option value="CP">CP</option>
            <option value="TCG">TCG</option>
            <option value="BAJI">BAJI</option>
          </select>
          <label class="text-sm text-gray-600 font-medium ml-2">篩選遊戲名：</label>
          <input id="trend-game-filter" type="text" placeholder="輸入部分名稱..." class="border border-gray-300 rounded px-2 py-1 text-sm w-44">
          <button id="trend-chart-btn" class="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">更新圖表</button>
        </div>
        <div id="trend-rank-wrap" style="position:relative;height:380px;">
          <canvas id="trend-rank-canvas"></canvas>
        </div>
        <p class="text-xs text-gray-400 mt-2">Y 軸越低代表排名越高（Rank 1 在頂端）。折線中斷表示該週未進 Top 20。預設顯示出現頻率最高的前 15 款。</p>
      </div>
    </div>

    <!-- 常勝軍 -->
    <div>
      <h2 class="text-xl font-bold mb-3">🏆 常勝軍（全勤上榜）</h2>
      <div id="trend-winners-wrap" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
    </div>

    <!-- 進出榜 -->
    <div>
      <h2 class="text-xl font-bold mb-3">↕ 進榜 / 掉榜（最近兩週對比）</h2>
      <div id="trend-entry-exit-wrap"></div>
    </div>

  </div>
</section>'''
assert OLD_SEC in html, '[FAIL] trend section sentinel not found'
html = html.replace(OLD_SEC, NEW_SEC, 1)
print('✅ 3. trend section DOM 展開')

# ──────────────────────────────────────────────
# 4. renderActive() 加 trend 分支
# ──────────────────────────────────────────────
OLD_ACTIVE = "  else if (active === 'vendors') renderVendors();\n}"
NEW_ACTIVE = "  else if (active === 'vendors') renderVendors();\n  else if (active === 'trend') renderTrend();\n}"
assert OLD_ACTIVE in html, '[FAIL] renderActive sentinel not found'
html = html.replace(OLD_ACTIVE, NEW_ACTIVE, 1)
print('✅ 4. renderActive() 加 trend 分支')

# ──────────────────────────────────────────────
# 5. 注入 renderTrend 系列函式
# ──────────────────────────────────────────────
TREND_JS = r"""
// ===== Render: 跨週趨勢頁籤 (Phase 2E-A) =====

let _trendChart = null;
let _trendBound = false;

function renderTrend() {
  renderRankLineChart();
  renderPersistentWinners();
  renderEntryExit();
  if (!_trendBound) {
    _trendBound = true;
    document.getElementById('trend-chart-btn')?.addEventListener('click', renderRankLineChart);
    document.getElementById('trend-platform-sel')?.addEventListener('change', renderRankLineChart);
  }
}

function getTrendWeeks() {
  return Object.values(STATE.weekly).sort((a, b) => a.week - b.week);
}

function renderRankLineChart() {
  const weeks = getTrendWeeks();
  const wrap = document.getElementById('trend-rank-wrap');
  if (!wrap) return;
  if (weeks.length < 2) {
    wrap.innerHTML = '<div class="text-gray-400 text-sm py-12 text-center">需要 ≥ 2 週資料</div>';
    return;
  }

  const platform = document.getElementById('trend-platform-sel')?.value || 'PT';
  const filter = (document.getElementById('trend-game-filter')?.value || '').trim().toLowerCase();

  // 收集該平台所有遊戲名稱（聯集）
  const allNames = new Set();
  weeks.forEach(wk => {
    (wk.platforms?.[platform]?.rankings || []).forEach(r => { if (r.name) allNames.add(r.name); });
  });

  let names = [...allNames];
  if (filter) {
    names = names.filter(n => n.toLowerCase().includes(filter));
  } else {
    // 按出現週數排序取前 15
    const freq = {};
    names.forEach(n => { freq[n] = 0; });
    weeks.forEach(wk => {
      const inRank = new Set((wk.platforms?.[platform]?.rankings || []).map(r => r.name));
      names.forEach(n => { if (inRank.has(n)) freq[n]++; });
    });
    names.sort((a, b) => freq[b] - freq[a]);
    names = names.slice(0, 15);
  }

  const labels = weeks.map(wk => `W${wk.week} (${wk.captureDate})`);
  const COLORS = [
    '#2563EB','#DC2626','#16A34A','#CA8A04','#9333EA',
    '#0891B2','#EA580C','#4F46E5','#BE185D','#0D9488',
    '#7C3AED','#B45309','#1D4ED8','#047857','#C2410C',
  ];
  const datasets = names.map((name, i) => ({
    label: name,
    data: weeks.map(wk => {
      const r = (wk.platforms?.[platform]?.rankings || []).find(x => x.name === name);
      return r ? r.rank : null;
    }),
    borderColor: COLORS[i % COLORS.length],
    backgroundColor: COLORS[i % COLORS.length] + '22',
    borderWidth: 2,
    pointRadius: 4,
    spanGaps: false,
    tension: 0.3,
  }));

  // 重建 canvas（避免 Chart.js 舊實例衝突）
  if (_trendChart) { _trendChart.destroy(); _trendChart = null; }
  wrap.innerHTML = '<canvas id="trend-rank-canvas"></canvas>';
  const ctx = document.getElementById('trend-rank-canvas').getContext('2d');
  _trendChart = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          reverse: true,
          min: 1,
          max: 20,
          title: { display: true, text: '排名（Top 20）' },
          ticks: { stepSize: 2 },
        },
        x: { title: { display: true, text: '週次' } },
      },
      plugins: {
        legend: { position: 'right', labels: { boxWidth: 12, font: { size: 10 } } },
        tooltip: {
          callbacks: {
            label: ctx => ctx.parsed.y !== null
              ? `${ctx.dataset.label}：第 ${ctx.parsed.y} 名`
              : `${ctx.dataset.label}：未上榜`,
          },
        },
      },
    },
  });
}

function renderPersistentWinners() {
  const weeks = getTrendWeeks();
  const wrap = document.getElementById('trend-winners-wrap');
  if (!wrap) return;
  if (weeks.length < 2) {
    wrap.innerHTML = '<div class="text-gray-400 text-sm col-span-3">需要 ≥ 2 週資料</div>';
    return;
  }

  const PLATFORMS = ['PT','BP','CP','TCG','BAJI'];
  wrap.innerHTML = PLATFORMS.map(code => {
    const allNames = new Set();
    weeks.forEach(wk => {
      (wk.platforms?.[code]?.rankings || []).forEach(r => { if (r.name) allNames.add(r.name); });
    });
    const winners = [];
    allNames.forEach(name => {
      const ranks = weeks.map(wk => {
        const r = (wk.platforms?.[code]?.rankings || []).find(x => x.name === name);
        return r ? r.rank : null;
      });
      const appeared = ranks.filter(r => r !== null).length;
      if (appeared === weeks.length) {
        const avg = (ranks.reduce((s, r) => s + r, 0) / appeared).toFixed(1);
        winners.push({ name, ranks, avg: parseFloat(avg) });
      }
    });
    winners.sort((a, b) => a.avg - b.avg);

    if (!winners.length) return `
      <div class="bg-white border border-gray-200 rounded p-4">
        <h3 class="font-bold text-blue-900 mb-2">${code}</h3>
        <div class="text-gray-400 text-sm">暫無連續 ${weeks.length} 週全勤款</div>
      </div>`;

    return `
      <div class="bg-white border border-gray-200 rounded p-4">
        <h3 class="font-bold text-blue-900 mb-3">${code}
          <span class="text-xs font-normal text-gray-500">（${weeks.length} 週全勤 · ${winners.length} 款）</span>
        </h3>
        <table class="w-full text-sm">
          <thead><tr class="text-gray-500 text-xs border-b border-gray-200">
            <th class="text-left pb-1 pr-2">遊戲</th>
            <th class="text-center pb-1 pr-1">均排</th>
            ${weeks.map(wk => `<th class="text-center pb-1">W${wk.week}</th>`).join('')}
          </tr></thead>
          <tbody>
            ${winners.map(w => `
              <tr class="border-t border-gray-100 hover:bg-blue-50">
                <td class="py-1 pr-2 text-xs">${escapeHtml(w.name)}</td>
                <td class="py-1 text-center text-xs text-blue-700 font-semibold pr-1">#${w.avg}</td>
                ${w.ranks.map(r => `<td class="py-1 text-center text-xs font-medium ${r <= 5 ? 'text-green-600' : r <= 10 ? 'text-blue-600' : 'text-gray-600'}">${r}</td>`).join('')}
              </tr>`).join('')}
          </tbody>
        </table>
      </div>`;
  }).join('');
}

function renderEntryExit() {
  const weeks = getTrendWeeks();
  const wrap = document.getElementById('trend-entry-exit-wrap');
  if (!wrap) return;
  if (weeks.length < 2) {
    wrap.innerHTML = '<div class="text-gray-400 text-sm">需要 ≥ 2 週資料</div>';
    return;
  }

  const prevWk = weeks[weeks.length - 2];
  const curWk  = weeks[weeks.length - 1];
  const PLATFORMS = ['PT','BP','CP','TCG','BAJI'];

  const renderList = (names, rankMap, colorCls, arrow) =>
    names.length
      ? '<ul class="text-xs space-y-0.5 ml-1">' +
          names.slice(0, 10).map(n =>
            `<li class="${colorCls}">${arrow} ${escapeHtml(n)} <span class="text-gray-400">#${rankMap.get(n)}</span></li>`
          ).join('') +
          (names.length > 10 ? `<li class="text-gray-400">...還有 ${names.length - 10} 款</li>` : '') +
        '</ul>'
      : '<div class="text-gray-400 text-xs ml-1">無</div>';

  wrap.innerHTML = `
    <div class="text-sm text-gray-500 mb-3">
      比較 W${prevWk.week} (${prevWk.captureDate}) → W${curWk.week} (${curWk.captureDate})
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    ${PLATFORMS.map(code => {
      const prev = new Map((prevWk.platforms?.[code]?.rankings || []).map(r => [r.name, r.rank]));
      const cur  = new Map((curWk.platforms?.[code]?.rankings  || []).map(r => [r.name, r.rank]));
      const entered = [...cur.keys()].filter(n => !prev.has(n));
      const dropped = [...prev.keys()].filter(n => !cur.has(n));
      return `
        <div class="bg-white border border-gray-200 rounded p-4">
          <h3 class="font-bold text-blue-900 mb-3">${code}</h3>
          <div class="mb-3">
            <div class="text-xs font-semibold text-green-700 mb-1">▲ 新進榜（${entered.length}）</div>
            ${renderList(entered, cur, 'text-green-700', '▲')}
          </div>
          <div>
            <div class="text-xs font-semibold text-red-700 mb-1">▼ 掉出榜（${dropped.length}）</div>
            ${renderList(dropped, prev, 'text-red-700', '▼')}
          </div>
        </div>`;
    }).join('')}
    </div>`;
}
"""

OLD_CLOSE = '</script>\n</body>\n</html>'
assert OLD_CLOSE in html, '[FAIL] closing script sentinel not found'
html = html.replace(OLD_CLOSE, TREND_JS + '\n</script>\n</body>\n</html>', 1)
print('✅ 5. renderTrend / renderRankLineChart / renderPersistentWinners / renderEntryExit 注入')

# ──────────────────────────────────────────────
# 寫回
# ──────────────────────────────────────────────
with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print()
print('🎉 Phase 2E-A 完成！')
print('   → 開啟 index.html，切換到「📈 跨週趨勢」頁籤驗收')
print('   → 確認：折線圖 / 常勝軍 / 進出榜 三個區塊')
print('   → 無 F12 紅字後 git commit + push')
