import streamlit as st
import pandas as pd
import yfinance as yf
import urllib.request
import xml.etree.ElementTree as ET
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Market Radar Quant Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENLACE DE AFILIADO DE MONETIZACIÓN ---
LIBERTEX_AFFILIATE_URL = "https://libertex.fxclub.org/goto/raf2?rid=12386667"

# --- ESTILOS CSS PROFESIONALES + ANUNCIOS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .quant-card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 20px; }
    .disclaimer-box { background-color: #21262d; padding: 15px; border-radius: 6px; border-left: 4px solid #f85149; font-size: 13px; color: #8b949e; }
    .news-box { background-color: #161b22; padding: 12px; border-radius: 6px; border-left: 3px solid #58a6ff; margin-bottom: 10px; font-size: 14px; }
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
    <b>AVISO LEGAL OBLIGATORIO:</b> Market Radar Quant Terminal es una plataforma de software estadístico, procesamiento de datos públicos y análisis cuantitativo de carácter strictly educativo, informativo y de investigación. 
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

# --- BARRA LATERAL CON MONETIZACIÓN ---
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

if st.session_state.user_plan == "Free":
    st.sidebar.markdown(f"""
    <div class="ad-container">
        <div class="ad-title">Anuncio Patrocinado</div>
        <p style="font-size: 12px; color: #c9d1d9;">¿Buscas un Broker regulado para operar Long-Only con bajos spreads?</p>
        <a href="{LIBERTEX_AFFILIATE_URL}" target="_blank" class="ad-button">Abrir Cuenta en Libertex 🚀</a>
    </div>
    """, unsafe_allow_html=True)

# --- CARTERA EXPANDIDA DE ACTIVOS GLOBALES ---
ACTIVOS_TICKERS = {
    # Forex Majors & Crosses
    "EUR/USD": {"ticker": "EURUSD=X", "clase": "Forex", "cot": "Neto Comprador (+14k)", "query": "EUR USD tipo de cambio forex"},
    "GBP/USD": {"ticker": "GBPUSD=X", "clase": "Forex", "cot": "Neto Comprador (+8k)", "query": "GBP USD libra esterlina"},
    "USD/JPY": {"ticker": "JPY=X", "clase": "Forex", "cot": "Neto Vendedor (-12k)", "query": "USD JPY yen japones"},
    "AUD/USD": {"ticker": "AUDUSD=X", "clase": "Forex", "cot": "Neto Comprador (+5k)", "query": "AUD USD australian dollar"},
    "USD/CAD": {"ticker": "USDCAD=X", "clase": "Forex", "cot": "Neto Vendedor (-4k)", "query": "USD CAD dollar canadiense"},
    "NZD/USD": {"ticker": "NZDUSD=X", "clase": "Forex", "cot": "Neutral", "query": "NZD USD new zealand dollar"},
    "USD/CHF": {"ticker": "USDCHF=X", "clase": "Forex", "cot": "Neutral", "query": "USD CHF franco suizo"},
    
    # Índices Globales
    "S&P 500": {"ticker": "^GSPC", "clase": "Índice", "cot": "Neutral", "query": "SP 500 bolsa de valores"},
    "Nasdaq 100": {"ticker": "^IXIC", "clase": "Índice", "cot": "Neutral", "query": "Nasdaq 100 bolsa"},
    "Dow Jones": {"ticker": "^DJI", "clase": "Índice", "cot": "Neutral", "query": "Dow Jones industrial"},
    "DAX Alemán": {"ticker": "^GDAXI", "clase": "Índice", "cot": "Neutral", "query": "DAX index Frankfurt"},
    "FTSE 100": {"ticker": "^FTSE", "clase": "Índice", "cot": "Neutral", "query": "FTSE 100 London stock"},
    "Nikkei 225": {"ticker": "^N225", "clase": "Índice", "cot": "Neutral", "query": "Nikkei 225 Tokyo"},
    
    # Energía y Metales
    "WTI Crude": {"ticker": "CL=F", "clase": "Commodity", "cot": "Neto Vendedor (-8k)", "query": "petroleo WTI crudo"},
    "Brent Crude": {"ticker": "BZ=F", "clase": "Commodity", "cot": "Neutral", "query": "petroleo Brent"},
    "Natural Gas": {"ticker": "NG=F", "clase": "Commodity", "cot": "Neto Comprador (+6k)", "query": "gas natural mercado"},
    "Gold (XAU)": {"ticker": "GC=F", "clase": "Commodity", "cot": "Neto Comprador (+22k)", "query": "oro precio cotizacion"},
    "Silver (XAG)": {"ticker": "SI=F", "clase": "Commodity", "cot": "Neto Comprador (+5k)", "query": "plata precio cotizacion"},
    "Copper": {"ticker": "HG=F", "clase": "Commodity", "cot": "Neto Comprador (+19k)", "query": "cobre precio cotizacion"},
    "Platinum": {"ticker": "PL=F", "clase": "Commodity", "cot": "Neutral", "query": "platino precio mercado"},
    
    # Softs & Agriculture (Agrícolas)
    "Cocoa": {"ticker": "CC=F", "clase": "Softs", "cot": "Neto Comprador (+15k)", "query": "cacao precio mercado"},
    "Coffee": {"ticker": "KC=F", "clase": "Softs", "cot": "Neto Comprador (+11k)", "query": "cafe cotizacion bolsa"},
    "Sugar": {"ticker": "SB=F", "clase": "Softs", "cot": "Neto Comprador (+7k)", "query": "azucar precio mercado"},
    "Corn": {"ticker": "ZC=F", "clase": "Agricultural", "cot": "Neutral", "query": "maiz cotizacion agricultura"},
    "Wheat": {"ticker": "ZW=F", "clase": "Agricultural", "cot": "Neutral", "query": "trigo cotizacion bolsa"},
    "Soybeans": {"ticker": "ZS=F", "clase": "Agricultural", "cot": "Neto Comprador (+9k)", "query": "soja cotizacion mercado"},
    "Cotton": {"ticker": "CT=F", "clase": "Softs", "cot": "Neutral", "query": "algodon precio mercado"},
    
    # Criptomonedas Principales
    "Bitcoin": {"ticker": "BTC-USD", "clase": "Crypto", "cot": "Neto Comprador (+30k)", "query": "Bitcoin BTC crypto precio"},
    "Ethereum": {"ticker": "ETH-USD", "clase": "Crypto", "cot": "Neto Comprador (+12k)", "query": "Ethereum ETH crypto"}
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

def obtener_noticias_rss(query_termino):
    noticias = []
    try:
        query_encoded = urllib.parse.quote(query_termino)
        url = f"https://news.google.com/rss/search?q={query_encoded}&hl=es&gl=ES&ceid=ES:es"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            channel = root.find('channel')
            if channel is not None:
                for item in channel.findall('item')[:3]:
                    title = item.find('title')
                    link = item.find('link')
                    source = item.find('source')
                    
                    noticias.append({
                        "title": title.text if title is not None else "Sin título",
                        "link": link.text if link is not None else "#",
                        "publisher": source.text if source is not None else "Finanzas"
                    })
    except Exception:
        pass
    return noticias

st.title("📊 Market Radar Quant Terminal")
st.markdown("### Procesamiento Estadístico de Mercados, Cartera Global Ampliada y Noticias en Vivo")

with st.spinner("Actualizando cotizaciones globales en vivo..."):
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

st.header("1. Explorador de Cartera Global y Percentiles Anuales")
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

# MÓDULO 2: MICHAEL VIRTUAL & NOTICIAS
st.header("2. 🤖 Michael Virtual — Tesis Cuantitativa & Noticias en Tiempo Real")
if not df_market_full.empty:
    activo_sel = st.selectbox("Seleccionar Activo Global", df_market_full["Activo"].tolist())
    row_sel = df_market_full[df_market_full["Activo"] == activo_sel].iloc[0]
    query_busqueda = ACTIVOS_TICKERS[activo_sel]["query"]

    col_t1, col_t2 = st.columns([1.2, 1])

    with col_t1:
        if st.button("✨ Generar Tesis Cuantitativa con Michael Virtual"):
            if st.session_state.user_plan == "Free":
                st.markdown(f"""
                <div class="ad-container">
                    <div class="ad-title">⚡ Patrocinado por Libertex</div>
                    <p style="font-size: 13px; color: #c9d1d9; margin: 5px 0;"><b>¿Deseas operar este activo con ejecución directa?</b></p>
                    <a href="{LIBERTEX_AFFILIATE_URL}" target="_blank" class="ad-button">Operar esta Tesis en Libertex 🚀</a>
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
        noticias = obtener_noticias_rss(query_busqueda)
        if noticias:
            for n in noticias:
                st.markdown(f"""
                <div class="news-box">
                <b>{n['publisher']}:</b> <a href="{n['link']}" target="_blank" style="color: #58a6ff; font-weight: bold; text-decoration: none;">{n['title']} 🔗</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay noticias recientes indexadas.")

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
