import streamlit as st
from pathlib import Path
import json

st.set_page_config(page_title='Football AI Analyzer', page_icon='⚽', layout='wide')

REPORT = Path('data/reports/backtest.json')

st.title('⚽ Football AI Analyzer')
st.caption('Panel personal de análisis estadístico. No realiza apuestas automáticamente.')

if not REPORT.exists():
    st.warning('Todavía no existe un informe. Ejecuta el workflow de datos/backtest primero.')
    st.stop()

report = json.loads(REPORT.read_text(encoding='utf-8'))
m = report.get('metrics_1x2', {})
b = report.get('baseline_1x2', {})

c1,c2,c3,c4 = st.columns(4)
c1.metric('Partidos evaluados', report.get('predictions_evaluated', '—'))
c2.metric('Acierto 1X2', f"{m.get('accuracy',0)*100:.2f}%")
c3.metric('Baseline', f"{b.get('accuracy',0)*100:.2f}%")
c4.metric('Ventaja', f"{(m.get('accuracy',0)-b.get('accuracy',0))*100:.2f} pp")

st.subheader('🏆 Ranking de señales')
signals = report.get('signal_ranking', [])
if signals:
    st.dataframe(signals, use_container_width=True, hide_index=True)
else:
    st.info('No hay señales en el informe.')

st.subheader('💰 Análisis de valor')
value = report.get('value_analysis', [])
if value:
    st.dataframe(value, use_container_width=True, hide_index=True)
else:
    st.info('Sin análisis de valor todavía.')

st.subheader('📐 Calibración')
cal = report.get('calibration', {})
if cal:
    st.json(cal)
else:
    st.info('Sin datos de calibración.')

st.divider()
st.caption('Las probabilidades son estimaciones y no garantías de resultados.')
