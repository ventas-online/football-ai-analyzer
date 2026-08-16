import streamlit as st
from pathlib import Path
import json
import pandas as pd

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

# --- Resumen ---
acc = float(m.get('accuracy', 0) or 0)
base = float(b.get('accuracy', 0) or 0)
edge = acc - base

c1, c2, c3, c4 = st.columns(4)
c1.metric('Partidos evaluados', f"{report.get('predictions_evaluated', '—'):,}")
c2.metric('Acierto 1X2', f'{acc * 100:.2f}%')
c3.metric('Baseline', f'{base * 100:.2f}%')
c4.metric('Ventaja', f'{edge * 100:+.2f} pp')

# --- Ranking de señales ---
st.subheader('🏆 Ranking de señales')
ranking = report.get('signal_ranking', {})
rows = []
for market, items in ranking.get('markets', {}).items():
    for item in items:
        rows.append({
            'Mercado': 'Over 2.5' if market == 'over_25' else 'BTTS Sí',
            'Umbral': f"≥ {float(item.get('threshold', 0)):.2f}",
            'Muestras': int(item.get('samples', 0)),
            'Prob. media': f"{float(item.get('mean_probability', 0)) * 100:.1f}%",
            'Acierto': f"{float(item.get('hit_rate', 0)) * 100:.1f}%",
            'Gap calibración': f"{float(item.get('calibration_gap', 0)) * 100:+.1f} pp",
            'Brier': f"{float(item.get('brier', 0)):.3f}",
            'Estado': item.get('status', '—'),
        })

if rows:
    df = pd.DataFrame(rows)
    status_order = {'KEEP_FOR_REVIEW': 0, 'REVIEW': 1, 'INSUFFICIENT_SAMPLE': 2}
    df['_order'] = df['Estado'].map(status_order).fillna(9)
    df = df.sort_values(['_order', 'Mercado', 'Muestras'], ascending=[True, True, False]).drop(columns='_order')
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption('KEEP_FOR_REVIEW = señal que merece conservarse para revisión; REVIEW = requiere análisis adicional; INSUFFICIENT_SAMPLE = demasiadas pocas muestras para concluir.')
else:
    st.info('No hay señales en el informe.')

# --- Análisis de valor ---
st.subheader('💰 Análisis de valor')
value = report.get('value_analysis', {})
signals = value.get('signals', []) if isinstance(value, dict) else value
value_rows = []
for item in signals or []:
    value_rows.append({
        'Mercado': 'Over 2.5' if item.get('market') == 'over_25' else 'BTTS Sí' if item.get('market') == 'btts_yes' else item.get('market', '—'),
        'Partidos': int(item.get('n', 0)),
        'Aciertos': int(item.get('wins', 0)),
        'Tasa acierto': f"{float(item.get('hit_rate', 0)) * 100:.1f}%",
        'Apuestas': int(item.get('bets', 0)),
        'ROI': '—' if item.get('status') == 'ODDS_REQUIRED' else f"{float(item.get('roi', 0)) * 100:.2f}%",
        'Estado': 'Faltan cuotas históricas' if item.get('status') == 'ODDS_REQUIRED' else item.get('status', '—'),
    })

if value_rows:
    st.dataframe(pd.DataFrame(value_rows), use_container_width=True, hide_index=True)
    if not value.get('odds_file_present', False):
        st.info('ℹ️ El ROI/EV no se calcula todavía porque no hay cuotas históricas reales cargadas. El sistema evita inventarlas.')
else:
    st.info('Sin análisis de valor todavía.')

# --- Rendimiento por periodo ---
st.subheader('📅 Rendimiento por periodo')
periods = report.get('calendar_period_metrics', {})
period_rows = []
for period, item in periods.items():
    period_rows.append({
        'Periodo': period,
        'Muestras': int(item.get('samples', 0)),
        'Accuracy': f"{float(item.get('accuracy', 0)) * 100:.1f}%",
        'Log loss': f"{float(item.get('log_loss', 0)):.3f}",
        'Brier': f"{float(item.get('brier_multiclass', 0)):.3f}",
    })
if period_rows:
    st.dataframe(pd.DataFrame(period_rows), use_container_width=True, hide_index=True)

# --- Calibración ---
st.subheader('📐 Calibración')
cal = report.get('calibration', {})
if cal:
    tab1, tab2 = st.tabs(['Over 2.5', 'BTTS Sí'])
    for tab, key in ((tab1, 'over_25'), (tab2, 'btts_yes')):
        with tab:
            items = cal.get(key, [])
            cal_rows = [{
                'Rango': x.get('range', '—'),
                'Muestras': int(x.get('samples', 0)),
                'Probabilidad media': f"{float(x.get('mean_probability', 0)) * 100:.1f}%",
                'Tasa observada': f"{float(x.get('observed_rate', 0)) * 100:.1f}%",
            } for x in items]
            if cal_rows:
                st.dataframe(pd.DataFrame(cal_rows), use_container_width=True, hide_index=True)
            else:
                st.info('Sin datos para este mercado.')
else:
    st.info('Sin datos de calibración.')

# --- Diagnóstico ---
with st.expander('🔎 Diagnóstico del modelo'):
    st.write(f"**Versión:** {report.get('model_version', '—')}")
    design = report.get('evaluation_design', {})
    st.write(f"**Método:** {design.get('method', '—')}")
    st.write(f"**Future leakage:** {'No detectado' if design.get('future_leakage') is False else 'Revisar'}")
    st.write(f"**Muestra mínima de señal:** {ranking.get('min_samples', design.get('minimum_signal_sample', '—'))}")
    st.write(f"**Partidos de entrada:** {report.get('matches_input', '—'):,}")
    st.write(f"**Partidos evaluados:** {report.get('predictions_evaluated', '—'):,}")

st.divider()
st.caption('Las probabilidades son estimaciones y no garantías de resultados.')
