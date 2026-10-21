import streamlit as st
import pandas as pd
import yfinance as yf
import urllib.request
import xml.etree.ElementTree as ET
import urllib.parse
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

# --- ESTILOS CSS PROFESIONALES ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .quant-card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 20px; }
    .disclaimer-box { background-color: #21262d; padding: 15px; border-radius: 6px; border-left: 4px solid #f85149; font-size: 13px; color: #8b949e; }
    .news-box { background-color: #161b22; padding: 12px; border-radius: 6px; border-left: 3px solid #58a6ff; margin-bottom: 10px; font-size: 14px; }
    
    .black-swan-card {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        border: 1px solid #da3633;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
    }
    
    .cal-card {
        background-color: #161b22;
        padding: 14px 18px;
        border-radius: 8px;
        border-left: 4px solid #30363d;
        border-top: 1px solid #21262d;
        border-right: 1px solid #21262d;
        border-bottom: 1px solid #21262d;
        margin-bottom: 12px;
    }
    .cal-card-high { border-left-color: #f85149 !important; }
    .cal-card-med { border-left-color: #d29922 !important; }
    .cal-card-low { border-left-color: #2ea043 !important; }
    
    .cal-header { display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #8b949e; margin-bottom: 6px; }
    .cal-title { font-size: 15px; font-weight: bold; color: #f0f6fc; margin-bottom: 8px; }
    .cal-metrics { display: flex; gap: 20px; font-size: 13px; color: #c9d1d9; }
    .cal-badge {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    .badge-high { background-color: rgba(248, 81, 73, 0.2); color: #f85149; }
    .badge-med { background-color: rgba(210, 153, 34, 0.2); color: #d29922; }
    .badge-low { background-color: rgba(46, 160, 67, 0.2); color: #3fb950; }

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
    
    with st.sidebar:
        render_adsense(ADSENSE_CLIENT_ID, ADSENSE_SLOT_ID, height=150)

# --- CARTERA COMPLETA RESTAURADA DE ACTIVOS GLOBALES ---
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

    # Commodities Energéticos, Metales y Agrícolas (¡Gas Natural Incluido!)
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

# --- NAVEGACIÓN PRINCIPAL POR PESTAÑAS (TABS) ---
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

    # MÓDULO 2: DATOS ECONÓMICOS RELEVANTES DE LA SEMANA
    st.header("2. 📊 Datos Económicos Relevantes de la Semana")

    hoy = datetime.now()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=4)

    str_inicio_sem = inicio_semana.strftime("%d/%m/%Y")
    str_fin_sem = fin_semana.strftime("%d/%m/%Y")

    st.caption(f"🗓️ **Semana en Curso:** {str_inicio_sem} al {str_fin_sem} | Cobertura Macroeconómica Global")

    ZONAS_HORARIAS = {
        "GMT / UTC (Tiempo Universal)": 0,
        "Nueva York / Wall St (EDT)": -4,
        "Londres (BST)": 1,
        "Madrid / Europa Central (CEST)": 2,
        "Chile / Santiago (CLT)": -3,
        "Buenos Aires (ART)": -3,
        "Ciudad de México (CST)": -6
    }

    def ajustar_hora(hora_gmt_str, offset_horas):
        try:
            partes = hora_gmt_str.replace(" GMT", "").split(":")
            hh = int(partes[0])
            mm = int(partes[1])
            nueva_hh = (hh + offset_horas) % 24
            return f"{nueva_hh:02d}:{mm:02d}"
        except Exception:
            return hora_gmt_
