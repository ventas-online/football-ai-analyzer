import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Football AI Analyzer", page_icon="⚽", layout="wide")
st.title("⚽ Football AI Analyzer")
st.caption("Análisis estadístico personal — no ejecuta apuestas automáticamente.")

# The backtest writes to data/reports/backtest.json. Keep artifact fallbacks
# so the dashboard can also be used with a downloaded workflow artifact.
REPORT_PATHS = [
    Path("data/reports/backtest.json"),
    Path("reports/backtest.json"),
    Path("artifacts/backtest.json"),
]
report_path = next((p for p in REPORT_PATHS if p.exists()), None)
if report_path is None:
    st.warning("No hay un informe generado todavía. Ejecuta el workflow de GitHub Actions y descarga su artefacto si estás ejecutando el dashboard fuera de GitHub.")
    st.stop()

with report_path.open(encoding="utf-8") as f:
    report = json.load(f)

metrics = report.get("metrics_1x2", {})
baseline = report.get("baseline_1x2", {})
accuracy = float(metrics.get("accuracy", 0) or 0)
baseline_accuracy = float(baseline.get("accuracy", 0) or 0)

cols = st.columns(4)
cols[0].metric("Predicciones", report.get("predictions_evaluated", "—"))
cols[1].metric("Acierto 1X2", f"{accuracy * 100:.2f}%")
cols[2].metric("Baseline", f"{baseline_accuracy * 100:.2f}%")
cols[3].metric("Ventaja", f"{(accuracy - baseline_accuracy) * 100:.2f} pp")

st.subheader("Cobertura")
st.write(f"Partidos de entrada: **{report.get('matches_input', '—')}**")
st.write(f"Diseño: **{report.get('evaluation_design', {}).get('method', '—')}**")

st.subheader("Ranking de señales")
signals = report.get("signal_ranking", [])
if signals:
    st.dataframe(signals, use_container_width=True)
else:
    st.info("Todavía no hay señales en el informe.")

st.subheader("Análisis de valor")
value = report.get("value_analysis", {})
st.write(f"Archivo de cuotas presente: **{value.get('odds_file_present', False)}**")
st.write(f"Filas de cuotas cargadas: **{value.get('odds_rows_loaded', 0)}**")
value_rows = value.get("signals", [])
if value_rows:
    st.dataframe(value_rows, use_container_width=True)
else:
    st.info("Sin cuotas históricas disponibles: las señales de valor quedan como ODDS_REQUIRED.")

st.subheader("Diagnóstico de calibración")
calibration = report.get("calibration", {})
for market, rows in calibration.items():
    st.markdown(f"**{market}**")
    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("Sin datos de calibración.")

st.divider()
st.caption("Las probabilidades son estimaciones estadísticas y no garantizan resultados.")
