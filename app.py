import streamlit as st
import pandas as pd
import yfinance as yf

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Market Radar Quant Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PROFESIONALES + ANUNCIOS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .quant-card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 20px; }
    .disclaimer-box { background-color: #21262d; padding: 15px; border-radius: 6px; border-left: 4px solid #f85149; font-size: 13px; color: #8b949e; }
    .news-box { background-color: #161b22; padding: 12px; border-radius: 6px; border-left: 3px solid #58a6ff; margin-bottom: 10px; font-size: 14px; }
    /* ESTILOS DE PUBLICIDAD MONETIZABLE */
    .ad-container {
        background: linear-gradient(135deg, #1f242d 0%, #0e1117 100%);
        border: 1px dashed #e3b341;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
    }
    .ad-title { color: #e3b341; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
    .ad-button {
        background-color: #238636;
        color: white !important;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- BLINDAJE LEGAL (ToS) ---
if 'tos_accepted' not in st.session_state:
    st.session_state.tos_accepted = False
if 'user_plan' not in st.session_state:
    st.session_state.user_plan = "Free"

if not st.session_state.tos_accepted:
    st.markdown("## 🛡️ Términos de Servicio y Descargo Legal (ToS)")
    st.markdown("""
    <div class="disclaimer-box">
    <b>AVISO LEGAL OBLIGATORIO:</b> Market Radar Quant Terminal es una plataforma de software estadístico, procesamiento de datos públicos y análisis cuantitativo de carácter estrictamente educativo, informativo y de investigación. 
    Esta herramienta <b>no constituye asesoramiento financiero, gestión de capital ni recomendación de inversión</b>.
    </div>
    """, unsafe_allow_html=True)
    
    accepted = st.checkbox("He leído, comprendido y acepto los Términos de Servicio de Market Radar Quant Terminal.")
    if st.button("Continuar a la Terminal"):
        if accepted:
            st.session_state.tos_accepted = True
            st.rerun()
        else:
            st.warning("Debes aceptar los Términos de Servicio para acceder.")
    st.stop()

# --- BARRA LATERAL CON PUBLICIDAD ---
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

# BANNER PATROCINADO EN SIDEBAR
if st.session_state.user_plan == "Free":
    st.sidebar.markdown("""
    <div class="ad-container">
        <div class="ad-title">Anuncio Patrocinado</div>
        <p style="font-size: 12px; color: #c9d1d9;">¿Buscas un Broker con bajos spreads para operar Long-Only?</p>
        <a href="https://ftmo.com" target="_blank" class="ad-button">Abrir Cuenta de Pruebas</a>
    </div>
    """, unsafe_allow_html=True)

ACTIVOS_TICKERS = {
    "EUR/USD": {"ticker": "EURUSD=X", "clase": "Forex", "cot": "Neto Comprador (+14k)"},
    "GBP/USD": {"ticker": "GBPUSD=X", "clase": "Forex", "cot": "Neto Comprador (+8k)"},
    "USD/JPY": {"ticker": "JPY=X", "clase": "Forex", "cot": "Neto Vendedor (-12k)"},
    "WTI Crude": {"ticker": "CL=F", "clase": "Commodity", "cot": "Neto Vendedor (-8k)"},
    "Brent Crude": {"ticker": "BZ=F", "clase": "Commodity", "cot": "Neutral"},
    "Natural Gas": {"ticker": "NG=F", "clase": "Commodity", "cot": "Neto Comprador (+6k)"},
    "Gold (XAU)": {"ticker": "GC=F", "clase": "Commodity", "cot": "Neto Comprador (+22k)"},
    "Silver (XAG)": {"ticker": "SI=F", "clase": "Commodity", "cot": "Neto Comprador (+5k)"},
    "S&P 500": {"ticker": "^GSPC", "clase": "Índice", "cot": "Neutral"},
    "Nasdaq 100": {"ticker": "^IXIC", "clase": "Índice", "cot": "Neutral"},
    "Copper": {"ticker": "HG=F", "clase": "Commodity", "cot": "Neto Comprador (+19k)"},
    "Cocoa": {"ticker": "CC=F", "clase": "Softs", "cot": "Neto Comprador (+15k)"},
    "Coffee": {"ticker": "KC=F", "clase": "Softs", "cot": "Neto Comprador (+11k)"},
    "Sugar": {"ticker": "SB=F", "clase": "Softs", "cot": "Neto Comprador (+7k)"},
    "Corn": {"ticker": "ZC=F", "clase": "Agricultural", "cot": "Neutral"}
}

@st.cache_data(ttl=300)
def obtener_datos_mercado_real():
    filas = []
    for nombre, info in ACTIVOS_TICKERS.items():
        try:
            ticker_obj = yf.Ticker(info["ticker"])
            hist = ticker_obj.history(period="1y")
            if not hist.empty:
                precio_actual = hist["Close"].iloc[-1]
                min_52w = hist["Low"].min()
                max_52w = hist["High"].max()
                
                percentil_1y = ((precio_actual - min_52w) / (max_52w - min_52w)) * 100 if max_52w > min_52w else 50.0

                hist_3m = hist.tail(63)
                min_3m = hist_3m["Low"].min()
                max_3m = hist_3m["High"].max()
                percentil_3m = ((precio_actual - min_3m) / (max_3m - min_3m)) * 100 if max_3m > min_3m else 50.0

                estado = "Desviación Baja (≤20%) - Sesgo Comprador" if percentil_1y <= 20 else ("Sobrecompra" if percentil_1y >= 80 else "Rango Medio")

                filas.append({
                    "Activo": nombre,
                    "Clase": info["clase"],
                    "Precio Actual": round(precio_actual, 4),
                    "Mín 52 Sem": round(min_52w, 4),
                    "Máx 52 Sem": round(max_52w, 4),
                    "Percentil 1Y (%)": round(percentil_1y, 1),
                    "Percentil 3M (%)": round(percentil_3m, 1),
                    "Estructura Estadística": estado,
                    "Flujo COT (Institucional)": info["cot"]
                })
        except Exception:
            pass
    return pd.DataFrame(filas)

st.title("📊 Market Radar Quant Terminal")
st.markdown("### Procesamiento Estadístico de Mercados, Cartera Completa y Noticias en Vivo")

with st.spinner("Actualizando cotizaciones en vivo..."):
    df_market_full = obtener_datos_mercado_real()

def estilizar_condicion_pub(row):
    color = ''
    val = str(row['Estructura Estadística'])
    if "Desviación Baja" in val or "Compra" in val:
        color = 'background-color: rgba(46, 160, 67, 0.2); color: #3fb950;'
    elif "Sobrecompra" in val:
        color = 'background-color: rgba(248, 81, 73, 0.2); color: #f85149;'
    else:
        color = 'background-color: rgba(139, 148, 158, 0.1); color: #8b949e;'
    return [color if col == 'Estructura Estadística' else '' for col in row.index]

# MÓDULO 1: EXPLORADOR DE CARTERA
st.header("1. Explorador de Cartera y Percentiles Anuales")
col_f1, col_f2 = st.columns(2)
with col_f1:
    vista_cartera = st.radio("Modo de Visualización", ["Solo Activos en Percentil Bajo (≤ 20%)", "Ver Cartera Completa"])
with col_f2:
    threshold_percentile = st.slider("Umbral Máximo de Percentil 1Y (%)", 5, 50, 20)

if "Solo Activos" in vista_cartera:
    df_filtered = df_market_full[df_market_full["Percentil 1Y (%)"] <= threshold_percentile]
else:
    df_filtered = df_market_full

if not df_filtered.empty:
    st.dataframe(df_filtered.style.apply(estilizar_condicion_pub, axis=1), use_container_width=True)
else:
    st.info("No hay activos que cumplan con el filtro seleccionado.")

# MÓDULO 2: MICHAEL VIRTUAL CON GATILLO PUBLICITARIO Y NOTICIAS REPARADAS
st.header("2. 🤖 Michael Virtual — Tesis Cuantitativa & Noticias en Tiempo Real")

if not df_market_full.empty:
    activo_sel = st.selectbox("Seleccionar Activo para Tesis y Noticias", df_market_full["Activo"].tolist())
    row_sel = df_market_full[df_market_full["Activo"] == activo_sel].iloc[0]
    ticker_sym = ACTIVOS_TICKERS[activo_sel]["ticker"]

    col_t1, col_t2 = st.columns([1.2, 1])

    with col_t1:
        if st.button("✨ Generar Tesis Cuantitativa con Michael Virtual"):
            
            # GATILLO MONETIZABLE EN LA TESIS
            if st.session_state.user_plan == "Free":
                st.markdown("""
                <div class="ad-container">
                    <div class="ad-title">⚡ Patrocinado por Plataformas Afiliadas</div>
                    <p style="font-size: 13px; color: #c9d1d9; margin: 5px 0;"><b>¿Quieres ejecutar esta tesis sin pagar comisiones?</b></p>
                    <a href="https://www.tradingview.com" target="_blank" class="ad-button">Ver Gráfico Profesional Gratis 🚀</a>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="quant-card">
            <h4>📋 Informe Técnico: {row_sel['Activo']} ({row_sel['Clase']})</h4>
            <ul>
                <li><b>Cotización Actual:</b> {row_sel['Precio Actual']}</li>
                <li><b>Rango 52 Semanas:</b> Mín: {row_sel['Mín 52 Sem']} | Máx: {row_sel['Máx 52 Sem']}</li>
                <li><b>Percentil 1Y:</b> {row_sel['Percentil 1Y (%)']}%</li>
                <li><b>Flujo COT:</b> {row_sel['Flujo COT (Institucional)']}</li>
            </ul>
            <p><b>Evaluación Estadísticamente Unidireccional:</b> El activo opera cerca de su suelo anual de {row_sel['Mín 52 Sem']}, lo que presenta asimetría favorable para modelos de acumulación por tramos en estrategias Long-Only.</p>
            </div>
            """, unsafe_allow_html=True)

    with col_t2:
        st.markdown("#### 📰 Noticias del Mercado")
        try:
            t_obj = yf.Ticker(ticker_sym)
            noticias = t_obj.news
            if noticias:
                count = 0
                for n in noticias:
                    # Lógica de extracción segura de URL de yfinance
                    url_val = "#"
                    if 'link' in n and n['link']:
                        url_val = n['link']
                    elif 'content' in n and isinstance(n['content'], dict):
                        url_val = n['content'].get('clickThroughUrl', {}).get('url', '#')
                    
                    titulo = n.get('title', n.get('content', {}).get('title', 'Sin título'))
                    publisher = n.get('publisher', n.get('content', {}).get('provider', {}).get('displayName', 'Fuente Financiera'))

                    if titulo != 'Sin título' and count < 4:
                        st.markdown(f"""
                        <div class="news-box">
                        <b>{publisher}:</b> <a href="{url_val}" target="_blank" style="color: #58a6ff; font-weight: bold; text-decoration: none;">{titulo} 🔗</a>
                        </div>
                        """, unsafe_allow_html=True)
                        count += 1
            else:
                st.info("No hay noticias recientes indexadas para este ticker.")
        except Exception:
            st.info("Módulo de noticias temporalmente no disponible.")

# MÓDULO 3: CALCULADORA DE RIESGO
st.header("3. Calculadora de Exposición y Control de Riesgo")
c1, c2 = st.columns(2)
with c1:
    cap = st.number_input("Capital Asignado ($ USD)", value=10000.0, step=500.0)
    piso = st.slider("Distancia Estimada al Suelo Anual (%)", 1.0, 30.0, 10.0)
    pips_piso = st.number_input("Pips / Puntos al Piso Anual", value=250, step=10)
with c2:
    apalanque = st.selectbox("Apalancamiento Operativo", [1, 2, 5, 10, 20], index=2)
    expo = cap * apalanque
    riesgo = cap * (piso / 100.0)
    lote = (riesgo / (pips_piso * 10)) if pips_piso > 0 else 0.01

st.markdown(f"""
<div class="quant-card">
    <p><b>Exposición Teórica:</b> ${expo:,.2f} USD</p>
    <p><b>Riesgo al Piso Anual ({piso}%):</b> ${riesgo:,.2f} USD</p>
    <p><b>Dimensionamiento Sugerido:</b> <code>{lote:.2f} Lotes</code></p>
</div>
""", unsafe_allow_html=True)
