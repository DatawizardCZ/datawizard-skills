// Šablona pro use_figma (spolu se skillem figma-use-motion): animace podle časování v layoutu.
// Hotový kód vyrábí `pmap.py figma <spec> --part motion --ids <ids.json>`.
const L = /*LAYOUT*/null;
const IDS = /*IDS*/null;
if (!L || L.schema !== 1 || !IDS) throw new Error('Chybí layout nebo ids; vygeneruj kód znovu přes pmap.py figma.');
const S = 2;
const N = {};
const keys = Object.keys(IDS);
const nodes = await Promise.all(keys.map(k => figma.getNodeByIdAsync(IDS[k])));
keys.forEach((k, i) => { N[k] = nodes[i]; });
const mutated = new Set();
const missing = [];
const r3 = x => Math.round(x * 1000) / 1000;
function kf(key, name, frames) {
  const node = N[key];
  if (!node) { missing.push(key); return; }
  let last = -1;
  const fixedFrames = frames.map(([t, v, e]) => { t = Math.max(r3(t), r3(last + 0.01)); last = t; return [t, v, e]; });
  node.applyManualKeyframeTrack({ type: 'PROPERTY', name }, {
    keyframes: fixedFrames.map(([t, v, e]) => ({ timelinePosition: t, value: { type: 'FLOAT', value: v }, ...(e ? { easing: { type: e } } : {}) })),
  });
  mutated.add(node.id);
}
function appear(key, t, { dy = 14, dx = 0, dur = 0.45 } = {}) {
  kf(key, 'OPACITY', [[t, 0], [t + dur * 0.8, 1, 'EASE_OUT']]);
  if (dy) kf(key, 'TRANSLATION_Y', [[t, dy], [t + dur, 0, 'EASE_OUT']]);
  if (dx) kf(key, 'TRANSLATION_X', [[t, dx], [t + dur, 0, 'EASE_OUT']]);
}
function draw(key, t, dur) {
  kf(key, 'OPACITY', [[t, 0], [t + 0.04, 1, 'HOLD']]);
  kf(key, 'PATH_TRIM_END', [[t, 0], [t + dur, 1, 'EASE_IN_AND_OUT']]);
}

appear('title', 0, { dy: 18, dur: 0.6 });
appear('subtitle', 0.15, { dy: 12, dur: 0.6 });
L.lanes.forEach(ln => appear('lane:' + ln.id, ln.t, { dy: 0, dx: -24, dur: 0.5 }));
L.cards.forEach(c => {
  appear('card:' + c.id, c.t);
  c.items.forEach((it, i) => appear('item:' + c.id + ':' + i, it.t, { dy: 8, dur: 0.35 }));
});
L.spans.forEach(sp => appear('span:' + sp.key.split(':')[1], sp.t, { dy: 10, dur: 0.5 }));
L.wires.forEach(w => {
  const k = 'wire:' + w.id;
  if (w.kind === 'loop' || w.kind === 'alt') appear(k, w.t, { dy: 0, dx: 16, dur: 0.5 });   // PATH_TRIM nejde na čárkované čáry
  else draw(k, w.t, w.kind === 'state' ? 0.25 : 0.45);
  if (w.label) appear('label:' + w.id, w.label_t, { dy: 6, dur: 0.35 });
});
if (L.states) {
  appear('states-label', 0.3, { dy: 8, dur: 0.4 });
  L.states.pills.forEach(p => {
    kf('state:' + p.id, 'OPACITY', [[p.t, 0], [p.t + 0.35, 0.35, 'EASE_OUT'], [p.lit_t, 0.35], [p.lit_t + 0.3, 1, 'EASE_OUT']]);
    kf('state:' + p.id, 'TRANSLATION_Y', [[p.t, 10], [p.t + 0.4, 0, 'EASE_OUT']]);
  });
  // rámeček stojí na posledním stavu; animace ho posouvá z prvního stavu (posun je relativní k poloze)
  const steps = L.states.ring.steps, last = steps[steps.length - 1].dx;
  kf('ring', 'OPACITY', [[steps[0].t, 0], [steps[0].t + 0.3, 1, 'EASE_OUT']]);
  const fr = [[steps[0].t, (steps[0].dx - last) * S]];
  steps.slice(1).forEach((s, i) => { fr.push([s.t - 0.3, (steps[i].dx - last) * S]); fr.push([s.t, (s.dx - last) * S, 'EASE_IN_AND_OUT']); });
  kf('ring', 'TRANSLATION_X', fr);
}
const anyNode = N['card:' + L.cards[0].id];
const tl = anyNode && anyNode.timelines && anyNode.timelines[0];
const warnings = missing.length ? ['chybí uzly: ' + missing.join(', ')] : [];
if (tl) { if (tl.duration < L.duration) anyNode.setTimelineDuration(tl.id, L.duration); }
else warnings.push('rámec nemá časovou osu; animace se nenastavila');
return { mutatedNodeIds: [...mutated], count: mutated.size, timelines: anyNode ? anyNode.timelines : [], warnings };
