// ねこねこショップ☆ 共通スクリプト
(function () {
  // トップへ戻るボタン
  var top = document.getElementById('totop');
  if (top) {
    var onScroll = function () { top.classList.toggle('show', window.scrollY > 600); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // 現在地のメニューを強調
  var links = [].slice.call(document.querySelectorAll('.nav a[href^="#"]'));
  if (links.length && 'IntersectionObserver' in window) {
    var map = {};
    links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.classList.remove('on'); });
        var a = map[e.target.id];
        if (a) {
          a.classList.add('on');
          var nav = a.parentNode;
          nav.scrollTo({ left: a.offsetLeft - 16, behavior: 'smooth' });
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) io.observe(s); });
  }

  // Q&A 検索・カテゴリ
  var input = document.getElementById('qa-search');
  if (!input) return;
  var tabs = [].slice.call(document.querySelectorAll('#qa-tabs button'));
  var groups = [].slice.call(document.querySelectorAll('.qa-group'));
  var empty = document.getElementById('qa-empty');
  var cat = 'all';
  var kata2hira = function (s) { return s.replace(/[ァ-ヶ]/g, function (c) { return String.fromCharCode(c.charCodeAt(0) - 0x60); }); };
  var norm = function (s) { return kata2hira(s.normalize('NFKC').toLowerCase()).replace(/\s+/g, ''); };
  groups.forEach(function (g) {
    [].slice.call(g.querySelectorAll('details.qa')).forEach(function (d) { d._text = norm(d.textContent); });
  });

  function apply() {
    var q = norm(input.value);
    var hits = 0;
    groups.forEach(function (g) {
      var inCat = cat === 'all' || g.dataset.cat === cat;
      var shown = 0;
      [].slice.call(g.querySelectorAll('details.qa')).forEach(function (d) {
        var ok = inCat && (!q || d._text.indexOf(q) >= 0);
        d.style.display = ok ? '' : 'none';
        if (q) d.open = ok;
        if (ok) shown++;
      });
      g.style.display = shown ? '' : 'none';
      hits += shown;
    });
    empty.style.display = hits ? 'none' : 'block';
  }
  input.addEventListener('input', apply);
  tabs.forEach(function (b) {
    b.addEventListener('click', function () {
      tabs.forEach(function (x) { x.classList.remove('on'); });
      b.classList.add('on');
      cat = b.dataset.cat;
      apply();
    });
  });

  // #q-xxx で直接開く
  function openHash() {
    var t = location.hash && document.getElementById(location.hash.slice(1));
    if (t && t.tagName === 'DETAILS') t.open = true;
  }
  window.addEventListener('hashchange', openHash);
  openHash();
})();

// 期限つきのお知らせ（data-until の日付以降は「終了」表示にする。PICK UP は隠す）
(function () {
  var today = new Date(); today.setHours(0, 0, 0, 0);
  [].slice.call(document.querySelectorAll('[data-until]')).forEach(function (el) {
    var d = new Date(el.getAttribute('data-until') + 'T00:00:00');
    if (isNaN(d) || today < d) return;
    if (el.classList.contains('latest')) el.style.display = 'none';
    else el.classList.add('ended');
  });
})();
