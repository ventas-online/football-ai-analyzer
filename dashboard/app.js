async function loadReport() {
  const fallback = {model_version:'ensemble-v3-form-elo-poisson-mc', predictions_evaluated:0, baseline_1x2:{accuracy:null}, metrics_1x2:{accuracy:null}, value_analysis:{odds_rows_loaded:0, signals:[]}, signal_ranking:[]};
  try {
    const res = await fetch('../data/reports/backtest.json', {cache:'no-store'});
    if (!res.ok) throw new Error('report unavailable');
    return await res.json();
  } catch (_) { return fallback; }
}

function pct(x) { return Number.isFinite(Number(x)) ? `${(Number(x) * 100).toFixed(1)}%` : '—'; }
function marketName(m) { return ({over_25:'Over 2.5', btts_yes:'BTTS Sí'}[m] || m); }

function render(report) {
  const signals = document.querySelector('#signals');
  const rows = (report.value_analysis?.signals || []).filter(x => x.status === 'VALUE_CANDIDATE').slice(0, 10);
  if (signals) {
    signals.innerHTML = rows.length ? rows.map(x => `
      <div class="signal"><div><strong>${marketName(x.market)}</strong><small>${x.date} · ${x.home_team} vs ${x.away_team}</small></div>
      <div class="prob">${pct(x.probability)}</div><span>${x.market_odds ? `Edge ${pct(x.edge)}` : 'ODDS REQUIRED'}</span></div>`).join('')
      : '<p>No hay señales de valor con cuotas reales cargadas.</p>';
  }
  const count = document.querySelector('#count'); if (count) count.textContent = String(report.predictions_evaluated || 0);
  const version = document.querySelector('#version'); if (version) version.textContent = report.model_version || '—';
  const accuracy = document.querySelector('#accuracy'); if (accuracy) accuracy.textContent = pct(report.metrics_1x2?.accuracy);
  const baseline = document.querySelector('#baseline'); if (baseline) baseline.textContent = pct(report.baseline_1x2?.accuracy);
  const odds = document.querySelector('#odds'); if (odds) odds.textContent = String(report.value_analysis?.odds_rows_loaded || 0);
}

document.addEventListener('DOMContentLoaded', async () => render(await loadReport()));
