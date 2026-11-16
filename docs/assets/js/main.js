/* KAB EXPORT — interacciones del sitio */
(function () {
  var NS = 'http://www.w3.org/2000/svg';
  var lang = document.documentElement.lang === 'en' ? 'en' : 'es';

  function hex(cx, cy, r) {
    var p = [];
    for (var i = 0; i < 6; i++) {
      var a = Math.PI / 180 * (60 * i - 90);
      p.push((cx + r * Math.cos(a)).toFixed(1) + ',' + (cy + r * Math.sin(a)).toFixed(1));
    }
    return p.join(' ');
  }
  function el(name, attrs) {
    var n = document.createElementNS(NS, name);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    return n;
  }

  // Menú móvil
  var btn = document.querySelector('.menu-btn');
  var links = document.getElementById('nav-links');
  if (btn && links) {
    btn.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Panal de la portada
  var comb = document.getElementById('comb');
  if (comb) {
    var r = 34, w = Math.sqrt(3) * r, n = 0;
    var fills = { '2,2': 1, '3,2': .85, '2,3': .7, '3,3': 1, '1,3': .45, '2,4': .9, '3,4': .6, '4,3': .5, '1,2': .3, '2,1': .55, '4,4': .35 };
    for (var row = 0; row < 8; row++) {
      for (var col = 0; col < 7; col++) {
        var cx = 30 + col * w + (row % 2 ? w / 2 : 0), cy = 30 + row * r * 1.5;
        if (Math.hypot(cx - 210, cy - 215) > 180) continue;
        var f = fills[col + ',' + row];
        var p = el('polygon', { points: hex(cx, cy, r - 3), 'class': f ? 'cell h' : 'cell' });
        if (f) { p.setAttribute('fill-opacity', f); p.style.animationDelay = (n++ * 0.12) + 's'; }
        comb.appendChild(p);
      }
    }
    comb.appendChild(el('path', { d: 'M232 200 C 300 160, 340 110, 400 40', fill: 'none', stroke: 'var(--on-forest)', 'stroke-width': 2, 'stroke-dasharray': '2 8', 'stroke-linecap': 'round' }));
    comb.appendChild(el('circle', { cx: 400, cy: 40, r: 6, fill: 'var(--honey-soft)' }));
  }

  // Mapa de rutas (proyección equirectangular, lon -128..-58, lat 58..10)
  var map = document.getElementById('map');
  if (map) {
    var T = {
      es: { ca: 'Canadá', us: 'Estados Unidos', av: 'Alta Verapaz', gt: 'Guatemala · origen', note: 'Esquema, no a escala' },
      en: { ca: 'Canada', us: 'United States', av: 'Alta Verapaz', gt: 'Guatemala · origin', note: 'Schematic, not to scale' }
    }[lang];
    var xy = function (lat, lon) { return [(lon + 128) / 70 * 800, (58 - lat) / 48 * 300]; };
    var html = '<defs><pattern id="dots" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.3" class="dotgrid"/></pattern></defs><rect width="800" height="300" fill="url(#dots)" opacity=".7"/>';
    var o = xy(15.9, -90.3);
    var dests = [
      { n: T.us, lat: 39, lon: -96, lift: 40, dx: -12, anchor: 'end', dy: 4 },
      { n: T.ca, lat: 47, lon: -79, lift: 50, dx: 12, anchor: 'start', dy: 4 }
    ];
    dests.forEach(function (d, i) {
      var t = xy(d.lat, d.lon), mx = (o[0] + t[0]) / 2 + (t[0] < o[0] ? -50 : 50), my = Math.min(o[1], t[1]) - d.lift;
      var path = 'M' + o[0] + ' ' + o[1] + ' Q' + mx + ' ' + my + ' ' + t[0] + ' ' + t[1];
      html += '<path class="route" d="' + path + '"/>';
      html += '<circle class="pulse" r="3.5" fill="var(--honey)"><animateMotion dur="' + (4 + i) + 's" repeatCount="indefinite" path="' + path + '"/></circle>';
      html += '<circle class="dest" cx="' + t[0] + '" cy="' + t[1] + '" r="5"/>';
      html += '<text class="lbl" x="' + (t[0] + d.dx) + '" y="' + (t[1] + d.dy) + '" text-anchor="' + d.anchor + '">' + d.n + '</text>';
    });
    html += '<circle class="origin" cx="' + o[0] + '" cy="' + o[1] + '" r="11" opacity=".25"/><circle class="origin" cx="' + o[0] + '" cy="' + o[1] + '" r="6"/>';
    html += '<text class="lbl" x="' + (o[0] + 16) + '" y="' + (o[1] + 4) + '">' + T.av + '</text><text class="lbl-s" x="' + (o[0] + 16) + '" y="' + (o[1] + 20) + '">' + T.gt + '</text>';
    html += '<text class="lbl-s" x="790" y="290" text-anchor="end">' + T.note + '</text>';
    map.innerHTML = html;
  }

  // Copiar correo
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var label = b.textContent;
      var ok = lang === 'en' ? 'Copied' : 'Copiado';
      var done = function (t) { b.textContent = t; setTimeout(function () { b.textContent = label; }, 1800); };
      if (navigator.clipboard) navigator.clipboard.writeText(b.getAttribute('data-copy')).then(function () { done(ok); }, function () { done(label); });
    });
  });

  // Producto preseleccionado en el formulario (?p=cardamomo, ?p=pimienta-gorda…)
  var sel = document.getElementById('f-product');
  if (sel) {
    var m = location.search.match(/[?&]p=([a-z-]+)/);
    if (m) for (var i = 0; i < sel.options.length; i++) if (sel.options[i].getAttribute('data-k') === m[1]) sel.selectedIndex = i;
  }
})();
