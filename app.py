import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Market Radar Quant Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PROFESIONALES ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .quant-card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 20px; }
    .disclaimer-box { background-color: #21262d; padding: 15px; border-radius: 6px; border-left: 4px solid #f85149; font-size: 13px; color: #8b949e; }
    </style>
""", unsafe_allow_html=True)

# --- ESTADO DE SESIÓN Y BLINDAJE LEGAL ---
if 'tos_accepted' not in st.session_state:
    st.session_state.tos_accepted = False
if 'user_plan' not in st.session_state:
    st.session_state.user_plan = "Free"

if not st.session_state.tos_accepted:
    st.markdown("## 🛡️ Términos de Servicio y Descargo Legal (ToS)")
    st.markdown("""
    <div class="disclaimer-box">
    <b>AVISO LEGAL OBLIGATORIO:</b> Market Radar Quant Terminal es una plataforma de software estadístico, procesamiento de datos públicos y análisis cuantitativo de carácter estrictamente educativo, informativo y de investigación. 
    Esta herramienta <b>no constituye asesoramiento financiero, gestión de capital ni recomendación de inversión</b>. La plataforma no tiene acceso a fondos de terceros ni ejecuta operaciones automáticas en brokers. 
    El usuario asume absoluta e íntegramente la responsabilidad sobre sus decisiones operativas y gestión de riesgo.
    </div>
    """, unsafe_allow_html=True)
    
    accepted = st.checkbox("He leído, comprendido y acepto los Términos de Servicio y el Descargo de Responsabilidad de Market Radar Quant Terminal.")
    if st.button("Continuar a la Terminal"):
        if accepted:
            st.session_state.tos_accepted = True
            st.rerun()
        else:
            st.warning("Debes aceptar los Términos de Servicio para acceder.")
    st.stop()

# --- BARRA LATERAL SAAS ---
st.sidebar.title("🔐 Licencia SaaS")
user_email = st.sidebar.text_input("Correo Registrado", "usuario@ejemplo.com")
selected_plan = st.sidebar.selectbox("Plan de Suscripción", ["Basic (Gratuito)", "Pro ($19.99/mes)", "Institutional / VIP ($49.99/mes)"])

if st.sidebar.button("Validar Licencia"):
    if "Pro" in selected_plan:
        st.session_state.user_plan = "Pro"
    elif "Institutional" in selected_plan:
        st.session_state.user_plan = "Institutional"
    else:
        st.session_state.user_plan = "Free"
    st.sidebar.success(f"Nivel Activo: {st.session_state.user_plan}")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Plan Actual:** `{st.session_state.user_plan}`")

# --- CONTENIDO PRINCIPAL ---
st.title("📊 Market Radar Quant Terminal")
st.markdown("### Procesamiento Estadístico de Mercados y Flujos Institucionales")

# MÓDULO 1: RADAR DE PERCENTILES
st.header("1. Radar Cuantitativo de Activos")
df_market = pd.DataFrame({
    "Activo": ["EUR/USD", "WTI Crude", "Gold (XAU)", "S&P 500", "Copper"],
    "Clase": ["Forex", "Commodity", "Commodity", "Índice", "Commodity"],
    "Precio Actual": [1.0850, 78.40, 2380.50, 5250.00, 4.25],
    "Percentil 1Y": [15.2, 88.5, 92.1, 85.0, 18.3],
    "Percentil 3M": [10.5, 75.2, 80.0, 70.4, 12.1],
    "Estado Estadístico": ["Rango de Desviación Bajo (≤20%)", "Sobrecompra", "Sobrecompra", "Sobrecompra", "Rango de Desviación Bajo (≤20%)"],
    "Flujo COT (Institucional)": ["Neto Comprador (+14k)", "Neto Vendedor (-8k)", "Neto Comprador (+22k)", "Neutral", "Neto Comprador (+19k)"]
})
st.dataframe(df_market, use_container_width=True)

# MÓDULO 2: MICHAEL VIRTUAL (MOTOR ACADÉMICO)
st.header("2. Michael Virtual — Asistente de Tesis Cuantitativas")
activo_sel = st.selectbox("Seleccionar Activo para Histórico", df_market["Activo"].tolist())
row_sel = df_market[df_market["Activo"] == activo_sel].iloc[0]

if st.button("Generar Resumen Estadístico"):
    st.markdown(f"""
    <div class="quant-card">
    <h4>📋 Resumen de Métricas Históricas: {row_sel['Activo']}</h4>
    <ul>
        <li><b>Cotización:</b> {row_sel['Precio Actual']}</li>
        <li><b>Percentil 1Y:</b> {row_sel['Percentil 1Y']}% ({row_sel['Estado Estadístico']})</li>
        <li><b>Reporte CFTC / COT:</b> {row_sel['Flujo COT (Institucional)']}</li>
    </ul>
    <p><b>Nota Analítica:</b> El activo cotiza en rangos estadísticos de desviación respecto a su media histórica. Los datos no constituyen recomendación de compra o venta.</p>
    </div>
    """, unsafe_allow_html=True)

# MÓDULO 3: CALCULADORA DE RIESGO
st.header("3. Calculadora de Exposición y Control de Riesgo")
c1, c2 = st.columns(2)
with c1:
    cap = st.number_input("Capital Asignado ($ USD)", value=10000.0)
    piso = st.slider("Distancia al Suelo Anual Estimada (%)", 1.0, 30.0, 10.0)
with c2:
    apalanque = st.selectbox("Apalancamiento Máximo", [1, 2, 5, 10, 20], index=2)
    expo = cap * apalanque
    riesgo = cap * (piso / 100.0)

st.markdown(f"""
<div class="quant-card">
    <p><b>Exposición Teórica:</b> ${expo:,.2f} USD</p>
    <p><b>Riesgo Estimado al Piso Anual:</b> ${riesgo:,.2f} USD</p>
</div>
""", unsafe_allow_html=True)

# BLOQUEO DE PLANES
if st.session_state.user_plan == "Free":
    st.info("🔒 **Funciones Pro/VIP Bloqueadas:** Actualiza tu cuenta para acceder a alertas por Telegram y backtesting.")
else:
    st.success("✨ Módulo Pro Activo: Conexión de alertas y datos extendidos habilitados.")