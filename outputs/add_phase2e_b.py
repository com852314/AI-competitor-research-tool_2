#!/usr/bin/env python3
# Phase 2E-B: 廠家市占週週變化圖（Stacked Bar Chart）

HTML_PATH = r"D:\Claude Project\競品調研(排名)\index.html"

with open(HTML_PATH, encoding='utf-8') as f:
    html = f.read()

# ──────────────────────────────────────────────
# 1. 在 trend section 新增廠家市占區塊
# ──────────────────────────────────────────────
OLD_END = '''      <div id="trend-entry-exit-wrap"></div>
    </div>

  </div>
</section>'''

NEW_END = '''      <div id="trend-entry-exit-wrap"></div>
    </div>

    <!-- 廠家市占 -->
    <div>
      <h2 class="text-xl font-bold mb-3">🏢 廠家市占週週變化</h2>
      <div class="bg-white border border-gray-200 rounded p-4">
        <div class="flex flex-wrap items-center gap-3 mb-4">
          <label class="text-sm text-gray-600 font-medium">平台：</label>
          <select id="trend-vendor-platform-sel" class="border border-gray-300 rounded px-2 py-1 text-sm">
            <option value="PT">PT</option>
            <option value="BP">BP</option>
            <option value="CP">CP</option>
            <option value="TCG">TCG</option>
            <option value="BAJI">BAJI</option>
          </select>
          <label class="text-sm text-gray-600 font-medium ml-2">顯示方式：</label>
          <select id="trend-vendor-mode-sel" class="border border-gray-300 rounded px-2 py-1 text-sm">
            <option value="count">數量（款數）</option>
            <option value="pct">佔比（%）</option>
          </select>
        </div>
        <div id="trend-vendor-wrap" style="position:relative;height:360px;">
          <canvas id="trend-vendor-canvas"></canvas>
        </div>
        <p class="text-xs text-gray-400 mt-2">各週 Top 20 中每個廠家的上榜款數（或佔比）。僅顯示出現頻率前 10 名廠家，其餘歸入「其他」。</p>
      </div>
    </div>

  </div>
</section>'''

assert OLD_END in html, '[FAIL] trend section end sentinel not found'
html = html.replace(OLD_END, NEW_END, 1)
print('✅ 1. 廠家市占區塊 DOM 加入')

# ──────────────────────────────────────────────
# 2. renderTrend() 加 renderVendorShareTrend 呼叫
# ──────────────────────────────────────────────
OLD_RENDER = '''function renderTrend() {
  renderRankLineChart();
  renderPersistentWinners();
  renderEntryExit();'''

NEW_RENDER = '''function renderTrend() {
  renderRankLineChart();
  renderPersistentWinners();
  renderEntryExit();
  renderVendorShareTrend();'''

assert OLD_RENDER in html, '[FAIL] renderTrend sentinel not found'
html = html.replace(OLD_RENDER, NEW_RENDER, 1)
print('✅ 2. renderTrend() 加入 renderVendorShareTrend 呼叫')

# ──────────────────────────────────────────────
# 3. _trendBound 事件綁定加入廠家圖控制項
# ──────────────────────────────────────────────
OLD_BOUND = """    document.getElementById('trend-chart-btn')?.addEventListener('click', renderRankLineChart);
    document.getElementById('trend-platform-sel')?.addEventListener('change', renderRankLineChart);"""

NEW_BOUND = """    document.getElementById('trend-chart-btn')?.addEventListener('click', renderRankLineChart);
    document.getElementById('trend-platform-sel')?.addEventListener('change', renderRankLineChart);
    document.getElementById('trend-vendor-platform-sel')?.addEventListener('change', renderVendorShareTrend);
    document.getElementById('trend-vendor-mode-sel')?.addEventListener('change', renderVendorShareTrend);"""

assert OLD_BOUND in html, '[FAIL] _trendBound event sentinel not found'
html = html.replace(OLD_BOUND, NEW_BOUND, 1)
print('✅ 3. 廠家圖控制項事件綁定加入')

# ──────────────────────────────────────────────
# 4. 注入 renderVendorShareTrend 函式
# ──────────────────────────────────────────────
VENDOR_JS = r"""
function renderVendorShareTrend() {
  const weeks = getTrendWeeks();
  const wrap = document.getElementById('trend-vendor-wrap');
  if (!wrap) return;
  if (weeks.length < 2) {
    wrap.innerHTML = '<div class="text-gray-400 text-sm py-12 text-center">需要 ≥ 2 週資料</div>';
    return;
  }

  const platform = document.getElementById('trend-vendor-platform-sel')?.value || 'PT';
  const mode     = document.getElementById('trend-vendor-mode-sel')?.value || 'count';

  // 收集所有廠家出現頻次（跨所有週）
  const totalFreq = {};
  weeks.forEach(wk => {
    (wk.platforms?.[platform]?.rankings || []).forEach(r => {
      const v = r.vendor || '(未知)';
      totalFreq[v] = (totalFreq[v] || 0) + 1;
    });
  });

  // 取前 10 名廠家，其餘歸「其他」
  const TOP_N = 10;
  const sorted = Object.entries(totalFreq).sort((a, b) => b[1] - a[1]);
  const topVendors = sorted.slice(0, TOP_N).map(([v]) => v);
  const hasOther   = sorted.length > TOP_N;

  const COLORS = [
    '#2563EB','#DC2626','#16A34A','#CA8A04','#9333EA',
    '#0891B2','#EA580C','#4F46E5','#BE185D','#0D9488',
    '#9CA3AF', // 「其他」用灰色
  ];

  const labels = weeks.map(wk => `W${wk.week} (${wk.captureDate})`);

  const datasets = [
    ...topVendors.map((vendor, i) => ({
      label: vendor,
      data: weeks.map(wk => {
        const rankings = wk.platforms?.[platform]?.rankings || [];
        const cnt = rankings.filter(r => (r.vendor || '(未知)') === vendor).length;
        return mode === 'pct' ? (rankings.length ? +(cnt / rankings.length * 100).toFixed(1) : 0) : cnt;
      }),
      backgroundColor: COLORS[i % (COLORS.length - 1)],
      borderWidth: 0,
      stack: 'stack',
    })),
    ...(hasOther ? [{
      label: '其他',
      data: weeks.map(wk => {
        const rankings = wk.platforms?.[platform]?.rankings || [];
        const topSet = new Set(topVendors);
        const cnt = rankings.filter(r => !topSet.has(r.vendor || '(未知)')).length;
        return mode === 'pct' ? (rankings.length ? +(cnt / rankings.length * 100).toFixed(1) : 0) : cnt;
      }),
      backgroundColor: COLORS[COLORS.length - 1],
      borderWidth: 0,
      stack: 'stack',
    }] : []),
  ];

  if (window._trendVendorChart) { window._trendVendorChart.destroy(); window._trendVendorChart = null; }
  wrap.innerHTML = '<canvas id="trend-vendor-canvas"></canvas>';
  const ctx = document.getElementById('trend-vendor-canvas').getContext('2d');
  window._trendVendorChart = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { stacked: true, title: { display: true, text: '週次' } },
        y: {
          stacked: true,
          min: 0,
          title: { display: true, text: mode === 'pct' ? '佔比 (%)' : '上榜款數' },
          ...(mode === 'pct' ? { max: 100 } : {}),
        },
      },
      plugins: {
        legend: { position: 'right', labels: { boxWidth: 12, font: { size: 10 } } },
        tooltip: {
          callbacks: {
            label: ctx => mode === 'pct'
              ? `${ctx.dataset.label}：${ctx.parsed.y}%`
              : `${ctx.dataset.label}：${ctx.parsed.y} 款`,
          },
        },
      },
    },
  });
}
"""

OLD_CLOSE = '</script>\n</body>\n</html>'
assert OLD_CLOSE in html, '[FAIL] closing script sentinel not found'
html = html.replace(OLD_CLOSE, VENDOR_JS + '\n</script>\n</body>\n</html>', 1)
print('✅ 4. renderVendorShareTrend 函式注入')

# ──────────────────────────────────────────────
# 寫回
# ──────────────────────────────────────────────
with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print()
print('Phase 2E-B 完成！')
print('   -> 開啟 index.html，切換到「跨週趨勢」頁籤')
print('   -> 確認最下方「廠家市占週週變化」Stacked Bar Chart')
print('   -> 可切換平台 / 數量 vs 佔比')
print('   -> 無 F12 紅字後 git commit + push')
