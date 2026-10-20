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

# --- ESTILOS CSS PROFESIONALES + TARJETAS MACRO ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .quant-card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 20px; }
    .disclaimer-box { background-color: #21262d; padding: 15px; border-radius: 6px; border-left: 4px solid #f85149; font-size: 13px; color: #8b949e; }
    .news-box { background-color: #161b22; padding: 12px; border-radius: 6px; border-left: 3px solid #58a6ff; margin-bottom: 10px; font-size: 14px; }
    
    /* TARJETAS PARA EL CALENDARIO ECONÓMICO */
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

# --- CARTERA EXPANDIDA DE ACTIVOS GLOBALES ---
ACTIVOS_TICKERS = {
    "EUR/USD": {"ticker": "EURUSD=X", "clase": "Forex", "cot": "Neto Comprador (+14k)", "query": "EUR USD tipo de cambio forex", "swap_long": -3.5, "swap_short": 1.2},
    "GBP/USD": {"ticker": "GBPUSD=X", "clase": "Forex", "cot": "Neto Comprador (+8k)", "query": "GBP USD libra esterlina", "swap_long": -2.8, "swap_short": 0.9},
    "USD/JPY": {"ticker": "JPY=X", "clase": "Forex", "cot": "Neto Vendedor (-12k)", "query": "USD JPY yen japones", "swap_long": 4.2, "swap_short": -6.5},
    "AUD/USD": {"ticker": "AUDUSD=X", "clase": "Forex", "cot": "Neto Comprador (+5k)", "query": "AUD USD australian dollar", "swap_long": -1.5, "swap_short": -0.4},
    "USD/CAD": {"ticker": "USDCAD=X", "clase": "Forex", "cot": "Neto Vendedor (-4k)", "query": "USD CAD dollar canadiense", "swap_long": 0.5, "swap_short": -2.1},
    "NZD/USD": {"ticker": "NZDUSD=X", "clase": "Forex", "cot": "Neutral", "query": "NZD USD new zealand dollar", "swap_long": -1.2, "swap_short": -0.8},
    "USD/CHF": {"ticker": "USDCHF=X", "clase": "Forex", "cot": "Neutral", "query": "USD CHF franco suizo", "swap_long": 2.1, "swap_short": -4.0},
    "S&P 500": {"ticker": "^GSPC", "clase": "Índice", "cot": "Neutral", "query": "SP 500 bolsa de valores", "swap_long": -1.2, "swap_short": -0.8},
    "Nasdaq 100": {"ticker": "^IXIC", "clase": "Índice", "cot": "Neutral", "query": "Nasdaq 100 bolsa", "swap_long": -1.5, "swap_short": -1.0},
    "Dow Jones": {"ticker": "^DJI", "clase": "Índice", "cot": "Neutral", "query": "Dow Jones industrial", "swap_long": -1.1, "swap_short": -0.7},
    "DAX Alemán": {"ticker": "^GDAXI", "clase": "Índice", "cot": "Neutral", "query": "DAX index Frankfurt", "swap_long": -1.3, "swap_short": -0.9},
    "FTSE 100": {"ticker": "^FTSE", "clase": "Índice", "cot": "Neutral", "query": "FTSE 100 London stock", "swap_long": -1.0, "swap_short": -0.6},
    "Nikkei 225": {"ticker": "^N225", "clase": "Índice", "cot": "Neutral", "query": "Nikkei 225 Tokyo", "swap_long": -0.8, "swap_short": -0.5},
    "WTI Crude": {"ticker": "CL=F", "clase": "Commodity", "cot": "Neto Vendedor (-8k)", "query": "petroleo WTI crudo", "swap_long": -2.0, "swap_short": 0.5},
    "Brent Crude": {"ticker": "BZ=F", "clase": "Commodity", "cot": "Neutral", "query": "petroleo Brent", "swap_long": -2.2, "swap_short": 0.4},
    "Natural Gas": {"ticker": "NG=F", "clase": "Commodity", "cot": "Neto Comprador (+6k)", "query": "gas natural mercado", "swap_long": -1.8, "swap_short": -0.2},
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

# MÓDULO 2: CALENDARIO ECONÓMICO GLOBAL CON ZONA HORARIA
st.header("2. 📅 Calendario Económico Global & Eventos Macro")

# Generador de Fechas Dinámicas
hoy = datetime.now()
fecha_hoy = hoy.strftime("%Y-%m-%d")
fecha_manana = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
fecha_pasado = (hoy + timedelta(days=2)).strftime("%Y-%m-%d")

# Mapeo y conversión de Horas por Zona Horaria (Offset relativo a GMT)
ZONAS_HORARIAS = {
    "GMT / UTC (Tiempo Universal)": 0,
    "Chile / Santiago (CLT)": -3,
    "Nueva York / Wall St (EDT)": -4,
    "Londres (BST)": 1,
    "Madrid / Europa Central (CEST)": 2,
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
        return hora_gmt_str

col_cal1, col_cal2 = st.columns([1, 2.2])

with col_cal1:
    zona_horaria_sel = st.selectbox("🌐 Zona Horaria", list(ZONAS_HORARIAS.keys()), index=1)
    offset_sel = ZONAS_HORARIAS[zona_horaria_sel]
    
    pais_sel = st.selectbox(
        "Filtrar por País / Región", 
        ["Todos los Países", "EE.UU. (USD)", "Eurozona (EUR)", "Reino Unido (GBP)", "Japón (JPY)", "China (CNY)", "Canadá (CAD)", "Australia (AUD)", "Suiza (CHF)", "Chile (CLP)", "Brasil (BRL)", "México (MXN)"]
    )
    impacto_sel = st.multiselect(
        "Filtrar por Relevancia", 
        ["🔴 Alto Impacto", "🟡 Impacto Medio", "🟢 Bajo Impacto"], 
        default=["🔴 Alto Impacto", "🟡 Impacto Medio"]
    )

# Lista Ampliada de Eventos Económicos Globales
eventos_globales = [
    {"Fecha": fecha_hoy, "Hora_GMT": "13:30", "País": "EE.UU. (USD)", "Bandera": "🇺🇸", "Evento": "Índice de Precios al Consumidor (IPC MoM)", "Impacto": "🔴 Alto Impacto", "Previo": "0.2%", "Previsión": "0.3%"},
    {"Fecha": fecha_hoy, "Hora_GMT": "15:00", "País": "EE.UU. (USD)", "Bandera": "🇺🇸", "Evento": "Ventas de Viviendas Existentes", "Impacto": "🟡 Impacto Medio", "Previo": "3.95M", "Previsión": "4.01M"},
    {"Fecha": fecha_hoy, "Hora_GMT": "09:00", "País": "Eurozona (EUR)", "Bandera": "🇪🇺", "Evento": "IPC Zona Euro (YoY Final)", "Impacto": "🔴 Alto Impacto", "Previo": "2.2%", "Previsión": "2.2%"},
    {"Fecha": fecha_hoy, "Hora_GMT": "21:00", "País": "Chile (CLP)", "Bandera": "🇨🇱", "Evento": "Decisión de Tasa de Interés del Banco Central (BCCh)", "Impacto": "🔴 Alto Impacto", "Previo": "5.75%", "Previsión": "5.50%"},
    {"Fecha": fecha_manana, "Hora_GMT": "06:00", "País": "Reino Unido (GBP)", "Bandera": "🇬🇧", "Evento": "Ventas al Por Menor (MoM)", "Impacto": "🟡 Impacto Medio", "Previo": "0.6%", "Previsión": "0.4%"},
    {"Fecha": fecha_manana, "Hora_GMT": "12:30", "País": "Canadá (CAD)", "Bandera": "🇨🇦", "Evento": "Ventas Minoristas Básicas (MoM)", "Impacto": "🟡 Impacto Medio", "Previo": "0.3%", "Previsión": "0.2%"},
    {"Fecha": fecha_manana, "Hora_GMT": "12:00", "País": "Brasil (BRL)", "Bandera": "🇧🇷", "Evento": "Índice de Precios al Consumidor IPCA-15", "Impacto": "🔴 Alto Impacto", "Previo": "0.19%", "Previsión": "0.25%"},
    {"Fecha": fecha_manana, "Hora_GMT": "23:30", "País": "Japón (JPY)", "Bandera": "🇯🇵", "Evento": "Tasa de Inflación Nacional (YoY)", "Impacto": "🔴 Alto Impacto", "Previo": "2.8%", "Previsión": "2.7%"},
    {"Fecha": fecha_pasado, "Hora_GMT": "01:30", "País": "China (CNY)", "Bandera": "🇨🇳", "Evento": "Tasa Preferencial de Préstamos del PBoC", "Impacto": "🔴 Alto Impacto", "Previo": "3.35%", "Previsión": "3.35%"},
    {"Fecha": fecha_pasado, "Hora_GMT": "01:30", "País": "Australia (AUD)", "Bandera": "🇦🇺", "Evento": "Cambio en el Empleo", "Impacto": "🔴 Alto Impacto", "Previo": "58.2K", "Previsión": "25.0K"},
    {"Fecha": fecha_pasado, "Hora_GMT": "07:30", "País": "Suiza (CHF)", "Bandera": "🇨🇭", "Evento": "Decisión de Tasa de Interés de la SNB", "Impacto": "🔴 Alto Impacto", "Previo": "1.25%", "Previsión": "1.00%"},
    {"Fecha": fecha_pasado, "Hora_GMT": "19:00", "País": "México (MXN)", "Bandera": "🇲🇽", "Evento": "Decisión de Política Monetaria Banxico", "Impacto": "🔴 Alto Impacto", "Previo": "10.75%", "Previsión": "10.50%"}
]

# Filtrado y conversión de hora
eventos_filtrados = [
    e for e in eventos_globales 
    if (pais_sel == "Todos los Países" or e["País"] == pais_sel)
    and (not impacto_sel or e["Impacto"] in impacto_sel)
]

with col_cal2:
    st.markdown(f"##### 📌 Publicaciones Macroeconómicas ({zona_horaria_sel})")
    if eventos_filtrados:
        for ev in eventos_filtrados:
            hora_ajustada = ajustar_hora(ev["Hora_GMT"], offset_sel)
            card_class = "cal-card-high" if "🔴" in ev["Impacto"] else ("cal-card-med" if "🟡" in ev["Impacto"] else "cal-card-low")
            badge_class = "badge-high" if "🔴" in ev["Impacto"] else ("badge-med" if "🟡" in ev["Impacto"] else "badge-low")
            
            st.markdown(f"""
            <div class="cal-card {card_class}">
                <div class="cal-header">
                    <span>🗓️ <b>{ev['Fecha']}</b> | ⏰ <b>{hora_ajustada} hrs</b></span>
                    <span class="cal-badge {badge_class}">{ev['Impacto']}</span>
                </div>
                <div class="cal-title">{ev['Bandera']} {ev['País']} — {ev['Evento']}</div>
                <div class="cal-metrics">
                    <span><b>Previo:</b> {ev['Previo']}</span>
                    <span><b>Previsión:</b> {ev['Previsión']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay eventos programados que coincidan con los filtros seleccionados.")

# MÓDULO 3: MICHAEL VIRTUAL & NOTICIAS
st.header("3. 🤖 Michael Virtual — Tesis Cuantitativa & Noticias en Tiempo Real")
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
                
                render_adsense(ADSENSE_CLIENT_ID, ADSENSE_SLOT_ID, height=120)

            st.markdown(f"""
            <div class="quant-card">
            <h4>📋 Informe Técnico: {row_sel['Activo']} ({row_sel['Clase']})</h4>
            <ul>
                <li><b>Cotización Actual:</b> {row_sel['Precio Actual']}</li>
                <li><b>Rango 52 Semanas:</b> Mín: {row_sel['Mín 52 Sem']} | Máx: {row_sel['Máx 52 Sem']}</li>
                <li><b>Percentil 1Y:</b> {row_sel['Percentil 1Y (%)']}%</li>
                <li><b>Flujo COT:</b> {row_sel['Flujo COT (Institucional)']}</li>
                <li><b>Swap Diario Long:</b> <span style="color: {'#3fb950' if row_sel['Swap Long ($/lote)'] > 0 else '#f85149'};">{row_sel['Swap Long ($/lote)']} USD/lote</span></li>
                <li><b>Swap Diario Short:</b> <span style="color: {'#3fb950' if row_sel['Swap Short ($/lote)'] > 0 else '#f85149'};">{row_sel['Swap Short ($/lote)']} USD/lote</span></li>
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

# MÓDULO 4: CALCULADORA DE RIESGO Y COSTOS SWAP OVERNIGHT
st.header("4. Calculadora de Exposición, Lotaje y Costos Swap (Overnight)")
c1, c2 = st.columns(2)
with c1:
    cap = st.number_input("Capital Asignado ($ USD)", value=10000.0, step=500.0)
    piso = st.slider("Distancia Estimada al Suelo Anual (%)", 1.0, 30.0, 10.0)
    pips_piso = st.number_input("Pips / Puntos al Piso Anual", value=250, step=10)
    dias_operados = st.number_input("Días Estimados de Posición (Overnight)", value=5, min_value=1, step=1)
    direccion_pos = st.radio("Dirección de la Operación", ["Comprado (Long)", "Vendido (Short)"])

with c2:
    apalanque = st.selectbox("Apalancamiento Operativo", [1, 2, 5, 10, 20], index=2)
    expo = cap * apalanque
    riesgo = cap * (piso / 100.0)
    lote = (riesgo / (pips_piso * 10)) if pips_piso > 0 else 0.01
    
    swap_rate_unit = row_sel['Swap Long ($/lote)'] if "Long" in direccion_pos else row_sel['Swap Short ($/lote)']
    costo_swap_total = lote * swap_rate_unit * dias_operados

st.markdown(f"""
<div class="quant-card">
    <h4>📊 Métricas de Control de Riesgo y Swap</h4>
    <p><b>Exposición Teórica:</b> ${expo:,.2f} USD</p>
    <p><b>Riesgo al Piso Anual ({piso}%):</b> ${riesgo:,.2f} USD</p>
    <p><b>Dimensionamiento Sugerido:</b> <code>{lote:.2f} Lotes</code></p>
    <p><b>Costo / Crédito Swap Estimado ({dias_operados} días para {activo_sel}):</b> 
       <code style="font-size: 16px; color: {'#3fb950' if costo_swap_total >= 0 else '#f85149'};">${costo_swap_total:,.2f} USD</code>
    </p>
    <p style="font-size: 11px; color: #8b949e;">⚠️ <i>Nota: Los días miércoles se aplica un Triple Swap (3 noches) por financiamiento del fin de semana.</i></p>
</div>
""", unsafe_allow_html=True)

# MÓDULO 5: CANALES Y MEDIOS DE REFERENCIA
st.header("5. 📺 Canales y Fuentes de Referencia Macroeconómica")
st.markdown("""
<div class="disclaimer-box" style="margin-bottom: 15px;">
<b>Nota legal sobre enlaces externos:</b> Los enlaces a medios de comunicación y plataformas asociadas se proporcionan exclusivamente con fines informativos y de contexto educativo. Market Radar Quant Terminal no mantiene afiliación directa ni se hace responsable por los análisis emitidos por terceros.
</div>
""", unsafe_allow_html=True)

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
