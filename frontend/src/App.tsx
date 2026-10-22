import { FormEvent, useState } from "react";

const API = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
type Result = {
  method: string; statistic: number; p_value: number; alpha: number;
  statistically_significant: boolean; sample_size_control: number;
  sample_size_treatment: number; effect: Record<string, number | number[] | null>;
  interpretation: string;
};

export default function App() {
  const [method, setMethod] = useState("welch_t");
  const [control, setControl] = useState("1,0,1,1,0,1,0,1,1,0");
  const [treatment, setTreatment] = useState("1,1,1,1,0,1,1,1,0,1");
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function run(event: FormEvent) {
    event.preventDefault(); setLoading(true); setError(""); setResult(null);
    const values = (text: string) => text.split(",").map((x) => Number(x.trim()));
    try {
      const response = await fetch(`${API}/api/v1/experiments/analyze`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ method, control: values(control), treatment: values(treatment), alpha: 0.05 }),
      });
      const body = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(body.detail) ? body.detail.map((x: { msg: string }) => x.msg).join("; ") : body.detail;
        throw new Error(detail || "Analysis failed.");
      }
      setResult(body as Result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not connect to the API. Start FastAPI and try again.");
    } finally { setLoading(false); }
  }

  return <main className="shell">
    <header className="topbar"><a className="brand" href="#"><span className="mark">∑</span> EvidenceLab</a><span className="status"><i /> Statistical workspace</span></header>
    <section className="hero"><p className="eyebrow">EXPERIMENTATION & CAUSAL INFERENCE</p><h1>Make decisions with<br/><em>statistical evidence.</em></h1><p className="intro">A transparent workspace for experiment analysis. Quantify uncertainty, inspect effect sizes, and keep assumptions visible.</p></section>
    <section className="grid">
      <form className="panel" onSubmit={run}>
        <div className="heading"><div><p className="eyebrow">01 / ANALYSIS SETUP</p><h2>Compare two groups</h2></div><span className="step">01</span></div>
        <label>Statistical method<select value={method} onChange={e => setMethod(e.target.value)}><option value="welch_t">Welch's t-test · continuous outcome</option><option value="proportion_z">Two-proportion z-test · conversion</option><option value="chi_square">Chi-square · category counts</option></select></label>
        <label>Control data <small>comma-separated values</small><textarea rows={4} value={control} onChange={e => setControl(e.target.value)} required /></label>
        <label>Treatment data <small>comma-separated values</small><textarea rows={4} value={treatment} onChange={e => setTreatment(e.target.value)} required /></label>
        <div className="notice"><b>Input format</b><p>For proportion testing, enter successes,total (e.g. 42,500) per group. For chi-square, enter category counts in the same order.</p></div>
        <button disabled={loading}>{loading ? "Analyzing…" : "Run analysis"} <span>↗</span></button>
        {error && <p className="error" role="alert">{error}</p>}
      </form>
      <section className="panel results" aria-live="polite">
        <div className="heading"><div><p className="eyebrow">02 / STATISTICAL OUTPUT</p><h2>Results & interpretation</h2></div><span className="step">02</span></div>
        {!result ? <div className="empty"><div className="empty-icon">∿</div><h3>Your evidence appears here</h3><p>Run an analysis to inspect the test statistic, p-value, effect estimate, and interpretation.</p></div> : <>
          <div className="banner"><small>RESULT AT α = {result.alpha}</small><strong>{result.statistically_significant ? "Statistically significant" : "Not statistically significant"}</strong></div>
          <div className="metrics"><div><small>P-value</small><strong>{result.p_value.toPrecision(4)}</strong></div><div><small>Test statistic</small><strong>{result.statistic.toFixed(3)}</strong></div><div><small>Control n</small><strong>{result.sample_size_control.toLocaleString()}</strong></div><div><small>Treatment n</small><strong>{result.sample_size_treatment.toLocaleString()}</strong></div></div>
          <div className="effect"><p className="eyebrow">EFFECT ESTIMATE</p>{Object.entries(result.effect).map(([key,value]) => <div className="effect-row" key={key}><span>{key.replaceAll("_"," ")}</span><b>{Array.isArray(value) ? value.map(x => x.toFixed(4)).join(" to ") : typeof value === "number" ? value.toFixed(4) : value ?? "—"}</b></div>)}</div>
          <div className="interpretation"><small>INTERPRETATION</small><p>{result.interpretation}</p></div>
        </>}
        <p className="footnote">Statistical significance is not practical significance. Verify design assumptions and data quality before deciding.</p>
      </section>
    </section>
    <footer><span>EvidenceLab · Transparent statistical results</span><span>React · FastAPI · Statsmodels</span></footer>
  </main>;
}
