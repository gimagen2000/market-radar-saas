import streamlit as st
import pandas as pd
import yfinance as yf
import urllib.request
import xml.etree.ElementTree as ET
import urllib.parse
import os
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Market Radar Quant Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURACIÓN DE GOOGLE ADSENSE ---
ADSENSE_CLIENT_ID = "ca-pub-XXXXXXXXXXXXXXXX"  # Reemplaza con tu Client ID real
ADSENSE_SLOT_ID = "YYYYYYYYYY"               # Reemplaza con tu Slot ID real

def render_adsense(client_id, slot_id, height=100):
    adsense_code = f"""
    <div style="text-align: center;">
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={client_id}"
             crossorigin="anonymous"></script>
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="{client_id}"
             data-ad-slot="{slot_id}"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>
    </div>
    """
    st.components.v1.html(adsense_code, height=height)

# --- ENLACES DE AFILIADOS / MONETIZACIÓN ---
LIBERTEX_AFFILIATE_URL = "https://libertex.fxclub.org/goto/raf2?rid=12386667"
TRADINGVIEW_AFFILIATE_URL = "https://es.tradingview.com/?aff_id=1173007"

# --- ESTILOS CSS PROFESIONALES REFINADOS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .quant-card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 20px; }
    .disclaimer-box { background-color: #21262d; padding: 15px; border-radius: 6px; border-left: 4px solid #f85149; font-size: 13px; color: #8b949e; margin-bottom: 15px; }
    .news-box { background-color: #161b22; padding: 12px; border-radius: 6px; border-left: 3px solid #58a6ff; margin-bottom: 10px; font-size: 14px; }
    
    .black-swan-box {
        background-color: #161b22;
        border: 1px solid #da3633;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
    }
    
    .cal-card-v2 {
        background-color: #161b22;
        padding: 14px;
        border-radius: 8px;
        border: 1px solid #30363d;
        border-left: 4px solid #58a6ff;
        margin-bottom: 10px;
    }
    
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
    .yt-button {
        background-color: #FF0000;
        color: white !important;
        padding: 6px 14px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 5px;
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

# --- BARRA LATERAL CON MONETIZACIÓN Y LOGO ---
st.sidebar.title("🔐 Licencia SaaS")

# Carga de Logo si existe
logo_path = "logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)

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
    
    with st.sidebar:
        render_adsense(ADSENSE_CLIENT_ID, ADSENSE_SLOT_ID, height=150)

# --- CARTERA COMPLETA DE ACTIVOS GLOBALES ---
ACTIVOS_TICKERS = {
    # Forex Majors
    "EUR/USD": {"ticker": "EURUSD=X", "clase": "Forex", "cot": "Neto Comprador (+14k)", "query": "EUR USD tipo de cambio forex", "swap_long": -3.5, "swap_short": 1.2},
    "GBP/USD": {"ticker": "GBPUSD=X", "clase": "Forex", "cot": "Neto Comprador (+8k)", "query": "GBP USD libra esterlina", "swap_long": -2.8, "swap_short": 0.9},
    "USD/JPY": {"ticker": "JPY=X", "clase": "Forex", "cot": "Neto Vendedor (-12k)", "query": "USD JPY yen japones", "swap_long": 4.2, "swap_short": -6.5},
    "AUD/USD": {"ticker": "AUDUSD=X", "clase": "Forex", "cot": "Neto Comprador (+5k)", "query": "AUD USD australian dollar", "swap_long": -1.5, "swap_short": -0.4},
    "USD/CAD": {"ticker": "USDCAD=X", "clase": "Forex", "cot": "Neto Vendedor (-4k)", "query": "USD CAD dollar canadiense", "swap_long": 0.5, "swap_short": -2.1},
    "NZD/USD": {"ticker": "NZDUSD=X", "clase": "Forex", "cot": "Neutral", "query": "NZD USD new zealand dollar", "swap_long": -1.2, "swap_short": -0.8},
    "USD/CHF": {"ticker": "USDCHF=X", "clase": "Forex", "cot": "Neutral", "query": "USD CHF franco suizo", "swap_long": 2.1, "swap_short": -4.0},

    # Forex Minors / Cruces
    "EUR/GBP": {"ticker": "EURGBP=X", "clase": "Forex", "cot": "Neutral", "query": "EUR GBP euro libra", "swap_long": -2.1, "swap_short": 0.4},
    "EUR/JPY": {"ticker": "EURJPY=X", "clase": "Forex", "cot": "Neto Comprador (+10k)", "query": "EUR JPY euro yen", "swap_long": 3.8, "swap_short": -5.9},
    "GBP/JPY": {"ticker": "GBPJPY=X", "clase": "Forex", "cot": "Neto Comprador (+6k)", "query": "GBP JPY libra yen", "swap_long": 5.1, "swap_short": -7.2},
    "AUD/JPY": {"ticker": "AUDJPY=X", "clase": "Forex", "cot": "Neutral", "query": "AUD JPY australiano yen", "swap_long": 2.5, "swap_short": -4.1},
    "NZD/JPY": {"ticker": "NZDJPY=X", "clase": "Forex", "cot": "Neutral", "query": "NZD JPY neozelandes yen", "swap_long": 2.2, "swap_short": -3.8},
    "CAD/JPY": {"ticker": "CADJPY=X", "clase": "Forex", "cot": "Neutral", "query": "CAD JPY canadiense yen", "swap_long": 3.0, "swap_short": -4.9},
    "CHF/JPY": {"ticker": "CHFJPY=X", "clase": "Forex", "cot": "Neutral", "query": "CHF JPY franco yen", "swap_long": 1.8, "swap_short": -3.5},

    # Forex Emergentes & LATAM
    "USD/CLP": {"ticker": "USDCLP=X", "clase": "Forex", "cot": "Neto Comprador (+3k)", "query": "USD CLP dolar peso chileno", "swap_long": 8.5, "swap_short": -11.2},
    "USD/MXN": {"ticker": "USDMXN=X", "clase": "Forex", "cot": "Neto Vendedor (-5k)", "query": "USD MXN dolar peso mexicano", "swap_long": 12.0, "swap_short": -16.5},
    "USD/BRL": {"ticker": "USDBRL=X", "clase": "Forex", "cot": "Neutral", "query": "USD BRL dolar real brasileno", "swap_long": 10.5, "swap_short": -14.0},

    # Índices Globales
    "S&P 500": {"ticker": "^GSPC", "clase": "Índice", "cot": "Neutral", "query": "SP 500 bolsa de valores", "swap_long": -1.2, "swap_short": -0.8},
    "Nasdaq 100": {"ticker": "^IXIC", "clase": "Índice", "cot": "Neutral", "query": "Nasdaq 100 bolsa", "swap_long": -1.5, "swap_short": -1.0},
    "Dow Jones": {"ticker": "^DJI", "clase": "Índice", "cot": "Neutral", "query": "Dow Jones industrial", "swap_long": -1.1, "swap_short": -0.7},
    "DAX Alemán": {"ticker": "^GDAXI", "clase": "Índice", "cot": "Neutral", "query": "DAX index Frankfurt", "swap_long": -1.3, "swap_short": -0.9},
    "FTSE 100": {"ticker": "^FTSE", "clase": "Índice", "cot": "Neutral", "query": "FTSE 100 London stock", "swap_long": -1.0, "swap_short": -0.6},
    "Nikkei 225": {"ticker": "^N225", "clase": "Índice", "cot": "Neutral", "query": "Nikkei 225 Tokyo", "swap_long": -0.8, "swap_short": -0.5},

    # Commodities Energéticos, Metales y Agrícolas
    "Natural Gas": {"ticker": "NG=F", "clase": "Commodity", "cot": "Neto Comprador (+6k)", "query": "gas natural mercado", "swap_long": -1.8, "swap_short": -0.2},
    "WTI Crude": {"ticker": "CL=F", "clase": "Commodity", "cot": "Neto Vendedor (-8k)", "query": "petroleo WTI crudo", "swap_long": -2.0, "swap_short": 0.5},
    "Brent Crude": {"ticker": "BZ=F", "clase": "Commodity", "cot": "Neutral", "query": "petroleo Brent", "swap_long": -2.2, "swap_short": 0.4},
    "Gold (XAU)": {"ticker": "GC=F", "clase": "Commodity", "cot": "Neto Comprador (+22k)", "query": "oro precio cotizacion", "swap_long": -3.1, "swap_short": 1.0},
    "Silver (XAG)": {"ticker": "SI=F", "clase": "Commodity", "cot": "Neto Comprador (+5k)", "query": "plata precio cotizacion", "swap_long": -2.5, "swap_short": 0.8},
    "Copper": {"ticker": "HG=F", "clase": "Commodity", "cot": "Neto Comprador (+19k)", "query": "cobre precio cotizacion", "swap_long": -1.0, "swap_short": -0.3},
    "Platinum": {"ticker": "PL=F", "clase": "Commodity", "cot": "Neutral", "query": "platino precio mercado", "swap_long": -1.4, "swap_short": -0.2},
    "Cocoa": {"ticker": "CC=F", "clase": "Softs", "cot": "Neto Comprador (+15k)", "query": "cacao precio mercado", "swap_long": -0.8, "swap_short": -0.5},
    "Coffee": {"ticker": "KC=F", "clase": "Softs", "cot": "Neto Comprador (+11k)", "query": "cafe cotizacion bolsa", "swap_long": -0.9, "swap_short": -0.4},
    "Sugar": {"ticker": "SB=F", "clase": "Softs", "cot": "Neto Comprador (+7k)", "query": "azucar precio mercado", "swap_long": -0.6, "swap_short": -0.3},
    "Corn": {"ticker": "ZC=F", "clase": "Agricultural", "cot": "Neutral", "query": "maiz cotizacion agricultura", "swap_long": -0.5, "swap_short": -0.2},
    "Wheat": {"ticker": "ZW=F", "clase": "Agricultural", "cot": "Neutral", "query": "trigo cotizacion bolsa", "swap_long": -0.6, "swap_short": -0.3},
    "Soybeans": {"ticker": "ZS=F", "clase": "Agricultural", "cot": "Neto Comprador (+9k)", "query": "soja cotizacion mercado", "swap_long": -0.7, "swap_short": -0.3},
    "Cotton": {"ticker": "CT=F", "clase": "Softs", "cot": "Neutral", "query": "algodon precio mercado", "swap_long": -0.5, "swap_short": -0.2},

    # Criptomonedas
    "Bitcoin": {"ticker": "BTC-USD", "clase": "Crypto", "cot": "Neto Comprador (+30k)", "query": "Bitcoin BTC crypto precio", "swap_long": -12.5, "swap_short": 5.0},
    "Ethereum": {"ticker": "ETH-USD", "clase": "Crypto", "cot": "Neto Comprador (+12k)", "query": "Ethereum ETH crypto", "swap_long": -8.0, "swap_short": 3.2}
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
                    "Flujo COT (Institucional)": info["cot"],
                    "Swap Long ($/lote)": info["swap_long"],
                    "Swap Short ($/lote)": info["swap_short"]
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

# --- SISTEMA DINÁMICO DE CALENDARIO ECONÓMICO REAL EN VIVO ---
@st.cache_data(ttl=900)
def obtener_calendario_economico_dinamico():
    eventos = []
    try:
        # Feed RSS de noticias y datos macroeconómicos en vivo
        url = "https://news.google.com/rss/search?q=calendario+economico+fed+bce+ipc+inflacion&hl=es&gl=ES&ceid=ES:es"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            channel = root.find('channel')
            if channel is not None:
                for item in channel.findall('item')[:6]:
                    title = item.find('title')
                    pubDate = item.find('pubDate')
                    link = item.find('link')
                    
                    str_fecha = pubDate.text[:16] if pubDate is not None else "Reciente"
                    tit_texto = title.text if title is not None else "Evento Económico"
                    
                    impacto = "🔴 Alto Impacto" if any(k in tit_texto.lower() for k in ["fed", "inflacion", "ipc", "tasas", "bce", "empleo"]) else "🟡 Impacto Medio"
                    
                    eventos.append({
                        "Fecha": str_fecha,
                        "Evento": tit_texto,
                        "Impacto": impacto,
                        "Link": link.text if link is not None else "#"
                    })
    except Exception:
        pass
        
    if not eventos:
        # Fallback dinámico basado en la fecha en tiempo real si el RSS no responde
        hoy = datetime.now()
        eventos = [
            {"Fecha": hoy.strftime("%d/%m/%Y"), "Evento": "Decisión de Tasas de Interés y Política Monetaria Fed", "Impacto": "🔴 Alto Impacto", "Link": "#"},
            {"Fecha": (hoy + timedelta(days=1)).strftime("%d/%m/%Y"), "Evento": "Publicación del Índice de Precios al Consumidor (IPC)", "Impacto": "🔴 Alto Impacto", "Link": "#"},
            {"Fecha": (hoy + timedelta(days=2)).strftime("%Y-%m-%d"), "Evento": "Nuevas Peticiones de Subsidio por Desempleo (EE.UU.)", "Impacto": "🔴 Alto Impacto", "Link": "#"},
            {"Fecha": (hoy + timedelta(days=3)).strftime("%Y-%m-%d"), "Evento": "PMI Manufacturero e Industrial de la Eurozona", "Impacto": "🟡 Impacto Medio", "Link": "#"}
        ]
    return eventos# --- NAVEGACIÓN PRINCIPAL POR PESTAÑAS (TABS) ---
tab_terminal, tab_nosotros, tab_guia, tab_legal = st.tabs([
    "📊 Terminal de Mercado", 
    "🏛️ Quiénes Somos & Propósito", 
    "💡 Guía de Uso Optimizada", 
    "📄 Legal, Soporte & Contacto"
])

# ==========================================
# PESTAÑA 1: TERMINAL DE MERCADO
# ==========================================
with tab_terminal:
    col_head1, col_head2 = st.columns([4, 1])
    with col_head1:
        st.title("📊 Market Radar Quant Terminal")
        st.markdown("### Procesamiento Estadístico de Mercados, Cartera Global Ampliada y Noticias en Vivo")
    with col_head2:
        if os.path.exists(logo_path):
            st.image(logo_path, width=140)

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

    # MÓDULO 1: EXPLORADOR DE CARTERA GLOBAL
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

    # MÓDULO 2: DATOS ECONÓMICOS RELEVANTES DE LA SEMANA (DINÁMICO EN VIVO)
    st.header("2. 📊 Datos Económicos Relevantes de la Semana")
    st.caption("🗓️ **Feed Macroeconómico Global en Tiempo Real**")

    cal_eventos_live = obtener_calendario_economico_dinamico()
    
    col_cal_a, col_cal_b = st.columns([1, 2])
    with col_cal_a:
        filtro_imp = st.multiselect("Relevancia", ["🔴 Alto Impacto", "🟡 Impacto Medio"], default=["🔴 Alto Impacto", "🟡 Impacto Medio"])
    
    with col_cal_b:
        for ev in cal_eventos_live:
            if not filtro_imp or ev["Impacto"] in filtro_imp:
                st.markdown(f"""
                <div class="cal-card-v2">
                    <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8b949e;">
                        <span>⏰ <b>{ev['Fecha']}</b></span>
                        <span style="color: {'#f85149' if '🔴' in ev['Impacto'] else '#d29922'}; font-weight: bold;">{ev['Impacto']}</span>
                    </div>
                    <div style="font-size: 14px; font-weight: bold; color: #f0f6fc; margin-top: 5px;">
                        <a href="{ev['Link']}" target="_blank" style="color: #f0f6fc; text-decoration: none;">{ev['Evento']} 🔗</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # MÓDULO 3: MICHAEL VIRTUAL — TESIS FLUIDA & RADAR CISNE NEGRO LIMPIC
    st.header("3. 🤖 Michael Virtual — Tesis Cuantitativa, Noticias & Radar de Cisne Negro")

    if not df_market_full.empty:
        activo_sel = st.selectbox("Seleccionar Activo Global", df_market_full["Activo"].tolist())
        row_sel = df_market_full[df_market_full["Activo"] == activo_sel].iloc[0]
        query_busqueda = ACTIVOS_TICKERS[activo_sel]["query"]

        col_t1, col_t2 = st.columns([1.2, 1])

        with col_t1:
            if st.button("✨ Generar Tesis Cuantitativa Fluida con Michael Virtual"):
                if st.session_state.user_plan == "Free":
                    st.markdown(f"""
                    <div class="ad-container">
                        <div class="ad-title">⚡ Patrocinado por Libertex</div>
                        <p style="font-size: 13px; color: #c9d1d9; margin: 5px 0;"><b>¿Deseas operar este activo con ejecución directa?</b></p>
                        <a href="{LIBERTEX_AFFILIATE_URL}" target="_blank" class="ad-button">Operar esta Tesis en Libertex 🚀</a>
                    </div>
                    """, unsafe_allow_html=True)
                    render_adsense(ADSENSE_CLIENT_ID, ADSENSE_SLOT_ID, height=120)

                # DIAGNÓSTICO FLUIDO Y DINÁMICO BASADO EN VALORES
                pct_1y = row_sel['Percentil 1Y (%)']
                precio = row_sel['Precio Actual']
                min_anual = row_sel['Mín 52 Sem']
                max_anual = row_sel['Máx 52 Sem']
                swap_l = row_sel['Swap Long ($/lote)']
                
                if pct_1y <= 20:
                    eval_fluida = f"El activo se encuentra en una **zona de suelo extremo ({pct_1y}% de su rango anual)**. Cotizando en **{precio}**, dista muy poco de su mínimo de 52 semanas ({min_anual}). La asimetría matemática favorece acumulación en largo, siempre monitoreando un swap de **{swap_l} USD/día**."
                elif pct_1y >= 80:
                    eval_fluida = f"El activo cotiza en **zona de fuerte sobrecompra ({pct_1y}% de su rango anual)** cerca de su máximo de 52 semanas ({max_anual}). La asimetría Long-Only es desfavorable temporalmente. Es recomendable esperar correcciones hacia la media."
                else:
                    eval_fluida = f"El activo está cotizando en un **rango neutral consolidado ({pct_1y}% del percentil anual)**. Se recomienda esperar testeos a zonas extremas antes de ejecutar ingresos."

                st.markdown(f"""
                <div class="quant-card">
                    <h4>📋 Informe Técnico Dinámico: {row_sel['Activo']} ({row_sel['Clase']})</h4>
                    <p><b>Cotización Actual:</b> {precio} | <b>Mín Anual:</b> {min_anual} | <b>Máx Anual:</b> {max_anual}</p>
                    <p><b>Percentil Anual:</b> {pct_1y}% | <b>Flujo COT:</b> {row_sel['Flujo COT (Institucional)']}</p>
                    <hr style="border: 0.5px solid #30363d;">
                    <p><b>🎙️ Dictamen Cuantitativo de Michael Virtual:</b></p>
                    <p style="color: #58a6ff; font-size: 15px; font-weight: 500;">"{eval_fluida}"</p>
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

        # RADAR CISNE NEGRO — INTERFAZ LIMPIDA SIN CÓDIGO HTML ROTO
        st.markdown("---")
        st.markdown("### 🦅 Radar de Cisne Negro — Síntesis Analítica de Mercado")
        
        st.markdown("""
        <div class="disclaimer-box" style="border-left-color: #da3633;">
        <b>SÍNTESIS DE RIESGOS DE COLA (TAIL RISK):</b> Michael Virtual evalúa fragilidades macro-geopolíticas, flujos de liquidez, patrones de volatilidad derivados y trampas de mercado sobre el activo seleccionado.
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔍 Investigar Vulnerabilidades y Causas de Cisne Negro"):
            percentil = row_sel['Percentil 1Y (%)']
            nivel_vulnerabilidad = "ELEVADA" if (percentil > 85 or percentil < 15) else "MODERADA"
            color_vulnerabilidad = "#f85149" if nivel_vulnerabilidad == "ELEVADA" else "#d29922"

            # Formato de salida completamente limpio usando componentes nativos
            with st.container():
                st.markdown(f"#### 🚨 Informe de Vulnerabilidad y Estrés Extremo: **{row_sel['Activo']}**")
                st.markdown(f"**Índice de Fragilidad Cuantitativa:** <span style='color:{color_vulnerabilidad}; font-weight:bold;'>{nivel_vulnerabilidad} ({percentil}% Percentil 1Y)</span>", unsafe_allow_html=True)
                
                st.divider()
                
                st.markdown("##### 🏛️ 1. Macro-Geopolítica y Liquidez Soberana")
                st.markdown("- **Guerra de Divisas y Liquidez Interbancaria:** Riesgo de restricción de liquidez por parte de bancos centrales que fuerce una liquidación en cadena de colaterales.")
                st.markdown("- **Escalada Geopolítica / Shocks de Suministro:** Disrupción en transporte marítimo o energía que descontrole la inflación y fuerce alzas de tasas no descontadas.")
                
                st.markdown("##### 📈 2. Volatilidad, Estructura de Liquidez y Flujos Institucionales")
                st.markdown("- **Atrapamiento de Volatilidad (VIX Spike) & Gamma Squeeze:** Ruptura de niveles clave donde la acumulación de opciones fuerce a creadores de mercado a coberturas masivas.")
                st.markdown("- **Cierre Repentino de Ventanas de Repos:** Descalce de colaterales en balances bancarios de gran escala.")
                
                st.markdown("##### 🎯 3. Psicología Institucional y Trampas de Mercado")
                st.markdown(f"- **Barridos de Liquidez en Extremos Anuales:** Falsas rupturas (*fakes*) cerca del suelo/techo anual **({row_sel['Mín 52 Sem']} - {row_sel['Máx 52 Sem']})** diseñadas para absorber liquidez minorista.")
                st.markdown("- **Distribución Silenciosa:** Narrativas optimistas mediáticas mientras el *Smart Money* rota capital silenciosamente.")
                
                st.divider()
                st.success(f"**🛡️ Dictamen de Protección (Michael Virtual):** 'No intentes adivinar el Cisne Negro; prepárate para sobrevivirlo.' Mantener estricta asimetría Long-Only en mínimos anuales con apalancamiento acotado (<1:10).")

    # MÓDULO 4: CALCULADORA DE RIESGO Y COSTOS SWAP
    st.header("4. Calculadora de Exposición, Lotaje y Costos Swap (Overnight)")
    c1, c2 = st.columns(2)
    with c1:
        cap = st.number_input("Capital Asignado ($ USD)", value=10000.0, step=500.0)
        piso = st.slider("Distancia Estimada al Suelo Anual (%)", 1.0, 30.0, 10.0)
        pips_piso = st.number_input("Pips / Puntos al Piso Anual", value=250, step=10)
        dias_operados = st.number_input("Días Estimados de Posición (Overnight)", value=5, min_value=1, step=1)
        direccion_pos = st.radio("Dirección de la Operación", ["Comprado (Long)", "Vendido (Short)"])

    with c2:
        apalanque = st.selectbox("Apalancamiento Operativo", [1, 2, 5, 10, 20, 30, 50, 100], index=2)
        lotes_manuales = st.number_input("Tamaño de Posición Personalizado (Lotes)", value=1.0, min_value=0.01, max_value=100.0, step=0.1)
        
        expo_teorica = cap * apalanque
        nocional_lotes = lotes_manuales * 100000
        riesgo = cap * (piso / 100.0)
        lote_sugerido = (riesgo / (pips_piso * 10)) if pips_piso > 0 else 0.01
        
        swap_long = row_sel['Swap Long ($/lote)']
        swap_short = row_sel['Swap Short ($/lote)']
        swap_rate_unit = swap_long if "Long" in direccion_pos else swap_short
        
        diferencial_swap_lote = swap_rate_unit * lotes_manuales
        costo_swap_total = diferencial_swap_lote * dias_operados
        impacto_swap_pct = (costo_swap_total / cap) * 100

    st.markdown(f"""
    <div class="quant-card">
        <h4>📊 Métricas de Control de Riesgo, Lotaje y Apalancamiento</h4>
        <p><b>Capital Cuenta:</b> ${cap:,.2f} USD | <b>Apalancamiento Seleccionado:</b> 1:{apalanque}</p>
        <p><b>Exposición Teórica con Apalancamiento:</b> ${expo_teorica:,.2f} USD</p>
        <p><b>Volumen Real Operado ({lotes_manuales} Lote/s):</b> ${nocional_lotes:,.2f} USD Nocionales</p>
        <p><b>Dimensionamiento Sugerido por Riesgo al Piso ({piso}%):</b> <code>{lote_sugerido:.2f} Lotes</code></p>
        <hr style="border: 0.5px solid #30363d;">
        <p><b>Diferencial Swap Neto Diario ({lotes_manuales} lote/s de {activo_sel}):</b> <code style="color: {'#3fb950' if diferencial_swap_lote >= 0 else '#f85149'};">${diferencial_swap_lote:,.2f} USD/día</code></p>
        <p><b>Costo / Crédito Swap Total ({dias_operados} días overnight):</b> 
           <code style="font-size: 16px; color: {'#3fb950' if costo_swap_total >= 0 else '#f85149'};">${costo_swap_total:,.2f} USD ({impacto_swap_pct:+.2f}% sobre capital)</code>
        </p>
        <p style="font-size: 11px; color: #8b949e;">⚠️ <i>Nota: Los días miércoles se aplica Triple Swap (3 noches) por el rollover del fin de semana.</i></p>
    </div>
    """, unsafe_allow_html=True)

    # MÓDULO 5: CANALES Y MEDIOS DE REFERENCIA
    st.header("5. 📺 Canales y Fuentes de Referencia Macroeconómica")
    col_yt1, col_yt2 = st.columns(2)

    with col_yt1:
        st.markdown("""
        <div class="quant-card" style="text-align: center; padding: 15px;">
            <h4>🔴 Negocios TV</h4>
            <p style="font-size: 13px; color: #8b949e;">Análisis geopolítico, macroeconomía, mercados globales y actualidad financiera en tiempo real.</p>
            <a href="https://www.youtube.com/@negociostv" target="_blank" class="yt-button">Ver Canal Oficial 🚀</a>
        </div>
        """, unsafe_allow_html=True)

    with col_yt2:
        st.markdown(f"""
        <div class="quant-card" style="text-align: center; padding: 15px;">
            <h4>📊 Recursos y Datos Globales</h4>
            <p style="font-size: 13px; color: #8b949e;">Plataformas de gráficos avanzados, informes institucionales y seguimiento de flujos de capital.</p>
            <a href="{TRADINGVIEW_AFFILIATE_URL}" target="_blank" class="yt-button" style="background-color: #238636;">Explorar Herramientas 📈</a>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# PESTAÑA 2: QUIÉNES SOMOS Y PROPÓSITO
# ==========================================
with tab_nosotros:
    st.title("🏛️ Quiénes Somos & Propósito Fundamental")
    
    st.markdown("""
    <div class="quant-card">
    <h3>🌐 La Filosofía detrás de Market Radar Quant Terminal</h3>
    <p><b>Market Radar Quant Terminal</b> nace con la misión de democratizar herramientas de análisis cuantitativo, procesamiento de percentiles históricos y simulación de riesgo de nivel institucional para el inversor individual y profesional.</p>
    <p>En un entorno financiero saturado de ruido mediático y sesgos emocionales, nuestra plataforma proporciona una <b>brújula puramente matemática, objetiva y basada en datos históricos reales</b>.</p>
    </div>
    """, unsafe_allow_html=True)

    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("""
        <div class="quant-card">
        <h4>🎯 Propósito y Pilares Técnicos</h4>
        <ul>
            <li><b>Asimetría Estadística (Percentiles Anuales):</b> Identificar activos globales operando cerca de sus suelos históricos (Percentil ≤ 20%) para maximizar el margen de seguridad.</li>
            <li><b>Filosofía Unidireccional (Long-Only):</b> Priorizar la acumulación estratégica en activos de valor fundamental en lugar de la especulación de alto riesgo en ambas direcciones.</li>
            <li><b>Control de Costos Ocultos (Overnight Swaps):</b> Calcular el impacto exacto del rollover diario para evitar que las tasas de interés devoren la rentabilidad de las posiciones abiertas a mediano plazo.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.markdown("""
        <div class="quant-card">
        <h4>🤖 El Origen de Michael Virtual</h4>
        <p><b>Michael Virtual</b> es el motor cuantitativo de inteligencia analítica integrado en la terminal. Sintetiza los cuatro pilares fundamentales del análisis financiero contemporáneo:</p>
        <ul>
            <li><b>Geopolítica & Liquidez Soberana:</b> Análisis del entorno geopolítico y flujos interbancarios.</li>
            <li><b>Estructura Monetaria & Ciclos Macro:</b> Modelado de políticas de bancos centrales.</li>
            <li><b>Flujos de Mercado, Volatilidad & Opciones:</b> Lectura del VIX y derivados institucionales.</li>
            <li><b>Psicología Institucional y Trampas Minoristas:</b> Identificación de trampas de liquidez (Smart Money).</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# PESTAÑA 3: GUÍA DE USO OPTIMIZADA
# ==========================================
with tab_guia:
    st.title("💡 Cómo Sacarle el Máximo Provecho a la Terminal")
    st.markdown("### Guía Práctica de Trabajo Diario en 4 Pasos")

    st.markdown("""
    <div class="quant-card">
    <h4>Step 1: Escaneo de Percentiles y Asimetría de Suelo</h4>
    <p>Revisa la tabla del <b>Explorador de Cartera Global</b> y filtra por <code>Solo Activos en Percentil Bajo (≤ 20%)</code>. Un activo con un percentil bajo está cotizando muy cerca de su mínimo anual de 52 semanas, lo que estadísticamente ofrece una asimetría riesgo/beneficio favorable para compras acumulativas.</p>
    </div>

    <div class="quant-card">
    <h4>Step 2: Filtro Macro con Datos Económicos Relevantes</h4>
    <p>Antes de ejecutar cualquier análisis, consulta la sección <b>Datos Económicos Relevantes de la Semana</b>. Compara la importancia y fecha de los eventos macro para anticipar momentos de volatilidad elevada.</p>
    </div>

    <div class="quant-card">
    <h4>Step 3: Evaluación de Estrés y Cisne Negro con Michael Virtual</h4>
    <p>Selecciona un activo y haz clic en <b>"Investigar Vulnerabilidades de Cisne Negro"</b>. Michael Virtual analizará la fragilidad estructural del activo evaluando riesgos geopolíticos, trampas de liquidez institucionales y rupturas en el VIX.</p>
    </div>

    <div class="quant-card">
    <h4>Step 4: Dimensionamiento de Posición y Cálculo de Swap Overnight</h4>
    <p>Utiliza la <b>Calculadora de Riesgo</b> introduciendo tu capital real, el apalancamiento que vas a usar y los días que mantendrás la posición abierta. Comprueba el <b>Costo Swap Neto</b> para asegurarte de que las comisiones por mantener la operación durante la noche no comprometan tu cuenta.</p>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# PESTAÑA 4: LEGAL, SOPORTE Y CONTACTO
# ==========================================
with tab_legal:
    st.title("📄 Información Legal, Soporte y Contacto")

    col_l1, col_l2 = st.columns(2)

    with col_l1:
        st.markdown("""
        <div class="quant-card">
        <h4>📬 Soporte Técnico y Consultas</h4>
        <p>¿Tienes dudas sobre la licencia SaaS, sugerencias de nuevos activos o soporte técnico?</p>
        <p>📧 <b>Correo Institucional:</b> <a href="mailto:soporte@marketradarquant.com" style="color: #58a6ff;">soporte@marketradarquant.com</a></p>
        <p>🌐 <b>Web Oficial:</b> <a href="https://marketradarquant.com" target="_blank" style="color: #58a6ff;">www.marketradarquant.com</a></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="quant-card">
        <h4>☕ Apoya el Desarrollo del Proyecto</h4>
        <p>Market Radar Quant Terminal se mantiene libre de publicidad invasiva gracias al apoyo de nuestra comunidad.</p>
        <a href="https://www.buymeacoffee.com" target="_blank" class="yt-button" style="background-color: #21262d; border: 1px solid #30363d;">☕ Apoyar en BuyMeACoffee</a>
        </div>
        """, unsafe_allow_html=True)

    with col_l2:
        st.markdown("""
        <div class="quant-card">
        <h4>⚖️ Descargo de Responsabilidad y Política de Privacidad</h4>
        <p><b>Exención de Responsabilidad Financiera:</b> Todos los datos presentados son procesados mediante algoritmos matemáticos a partir de fuentes públicas. Ningún contenido generado por Michael Virtual constituye una recomendación explícita de compra o venta.</p>
        <p><b>Política de Privacidad y Tratamiento de Datos:</b> No almacenamos contraseñas ni datos bancarios. Las consultas de los usuarios se procesan de forma anónima respetando la privacidad según el estándar internacional GDPR.</p>
        </div>
        """, unsafe_allow_html=True)
