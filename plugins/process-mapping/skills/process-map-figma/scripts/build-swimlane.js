// Šablona pro use_figma: postaví swimlane procesní mapu z layoutu (pmap.py layout).
// Hotový kód vyrábí `pmap.py figma <spec> --part build`; data se vkládají jako JSON literál.
// Měřítko S = 2: jedna jednotka layoutu = 2 px ve Figmě. Statický návrh = finální stav animace.
const L = /*LAYOUT*/null;
if (!L || L.schema !== 1) throw new Error('Neznámá verze layoutu; vygeneruj kód znovu přes pmap.py figma.');
const META = L.meta;
const S = 2, HEAD = 200, PAD = 80;
const hex = h => { h = h.replace('#', ''); return { r: parseInt(h.slice(0, 2), 16) / 255, g: parseInt(h.slice(2, 4), 16) / 255, b: parseInt(h.slice(4, 6), 16) / 255 }; };
const solid = (h, o) => o == null ? [{ type: 'SOLID', color: hex(h) }] : [{ type: 'SOLID', color: hex(h), opacity: o }];
const C = { bg: '#FAF7F2', ink: '#1F1A17', muted: '#6E645B', line: '#E6DED4', band: '#F3EEE7', arrow: '#5C534B', amber: '#D98E04', amberBg: '#FFF5E1', chip: '#EEF2FD', alt: '#9A8F84' };
const LANE_COLORS = ['#C8364F', '#3A5BD9', '#9A6B2F', '#2E8B57', '#7B4FC9', '#0E8A8A'];
await Promise.all(['Regular', 'Medium', 'Semi Bold', 'Bold'].map(s => figma.loadFontAsync({ family: 'Inter', style: s })));

const ids = {};
const page = figma.currentPage;
const hadContent = page.children.length > 0;
const right = page.children.reduce((m, n) => Math.max(m, n.x + n.width), 0);
const root = figma.createFrame();
root.name = 'Procesní mapa · ' + META.title;
root.resize(L.width * S + PAD * 2, L.height * S + HEAD + PAD);
root.x = hadContent ? right + 200 : 0; root.y = 0;
root.fills = solid(C.bg); root.clipsContent = true;
ids.root = root.id;
const X = v => PAD + v * S, Y = v => HEAD + v * S;

function T(str, size, style, color, width, opts = {}) {
  const t = figma.createText();
  t.fontName = { family: 'Inter', style }; t.characters = str; t.fontSize = size; t.fills = solid(color);
  if (opts.ls != null) t.letterSpacing = { unit: 'PERCENT', value: opts.ls };
  if (opts.lh != null) t.lineHeight = { unit: 'PERCENT', value: opts.lh };
  if (width) { t.resize(width, t.height); t.textAutoResize = 'HEIGHT'; }
  return t;
}
function put(node, parent, x, y, key) { parent.appendChild(node); node.x = x; node.y = y; if (key) { node.name = key; ids[key] = node.id; } return node; }
function badge(label, color) {
  const b = figma.createAutoLayout('HORIZONTAL');
  b.paddingLeft = b.paddingRight = 10; b.paddingTop = b.paddingBottom = 5; b.cornerRadius = 6; b.fills = solid(color, 0.12);
  b.appendChild(T(label, 16, 'Bold', color, null, { ls: 6 }));
  return b;
}
function fixed(f, w, h) { f.resize(w, h); f.primaryAxisSizingMode = 'FIXED'; f.counterAxisSizingMode = 'FIXED'; }
const laneIdx = {}; L.lanes.forEach((ln, i) => { laneIdx[ln.id] = i; });
const laneColor = id => LANE_COLORS[laneIdx[id] % LANE_COLORS.length];

put(T(META.title, 60, 'Bold', C.ink, null, { ls: -2 }), root, PAD, 64, 'title');
put(T(META.subtitle, 22, 'Regular', C.muted), root, PAD + 2, 140, 'subtitle');

L.lanes.forEach((ln, i) => {
  const f = figma.createFrame(); put(f, root, X(0), Y(ln.y), 'lane:' + ln.id);
  f.resize(L.width * S, ln.h * S); f.clipsContent = false; f.fills = ln.alt ? solid(C.band) : solid('#FFFFFF', 0.6);
  const strip = figma.createRectangle(); f.appendChild(strip); strip.x = 0; strip.y = 0; strip.resize(6, ln.h * S); strip.fills = solid(laneColor(ln.id));
  if (i > 0) { const sep = figma.createRectangle(); f.appendChild(sep); sep.x = 0; sep.y = 0; sep.resize(L.width * S, 1); sep.fills = solid(C.line); }
  const lab = T(ln.name.toUpperCase(), 20, 'Bold', laneColor(ln.id), null, { ls: 8 }); f.appendChild(lab); lab.x = 40; lab.y = 12;
});

for (const c of L.cards) {
  const col = c.type === 'decision' ? C.amber : laneColor(c.lane);
  const f = figma.createAutoLayout('VERTICAL'); put(f, root, X(c.x), Y(c.y), 'card:' + c.id);
  fixed(f, c.w * S, c.h * S);
  f.paddingLeft = f.paddingRight = 24; f.paddingTop = 24; f.paddingBottom = 16; f.itemSpacing = 8;
  f.cornerRadius = (c.type === 'start' || c.type === 'end') ? 40 : 16; f.clipsContent = true;
  f.fills = solid(c.type === 'decision' ? C.amberBg : '#FFFFFF');
  f.strokes = solid(c.type === 'decision' ? C.amber : C.line); f.strokeWeight = c.type === 'decision' ? 2 : 1; f.strokeAlign = 'INSIDE';
  f.effects = [{ type: 'DROP_SHADOW', color: { r: 0.24, g: 0.16, b: 0.1, a: 0.07 }, offset: { x: 0, y: 6 }, radius: 18, spread: 0, visible: true, blendMode: 'NORMAL' }];
  const bar = figma.createRectangle(); f.appendChild(bar); bar.layoutPositioning = 'ABSOLUTE'; bar.x = 0; bar.y = 0; bar.resize(c.w * S, 6); bar.fills = solid(col);
  const head = figma.createAutoLayout('HORIZONTAL'); head.itemSpacing = 10; head.fills = []; f.appendChild(head);
  head.appendChild(badge(c.label, col));
  if (c.question) head.appendChild(badge('??', C.amber));
  const inner = c.w * S - 48;
  f.appendChild(T(c.title_lines.join(' '), 23, 'Bold', C.ink, inner, { lh: 120 }));
  if (c.type === 'checks') {
    if (c.sub_lines.length) f.appendChild(T(c.sub_lines[0], 18, 'Semi Bold', C.amber, inner));
    c.items.forEach((it, i) => {
      const chip = figma.createAutoLayout('VERTICAL'); f.appendChild(chip); chip.layoutPositioning = 'ABSOLUTE';
      chip.x = (it.x - c.x) * S; chip.y = (it.y - c.y) * S; fixed(chip, it.w * S, it.h * S);
      chip.paddingLeft = chip.paddingRight = 16; chip.paddingTop = chip.paddingBottom = 12; chip.itemSpacing = 2; chip.cornerRadius = 10; chip.fills = solid(C.chip);
      chip.appendChild(T(it.title, 20, 'Semi Bold', C.ink)); chip.appendChild(T(it.sub, 17, 'Regular', C.muted));
      chip.name = 'item:' + c.id + ':' + i; ids[chip.name] = chip.id;
    });
  } else if (c.sub_lines.length) {
    f.appendChild(T(c.sub_lines.join(' '), 18, 'Regular', C.muted, inner, { lh: 130 }));
  }
  fixed(f, c.w * S, c.h * S);
}

for (const sp of L.spans) {
  const f = figma.createAutoLayout('VERTICAL'); put(f, root, X(sp.x), Y(sp.y), 'span:' + sp.key.split(':')[1]);
  f.paddingLeft = 28; f.itemSpacing = 6; f.primaryAxisAlignItems = 'CENTER'; f.cornerRadius = 14;
  f.fills = solid('#FFFFFF', 0.9); f.strokes = solid(laneColor(sp.lane)); f.strokeWeight = 1.5; f.dashPattern = [6, 5];
  f.appendChild(badge(sp.title.toUpperCase(), laneColor(sp.lane))); f.appendChild(T(sp.text, 20, 'Medium', C.ink));
  fixed(f, sp.w * S, sp.h * S);
}

for (const w of L.wires) {
  const pts = w.points.map(p => [X(p[0]), Y(p[1])]);
  const a = pts[pts.length - 2], b = pts[pts.length - 1];
  const len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
  pts[pts.length - 1] = [b[0] + (b[0] - a[0]) / len * 6, b[1] + (b[1] - a[1]) / len * 6];   // hrot blíž ke kartě
  const vec = figma.createVector(); root.appendChild(vec);
  const minX = Math.min(...pts.map(p => p[0])), minY = Math.min(...pts.map(p => p[1]));
  await vec.setVectorNetworkAsync({
    vertices: pts.map((p, i) => ({ x: p[0] - minX, y: p[1] - minY, strokeCap: i === pts.length - 1 ? 'ARROW_EQUILATERAL' : 'NONE', cornerRadius: 12 })),
    segments: pts.slice(1).map((_, i) => ({ start: i, end: i + 1 })),
  });
  vec.x = minX; vec.y = minY; vec.fills = [];
  vec.strokes = solid(w.kind === 'loop' ? C.amber : w.kind === 'alt' ? C.alt : C.arrow);
  vec.strokeWeight = 2.5; vec.strokeJoin = 'ROUND'; vec.strokeAlign = 'CENTER';
  if (w.kind === 'loop' || w.kind === 'alt') vec.dashPattern = [7, 6];
  vec.name = 'wire:' + w.id; ids[vec.name] = vec.id;
  if (w.label) {
    const t = T(w.label, 22, 'Semi Bold', w.kind === 'loop' ? C.amber : C.muted);
    const lx = w.label_anchor === 'start' ? X(w.label_pos[0]) : X(w.label_pos[0]) - t.width / 2;
    put(t, root, lx, Y(w.label_pos[1]) - 24, 'label:' + w.id);
  }
}

if (L.states) {
  const st = L.states;
  put(T(st.label.toUpperCase(), 20, 'Bold', C.ink, null, { ls: 8 }), root, X(20), Y(st.label_y) - 24, 'states-label');
  st.pills.forEach(p => {
    const f = figma.createAutoLayout('VERTICAL'); put(f, root, X(p.x), Y(p.y), 'state:' + p.id);
    f.paddingLeft = f.paddingRight = 24; f.itemSpacing = 4; f.primaryAxisAlignItems = 'CENTER'; f.cornerRadius = 16;
    f.fills = solid('#FFFFFF'); f.strokes = solid(C.line); f.strokeWeight = 1;
    f.appendChild(T(p.name, 22, 'Semi Bold', C.ink)); f.appendChild(T(p.sub, 17, 'Regular', C.muted));
    fixed(f, p.w * S, p.h * S);
  });
  const r = st.ring, last = r.steps[r.steps.length - 1].dx;
  const ring = figma.createRectangle(); put(ring, root, X(r.x + last), Y(r.y), 'ring');   // klidový stav = poslední stav
  ring.resize(r.w * S, r.h * S); ring.cornerRadius = 20; ring.fills = []; ring.strokes = solid(C.amber); ring.strokeWeight = 3;
}

await root.screenshot({ scale: 0.4 });
return { ids, frameId: root.id };
