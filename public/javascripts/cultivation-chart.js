/* ============================================================
   境界数据可视化（战力 / 寿元 共用同一套渲染）
   —— 一个 [data-cultivation] 容器 = 一张图，指标由 data-metric 指定。

   机制：一根滑块控制「刻度顶点」，即当前 100% 代表哪个境界。
   柱长 = 该境界数值相对顶点的线性占比，所以：
     · 顶点越低，画面里的境界越少、细节越清楚；
     · 顶点越高，低境界等比缩窄，最终归零消失。
   每个境界用 { lo, hi } 描述数值，支持区间（如灵界寿元为预估区间，
   此时柱体从 lo 画到 hi，而非从 0 起）。

   想加新指标：往 METRICS 里加一项即可，不必改渲染逻辑。
   ============================================================ */
(function () {
  'use strict';

  /* 境界结构依起点官方资源站：炼气 1–13 层，筑基以上分初/中/后/大圆满，
     渡劫为大乘后的飞升环节而非独立境界，道祖无内部细分 */
  var REALM = [
    { name: '炼气期', world: 'ren',  exp: 0 },
    { name: '筑基期', world: 'ren',  exp: 1 },
    { name: '结丹期', world: 'ren',  exp: 2 },
    { name: '元婴期', world: 'ren',  exp: 3 },
    { name: '化神期', world: 'ren',  exp: 4 },
    { name: '炼虚期', world: 'ling', exp: 5 },
    { name: '合体期', world: 'ling', exp: 6 },
    { name: '大乘期', world: 'ling', exp: 7 },
    { name: '真仙境', world: 'xian', exp: 8 },
    { name: '金仙境', world: 'xian', exp: 9 },
    { name: '太乙境', world: 'xian', exp: 10 },
    { name: '大罗境', world: 'xian', exp: 11 },
    { name: '道祖境', world: 'xian', exp: 12 }
  ];

  var TOP = REALM.length - 1;      // 滑块上限（道祖境）
  var START = 4;                   // 默认顶点：化神期，此时画面恰为人界五境
  var STEP_MS = 260;               // 自动播放步进
  var AXIS = ['0', '25%', '50%', '75%', '100%'];

  /* 相对炼气一层的战力倍数写法 */
  var READ = ['×1', '×10', '×100', '×1000', '×1万', '×10万', '×100万',
              '×1000万', '×1亿', '×10亿', '×100亿', '×1000亿', '×1万亿'];

  /* 换算器用的细分境界（含小阶段），value 为相对炼气一层的战力估值。
     跨大境界约 ×10、同境界内约 ×3~4，为综合流传口径的估值模型，非官方。 */
  var COMPARE = [
    { name: '炼气初期（1–4 层）', world: 'ren',  value: 0.5 },
    { name: '炼气中期（5–9 层）', world: 'ren',  value: 0.8 },
    { name: '炼气后期（10–13 层）', world: 'ren', value: 1 },
    { name: '筑基初期', world: 'ren',  value: 3 },
    { name: '筑基中期', world: 'ren',  value: 6 },
    { name: '筑基后期', world: 'ren',  value: 10 },
    { name: '筑基大圆满（假丹）', world: 'ren', value: 12 },
    { name: '结丹初期', world: 'ren',  value: 100 },
    { name: '结丹中期', world: 'ren',  value: 200 },
    { name: '结丹后期', world: 'ren',  value: 600 },
    { name: '结丹大圆满', world: 'ren',  value: 800 },
    { name: '元婴初期', world: 'ren',  value: 6000 },
    { name: '元婴中期', world: 'ren',  value: 18000 },
    { name: '元婴后期', world: 'ren',  value: 72000 },
    { name: '元婴大圆满', world: 'ren',  value: 90000 },
    { name: '化神初期', world: 'ren',  value: 720000 },
    { name: '化神中期', world: 'ren',  value: 1440000 },
    { name: '化神后期', world: 'ren',  value: 4320000 },
    { name: '化神大圆满', world: 'ren',  value: 5400000 },
    { name: '炼虚初期', world: 'ling', value: 54000000 },
    { name: '炼虚中期', world: 'ling', value: 108000000 },
    { name: '炼虚后期', world: 'ling', value: 324000000 },
    { name: '炼虚大圆满', world: 'ling', value: 405000000 },
    { name: '合体初期', world: 'ling', value: 4050000000 },
    { name: '合体中期', world: 'ling', value: 12150000000 },
    { name: '合体后期', world: 'ling', value: 36450000000 },
    { name: '合体大圆满', world: 'ling', value: 45562500000 },
    { name: '大乘初期', world: 'ling', value: 455625000000 },
    { name: '大乘中期', world: 'ling', value: 1366875000000 },
    { name: '大乘后期', world: 'ling', value: 4100625000000 },
    { name: '大乘大圆满', world: 'ling', value: 5125781250000 },
    { name: '真仙初期', world: 'xian', value: 51257812500000 },
    { name: '真仙中期', world: 'xian', value: 153773437500000 },
    { name: '真仙后期', world: 'xian', value: 615093750000000 },
    { name: '真仙大圆满', world: 'xian', value: 768867187500000 },
    { name: '金仙初期', world: 'xian', value: 7688671875000000 },
    { name: '金仙中期', world: 'xian', value: 23066015625000000 },
    { name: '金仙后期', world: 'xian', value: 92264062500000000 },
    { name: '金仙大圆满', world: 'xian', value: 115330078125000000 },
    { name: '太乙初期', world: 'xian', value: 1153300781250000000 },
    { name: '太乙中期', world: 'xian', value: 3459902343750000000 },
    { name: '太乙后期', world: 'xian', value: 13839609375000000000 },
    { name: '太乙大圆满', world: 'xian', value: 17299511718750000000 },
    { name: '大罗初期（斩一尸）', world: 'xian', value: 172995117187500000000 },
    { name: '大罗中期（斩二尸）', world: 'xian', value: 518985351562500000000 },
    { name: '大罗后期（斩三尸）', world: 'xian', value: 2075941406250000000000 },
    { name: '大罗大圆满', world: 'xian', value: 2594926757812500000000 },
    { name: '道祖境', world: 'xian', value: 25949267578125000000000 }
  ];

  var WORLD_LABEL = { ren: '人界', ling: '灵界', xian: '仙界' };

  var METRICS = {
    /* 战力：原著未给数值，此处为「每级约 ×10」的单规则估值模型 */
    power: {
      title: '相对战力',
      note: '自建估值模型，非原著数值',
      values: REALM.map(function (r) {
        return { lo: 0, hi: Math.pow(10, r.exp), txt: READ[r.exp] };
      })
    },

    /* 寿元：人界与仙界为官方口径，灵界三境为基于天劫设定的预估区间。
       lo=0 表示点位数据（柱自 0 起），lo>0 表示区间数据（柱画在区间两端之间） */
    life: {
      title: '寿元',
      note: '人界、仙界为官方口径；灵界三境为预估区间',
      values: [
        { lo: 0,     hi: 100,     txt: '约百年' },
        { lo: 0,     hi: 200,     txt: '约二百年' },
        { lo: 0,     hi: 500,     txt: '约五百余岁' },
        { lo: 0,     hi: 1000,    txt: '一千余岁' },
        { lo: 0,     hi: 2000,    txt: '两千余岁' },
        { lo: 10000, hi: 20000,   txt: '1–2 万年',   est: true },
        { lo: 50000, hi: 100000,  txt: '5–10 万年',  est: true },
        { lo: 50000, hi: 300000,  txt: '5–30 万年',  est: true },
        { lo: 0,     hi: 1000000, txt: '以百万年计' },
        { lo: 0,     hi: 1000000, txt: '以百万年计' },
        { lo: 0,     hi: 1000000, txt: '以百万年计' },
        { lo: 0,     hi: 1000000, txt: '以百万年计' },
        { lo: 0,     hi: 1000000, txt: '以百万年计' }
      ]
    },

    /* 换算器：不画阶梯，渲染两个下拉框 + 结果卡 */
    compare: {
      title: '跨境界换算',
      note: '综合流传口径的估值模型，非官方数值'
    }
  };

  function each(list, fn) {
    Array.prototype.forEach.call(list, fn);
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  /* 倍数的中文写法：1e12 → 1万亿，1e6 → 100万。
     支持任意大小（含非整倍数），避免出现 5.19e+22 这类科学计数法 */
  function fmtRatio(r) {
    if (r >= 1e12) return trim((r / 1e12)) + '万亿';
    if (r >= 1e8) return trim(r / 1e8) + '亿';
    if (r >= 1e4) return trim(r / 1e4) + '万';
    if (r !== Math.floor(r)) return r.toFixed(1);
    return String(r);
  }
  function trim(n) {
    var s = String(Math.round(n * 100) / 100);
    return s.replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
  }

  /* 换算器：1 个强者 ≈ 几个弱者，并给出抗衡判断 */
  function renderCompare(root) {
    root.classList.add('cv-chart');

    function options(sel, selected) {
      var html = '';
      var last = '';
      for (var i = 0; i < COMPARE.length; i++) {
        var r = COMPARE[i];
        if (r.world !== last) {
          if (last) html += '</optgroup>';
          html += '<optgroup label="' + WORLD_LABEL[r.world] + '">';
          last = r.world;
        }
        html += '<option value="' + i + '"' + (i === selected ? ' selected' : '') + '>'
          + esc(r.name) + '</option>';
      }
      html += '</optgroup>';
      sel.innerHTML = html;
    }

    function judge(ratio) {
      if (ratio >= 100) {
        return { tag: '天堑 · 数量无意义', cls: 'cv-tag-tianqian',
          desc: '差距超过 100 倍，属质变鸿沟。再多低境界修士也只是「凑数的炮灰」，数量无法弥补，除非弱者持有逆天法宝（韩立式特例）。' };
      }
      if (ratio >= 30) {
        return { tag: '数量可消耗 · 极难取胜', cls: 'cv-tag-hard',
          desc: '差距 30–99 倍。堆数量可以消耗对方法力与体力，但几乎不可能正面取胜，正常会被逐一击破。' };
      }
      if (ratio >= 10) {
        return { tag: '需大量数量勉强周旋', cls: 'cv-tag-hard',
          desc: '差距 10–29 倍。需要数十倍数量才能勉强周旋，胜算仍很低，且对方可「杀出重围」逐个击破。' };
      }
      if (ratio >= 3) {
        return { tag: '需数个才有机会', cls: 'cv-tag-balance',
          desc: '差距 3–9 倍。需要数个低境界修士联手才有一战之力，属「质量压制、数量可补」区间。' };
      }
      return { tag: '可正面抗衡', cls: 'cv-tag-weak',
        desc: '差距小于 3 倍，处于同一档次，可正面交手，胜负取决于法宝、功法、神识与临场发挥。' };
    }

    root.innerHTML =
      '<div class="cv-compare">'
      + '<div class="cv-calc">'
      +   '<label>1 个</label>'
      +   '<select class="cv-select" data-side="strong"></select>'
      +   '<span class="cv-arrow">≈</span>'
      +   '<label>几个</label>'
      +   '<select class="cv-select" data-side="weak"></select>'
      +   '<label>？</label>'
      + '</div>'
      + '<div class="cv-result" data-role="result"></div>'
      + '<p class="cv-caption"><span class="cv-src">数据口径：'
      + esc(METRICS.compare.note) + '。真实胜负还取决于法宝、功法、神识与经验。</span></p>'
      + '</div>';

    var selStrong = root.querySelector('[data-side="strong"]');
    var selWeak = root.querySelector('[data-side="weak"]');
    var result = root.querySelector('[data-role="result"]');

    options(selStrong, 11);   // 默认：元婴初期
    options(selWeak, 9);      // 默认：结丹后期

    function update() {
      var s = COMPARE[+selStrong.value];
      var w = COMPARE[+selWeak.value];
      var ratio = s.value / w.value;
      /* 始终以「强者 ÷ 弱者」来算差距与判断，避免 ratio<1 时出现
         「差距 9e-8 倍 / 可正面抗衡」这类错误结论 */
      var gap = ratio >= 1 ? ratio : w.value / s.value;
      var j = judge(gap);
      var line;
      if (ratio >= 1) {
        line = '1 个 <b>' + esc(s.name) + '</b>（' + WORLD_LABEL[s.world] + '）≈ <b>'
          + fmtRatio(ratio) + '</b> 个 <b>' + esc(w.name) + '</b>（' + WORLD_LABEL[w.world] + '）';
      } else {
        line = '反过来：1 个 <b>' + esc(w.name) + '</b>（' + WORLD_LABEL[w.world] + '）≈ <b>'
          + fmtRatio(gap) + '</b> 个 <b>' + esc(s.name) + '</b>（' + WORLD_LABEL[s.world] + '）';
      }
      result.innerHTML =
        '<div class="cv-result-line">' + line + '</div>'
        + '<div class="cv-result-big">差距 ' + fmtRatio(gap) + ' 倍</div>'
        + '<span class="cv-tag ' + j.cls + '">' + j.tag + '</span>'
        + '<div class="cv-result-desc">' + j.desc + '</div>';
    }

    selStrong.addEventListener('change', update);
    selWeak.addEventListener('change', update);
    update();
  }

  function init(root) {
    var m = METRICS[root.getAttribute('data-metric')];
    if (!m) return;

    /* 样式类由脚本自己挂上，书写侧只需 data-cultivation + data-metric */
    root.classList.add('cv-chart');

    /* 换算器走独立渲染，不画阶梯 */
    if (root.getAttribute('data-metric') === 'compare') {
      renderCompare(root);
      return;
    }

    var apex = START;      // 当前刻度顶点（REALM 下标）
    var timer = null;

    root.innerHTML =
      '<div class="cv-tools">'
      + '<span class="cv-label">取景</span>'
      + '<input type="range" class="cv-slider" min="0" max="' + TOP + '" step="1"'
      +   ' value="' + START + '" aria-label="' + esc(m.title) + '刻度顶点">'
      + '<span class="cv-readout"></span>'
      + '<button type="button" class="cv-btn" data-replay="1">重播</button>'
      + '</div>'
      + '<div class="cv-rows">'
      /* 13 行一次渲染完毕；顶点之上的行靠 .is-off 收起，
         这样柱长与行高都能走 CSS 过渡，不必重排 DOM */
      + REALM.map(function (r, i) {
          var v = m.values[i];
          return '<div class="cv-row" data-i="' + i + '" data-world="' + r.world + '"'
            + (v.est ? ' data-est="1"' : '') + '>'
            + '<span class="cv-name">' + esc(r.name) + '</span>'
            + '<span class="cv-track"><span class="cv-bar"></span></span>'
            + '<span class="cv-val">' + esc(v.txt) + '</span>'
            + '</div>';
        }).join('')
      + '</div>'
      /* 刻度轴与数据行共用同一套 grid 列定义，因此刻度天然对齐柱体 */
      + '<div class="cv-axis"><span></span><span class="cv-ticks">'
      + AXIS.map(function (t, i) {
          return '<i style="left:' + i * 25 + '%">' + t + '</i>';
        }).join('')
      + '</span><span></span></div>'
      /* 子阶段刻度：显示当前顶点境界的初/中/后/大圆满落在轴上的位置 */
      + '<div class="cv-axis cv-sub"><span class="cv-sub-label">子阶段</span><span class="cv-subticks"></span><span></span></div>'
      + '<p class="cv-caption"></p>';

    var slider = root.querySelector('.cv-slider');
    var readout = root.querySelector('.cv-readout');
    var capEl = root.querySelector('.cv-caption');
    var rows = root.querySelectorAll('.cv-row');
    var subTicks = root.querySelector('.cv-subticks');

    function caption(i) {
      var v = m.values[i];
      var base = m.values[0];
      var s = '<b>刻度顶点：' + esc(REALM[i].name) + '</b>（100% = 该境界的' + m.title + '）。'
        + '柱长 = 各境界相对顶点的占比，' + esc(REALM[0].name) + '只占顶点的 1/'
        + fmtRatio(Math.round(v.hi / base.hi)) + '。';
      var above = TOP - i;
      s += above > 0
        ? '顶点之上还有 ' + above + ' 个更高境界未入画。'
        : '已至道祖境。';
      s += '<span class="cv-src">数据口径：' + esc(m.note) + '。</span>';
      return s;
    }

    function apply() {
      var apexVal = m.values[apex].hi;
      each(rows, function (row) {
        var v = m.values[+row.getAttribute('data-i')];
        row.classList.toggle('is-off', +row.getAttribute('data-i') > apex);
        /* toFixed(4) 到不了的地方就是真的 0 像素——不做兜底，
           消失本身就是这两个量级差要说明的事 */
        var bar = row.querySelector('.cv-bar');
        bar.style.left = ((v.lo / apexVal) * 100).toFixed(4) + '%';
        bar.style.width = (((v.hi - v.lo) / apexVal) * 100).toFixed(4) + '%';
      });
      readout.innerHTML = '<b>' + esc(REALM[apex].name) + '</b> · '
        + (apex + 1) + ' / ' + REALM.length + ' 境';
      capEl.innerHTML = caption(apex);
      slider.value = String(apex);
      renderSub(apexVal);
    }

    /* 子阶段刻度：把当前顶点境界的初/中/后/大圆满标在轴上。
       战力为对数量级，子阶段按该境界区间内的相对位置估算；
       寿元官方未按子阶段细分，故不显示。 */
    function renderSub(apexVal) {
      if (root.getAttribute('data-metric') !== 'power') {
        subTicks.innerHTML = '';
        return;
      }
      /* 每个大境界跨一个数量级（×10），子阶段大致落在
         初期 1/10、中期 3/10、后期 7/10、大圆满 9/10 处 */
      var stages = [
        { label: '初期', f: 0.1 },
        { label: '中期', f: 0.3 },
        { label: '后期', f: 0.7 },
        { label: '大圆满', f: 0.9 }
      ];
      subTicks.innerHTML = stages.map(function (st) {
        return '<i style="left:' + (st.f * 100).toFixed(1) + '%">' + st.label + '</i>';
      }).join('');
    }

    function stop() {
      if (timer !== null) {
        clearInterval(timer);
        timer = null;
      }
    }

    function play() {
      stop();
      apex = START;
      apply();
      timer = setInterval(function () {
        if (apex >= TOP) { stop(); return; }
        apex += 1;
        apply();
      }, STEP_MS);
    }

    slider.addEventListener('input', function () {
      stop();
      apex = +slider.value;
      apply();
    });
    root.querySelector('.cv-btn[data-replay]').addEventListener('click', play);

    var still = window.matchMedia
      && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (still) {
      apex = TOP;                // 减少动效偏好：直接给出终点画面
      apply();
    } else if ('IntersectionObserver' in window) {
      /* 首次滚入视口自动播一遍，之后完全交给滑块 */
      var io = new IntersectionObserver(function (entries) {
        if (!entries[0].isIntersecting) return;
        io.disconnect();
        play();
      }, { threshold: 0.4 });
      apex = START;
      apply();
      io.observe(root);
    } else {
      play();
    }
  }

  function boot() {
    each(document.querySelectorAll('[data-cultivation]'), init);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
