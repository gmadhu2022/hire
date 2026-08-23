/* Lightweight charts — pure SVG/CSS, no chart library needed. */

export function BarChart({ data, height = 150 }) {
  // data: [{ label, value, color? }]
  const max = Math.max(1, ...data.map((d) => d.value));
  return (
    <div className="flex items-end gap-3" style={{ height }}>
      {data.map((d) => (
        <div key={d.label} className="flex flex-1 flex-col items-center justify-end gap-2">
          <span className="text-xs font-bold text-slate-700">{d.value}</span>
          <div
            className={`w-full rounded-t transition-all duration-500 ${d.color || "bg-navy"}`}
            style={{ height: `${Math.max(4, (d.value / max) * (height - 46))}px` }}
            title={`${d.label}: ${d.value}`}
          />
          <span className="text-center text-[10px] leading-tight text-slate-500">{d.label}</span>
        </div>
      ))}
    </div>
  );
}

export function Donut({ value, size = 120, stroke = 12, label }) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, value));
  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#e2e8f0" strokeWidth={stroke} />
        <circle
          cx={size / 2} cy={size / 2} r={r} fill="none"
          stroke={pct >= 75 ? "#4faa38" : pct >= 40 ? "#10256b" : "#f59e0b"}
          strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={circ} strokeDashoffset={circ - (pct / 100) * circ}
          style={{ transition: "stroke-dashoffset .6s ease" }}
        />
      </svg>
      <div className="absolute text-center">
        <div className="text-xl font-extrabold text-slate-800">{pct}%</div>
        {label && <div className="text-[10px] uppercase tracking-wide text-slate-400">{label}</div>}
      </div>
    </div>
  );
}

export function MatchBar({ score }) {
  const tone = score >= 75 ? "bg-brandgreen" : score >= 45 ? "bg-navy" : "bg-amber-400";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-200">
        <div className={`h-full rounded-full ${tone} transition-all duration-500`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-[11px] font-bold text-slate-600">{score}%</span>
    </div>
  );
}
