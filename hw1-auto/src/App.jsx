import { useState, useCallback, useRef, useEffect, useMemo } from "react";

/* ═══ CALCULATOR ═══ */
const RMATS = [
  { name: "Сплав РС-3001", lo: 800, hi: 3000, Rlo: 50, Rhi: 30000, W0: 2 },
  { name: "Сплав РС-3710", lo: 100, hi: 2000, Rlo: 10, Rhi: 20000, W0: 2 },
  { name: "Кермет К-50С", lo: 1000, hi: 10000, Rlo: 100, Rhi: 100000, W0: 2 },
  { name: "Спец.сплав №3", lo: 350, hi: 500, Rlo: 100, Rhi: 50000, W0: 2 },
  { name: "Тантал ТВЧ", lo: 10, hi: 100, Rlo: 1, Rhi: 1000, W0: 3 },
  { name: "Нихром", lo: 50, hi: 300, Rlo: 5, Rhi: 3000, W0: 1 },
  { name: "Хром", lo: 500, hi: 500, Rlo: 50, Rhi: 30000, W0: 1 },
];

function runCalc(resistors, capacitors) {
  const log = [];
  const p = (t) => log.push(t);
  const H = 0.1;
  const sR = resistors.reduce((a, r) => a + r.R, 0);
  const sRi = resistors.reduce((a, r) => a + 1 / r.R, 0);
  const raw = Math.sqrt(sR / sRi);
  const rho = Math.round(raw / 100) * 100 || 100;
  p(`ρ_опт = √(ΣRi/ΣRi⁻¹) = ${raw.toFixed(3)} → ρ□ = ${rho} Ом/□`);

  // Material selection
  let cands = RMATS.filter(
    (m) =>
      m.lo <= rho &&
      rho <= m.hi &&
      resistors.every((r) => m.Rlo <= r.R && r.R <= m.Rhi),
  );
  let mat;
  if (cands.length) {
    mat = cands.reduce(
      (best, m) => {
        const span = m.hi - m.lo || 1;
        const c = 1 - Math.abs((rho - m.lo) / span - 0.5) * 2;
        return c > (best._c || -1) ? Object.assign(m, { _c: c }) : best;
      },
      { _c: -1 },
    );
  } else {
    mat = RMATS.reduce(
      (best, m) => {
        const d = rho < m.lo ? m.lo - rho : rho > m.hi ? rho - m.hi : 0;
        return d < (best._d ?? 1e9) ? { ...m, _d: d } : best;
      },
      { _d: 1e9 },
    );
    p(`⚠ Нет точного попадания, ближайший: ${mat.name}`);
  }
  p(`Материал: ${mat.name} (${mat.lo}–${mat.hi} Ом/□, W₀=${mat.W0})`);
  const W0 = mat.W0;

  // Resistors
  const rr = [];
  let hasMeander = false;
  p("");
  p("Коэффициенты формы:");
  for (const r of resistors) {
    const kf = r.R / rho;
    const form =
      kf < 0.1
        ? "rect (l<<b)"
        : kf < 1
          ? "rect (l<b)"
          : kf <= 10
            ? "rect (l>b)"
            : "МЕАНДР";
    p(`  ${r.name}: kф = ${r.R}/${rho} = ${kf.toFixed(3)} → ${form}`);
    if (kf >= 10) {
      hasMeander = true;
      continue;
    }

    const bPrec = r.delta <= 10 ? 0.3 : 0.2;
    const bW = Math.sqrt((rho * r.W) / (r.R * W0)) * 10; // mm

    let b = Math.ceil(Math.max(bPrec, bW) / H) * H;
    b = Math.round(b * 10) / 10;

    let l, Ra, da;
    for (let i = 0; i < 50; i++) {
      l = Math.round(Math.round((kf * b) / H) * H * 10) / 10;
      if (l < 0.5) l = 0.5;
      Ra = (rho * l) / b;
      da = (Math.abs(r.R - Ra) / r.R) * 100;
      if (da <= r.delta / 2) break;
      b = Math.round((b + H) * 10) / 10;
    }
    p(
      `  ${r.name}: b=${b} мм, l=${l} мм | bw=${bW.toFixed(3)}, bт=${bPrec} | R'=${Ra.toFixed(1)}, ΔR'=${da.toFixed(1)}% ${da <= r.delta ? "✅" : "⚠️"}`,
    );
    rr.push({ ...r, kf, b, l, Ra, da, ct: "resistor" });
  }
  if (hasMeander) return { error: "МЕАНДР (kф≥10)! Не поддерживается.", log };

  // Capacitors
  const C0 = 200000;
  p("");
  p("Конденсаторы:");
  p(`  Материал: Пятиокись тантала, C₀ = ${C0} пФ/см²`);
  const cc = capacitors.map((c) => {
    const S = (c.C / C0) * 100; // mm²
    const side = Math.round(Math.sqrt(S) * 100) / 100;
    const constr = S >= 5 ? "4.7а" : S >= 1 ? "4.7б" : "4.7в";
    p(
      `  ${c.name}: S = ${c.C}/${C0}×100 = ${S.toFixed(3)} мм² → ${side}×${side} мм (${constr})`,
    );
    return { ...c, S, side, constr, ct: "capacitor" };
  });

  return { log, rho, mat: mat.name, resistors: rr, capacitors: cc };
}

/* ═══ CONSTANTS ═══ */
const PAD_OVL = 0.2;
const GRID = 0.1;
const sn = (v) => Math.round(v / GRID) * GRID;

/* ═══ APP ═══ */
export default function App() {
  const [resistors, setR] = useState([
    { name: "R1", R: 110, delta: 10, W: 0.01 },
    { name: "R2", R: 600, delta: 10, W: 0.01 },
    { name: "R3", R: 1100, delta: 10, W: 0.005 },
    { name: "R4", R: 3200, delta: 10, W: 0.01 },
    { name: "R5", R: 15000, delta: 20, W: 0.005 },
    { name: "R6", R: 21000, delta: 20, W: 0.003 },
    { name: "R7", R: 18000, delta: 20, W: 0.005 },
  ]);
  const [capacitors, setC] = useState([{ name: "C1", C: 6300 }]);
  const [navesInput, setNI] = useState([
    { name: "VT1" },
    { name: "VT2" },
    { name: "VT3" },
    { name: "VT4" },
    { name: "VDex1" },
    { name: "VDex2" },
    { name: "VDex3" },
    { name: "VDex4" },
    { name: "VDom1" },
    { name: "VDom2" },
  ]);
  const [result, setResult] = useState(null);
  const [subW, setSubW] = useState(14);
  const [subH, setSubH] = useState(12);
  const [comps, setComps] = useState([]);
  const [pads, setPads] = useState([]);
  const [traces, setTraces] = useState([]); // [{points:[{x,y}], width}]
  const [wires, setWires] = useState([]); // [{x1,y1,x2,y2}]
  const [tab, setTab] = useState("input");
  const [tool, setTool] = useState("move"); // move|trace|wire|delTrace|delWire
  const [dragI, setDragI] = useState(null);
  const [dragOff, setDragOff] = useState(null);
  const [padDragI, setPadDragI] = useState(null);
  const [traceDraw, setTraceDraw] = useState(null);
  const [traceW, setTraceW] = useState(0.5);
  const [wireDraw, setWireDraw] = useState(null);
  const [mouse, setMouse] = useState({ x: 0, y: 0 });
  const svgRef = useRef(null);
  const SC = 38;
  const ox = SC * 2.5,
    oy = SC * 2;

  const doCalc = useCallback(() => {
    // Parse all values as numbers explicitly
    const rs = resistors.map((r) => ({
      ...r,
      R: Number(r.R),
      delta: Number(r.delta),
      W: Number(r.W),
    }));
    const cs = capacitors.map((c) => ({ ...c, C: Number(c.C) }));
    const r = runCalc(rs, cs);
    setResult(r);
    if (!r.error) {
      const all = [
        ...r.resistors,
        ...r.capacitors,
        ...navesInput.map((n) => ({
          ...n,
          ct: n.name.startsWith("VD") ? "diode" : "transistor",
          w: 1,
          h: 1,
        })),
      ];
      let cx = 1.5,
        cy = 1.5,
        rh = 0;
      const placed = all.map((c, i) => {
        let w =
          c.ct === "resistor"
            ? c.l + PAD_OVL * 2
            : c.ct === "capacitor"
              ? c.side + 0.4
              : 1;
        let h =
          c.ct === "resistor" ? c.b : c.ct === "capacitor" ? c.side + 0.4 : 1;
        if (cx + w + 1 > subW) {
          cx = 1.5;
          cy += rh + 0.5;
          rh = 0;
        }
        const p = { ...c, w, h, x: sn(cx), y: sn(cy), idx: i };
        cx += w + 0.5;
        rh = Math.max(rh, h);
        return p;
      });
      setComps(placed);
    }
    setTab("calc");
  }, [resistors, capacitors, navesInput, subW]);

  const svgPt = useCallback(
    (e) => {
      const svg = svgRef.current;
      if (!svg) return { x: 0, y: 0 };
      const pt = svg.createSVGPoint();
      pt.x = e.clientX;
      pt.y = e.clientY;
      const cp = pt.matrixTransform(svg.getScreenCTM().inverse());
      return { x: (cp.x - ox) / SC, y: (cp.y - oy) / SC };
    },
    [ox, oy],
  );

  // Mouse tracking
  useEffect(() => {
    const mm = (e) => {
      const p = svgPt(e);
      setMouse({ x: sn(p.x), y: sn(p.y) });
    };
    window.addEventListener("mousemove", mm);
    return () => window.removeEventListener("mousemove", mm);
  }, [svgPt]);

  // Component drag
  const onCompMD = (e, idx) => {
    if (tool !== "move") return;
    e.preventDefault();
    e.stopPropagation();
    const p = svgPt(e);
    setDragI(idx);
    setDragOff({ dx: p.x - comps[idx].x, dy: p.y - comps[idx].y });
  };

  // Pad drag
  const onPadMD = (e, idx) => {
    e.preventDefault();
    e.stopPropagation();
    setPadDragI(idx);
  };

  // SVG click handler
  const onSvgClick = (e) => {
    if (e.target.closest("[data-trace-idx]") && tool === "delTrace") {
      const idx = Number(e.target.closest("[data-trace-idx]").dataset.traceIdx);
      setTraces(traces.filter((_, i) => i !== idx));
      return;
    }
    if (e.target.closest("[data-wire-idx]") && tool === "delWire") {
      const idx = Number(e.target.closest("[data-wire-idx]").dataset.wireIdx);
      setWires(wires.filter((_, i) => i !== idx));
      return;
    }

    const p = svgPt(e);
    const sx = sn(p.x),
      sy = sn(p.y);

    if (tool === "trace") {
      if (!traceDraw) {
        setTraceDraw({ points: [{ x: sx, y: sy }], width: traceW });
      } else {
        const last = traceDraw.points[traceDraw.points.length - 1];
        // Force orthogonal: pick axis with larger delta
        const dx = Math.abs(sx - last.x),
          dy = Math.abs(sy - last.y);
        let nx, ny;
        if (dx >= dy) {
          nx = sx;
          ny = last.y;
        } // horizontal
        else {
          nx = last.x;
          ny = sy;
        } // vertical
        // Don't add zero-length segments
        if (Math.abs(nx - last.x) > 0.05 || Math.abs(ny - last.y) > 0.05) {
          setTraceDraw({
            ...traceDraw,
            points: [...traceDraw.points, { x: sn(nx), y: sn(ny) }],
          });
        }
      }
    }

    if (tool === "wire") {
      if (!wireDraw) {
        setWireDraw({ x1: sx, y1: sy });
      } else {
        setWires([...wires, { ...wireDraw, x2: sx, y2: sy }]);
        setWireDraw(null);
      }
    }
  };

  const finishTrace = useCallback(() => {
    if (traceDraw && traceDraw.points.length >= 2) {
      setTraces((prev) => [...prev, traceDraw]);
    }
    setTraceDraw(null);
  }, [traceDraw]);

  // Drag handlers
  useEffect(() => {
    const mm = (e) => {
      if (dragI !== null) {
        const p = svgPt(e);
        let nx = sn(p.x - dragOff.dx),
          ny = sn(p.y - dragOff.dy);
        nx = Math.max(0.1, Math.min(subW - comps[dragI].w - 0.1, nx));
        ny = Math.max(0.1, Math.min(subH - comps[dragI].h - 0.1, ny));
        const nc = [...comps];
        nc[dragI] = { ...nc[dragI], x: nx, y: ny };
        setComps(nc);
      }
      if (padDragI !== null) {
        const p = svgPt(e);
        const dists = [
          { side: "top", d: Math.abs(p.y) },
          { side: "bottom", d: Math.abs(p.y - subH) },
          { side: "left", d: Math.abs(p.x) },
          { side: "right", d: Math.abs(p.x - subW) },
        ].sort((a, b) => a.d - b.d);
        const best = dists[0];
        let pos =
          best.side === "top" || best.side === "bottom"
            ? p.x / subW
            : p.y / subH;
        pos = Math.max(0.02, Math.min(0.98, pos));
        const np = [...pads];
        np[padDragI] = {
          ...np[padDragI],
          side: best.side,
          pos: Math.round(pos * 100) / 100,
        };
        setPads(np);
      }
    };
    const mu = () => {
      setDragI(null);
      setDragOff(null);
      setPadDragI(null);
    };
    window.addEventListener("mousemove", mm);
    window.addEventListener("mouseup", mu);
    return () => {
      window.removeEventListener("mousemove", mm);
      window.removeEventListener("mouseup", mu);
    };
  }, [dragI, dragOff, padDragI, comps, pads, svgPt, subW, subH]);

  // Keyboard
  useEffect(() => {
    const kd = (e) => {
      if (e.key === "Enter") finishTrace();
      if (e.key === "Escape") {
        setTraceDraw(null);
        setWireDraw(null);
      }
    };
    window.addEventListener("keydown", kd);
    return () => window.removeEventListener("keydown", kd);
  }, [finishTrace]);

  // Pad position
  const padXY = (p) => {
    const s = p.sz || 0.3;
    if (p.side === "top") return { x: p.pos * subW - s / 2, y: -s };
    if (p.side === "bottom") return { x: p.pos * subW - s / 2, y: subH };
    if (p.side === "left") return { x: -s, y: p.pos * subH - s / 2 };
    return { x: subW, y: p.pos * subH - s / 2 };
  };

  const svgW = (subW + 5) * SC,
    svgH = (subH + 4) * SC;
  const addPad = () =>
    setPads([
      ...pads,
      {
        id: Date.now(),
        name: "",
        side: "left",
        pos: 0.5,
        sz: 0.3,
        hasCenter: true,
      },
    ]);

  // Build trace segments for rendering (no internal borders)
  const traceSegs = (tr) => {
    const segs = [];
    const hw = tr.width / 2;
    for (let j = 0; j < tr.points.length - 1; j++) {
      const a = tr.points[j],
        b = tr.points[j + 1];
      const isH = Math.abs(a.y - b.y) < 0.05;
      if (isH) {
        segs.push({
          x: Math.min(a.x, b.x),
          y: a.y - hw,
          w: Math.abs(b.x - a.x),
          h: tr.width,
        });
      } else {
        segs.push({
          x: a.x - hw,
          y: Math.min(a.y, b.y),
          w: tr.width,
          h: Math.abs(b.y - a.y),
        });
      }
    }
    return segs;
  };

  // Build unified path for a trace (merged rectangles, single outline)
  const traceClipPath = (tr, id) => {
    const segs = traceSegs(tr);
    // Just use union of rects as a clip path
    return (
      <clipPath id={id}>
        {segs.map((s, i) => (
          <rect
            key={i}
            x={ox + s.x * SC}
            y={oy + s.y * SC}
            width={s.w * SC}
            height={s.h * SC}
          />
        ))}
      </clipPath>
    );
  };

  const S = {
    bg: "#0f172a",
    fg: "#e2e8f0",
    m: "#64748b",
    card: "#1e293b",
    brd: "#334155",
    acc: "#38bdf8",
    f: "'JetBrains Mono','Fira Code',monospace",
  };
  const inpS = {
    padding: "2px 4px",
    background: "#0f172a",
    border: "1px solid #475569",
    color: "#e2e8f0",
    borderRadius: 2,
    fontSize: 10,
    fontFamily: "inherit",
  };
  const rowS = {
    display: "flex",
    alignItems: "center",
    gap: 3,
    background: S.card,
    padding: "2px 5px",
    borderRadius: 3,
    border: `1px solid ${S.brd}`,
    marginBottom: 2,
  };
  const btnS = {
    marginLeft: "auto",
    padding: "0 7px",
    background: "#334155",
    border: "1px solid #475569",
    color: "#e2e8f0",
    borderRadius: 2,
    cursor: "pointer",
    fontSize: 12,
    fontFamily: "inherit",
  };
  const delBtn = {
    background: "transparent",
    border: "none",
    color: "#ef4444",
    cursor: "pointer",
    fontSize: 11,
  };

  return (
    <div
      style={{
        fontFamily: S.f,
        background: S.bg,
        color: S.fg,
        minHeight: "100vh",
      }}
    >
      <div
        style={{
          background: S.card,
          borderBottom: `1px solid ${S.brd}`,
          padding: "8px 14px",
          display: "flex",
          alignItems: "center",
          gap: 10,
          flexWrap: "wrap",
        }}
      >
        <div style={{ fontSize: 13, fontWeight: 700 }}>ГИС Редактор v6</div>
        <div style={{ flex: 1 }} />
        <label style={{ fontSize: 9, color: S.m }}>
          Подложка
          <input
            value={subW}
            onChange={(e) => setSubW(Number(e.target.value))}
            type="number"
            style={{ width: 35, margin: "0 2px", ...inpS }}
          />
          ×
          <input
            value={subH}
            onChange={(e) => setSubH(Number(e.target.value))}
            type="number"
            style={{ width: 35, ...inpS }}
          />
          мм
        </label>
        <button
          onClick={doCalc}
          style={{
            padding: "4px 12px",
            background: "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: 3,
            cursor: "pointer",
            fontWeight: 700,
            fontSize: 11,
            fontFamily: S.f,
          }}
        >
          ▶ Рассчитать
        </button>
      </div>

      <div
        style={{
          display: "flex",
          borderBottom: `1px solid ${S.brd}`,
          background: S.card,
        }}
      >
        {[
          ["input", "Ввод"],
          ["calc", "Расчёт"],
          ["topo", "Топология"],
          ["pads", "Площадки"],
        ].map(([k, l]) => (
          <button
            key={k}
            onClick={() => setTab(k)}
            style={{
              padding: "6px 13px",
              border: "none",
              cursor: "pointer",
              fontSize: 10,
              fontWeight: 600,
              background: tab === k ? S.bg : "transparent",
              color: tab === k ? S.acc : S.m,
              borderBottom:
                tab === k ? `2px solid ${S.acc}` : "2px solid transparent",
              fontFamily: S.f,
            }}
          >
            {l}
          </button>
        ))}
      </div>

      <div style={{ padding: "10px 14px" }}>
        {/* INPUT */}
        {tab === "input" && (
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <div style={{ flex: "1 1 280px" }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 5,
                  marginBottom: 4,
                }}
              >
                <div
                  style={{
                    width: 3,
                    height: 12,
                    background: "#d97706",
                    borderRadius: 1,
                  }}
                />
                <span style={{ fontSize: 10, fontWeight: 700 }}>Резисторы</span>
                <span style={{ fontSize: 8, color: S.m }}>
                  (имя, R Ом, ΔR%, W Вт)
                </span>
                <button
                  onClick={() =>
                    setR([
                      ...resistors,
                      {
                        name: `R${resistors.length + 1}`,
                        R: 1000,
                        delta: 10,
                        W: 0.01,
                      },
                    ])
                  }
                  style={btnS}
                >
                  +
                </button>
              </div>
              {resistors.map((r, i) => (
                <div key={i} style={rowS}>
                  <input
                    value={r.name}
                    onChange={(e) => {
                      const a = [...resistors];
                      a[i] = { ...a[i], name: e.target.value };
                      setR(a);
                    }}
                    style={{ width: 40, ...inpS }}
                  />
                  <input
                    value={r.R}
                    onChange={(e) => {
                      const a = [...resistors];
                      a[i] = { ...a[i], R: e.target.value };
                      setR(a);
                    }}
                    style={{ width: 65, ...inpS }}
                  />
                  <input
                    value={r.delta}
                    onChange={(e) => {
                      const a = [...resistors];
                      a[i] = { ...a[i], delta: e.target.value };
                      setR(a);
                    }}
                    style={{ width: 35, ...inpS }}
                  />
                  <input
                    value={r.W}
                    onChange={(e) => {
                      const a = [...resistors];
                      a[i] = { ...a[i], W: e.target.value };
                      setR(a);
                    }}
                    style={{ width: 55, ...inpS }}
                  />
                  <button
                    onClick={() => setR(resistors.filter((_, j) => j !== i))}
                    style={delBtn}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
            <div style={{ flex: "1 1 180px" }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 5,
                  marginBottom: 4,
                }}
              >
                <div
                  style={{
                    width: 3,
                    height: 12,
                    background: "#be185d",
                    borderRadius: 1,
                  }}
                />
                <span style={{ fontSize: 10, fontWeight: 700 }}>
                  Конденсаторы
                </span>
                <button
                  onClick={() =>
                    setC([
                      ...capacitors,
                      { name: `C${capacitors.length + 1}`, C: 1000 },
                    ])
                  }
                  style={btnS}
                >
                  +
                </button>
              </div>
              {capacitors.map((c, i) => (
                <div key={i} style={rowS}>
                  <input
                    value={c.name}
                    onChange={(e) => {
                      const a = [...capacitors];
                      a[i] = { ...a[i], name: e.target.value };
                      setC(a);
                    }}
                    style={{ width: 40, ...inpS }}
                  />
                  <input
                    value={c.C}
                    onChange={(e) => {
                      const a = [...capacitors];
                      a[i] = { ...a[i], C: e.target.value };
                      setC(a);
                    }}
                    style={{ width: 70, ...inpS }}
                  />
                  <button
                    onClick={() => setC(capacitors.filter((_, j) => j !== i))}
                    style={delBtn}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
            <div style={{ flex: "1 1 140px" }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 5,
                  marginBottom: 4,
                }}
              >
                <div
                  style={{
                    width: 3,
                    height: 12,
                    background: "#7c3aed",
                    borderRadius: 1,
                  }}
                />
                <span style={{ fontSize: 10, fontWeight: 700 }}>Навесные</span>
                <button
                  onClick={() =>
                    setNI([
                      ...navesInput,
                      { name: `VT${navesInput.length + 1}` },
                    ])
                  }
                  style={btnS}
                >
                  +
                </button>
              </div>
              {navesInput.map((n, i) => (
                <div key={i} style={rowS}>
                  <input
                    value={n.name}
                    onChange={(e) => {
                      const a = [...navesInput];
                      a[i] = { ...a[i], name: e.target.value };
                      setNI(a);
                    }}
                    style={{ width: 80, ...inpS }}
                  />
                  <button
                    onClick={() => setNI(navesInput.filter((_, j) => j !== i))}
                    style={delBtn}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CALC */}
        {tab === "calc" && result && (
          <div>
            {result.error && (
              <div
                style={{
                  background: "#7f1d1d",
                  border: "1px solid #ef4444",
                  padding: 10,
                  borderRadius: 4,
                  marginBottom: 10,
                  fontSize: 11,
                }}
              >
                ⚠️ {result.error}
              </div>
            )}
            <div
              style={{
                background: S.card,
                border: `1px solid ${S.brd}`,
                borderRadius: 4,
                padding: 12,
                fontSize: 10,
                lineHeight: 1.9,
                whiteSpace: "pre-wrap",
              }}
            >
              {result.log.map((l, i) => (
                <div key={i}>{l}</div>
              ))}
            </div>
          </div>
        )}

        {/* TOPOLOGY */}
        {tab === "topo" && comps.length > 0 && (
          <div>
            {/* Toolbar */}
            <div
              style={{
                display: "flex",
                gap: 5,
                marginBottom: 6,
                alignItems: "center",
                flexWrap: "wrap",
              }}
            >
              {[
                ["move", "☝ Двигать"],
                ["trace", "✏ Дорожка"],
                ["wire", "⚡ Навесной"],
                ["delTrace", "🗑 Удал. дорожку"],
                ["delWire", "🗑 Удал. провод"],
              ].map(([k, l]) => (
                <button
                  key={k}
                  onClick={() => {
                    setTool(k);
                    setTraceDraw(null);
                    setWireDraw(null);
                  }}
                  style={{
                    padding: "4px 9px",
                    fontSize: 9,
                    fontWeight: 600,
                    fontFamily: S.f,
                    cursor: "pointer",
                    borderRadius: 3,
                    background: tool === k ? "#2563eb" : S.card,
                    color: tool === k ? "#fff" : S.fg,
                    border: `1px solid ${tool === k ? "#2563eb" : S.brd}`,
                  }}
                >
                  {l}
                </button>
              ))}
              <span style={{ width: 1, height: 18, background: S.brd }} />
              <button
                onClick={addPad}
                style={{
                  padding: "4px 9px",
                  fontSize: 9,
                  fontFamily: S.f,
                  cursor: "pointer",
                  borderRadius: 3,
                  background: S.card,
                  color: S.fg,
                  border: `1px solid ${S.brd}`,
                }}
              >
                + Площадка
              </button>
              {tool === "trace" && (
                <>
                  <label style={{ fontSize: 8, color: S.m }}>
                    Ш:
                    <input
                      value={traceW}
                      onChange={(e) => setTraceW(Number(e.target.value))}
                      type="number"
                      step="0.1"
                      min="0.2"
                      style={{ width: 35, marginLeft: 2, ...inpS }}
                    />
                  </label>
                  <button
                    onClick={finishTrace}
                    style={{
                      padding: "3px 7px",
                      fontSize: 8,
                      fontFamily: S.f,
                      cursor: "pointer",
                      borderRadius: 2,
                      background: "#065f46",
                      color: "#fff",
                      border: "none",
                    }}
                  >
                    Enter: завершить
                  </button>
                  <button
                    onClick={() => setTraceDraw(null)}
                    style={{
                      padding: "3px 7px",
                      fontSize: 8,
                      fontFamily: S.f,
                      cursor: "pointer",
                      borderRadius: 2,
                      background: "#7f1d1d",
                      color: "#fca5a5",
                      border: "none",
                    }}
                  >
                    Esc: отмена
                  </button>
                </>
              )}
            </div>

            {/* SVG */}
            <div
              style={{
                overflow: "auto",
                background: "#fff",
                border: `1px solid ${S.brd}`,
                borderRadius: 4,
              }}
            >
              <svg
                ref={svgRef}
                width={svgW}
                height={svgH}
                style={{
                  display: "block",
                  cursor:
                    tool === "trace" || tool === "wire"
                      ? "crosshair"
                      : tool.startsWith("del")
                        ? "pointer"
                        : "default",
                }}
                onClick={onSvgClick}
              >
                <defs>
                  <pattern
                    id="hR"
                    patternUnits="userSpaceOnUse"
                    width="4"
                    height="4"
                    patternTransform="rotate(45)"
                  >
                    <line
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="4"
                      stroke="#1e293b"
                      strokeWidth="0.8"
                      opacity="0.35"
                    />
                  </pattern>
                  <pattern
                    id="hC"
                    patternUnits="userSpaceOnUse"
                    width="5"
                    height="5"
                    patternTransform="rotate(-45)"
                  >
                    <line
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="5"
                      stroke="#831843"
                      strokeWidth="1"
                      opacity="0.25"
                    />
                  </pattern>
                  <pattern
                    id="hTr"
                    patternUnits="userSpaceOnUse"
                    width="4"
                    height="4"
                    patternTransform="rotate(45)"
                  >
                    <line
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="4"
                      stroke="#0f172a"
                      strokeWidth="1"
                      opacity="0.4"
                    />
                  </pattern>
                  {/* Clip paths for traces (merged segments, no internal borders) */}
                  {traces.map((tr, ti) => traceClipPath(tr, `tc${ti}`))}
                  {traceDraw &&
                    traceDraw.points.length >= 2 &&
                    traceClipPath(traceDraw, "tcPreview")}
                </defs>

                {/* Grid */}
                <rect
                  x={ox}
                  y={oy}
                  width={subW * SC}
                  height={subH * SC}
                  fill="#fafafa"
                />
                {Array.from({ length: Math.round(subW * 2) + 1 }, (_, i) => {
                  const x = ox + (i * SC) / 2;
                  const mj = i % 2 === 0;
                  return (
                    <line
                      key={`gx${i}`}
                      x1={x}
                      y1={oy}
                      x2={x}
                      y2={oy + subH * SC}
                      stroke={mj ? "#d4d4d8" : "#e4e4e7"}
                      strokeWidth={mj ? 0.4 : 0.2}
                    />
                  );
                })}
                {Array.from({ length: Math.round(subH * 2) + 1 }, (_, i) => {
                  const y = oy + (i * SC) / 2;
                  const mj = i % 2 === 0;
                  return (
                    <line
                      key={`gy${i}`}
                      x1={ox}
                      y1={y}
                      x2={ox + subW * SC}
                      y2={y}
                      stroke={mj ? "#d4d4d8" : "#e4e4e7"}
                      strokeWidth={mj ? 0.4 : 0.2}
                    />
                  );
                })}
                <rect
                  x={ox}
                  y={oy}
                  width={subW * SC}
                  height={subH * SC}
                  fill="none"
                  stroke="#0f172a"
                  strokeWidth={3}
                />

                {/* TRACES - rendered with clip path for monolithic look */}
                {traces.map((tr, ti) => {
                  const segs = traceSegs(tr);
                  // Bounding box of all segments
                  let minX = Infinity,
                    minY = Infinity,
                    maxX = -Infinity,
                    maxY = -Infinity;
                  segs.forEach((s) => {
                    minX = Math.min(minX, s.x);
                    minY = Math.min(minY, s.y);
                    maxX = Math.max(maxX, s.x + s.w);
                    maxY = Math.max(maxY, s.y + s.h);
                  });
                  return (
                    <g
                      key={`tr${ti}`}
                      data-trace-idx={ti}
                      style={{
                        cursor: tool === "delTrace" ? "pointer" : "default",
                      }}
                    >
                      {/* Fill with hatch, clipped to union of rects */}
                      <rect
                        x={ox + minX * SC - 2}
                        y={oy + minY * SC - 2}
                        width={(maxX - minX) * SC + 4}
                        height={(maxY - minY) * SC + 4}
                        fill="#e5e7eb"
                        clipPath={`url(#tc${ti})`}
                      />
                      <rect
                        x={ox + minX * SC - 2}
                        y={oy + minY * SC - 2}
                        width={(maxX - minX) * SC + 4}
                        height={(maxY - minY) * SC + 4}
                        fill="url(#hTr)"
                        clipPath={`url(#tc${ti})`}
                      />
                      {/* Outer border only (draw each segment rect border, but inner edges will overlap) */}
                      {segs.map((s, si) => (
                        <rect
                          key={si}
                          x={ox + s.x * SC}
                          y={oy + s.y * SC}
                          width={s.w * SC}
                          height={s.h * SC}
                          fill="none"
                          stroke="#1e293b"
                          strokeWidth={1.5}
                        />
                      ))}
                    </g>
                  );
                })}

                {/* Trace preview while drawing */}
                {traceDraw &&
                  traceDraw.points.length >= 1 &&
                  (() => {
                    const pts = traceDraw.points;
                    const last = pts[pts.length - 1];
                    const hw = traceDraw.width / 2;
                    // Existing segments
                    const previewSegs = [];
                    for (let j = 0; j < pts.length - 1; j++) {
                      const a = pts[j],
                        b = pts[j + 1];
                      const isH = Math.abs(a.y - b.y) < 0.05;
                      if (isH)
                        previewSegs.push({
                          x: Math.min(a.x, b.x),
                          y: a.y - hw,
                          w: Math.abs(b.x - a.x),
                          h: traceDraw.width,
                        });
                      else
                        previewSegs.push({
                          x: a.x - hw,
                          y: Math.min(a.y, b.y),
                          w: traceDraw.width,
                          h: Math.abs(b.y - a.y),
                        });
                    }
                    // Preview to mouse
                    const dx = Math.abs(mouse.x - last.x),
                      dy = Math.abs(mouse.y - last.y);
                    const goH = dx >= dy;
                    const nx = goH ? mouse.x : last.x,
                      ny = goH ? last.y : mouse.y;
                    if (
                      Math.abs(nx - last.x) > 0.05 ||
                      Math.abs(ny - last.y) > 0.05
                    ) {
                      if (goH)
                        previewSegs.push({
                          x: Math.min(last.x, nx),
                          y: last.y - hw,
                          w: Math.abs(nx - last.x),
                          h: traceDraw.width,
                        });
                      else
                        previewSegs.push({
                          x: last.x - hw,
                          y: Math.min(last.y, ny),
                          w: traceDraw.width,
                          h: Math.abs(ny - last.y),
                        });
                    }
                    return (
                      <g opacity={0.5}>
                        {previewSegs.map((s, i) => (
                          <rect
                            key={i}
                            x={ox + s.x * SC}
                            y={oy + s.y * SC}
                            width={s.w * SC}
                            height={s.h * SC}
                            fill="rgba(37,99,235,0.15)"
                            stroke="#2563eb"
                            strokeWidth={1}
                            strokeDasharray="3,2"
                          />
                        ))}
                        {/* Point markers */}
                        {pts.map((pt, i) => (
                          <circle
                            key={i}
                            cx={ox + pt.x * SC}
                            cy={oy + pt.y * SC}
                            r={3}
                            fill="#2563eb"
                          />
                        ))}
                      </g>
                    );
                  })()}

                {/* Wire preview */}
                {wireDraw && (
                  <line
                    x1={ox + wireDraw.x1 * SC}
                    y1={oy + wireDraw.y1 * SC}
                    x2={ox + mouse.x * SC}
                    y2={oy + mouse.y * SC}
                    stroke="#7c3aed"
                    strokeWidth={1.5}
                    opacity={0.5}
                  />
                )}

                {/* External pads */}
                {pads.map((p, i) => {
                  const { x, y } = padXY(p);
                  const s = p.sz || 0.3;
                  return (
                    <g
                      key={`pad${i}`}
                      onMouseDown={(e) => onPadMD(e, i)}
                      style={{ cursor: "grab" }}
                    >
                      <rect
                        x={ox + x * SC}
                        y={oy + y * SC}
                        width={s * SC}
                        height={s * SC}
                        fill="#f1f5f9"
                        stroke="#0f172a"
                        strokeWidth={1.5}
                      />
                      <circle
                        cx={ox + (x + s / 2) * SC}
                        cy={oy + (y + s / 2) * SC}
                        r={2}
                        fill="#0f172a"
                      />
                      {p.name && (
                        <text
                          x={
                            ox +
                            (x + s / 2) * SC +
                            (p.side === "left"
                              ? x - s * 35
                              : p.side === "right"
                                ? x + s * 15
                                : 0)
                          }
                          y={
                            oy +
                            s * 30 +
                            (p.side === "top"
                              ? y - s * 1.2
                              : p.side === "bottom"
                                ? y + s * 0.5
                                : y - s * 1.7) *
                              SC
                          }
                          textAnchor="middle"
                          dominantBaseline={
                            p.side === "top" ? "auto" : "hanging"
                          }
                          fill="#0f172a"
                          fontSize={8}
                          fontWeight="600"
                          fontFamily="monospace"
                        >
                          {p.name}
                        </text>
                      )}
                    </g>
                  );
                })}

                {/* Components */}
                {comps.map((it, i) => {
                  const x = ox + it.x * SC,
                    y = oy + it.y * SC,
                    w = it.w * SC,
                    h = it.h * SC;
                  const isR = it.ct === "resistor",
                    isC = it.ct === "capacitor";
                  return (
                    <g
                      key={i}
                      onMouseDown={(e) => onCompMD(e, i)}
                      style={{ cursor: tool === "move" ? "grab" : "default" }}
                    >
                      {isR && (
                        <>
                          <rect
                            x={x}
                            y={y}
                            width={PAD_OVL * SC}
                            height={h}
                            fill="#bbf7d0"
                            stroke="#065f46"
                            strokeWidth={1}
                          />
                          <rect
                            x={x + w - PAD_OVL * SC}
                            y={y}
                            width={PAD_OVL * SC}
                            height={h}
                            fill="#bbf7d0"
                            stroke="#065f46"
                            strokeWidth={1}
                          />
                          <rect
                            x={x + PAD_OVL * SC}
                            y={y}
                            width={it.l * SC}
                            height={h}
                            fill="#fff7ed"
                            stroke="#78350f"
                            strokeWidth={1.5}
                          />
                          <rect
                            x={x + PAD_OVL * SC}
                            y={y}
                            width={it.l * SC}
                            height={h}
                            fill="url(#hR)"
                          />
                        </>
                      )}
                      {isC && (
                        <>
                          <rect
                            x={x}
                            y={y}
                            width={w}
                            height={h}
                            fill="none"
                            stroke="#831843"
                            strokeWidth={0.8}
                            strokeDasharray="3,2"
                          />
                          <rect
                            x={x + 0.1 * SC}
                            y={y + 0.1 * SC}
                            width={w - 0.2 * SC}
                            height={h - 0.2 * SC}
                            fill="#fdf2f8"
                            stroke="#831843"
                            strokeWidth={1.5}
                          />
                          <rect
                            x={x + 0.1 * SC}
                            y={y + 0.1 * SC}
                            width={w - 0.2 * SC}
                            height={h - 0.2 * SC}
                            fill="url(#hC)"
                          />
                        </>
                      )}
                      {!isR && !isC && (
                        <rect
                          x={x}
                          y={y}
                          width={w}
                          height={h}
                          fill="#ede9fe"
                          stroke="#5b21b6"
                          strokeWidth={1.5}
                          rx={2}
                        />
                      )}
                      <text
                        x={x + w / 2}
                        y={y + h / 2}
                        textAnchor="middle"
                        dominantBaseline="central"
                        fill={isR ? "#78350f" : isC ? "#831843" : "#5b21b6"}
                        fontSize={Math.min(10, Math.min(w, h) * 0.28)}
                        fontWeight="700"
                        fontFamily="monospace"
                        style={{ pointerEvents: "none" }}
                      >
                        {it.name}
                      </text>
                      {dragI === i && (
                        <rect
                          x={x - 1}
                          y={y - 1}
                          width={w + 2}
                          height={h + 2}
                          fill="none"
                          stroke="#2563eb"
                          strokeWidth={2}
                          strokeDasharray="3,2"
                        />
                      )}
                    </g>
                  );
                })}

                {/* NAVES WIRES - rendered LAST (on top of everything) */}
                {wires.map((w, i) => (
                  <g
                    key={`nw${i}`}
                    data-wire-idx={i}
                    style={{
                      cursor: tool === "delWire" ? "pointer" : "default",
                    }}
                  >
                    <line
                      x1={ox + w.x1 * SC}
                      y1={oy + w.y1 * SC}
                      x2={ox + w.x2 * SC}
                      y2={oy + w.y2 * SC}
                      stroke="#7c3aed"
                      strokeWidth={1.2}
                    />
                    <circle
                      cx={ox + w.x1 * SC}
                      cy={oy + w.y1 * SC}
                      r={2.5}
                      fill="#7c3aed"
                    />
                    <circle
                      cx={ox + w.x2 * SC}
                      cy={oy + w.y2 * SC}
                      r={2.5}
                      fill="#7c3aed"
                    />
                  </g>
                ))}

                {/* Axis labels */}
                {Array.from({ length: Math.ceil(subW) + 1 }, (_, i) => (
                  <text
                    key={`ax${i}`}
                    x={ox + i * SC}
                    y={oy - 10}
                    textAnchor="middle"
                    fill="#a1a1aa"
                    fontSize={8}
                    fontFamily="monospace"
                  >
                    {i}
                  </text>
                ))}
                {Array.from({ length: Math.ceil(subH) + 1 }, (_, i) => (
                  <text
                    key={`ay${i}`}
                    x={ox - 12}
                    y={oy + i * SC + 3}
                    textAnchor="end"
                    fill="#a1a1aa"
                    fontSize={8}
                    fontFamily="monospace"
                  >
                    {i}
                  </text>
                ))}
              </svg>
            </div>

            <div
              style={{ marginTop: 5, fontSize: 8, color: S.m, lineHeight: 1.5 }}
            >
              {tool === "move" && "☝ Перетаскивай компоненты и площадки"}
              {tool === "trace" &&
                "✏ Кликай точки дорожки (ортогональные). Enter — завершить, Esc — отмена. Несколько сегментов = змейка."}
              {tool === "wire" &&
                "⚡ Клик: начало → клик: конец навесного провода"}
              {tool === "delTrace" && "🗑 Кликни по дорожке чтобы удалить"}
              {tool === "delWire" && "🗑 Кликни по проводу чтобы удалить"}
            </div>
          </div>
        )}

        {tab === "topo" && comps.length === 0 && (
          <div style={{ color: S.m, padding: 30, textAlign: "center" }}>
            Нажми «▶ Рассчитать»
          </div>
        )}
      </div>
    </div>
  );
}
