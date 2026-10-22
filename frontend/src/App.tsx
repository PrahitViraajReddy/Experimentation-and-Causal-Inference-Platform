import { ChangeEvent, FormEvent, useEffect, useState } from "react";

const API = (import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? "http://127.0.0.1:8000" : "https://experimentation-and-causal-inference.onrender.com")).replace(/\/+$/, "");
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

  function changeMethod(next: string) {
    setMethod(next);
    if (next === "proportion_z") { setControl("42,500"); setTreatment("58,500"); }
    else if (next === "chi_square") { setControl("30,20"); setTreatment("20,30"); }
    else { setControl("1,0,1,1,0,1,0,1,1,0"); setTreatment("1,1,1,1,0,1,1,1,0,1"); }
  }
  const [result, setResult] = useState<Result | null>(null);
  const [csvText, setCsvText] = useState("");
  const [csvName, setCsvName] = useState("");
  const [advancedResult, setAdvancedResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">("checking");

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API}/api/v1/health`, { signal: controller.signal })
      .then((response) => { if (!response.ok) throw new Error("API health check failed"); return response.json(); })
      .then((body) => setApiStatus(body.status === "ok" ? "online" : "offline"))
      .catch((error) => { if (error.name !== "AbortError") setApiStatus("offline"); });
    return () => controller.abort();
  }, []);

  async function uploadCsv(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".csv")) { setError("Please upload a .csv file."); return; }
    setCsvName(file.name); setCsvText(await file.text()); setError(""); setAdvancedResult(null);
  }

  async function runAdvanced(kind: "bayesian" | "sequential") {
    setError(""); setAdvancedResult(null);
    try {
      const parse = (value: string) => value.split(",").map((part) => Number(part.trim()));
      const [cs, ct] = parse(control); const [ts, tt] = parse(treatment);
      if (![cs, ct, ts, tt].every(Number.isFinite)) throw new Error("For Bayesian/sequential analysis enter successes,total for both groups.");
      const response = await fetch(`${API}/api/v1/experiments/${kind}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ control_successes: cs, control_total: ct, treatment_successes: ts, treatment_total: tt, ...(kind === "sequential" ? { looks: 5, current_look: 1 } : {}) }) });
      const body = await response.json(); if (!response.ok) throw new Error(body.detail || "Advanced analysis failed."); setAdvancedResult(body);
    } catch (e) { setError(e instanceof Error ? e.message : "Advanced analysis failed."); }
  }

  async function runCsv() {
    setError(""); setAdvancedResult(null);
    if (!csvText) { setError("Upload a CSV file first."); return; }
    try {
      const response = await fetch(`${API}/api/v1/data/analyze-csv`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ csv_text: csvText, method: "welch_t", group_column: "variant", outcome_column: "converted" }) });
      const body = await response.json(); if (!response.ok) throw new Error(body.detail || "CSV analysis failed."); setAdvancedResult(body);
    } catch (e) { setError(e instanceof Error ? e.message : "CSV analysis failed."); }
  }

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
    <header className="topbar"><a className="brand" href="#"><span className="mark">∑</span> EvidenceLab</a><span className={`status api-status ${apiStatus}`} title={`Backend API: ${API}`}><i /> {apiStatus === "checking" ? "Connecting to API…" : apiStatus === "online" ? "API connected" : "API unavailable"}</span></header>
    <section className="hero"><p className="eyebrow">EXPERIMENTATION & CAUSAL INFERENCE</p><h1>Make decisions with<br/><em>statistical evidence.</em></h1><p className="intro">A transparent workspace for experiment analysis. Quantify uncertainty, inspect effect sizes, and keep assumptions visible.</p></section>
    <section className="grid">
      <form className="panel" onSubmit={run}>
        <div className="heading"><div><p className="eyebrow">01 / ANALYSIS SETUP</p><h2>Compare two groups</h2></div><span className="step">01</span></div>
        <label>Statistical method<select value={method} onChange={e => changeMethod(e.target.value)}><option value="welch_t">Welch's t-test · continuous outcome</option><option value="proportion_z">Two-proportion z-test · conversion</option><option value="chi_square">Chi-square · category counts</option></select></label>
        <label>Control data <small>{method === "proportion_z" ? "successes,total" : method === "chi_square" ? "category counts" : "comma-separated observations"}</small><textarea rows={4} value={control} onChange={e => setControl(e.target.value)} required /></label>
        <label>Treatment data <small>{method === "proportion_z" ? "successes,total" : method === "chi_square" ? "category counts in same order" : "comma-separated observations"}</small><textarea rows={4} value={treatment} onChange={e => setTreatment(e.target.value)} required /></label>
        <div className="notice"><b>Input format</b><p>{method === "proportion_z" ? "Enter successes,total for each group (e.g. 42,500). The values update automatically when you switch methods." : method === "chi_square" ? "Enter category counts for each group in the same category order." : "Enter raw numeric observations for each group, separated by commas."}</p></div>
        <button disabled={loading}>{loading ? "Analyzing…" : "Run analysis"} <span>↗</span></button>
        {error && <p className="error" role="alert">{error}</p>}
      </form>
      <section className="panel results" aria-live="polite">
        <div className="heading"><div><p className="eyebrow">02 / STATISTICAL OUTPUT</p><h2>Results & interpretation</h2></div><span className="step">02</span></div>
        {!result ? <div className="empty"><div className="empty-icon">∿</div><h3>Your evidence appears here</h3><p>Run an analysis to inspect the test statistic, p-value, effect estimate, and interpretation.</p></div> : <>
          <div className="banner"><small>RESULT AT α = {result.alpha}</small><strong>{result.statistically_significant ? "Statistically significant" : "Not statistically significant"}</strong></div>
          <div className="metrics"><div><small>P-value</small><strong>{result.p_value.toPrecision(4)}</strong></div><div><small>Test statistic</small><strong>{result.statistic.toFixed(3)}</strong></div><div><small>Control n</small><strong>{result.sample_size_control.toLocaleString()}</strong></div><div><small>Treatment n</small><strong>{result.sample_size_treatment.toLocaleString()}</strong></div></div>
          <div className="effect"><p className="eyebrow">EFFECT ESTIMATE</p>{Object.entries(result.effect).map(([key,value]) => <div className="effect-row" key={key}><span>{key.replace(/_/g, " ")}</span><b>{Array.isArray(value) ? value.map(x => x.toFixed(4)).join(" to ") : typeof value === "number" ? value.toFixed(4) : value ?? "—"}</b></div>)}</div>
          <div className="interpretation"><small>INTERPRETATION</small><p>{result.interpretation}</p></div>
        </>}
        <p className="footnote">Statistical significance is not practical significance. Verify design assumptions and data quality before deciding.</p>
      </section>
    </section>
    <section className="grid advanced-grid">
      <section className="panel">
        <div className="heading"><div><p className="eyebrow">03 / ADVANCED METHODS</p><h2>Bayesian & sequential</h2></div><span className="step">03</span></div>
        <p className="intro small-intro">Use successes,total values in the two input fields above. These methods analyze binary conversion outcomes.</p>
        <div className="button-row"><button type="button" onClick={() => runAdvanced("bayesian")}>Bayesian A/B</button><button type="button" className="secondary" onClick={() => runAdvanced("sequential")}>Sequential check</button></div>
        {advancedResult && <div className="json-result"><pre>{JSON.stringify(advancedResult, null, 2)}</pre></div>}
      </section>
      <section className="panel">
        <div className="heading"><div><p className="eyebrow">04 / DATA UPLOAD</p><h2>Analyze a CSV</h2></div><span className="step">04</span></div>
        <label>CSV file<input type="file" accept=".csv,text/csv" onChange={uploadCsv}/></label>
        {csvName && <p className="footnote">Selected: {csvName} · {(csvText.length / 1024).toFixed(1)} KB</p>}
        <p className="footnote">For this quick upload flow, include a <code>variant</code> column with two groups and a numeric <code>converted</code> outcome. The upload is analyzed in memory and is not stored.</p>
        <button type="button" onClick={runCsv}>Analyze uploaded CSV ↗</button>
      </section>
    </section>
    {result && (
      <section className="panel chart-panel">
        <p className="eyebrow">VISUAL SUMMARY</p>
        <h2>Group observations</h2>
        <div className="bars">
          <div>
            <span>Control · n={result.sample_size_control}</span>
            <div className="bar-track"><i style={{ width: "50%" }} /></div>
          </div>
          <div>
            <span>Treatment · n={result.sample_size_treatment}</span>
            <div className="bar-track"><i style={{ width: "75%" }} /></div>
          </div>
        </div>
        <p className="footnote">Bars show relative sample-size indicators, not the treatment effect. Interpret the numeric estimate and confidence interval above.</p>
      </section>
    )}
    <footer><span>EvidenceLab · Transparent statistical results</span><span>React · FastAPI · Statsmodels</span></footer>
  </main>;
}
