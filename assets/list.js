// 制作可能キャラ一覧
(function () {
  var D = window.CHAR_DATA;
  if (!D) return;
  var GROUPS = ['英数', 'あ', 'か', 'さ', 'た', 'な', 'は', 'ま', 'や', 'ら', 'わ'];
  var LIMIT = 24; // これを超えるキャラ数の作品は「もっと見る」で開く

  var kata2hira = function (s) { return s.replace(/[ァ-ヶ]/g, function (c) { return String.fromCharCode(c.charCodeAt(0) - 0x60); }); };
  var norm = function (s) { return kata2hira(String(s).normalize('NFKC').toLowerCase()).replace(/[\s・\-‐ー=!?:.〜~（）()"'☆★、。]/g, ''); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  var total = 0;
  D.works.forEach(function (w, i) {
    w.id = 'w' + i;
    w.key = norm(w.n) + '|' + norm(w.y);
    w.c.forEach(function (c) { c.key = norm(c[0]) + '|' + norm(c[1]); });
    total += w.c.length;
  });
  document.getElementById('n-works').textContent = D.works.length.toLocaleString();
  document.getElementById('n-chars').textContent = total.toLocaleString();
  document.getElementById('updated').textContent = D.updated.replace(/-/g, '/');

  var list = document.getElementById('list');
  var kana = document.getElementById('kana');
  var input = document.getElementById('q');
  var clear = document.getElementById('clear');
  var countEl = document.getElementById('count');
  var empty = document.getElementById('empty');
  var expanded = {};

  function render() {
    var q = norm(input.value);
    var html = '', hitWorks = 0, hitChars = 0, present = {};
    GROUPS.forEach(function (g) {
      var block = '';
      D.works.forEach(function (w) {
        if (w.g !== g) return;
        var workHit = !q || w.key.indexOf(q) >= 0;
        var chars = w.c;
        var hitSet = null;
        if (q && !workHit) {
          chars = w.c.filter(function (c) { return c.key.indexOf(q) >= 0; });
          if (!chars.length) return;
          hitSet = true;
        }
        hitWorks++;
        hitChars += chars.length;
        var open = q || expanded[w.id] || chars.length <= LIMIT;
        var shown = open ? chars : chars.slice(0, LIMIT);
        block += '<article class="work" id="' + w.id + '"><h3>' + esc(w.n) + '<span class="n">' + w.c.length + '</span></h3><div class="chips">' +
          shown.map(function (c) { return '<button class="chip' + (hitSet ? ' hit' : '') + '" type="button">' + esc(c[0]) + '</button>'; }).join('') +
          (open ? '' : '<button class="more" type="button" data-w="' + w.id + '">＋ あと' + (chars.length - LIMIT) + '人を見る</button>') +
          '</div></article>';
      });
      if (block) {
        present[g] = true;
        html += '<h2 class="ghead' + (g === '英数' ? ' en' : '') + '" id="g-' + g + '"><span>' + (g === '英数' ? 'A-Z' : g) + '</span></h2><div class="works">' + block + '</div>';
      }
    });
    list.innerHTML = html;
    empty.style.display = hitWorks ? 'none' : 'block';
    countEl.innerHTML = q ? '<b>' + hitWorks + '</b> 作品 / <b>' + hitChars + '</b> 人' : '<b>' + D.works.length + '</b> 作品';
    clear.classList.toggle('show', !!input.value);
    kana.innerHTML = GROUPS.map(function (g) {
      return '<a href="#g-' + g + '" class="' + (present[g] ? '' : 'off') + '">' + (g === '英数' ? 'A-Z' : g) + '</a>';
    }).join('');
  }

  var timer;
  input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(render, 120); });
  clear.addEventListener('click', function () { input.value = ''; render(); input.focus(); });

  list.addEventListener('click', function (e) {
    var more = e.target.closest('.more');
    if (more) { expanded[more.dataset.w] = true; render(); document.getElementById(more.dataset.w).scrollIntoView({ block: 'nearest' }); return; }
    var chip = e.target.closest('.chip');
    if (chip) copy(chip.textContent);
  });

  var toast = document.getElementById('toast'), tt;
  function showToast(msg) { toast.textContent = msg; toast.classList.add('show'); clearTimeout(tt); tt = setTimeout(function () { toast.classList.remove('show'); }, 1600); }
  function copy(text) {
    var done = function () { showToast('「' + text + '」をコピーしました'); };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () { fallback(text) && done(); });
    } else if (fallback(text)) done();
  }
  function fallback(text) {
    try {
      var t = document.createElement('textarea'); t.value = text; t.style.position = 'fixed'; t.style.opacity = '0';
      document.body.appendChild(t); t.select(); var ok = document.execCommand('copy'); document.body.removeChild(t); return ok;
    } catch (e) { return false; }
  }

  // ?q=xxx で検索した状態で開ける
  var m = location.search.match(/[?&]q=([^&]*)/);
  if (m) input.value = decodeURIComponent(m[1]);
  render();
})();
