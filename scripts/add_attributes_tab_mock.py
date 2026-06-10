"""
注入「🔬 遊戲屬性」分析頁籤（Mock v2）
- 分析對象：實際上榜 Top 20 的遊戲（加上屬性資料後）
- 篩選維度：平台 + 週次多選
- 圖表：波動度分布、主題、玩法功能、週次趨勢、上市年份
"""

INDEX_PATH = r"D:\Claude Project\競品調研(排名)\index.html"

with open(INDEX_PATH, encoding="utf-8") as f:
    html = f.read()

# ── 移除舊版 Mock Tab（若存在）──────────────────────────────────
import re
html = re.sub(
    r'\n  <!-- Attributes Tab \(mock\) -->.*?</section>\n',
    '\n',
    html,
    flags=re.DOTALL
)
# 移除舊版 JS
html = re.sub(
    r'\n// ===== 遊戲屬性分析 Tab（Mock 版）=====\n\(function.*?\}\)\(\);\n',
    '\n',
    html,
    flags=re.DOTALL
)
# 移除舊版 tab 按鈕（若已注入）
html = html.replace(
    '\n    <button class="tab-btn px-4 py-2 text-sm font-medium border-b-2 '
    'border-transparent text-gray-500 hover:text-gray-800" data-tab="attributes">🔬 遊戲屬性</button>',
    ''
)

# ── 1. Tab 按鈕 ─────────────────────────────────────────────────
TAB_BTN_OLD = (
    '<button class="tab-btn px-4 py-2 text-sm font-medium border-b-2 '
    'border-transparent text-gray-500 hover:text-gray-800" data-tab="trend">📈 跨週趨勢</button>'
)
TAB_BTN_NEW = (
    TAB_BTN_OLD + "\n"
    '    <button class="tab-btn px-4 py-2 text-sm font-medium border-b-2 '
    'border-transparent text-gray-500 hover:text-gray-800" data-tab="attributes">🔬 遊戲屬性</button>'
)
assert TAB_BTN_OLD in html, "找不到 trend tab 按鈕"
html = html.replace(TAB_BTN_OLD, TAB_BTN_NEW, 1)

# ── 2. Tab HTML ──────────────────────────────────────────────────
ATTR_HTML = """
  <!-- Attributes Tab (mock) -->
  <section id="tab-attributes" class="tab-content hidden">
    <div class="max-w-6xl mx-auto space-y-5">

      <!-- 篩選列 -->
      <div class="bg-white rounded border border-gray-200 p-3 flex flex-wrap gap-4 items-center">
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-gray-600">平台</span>
          <select id="attr-platform" class="border border-gray-300 rounded px-2 py-1 text-sm">
            <option value="ALL">全部平台</option>
            <option value="PT">PT Gaming</option>
            <option value="BP">BingoPlus</option>
            <option value="CP">Casino Plus</option>
            <option value="TCG">Luckyi (TCG)</option>
            <option value="BAJI">Baji</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-gray-600">週次</span>
          <div id="attr-week-btns" class="flex gap-1">
            <button class="attr-week-btn selected px-2 py-1 text-xs rounded border border-blue-500 bg-blue-50 text-blue-700" data-week="W1">W1</button>
            <button class="attr-week-btn selected px-2 py-1 text-xs rounded border border-blue-500 bg-blue-50 text-blue-700" data-week="W2">W2</button>
            <button class="attr-week-btn selected px-2 py-1 text-xs rounded border border-blue-500 bg-blue-50 text-blue-700" data-week="W3">W3</button>
            <button class="attr-week-btn selected px-2 py-1 text-xs rounded border border-blue-500 bg-blue-50 text-blue-700" data-week="W4">W4</button>
            <button class="attr-week-btn selected px-2 py-1 text-xs rounded border border-blue-500 bg-blue-50 text-blue-700" data-week="W5">W5</button>
          </div>
        </div>
        <span id="attr-filter-label" class="text-xs text-gray-400 ml-auto">⚠ Mock 資料</span>
      </div>

      <!-- 摘要卡片 -->
      <div class="grid grid-cols-4 gap-3">
        <div class="bg-white rounded border border-gray-200 p-3 text-center">
          <div class="text-2xl font-bold text-blue-600" id="attr-stat-appearances">—</div>
          <div class="text-xs text-gray-500 mt-1">上榜次數（去重前）</div>
        </div>
        <div class="bg-white rounded border border-gray-200 p-3 text-center">
          <div class="text-2xl font-bold text-indigo-600" id="attr-stat-unique">—</div>
          <div class="text-xs text-gray-500 mt-1">不重複遊戲款數</div>
        </div>
        <div class="bg-white rounded border border-gray-200 p-3 text-center">
          <div class="text-2xl font-bold text-green-600" id="attr-stat-rtp">—</div>
          <div class="text-xs text-gray-500 mt-1">平均 RTP</div>
        </div>
        <div class="bg-white rounded border border-gray-200 p-3 text-center">
          <div class="text-2xl font-bold text-orange-500" id="attr-stat-new-ratio">—</div>
          <div class="text-xs text-gray-500 mt-1">近 2 年新遊戲佔比</div>
        </div>
      </div>

      <!-- 波動度 + 上市年份 -->
      <div class="grid grid-cols-2 gap-4">
        <div class="bg-white rounded border border-gray-200 p-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3">波動度分布</h3>
          <div style="position:relative;height:210px;"><canvas id="attr-vol-canvas"></canvas></div>
        </div>
        <div class="bg-white rounded border border-gray-200 p-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3">上市年份分布（Top 20 上榜款）</h3>
          <div style="position:relative;height:210px;"><canvas id="attr-year-canvas"></canvas></div>
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

      <!-- 波動度週次趨勢 -->
      <div class="bg-white rounded border border-gray-200 p-4">
        <h3 class="text-sm font-semibold text-gray-700 mb-1">波動度趨勢（週次）</h3>
        <p class="text-xs text-gray-400 mb-3">Top 20 上榜遊戲中，各波動度佔比隨時間變化</p>
        <div style="position:relative;height:240px;"><canvas id="attr-trend-canvas"></canvas></div>
      </div>

      <p class="text-xs text-gray-400 text-center pb-2">⚠ 此頁籤目前使用模擬資料，待 attributes.json 建立後將自動切換為真實資料。</p>
    </div>
  </section>
"""

assert "</body>" in html
html = html.replace("</body>", ATTR_HTML + "\n</body>", 1)

# ── 3. JS ────────────────────────────────────────────────────────
ATTR_JS = r"""
// ===== 遊戲屬性分析 Tab（Mock v2）=====
(function () {

// ── Mock 資料：每個平台 × 週次的聚合分布（Top 20 上榜遊戲屬性）
// 結構：{ appearances, unique, rtp, newRatio, volatility{}, themes[], features[], yearDist{} }
const BASE = {
  PT: {
    rtp: 96.4, newRatio: 0.28,
    volatility: { High:8, "Med-High":3, Med:6, "Low-Med":3, Low:0 },
    themes: [["Asian",14],["Card",10],["Classic",8],["Fantasy",5],["Animal",4],["Adventure",3],["Western",2],["Mythology",2],["Fruit",1],["Horror",1],["Egyptian",1],["Others",3]],
    features: [["Wild",20],["Free Spins",18],["Scatter",18],["Multiplier",16],["Free Spins Multiplier",12],["Buy Feature",6],["Cascading",7],["Expanding Wild",5],["Sticky Wild",4],["Bonus Game",3],["Hold & Win",2],["Jackpot",2]],
    yearDist: {"2021":4,"2022":5,"2023":6,"2024":4,"2025":1},
  },
  BP: {
    rtp: 95.6, newRatio: 0.10,
    volatility: { High:2, "Med-High":2, Med:5, "Low-Med":9, Low:2 },
    themes: [["Classic",10],["Asian",5],["Western",4],["Animal",4],["Card",2],["Nature",2],["Fantasy",2],["Sports",1],["Mythology",1],["Fruit",1],["Adventure",1],["Others",3]],
    features: [["Wild",20],["Scatter",18],["Free Spins",15],["Multiplier",13],["Expanding Wild",8],["Sticky Wild",6],["Bonus Game",5],["Hold & Win",4],["Respins",4],["Tumble",3],["Free Spins Multiplier",3],["Buy Feature",1]],
    yearDist: {"2020":3,"2021":6,"2022":5,"2023":4,"2024":2,"2025":0},
  },
  CP: {
    rtp: 96.1, newRatio: 0.25,
    volatility: { High:9, "Med-High":3, Med:5, "Low-Med":2, Low:1 },
    themes: [["Asian",15],["Card",8],["Classic",6],["Fantasy",4],["Horror",3],["Western",2],["Mythology",2],["Adventure",2],["Animal",1],["Fruit",1],["Others",3]],
    features: [["Wild",20],["Free Spins",19],["Scatter",18],["Multiplier",16],["Free Spins Multiplier",13],["Buy Feature",8],["Cascading",6],["Expanding Wild",5],["Sticky Wild",3],["Bonus Game",2],["Hold & Win",2],["Jackpot",1]],
    yearDist: {"2021":5,"2022":6,"2023":5,"2024":3,"2025":1},
  },
  TCG: {
    rtp: 96.9, newRatio: 0.35,
    volatility: { High:11, "Med-High":4, Med:4, "Low-Med":1, Low:0 },
    themes: [["Asian",10],["Fantasy",7],["Classic",5],["Western",4],["Animal",4],["Mythology",3],["Adventure",3],["Card",2],["Nature",2],["Egyptian",2],["Horror",1],["Others",3]],
    features: [["Wild",20],["Free Spins",19],["Scatter",18],["Multiplier",17],["Buy Feature",11],["Cascading",10],["Free Spins Multiplier",9],["Avalanche",8],["Expanding Wild",6],["RTP Range",5],["Gonzo mechanic",5],["Sticky Wild",3]],
    yearDist: {"2021":2,"2022":4,"2023":6,"2024":6,"2025":2},
  },
  BAJI: {
    rtp: 95.8, newRatio: 0.30,
    volatility: { High:5, "Med-High":2, Med:6, "Low-Med":3, Low:0 },
    themes: [["Classic",8],["Asian",7],["Fantasy",4],["Animal",4],["Egyptian",3],["Adventure",2],["Mythology",2],["Card",2],["Horror",1],["Western",1],["Nature",1],["Others",3]],
    features: [["Wild",18],["Free Spins",16],["Scatter",16],["Multiplier",14],["Free Spins Multiplier",10],["Expanding Wild",7],["Bonus Game",6],["Sticky Wild",5],["Buy Feature",4],["Hold & Win",3],["Cascading",3],["Jackpot",2]],
    yearDist: {"2020":2,"2021":4,"2022":5,"2023":5,"2024":3,"2025":1},
  },
};

// 週次趨勢 mock（各平台 High% 隨週次）
const VOL_TREND = {
  ALL:  { High:[36,37,38,36,39], Med:[37,36,35,37,35], Low:[27,27,27,27,26] },
  PT:   { High:[40,41,42,40,43], Med:[33,32,32,33,32], Low:[27,27,26,27,25] },
  BP:   { High:[10,11,10,11,10], Med:[30,30,31,30,30], Low:[60,59,59,59,60] },
  CP:   { High:[45,45,46,44,46], Med:[28,28,27,28,27], Low:[27,27,27,28,27] },
  TCG:  { High:[52,54,55,53,57], Med:[24,23,23,24,22], Low:[24,23,22,23,21] },
  BAJI: { High:[26,27,28,27,29], Med:[38,37,37,38,37], Low:[36,36,35,35,34] },
};

const WEEKS = ["W1","W2","W3","W4","W5"];
const VOL_COLORS = { High:"#ef4444","Med-High":"#f97316",Med:"#eab308","Low-Med":"#22c55e",Low:"#3b82f6" };
let _charts = {};
let _attrRendered = false;

function getSelectedWeeks() {
  return [...document.querySelectorAll(".attr-week-btn.selected")].map(b => b.dataset.week);
}

function getSelectedPlatform() {
  return document.getElementById("attr-platform").value;
}

function computeAgg(platform, weeks) {
  const platforms = platform === "ALL" ? Object.keys(BASE) : [platform];
  const weekCount = weeks.length;
  const platCount = platforms.length;

  // 累加（每週每平台 20 場上榜）
  const vol = {};
  const themeMap = {};
  const featMap = {};
  const yearMap = {};
  let rtpSum = 0, newRatioSum = 0, count = 0;

  platforms.forEach(p => {
    const d = BASE[p];
    rtpSum += d.rtp;
    newRatioSum += d.newRatio;
    count++;
    // vol
    Object.entries(d.volatility).forEach(([k,v]) => { vol[k] = (vol[k]||0) + v * weekCount; });
    // theme (take top 12, scale by weekCount)
    d.themes.forEach(([name, cnt]) => { themeMap[name] = (themeMap[name]||0) + cnt * weekCount; });
    // features
    d.features.forEach(([name, cnt]) => { featMap[name] = (featMap[name]||0) + cnt * weekCount; });
    // year
    Object.entries(d.yearDist).forEach(([yr, cnt]) => { yearMap[yr] = (yearMap[yr]||0) + cnt * weekCount; });
  });

  const appearances = Object.values(vol).reduce((a,b)=>a+b,0);
  const unique = Math.round(appearances * 0.55); // 假設約 55% 去重率
  const rtp = rtpSum / count;
  const newRatio = newRatioSum / count;

  const themes = Object.entries(themeMap).sort((a,b)=>b[1]-a[1]).slice(0,12);
  const features = Object.entries(featMap).sort((a,b)=>b[1]-a[1]).slice(0,12);
  const years = Object.entries(yearMap).sort((a,b)=>a[0]>b[0]?1:-1);

  return { appearances, unique, rtp, newRatio, vol, themes, features, years };
}

function destroyChart(id) {
  if (_charts[id]) { _charts[id].destroy(); _charts[id] = null; }
}

function rebuildCanvas(id) {
  const wrap = document.getElementById(id).parentElement;
  destroyChart(id);
  wrap.innerHTML = `<canvas id="${id}"></canvas>`;
}

function renderAll() {
  const platform = getSelectedPlatform();
  const weeks = getSelectedWeeks();
  if (!weeks.length) return;

  const d = computeAgg(platform, weeks);

  // 摘要
  document.getElementById("attr-stat-appearances").textContent = d.appearances.toLocaleString();
  document.getElementById("attr-stat-unique").textContent = d.unique + " 款";
  document.getElementById("attr-stat-rtp").textContent = d.rtp.toFixed(1) + "%";
  document.getElementById("attr-stat-new-ratio").textContent = Math.round(d.newRatio * 100) + "%";
  document.getElementById("attr-filter-label").textContent =
    `⚠ Mock｜${platform === "ALL" ? "全平台" : platform} × W${weeks.map(w=>w.replace("W","")).join("/")}`;

  // 波動度
  rebuildCanvas("attr-vol-canvas");
  _charts["attr-vol-canvas"] = new Chart(document.getElementById("attr-vol-canvas"), {
    type: "pie",
    data: {
      labels: Object.keys(d.vol),
      datasets: [{ data: Object.values(d.vol),
        backgroundColor: Object.keys(d.vol).map(k=>VOL_COLORS[k]||"#d1d5db"), borderWidth:1 }]
    },
    options: { responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ position:"right", labels:{ font:{size:11} } } } }
  });

  // 上市年份
  rebuildCanvas("attr-year-canvas");
  _charts["attr-year-canvas"] = new Chart(document.getElementById("attr-year-canvas"), {
    type: "bar",
    data: {
      labels: d.years.map(y=>y[0]),
      datasets: [{ label:"款數", data: d.years.map(y=>y[1]),
        backgroundColor: d.years.map(y => parseInt(y[0])>=2024?"#6366f1":"#93c5fd"),
        borderRadius:3 }]
    },
    options: { responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false},
        tooltip:{ callbacks:{ label: ctx => ctx.raw + " 款" } } },
      scales:{ x:{grid:{display:false}}, y:{beginAtZero:true} } }
  });

  // 主題
  const thSorted = [...d.themes].sort((a,b)=>a[1]-b[1]);
  rebuildCanvas("attr-theme-canvas");
  _charts["attr-theme-canvas"] = new Chart(document.getElementById("attr-theme-canvas"), {
    type:"bar",
    data:{ labels:thSorted.map(t=>t[0]),
      datasets:[{ label:"上榜次數", data:thSorted.map(t=>t[1]),
        backgroundColor:"#f59e0b", borderRadius:3 }] },
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
      datasets:[{ label:"上榜次數", data:ftSorted.map(f=>f[1]),
        backgroundColor:"#10b981", borderRadius:3 }] },
    options:{ indexAxis:"y", responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false} },
      scales:{ x:{beginAtZero:true}, y:{ticks:{font:{size:11}}} } }
  });

  // 波動度趨勢
  const trend = VOL_TREND[platform] || VOL_TREND["ALL"];
  const selectedIdxs = weeks.map(w => WEEKS.indexOf(w)).filter(i=>i>=0);
  const tLabels = selectedIdxs.map(i=>"W"+(i+1));
  rebuildCanvas("attr-trend-canvas");
  _charts["attr-trend-canvas"] = new Chart(document.getElementById("attr-trend-canvas"), {
    type:"line",
    data:{
      labels: tLabels,
      datasets:[
        { label:"High %", data:selectedIdxs.map(i=>trend.High[i]),
          borderColor:"#ef4444", backgroundColor:"rgba(239,68,68,0.08)", tension:0.3, fill:false, pointRadius:4 },
        { label:"Med %",  data:selectedIdxs.map(i=>trend.Med[i]),
          borderColor:"#eab308", backgroundColor:"rgba(234,179,8,0.08)",  tension:0.3, fill:false, pointRadius:4 },
        { label:"Low %",  data:selectedIdxs.map(i=>trend.Low[i]),
          borderColor:"#3b82f6", backgroundColor:"rgba(59,130,246,0.08)", tension:0.3, fill:false, pointRadius:4 },
      ]
    },
    options:{ responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ position:"bottom", labels:{font:{size:11}} },
        tooltip:{ callbacks:{ label: ctx => ctx.dataset.label+": "+ctx.raw+"%" } } },
      scales:{ y:{ min:0, max:70, ticks:{ callback: v=>v+"%" } },
               x:{ grid:{display:false} } } }
  });
}

function initAttributesTab() {
  if (_attrRendered) return;
  _attrRendered = true;

  // 週次按鈕 toggle
  document.querySelectorAll(".attr-week-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      btn.classList.toggle("selected");
      const isOn = btn.classList.contains("selected");
      btn.classList.toggle("border-blue-500", isOn);
      btn.classList.toggle("bg-blue-50", isOn);
      btn.classList.toggle("text-blue-700", isOn);
      btn.classList.toggle("border-gray-300", !isOn);
      btn.classList.toggle("text-gray-400", !isOn);
      renderAll();
    });
  });

  document.getElementById("attr-platform").addEventListener("change", renderAll);

  renderAll();
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      if (btn.dataset.tab === "attributes") initAttributesTab();
    });
  });
});

})();
"""

last_script = html.rfind("</script>")
assert last_script != -1
html = html[:last_script] + ATTR_JS + "\n" + html[last_script:]

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✓ 遊戲屬性頁籤 Mock v2 注入完成（{len(html):,} chars）")
