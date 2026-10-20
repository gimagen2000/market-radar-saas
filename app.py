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
    Esta herramienta <b>no constituye asesoramiento financiero, gestión de capital ni recomend
