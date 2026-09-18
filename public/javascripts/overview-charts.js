/* ============================================================
   概览图表：人物关系图谱（力导向）+ 篇章×势力旭日图
   —— 数据全部复用主页面运行时已有的 INDEX / REFS / ENTRY_BY_KEY /
      REF_SCORE / CHAPTERS / DATA / baseName，不另造一份；
      篇章配色也取自 CHAPTERS 声明的 CSS 变量（canvas 读不了 var()，
      故用 getComputedStyle 解析成具体色值）。
      折叠区样式在 cultivation.css 的「概览图表」段。
   脚本在 </body> 前加载，DOM 与主 script 数据均已就绪，直接同步初始化。
   ============================================================ */
(function () {
  'use strict';

  if (typeof echarts === 'undefined') return;

  var MIN_REF = 3;   /* 基础名级被引≥3：跨篇合并后约 34 人，覆盖全部核心角色 */

  /* 篇章的顺序与配色只有一个来源：CHAPTERS（其 color 形如 var(--c1)）。
     页面调整篇章色时，两张图自动跟随，不必再维护第二份色值。 */
  var rootCS = getComputedStyle(document.documentElement);
  var ARCS = CHAPTERS.map(function (ch) {
    var m = /var\((--[\w-]+)\)/.exec(ch.color || '');
    return { name: ch.name, color: m ? rootCS.getPropertyValue(m[1]).trim() : '' };
  });
  var ARC_COLOR = {};
  ARCS.forEach(function (a) { ARC_COLOR[a.name] = a.color; });

  /* ECharts 的 legend.data 与 series.categories 形状相同，共用一份生成 */
  function arcItems() {
    return ARCS.map(function (a) { return { name: a.name, itemStyle: { color: a.color } }; });
  }

  var tip = { backgroundColor: '#161b24', borderColor: '#3a4356', textStyle: { color: '#e8e3d8', fontSize: 12 } };

  /* ================= 数据：人物关系图 ================= */
  /* 节点 = 基础名（跨篇同名合并），边 = 基础名级互引 */
  function buildGraphData() {
    var recs = INDEX.filter(function (e) { return e.lib === 'chars'; });

    /* 1) 节点：首个记录决定篇章归属与被引数（跨篇取先出现的一篇） */
    var baseMap = new Map();
    recs.forEach(function (e) {
      var b = baseName(e.name);
      var o = baseMap.get(b);
      if (!o) baseMap.set(b, o = { name: b, firstArc: e.tag, ref: REF_SCORE[e.key] || 0, recs: [] });
      o.recs.push(e);
    });
    var nodes = [...baseMap.values()]
      .filter(function (n) { return n.ref >= MIN_REF; })
      .map(function (n) {
        /* 跳转 key 取各篇记录中被引最高的一张（主卡） */
        var main = n.recs.reduce(function (a, b) {
          return (REF_SCORE[b.key] || 0) > (REF_SCORE[a.key] || 0) ? b : a;
        });
        return {
          name: n.name, value: n.ref, category: n.firstArc, key: main.key,
          symbolSize: Math.max(16, Math.min(64, 10 + Math.sqrt(n.ref) * 5)),
          title: main.sub || ''
        };
      });
    var nodeSet = new Set(nodes.map(function (n) { return n.name; }));

    /* 2) 边：两端都在图里才计入；同一条边双向提及只累计权重 */
    var edgeMap = new Map();
    recs.forEach(function (e) {
      var me = baseName(e.name);
      REFS[e.key].out.forEach(function (k) {
        var tgt = ENTRY_BY_KEY[k];
        if (!tgt) return;
        var other = baseName(tgt.name);
        if (me === other || !nodeSet.has(me) || !nodeSet.has(other)) return;
        var lo = me < other ? me : other;
        var hi = me < other ? other : me;
        var key = lo + '\u0000' + hi;   /* 名字里不会出现的分隔符，免得歧义 */
        var edge = edgeMap.get(key) || { source: lo, target: hi, w: 0 };
        edge.w += 1;
        edgeMap.set(key, edge);
      });
    });
    return { nodes: nodes, links: [...edgeMap.values()] };
  }

  /* ================= 数据：旭日图 篇章×势力 ================= */
  var TOP_CAMPS = 6;   /* 每篇单列前若干势力，其余并成「其他」 */
  function buildSunData() {
    var children = CHAPTERS.map(function (ch) {
      var byCamp = {};
      DATA[ch.id].forEach(function (c) {
        var camp = c.camp || '未注明';
        byCamp[camp] = (byCamp[camp] || 0) + 1;
      });
      var dist = Object.entries(byCamp).sort(function (a, b) { return b[1] - a[1]; });
      var color = ARC_COLOR[ch.name];
      /* 内圈势力扇区与外圈篇章同色，靠明度/层次区分 */
      var kids = dist.slice(0, TOP_CAMPS).map(function (x) {
        return { name: x[0], value: x[1], itemStyle: { color: color } };
      });
      var rest = dist.slice(TOP_CAMPS).reduce(function (s, x) { return s + x[1]; }, 0);
      if (rest > 0) kids.push({ name: '其他', value: rest, itemStyle: { color: color } });
      return { name: ch.name, itemStyle: { color: color }, children: kids };
    });
    return { name: '全书人物', children: children };
  }

  /* ================= 渲染 ================= */
  var graphInst = null, sunInst = null;
  var graphInited = false, sunInited = false;
  var graphNodes = [], graphLinks = [];   /* 全量数据，按篇章分批并入 */

  /* 三处（视图切换、load 后补帧、窗口 resize）都是同一件事，只写一份 */
  function resizeAll() {
    if (sunInst) sunInst.resize();
    if (graphInst) graphInst.resize();
  }

  function initGraph() {
    if (graphInited) return;
    var el = document.getElementById('chart-graph');
    if (!el || el.clientWidth === 0) return;
    graphInited = true;
    var d = buildGraphData();
    graphNodes = d.nodes;
    graphLinks = d.links;
    var nEl = document.getElementById('graph-core-n');
    if (nEl) nEl.textContent = d.nodes.length;

    graphInst = echarts.init(el);
    /* 初始：空 series，节点随后按篇章批次生长进入 */
    graphInst.setOption({
      backgroundColor: 'transparent',
      tooltip: Object.assign({
        formatter: function (p) {
          if (p.dataType !== 'node') return '';
          var x = p.data;
          return '<b style="color:#d4af6a">' + x.name + '</b><br>被引 ' + x.value
            + (x.title ? '<br>身份：' + x.title : '')
            + '<br>篇章：' + x.category;
        }
      }, tip),
      legend: {
        data: arcItems(),
        bottom: 2, textStyle: { color: '#cfc9ba', fontSize: 11 }, icon: 'circle', itemWidth: 9, itemHeight: 9
      },
      series: [{
        type: 'graph', layout: 'force',
        roam: 'move',                  /* 只允许拖拽平移，禁滚轮缩放，避免和页面滚动冲突 */
        draggable: true,
        top: 24, bottom: 56, left: 24, right: 24,   /* 四周留白：上方及两侧给节点、下方给图例 */
        /* 力导向的落点由力平衡决定，上面四个参数管不住它：边缘节点仍会贴边被裁，
           整体缩一点让四周留出余量（标签随之略小，仍可读） */
        zoom: 0.86,
        categories: arcItems(),
        force: { repulsion: 620, edgeLength: [70, 150], gravity: 0.1, friction: 0.6, layoutAnimation: true },
        /* 34 个标签必然互相压住：交给 LabelLayout 自动避让，挤不下的先藏起来 */
        labelLayout: { hideOverlap: true },
        label: { show: true, fontSize: 10.5, color: '#d8d2c2' },
        emphasis: { focus: 'adjacency', label: { fontSize: 13, color: '#d4af6a', fontWeight: 'bold' } },
        lineStyle: { color: '#8a7a52', curveness: 0.1, opacity: 0.25, width: 0.8 },
        emphasisLineStyle: { color: '#d4af6a', opacity: 0.8, width: 1.6 },
        data: [], links: []
      }]
    }, true);

    /* 节点点击 -> 跳转人物卡（通过 hash 路由触发主页面 gotoEntry） */
    graphInst.on('click', function (params) {
      if (params.dataType === 'node' && params.data.key) {
        location.hash = 'v-chars/' + params.data.key;
      }
    });

    /* 折叠/展开后 resize */
    var fold = el.closest('details.graph-fold');
    if (fold) {
      fold.addEventListener('toggle', function () {
        setTimeout(function () { graphInst.resize(); }, 60);
      });
    }

    /* 分批生长：按篇章依次把节点/边并入，制造"关系网逐卷展开"的过程感 */
    revealByArc();
  }

  /* 按篇章批次把节点/边并入图中，制造「关系网逐卷展开」的过程感 */
  var REVEAL_MS = 450;
  function revealByArc() {
    var shown = [];            /* 已入图节点；每批换新数组，ECharts 才会重算 */
    var shownLinks = [];
    var shownPairs = new Set(); /* 已入图的边（两端名+分隔符），防重复 */
    var i = 0;
    function step() {
      if (i >= ARCS.length) return;
      var arc = ARCS[i].name;
      shown = shown.concat(graphNodes.filter(function (n) { return n.category === arc; }));
      var names = new Set(shown.map(function (n) { return n.name; }));
      graphLinks.forEach(function (l) {
        var pair = l.source + '\u0000' + l.target;
        if (shownPairs.has(pair) || !names.has(l.source) || !names.has(l.target)) return;
        shownPairs.add(pair);
        shownLinks.push(l);
      });
      graphInst.setOption({ series: [{ data: shown, links: shownLinks.slice() }] });
      i++;
      if (i < ARCS.length) setTimeout(step, REVEAL_MS);
    }
    step();
  }

  function initSun() {
    if (sunInited) return;
    var el = document.getElementById('chart-sunburst');
    if (!el || el.clientWidth === 0) return;
    sunInited = true;
    sunInst = echarts.init(el);
    sunInst.setOption({
      backgroundColor: 'transparent',
      tooltip: Object.assign({
        formatter: function (p) {
          return '<b style="color:#d4af6a">' + p.data.name + '</b><br>收录 ' + p.data.value + ' 人';
        }
      }, tip),
      series: [{
        type: 'sunburst',
        data: [buildSunData()],
        radius: ['15%', '85%'],
        nodeClick: 'zoomToNode',
        /* 分层拉开层次：外圈是篇章（原色 + 粗边界），内圈是势力（同色压暗一档） */
        levels: [
          { label: { show: false } },   /* root 标签挤在中心洞里读不了，语义交给页面标题 */
          { itemStyle: { borderWidth: 2 } },
          { itemStyle: { borderWidth: 1, opacity: 0.7 } }
        ],
        label: { show: true, fontSize: 10, color: '#e8e3d8', minAngle: 7 },
        emphasis: { focus: 'ancestor' },
        itemStyle: { borderColor: '#0f1218', borderWidth: 1.5 }
      }]
    }, true);
  }

  /* 视图激活时懒初始化 + 校正 canvas 尺寸 */
  function sync() {
    var active = document.querySelector('.view.active');
    if (!active) return;
    if (active.id === 'v-home') initSun();
    else if (active.id === 'v-chars') initGraph();
    resizeAll();
    /* 视图切换自带过渡，稍后再对齐一次初始 canvas 尺寸 */
    setTimeout(resizeAll, 200);
  }

  /* 脚本在 </body> 前，DOM 与主页面数据均已就绪；等 window load 后再初始化，
     保证布局完成、canvas 尺寸正确 */
  function boot() {
    sync();
    setTimeout(resizeAll, 300);   /* 字体与布局稳定后再补一次 */
  }
  if (document.readyState === 'complete') {
    boot();
  } else {
    window.addEventListener('load', boot);
  }
  window.addEventListener('hashchange', function () {
    setTimeout(sync, 80);
  }, { passive: true });
  window.addEventListener('resize', resizeAll);
})();
