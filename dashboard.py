import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title='Football AI Analyzer', page_icon='⚽', layout='wide')

st.title('⚽ Football AI Analyzer')
st.caption('Análisis estadístico personal — no ejecuta apuestas automáticamente.')

report_path = Path('reports/backtest.json')
if not report_path.exists():
    report_path = Path('artifacts/backtest.json')

if not report_path.exists():
    st.warning('No hay un informe generado todavía. Ejecuta el workflow de GitHub Actions.')
    st.stop()

with report_path.open(encoding='utf-8') as f:
    report = json.load(f)

metrics = report.get('metrics', report)
cols = st.columns(4)
cols[0].metric('Predicciones', metrics.get('n_predictions', '—'))
cols[1].metric('Acierto 1X2', f"{metrics.get('accuracy', 0)*100:.2f}%")
cols[2].metric('Baseline', f"{metrics.get('baseline_accuracy', 0)*100:.2f}%")
cols[3].metric('Ventaja', f"{(metrics.get('accuracy', 0)-metrics.get('baseline_accuracy', 0))*100:.2f} pp")

st.subheader('Señales')
signals = report.get('signals', report.get('signal_ranking', []))
if signals:
    st.dataframe(signals, use_container_width=True)
else:
    st.info('Todavía no hay señales en el informe.')

st.subheader('Valor')
value = report.get('value_signals', [])
if value:
    st.dataframe(value, use_container_width=True)
else:
    st.info('Sin cuotas históricas disponibles: las señales de valor mostrarán ODDS_REQUIRED.')

st.divider()
st.caption('Las probabilidades son estimaciones estadísticas y no garantizan resultados.')
