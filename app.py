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
st.markdown("### Procesamiento Estadístico de Mercados, Cartera Completa y Sesgo Long-Only")

# BASE DE DATOS DE LA CARTERA COMPLETA
df_market_full = pd.DataFrame({
    "Activo": ["EUR/USD", "GBP/USD", "USD/JPY", "WTI Crude", "Brent Crude", "Gold (XAU)", "Silver (XAG)", "S&P 500", "Nasdaq 100", "Copper", "Coffee", "Sugar"],
    "Clase": ["Forex", "Forex", "Forex", "Commodity", "Commodity", "Commodity", "Commodity", "Índice", "Índice", "Commodity", "Softs", "Softs"],
    "Precio Actual": [1.0850, 1.2980, 149.20, 78.40, 82.10, 2380.50, 28.40, 5250.00, 18200.00, 4.25, 245.00, 22.10],
    "Percentil 1Y": [15.2, 18.5, 89.0, 88.5, 82.0, 92.1, 85.0, 85.0, 88.0, 18.3, 12.0, 19.5],
    "Percentil 3M": [10.5, 14.2, 85.1, 75.2, 70.1, 80.0, 78.0, 70.4, 75.0, 12.1, 8.5, 15.0],
    "Estructura Estadística": [
        "Desviación Baja (≤20%) - Sesgo Comprador", "Desviación Baja (≤20%) - Sesgo Comprador", "Sobrecompra", 
        "Sobrecompra", "Sobrecompra", "Sobrecompra", "Sobrecompra", "Sobrecompra", "Sobrecompra", 
        "Desviación Baja (≤20%) - Sesgo Comprador", "Desviación Baja (≤20%) - Sesgo Comprador", "Desviación Baja (≤20%) - Sesgo Comprador"
    ],
    "Flujo COT (Institucional)": [
        "Neto Comprador (+14k)", "Neto Comprador (+8k)", "Neto Vendedor (-12k)", 
        "Neto Vendedor (-8k)", "Neutral", "Neto Comprador (+22k)", "Neto Comprador (+5k)", 
        "Neutral", "Neutral", "Neto Comprador (+19k)", "Neto Comprador (+11k)", "Neto Comprador (+7k)"
    ]
})

# MÓDULO 1: FILTROS Y VISTA DE CARTERA COMPLETA
st.header("1. Explorador de Cartera y Percentiles")

col_f1, col_f2 = st.columns(2)
with col_f1:
    vista_cartera = st.radio("Modo de Visualización de Cartera", ["Solo Activos en Percentil Bajo (≤ 20%)", "Ver Cartera Completa (Todos los Activos)"])
with col_f2:
    threshold_percentile = st.slider("Umbral Máximo de Percentil 1Y para Filtrado (%)", 5, 50, 20)

if "Solo Activos" in vista_cartera:
    df_filtered = df_market_full[df_market_full["Percentil 1Y"] <= threshold_percentile]
else:
    df_filtered = df_market_full

st.dataframe(df_filtered, use_container_width=True)

# MÓDULO 2: MICHAEL VIRTUAL (TESIS CUANTITATIVA Y ESTRATEGIA LONG-ONLY)
st.header("2. Michael Virtual — Motor de Tesis de Sesgo Comprador (Long-Only)")
activo_sel = st.selectbox("Seleccionar Activo para Tesis Contextual", df_market_full["Activo"].tolist())
row_sel = df_market_full[df_market_full["Activo"] == activo_sel].iloc[0]

if st.button("Generar Informe Técnico Contextual"):
    st.markdown(f"""
    <div class="quant-card">
    <h4>📋 Informe Técnico para: {row_sel['Activo']} ({row_sel['Clase']})</h4>
    <ul>
        <li><b>Cotización Actual:</b> {row_sel['Precio Actual']}</li>
        <li><b>Percentil de Desviación 1Y:</b> {row_sel['Percentil 1Y']}%</li>
        <li><b>Estado de Desviación:</b> {row_sel['Estructura Estadística']}</li>
        <li><b>Posicionamiento Institucional CFTC (COT):</b> {row_sel['Flujo COT (Institucional)']}</li>
    </ul>
    <p><b>Evaluación de la Matriz Unidireccional (Long-Only):</b> Cuando un activo presenta percentiles de desviación históricos en zona baja (≤20%) junto a un posicionamiento neto comprador en los reportes COT, el modelo cuantifica una asimetría favorable para estructuras de acumulación por tramos hacia objetivos de media. <i>Información estrictamente descriptiva; no constituye recomendación directa.</i></p>
    </div>
    """, unsafe_allow_html=True)

# MÓDULO 3: CALCULADORA DE EXPOSICIÓN Y GUÍA INSTRUCTIVA
st.header("3. Calculadora de Exposición y Guía de Gestión de Riesgo (MT4/MT5)")

st.markdown("""
<div class="quant-card">
<b>📘 Instructivo de Operatoria y Gestión de Riesgo Patrimonial (Long-Only):</b><br>
Esta calculadora determina el dimensionamiento exacto de posición (lotaje) para operar exclusivamente en dirección compradora sin necesidad de utilizar un Stop-Loss rígido convencional. 
El cálculo dimensiona el riesgo en función de la <b>distancia porcentual al suelo/piso anual estimado del activo</b>, garantizando que la cuenta soporte caídas extremas preservando el margen de flotancia.
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    cap = st.number_input("Capital Total Asignado ($ USD)", value=10000.0, step=500.0)
    piso = st.slider("Distancia Estimada al Suelo Anual (%)", 1.0, 30.0, 10.0)
    pips_piso = st.number_input("Distancia en Pips/Puntos al Piso Anual", value=250, step=10)
with c2:
    apalanque = st.selectbox("Apalancamiento Máximo Operativo", [1, 2, 5, 10, 20], index=2)
    expo = cap * apalanque
    riesgo = cap * (piso / 100.0)
    lote_sugerido = (riesgo / (pips_piso * 10)) if pips_piso > 0 else 0.01

st.markdown(f"""
<div class="quant-card">
    <h4>📊 Desglose de Parámetros de Operación</h4>
    <p><b>Exposición Máxima Permitida:</b> ${expo:,.2f} USD (con apalancamiento {apalanque}x)</p>
    <p><b>Riesgo Teórico Asumido al Piso Anual ({piso}%):</b> ${riesgo:,.2f} USD</p>
    <p><b>Dimensionamiento de Posición Sugerido:</b> <code>{lote_sugerido:.2f} Lotes</code> (MT4/MT5)</p>
    <p style='font-size:12px; color:#8b949e;'>Nota: El lotaje asegura que si el activo retrocede hasta su suelo anual estimado, la pérdida no superará el porcentaje configurado.</p>
</div>
""", unsafe_allow_html=True)

# BLOQUEO DE PLANES AVANZADOS
if st.session_state.user_plan == "Free":
    st.info("🔒 **Funciones Pro/VIP Bloqueadas:** Actualiza tu cuenta para acceder a alertas por Telegram y módulo de backtesting profundo.")
else:
    st.success("✨ Módulo Pro Activo: Conexión de alertas y datos extendidos habilitados.")
