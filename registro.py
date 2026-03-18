import streamlit as st
from datetime import datetime
import requests
import json
import os

st.set_page_config(layout="wide", page_title="Registro Finanze", page_icon="💰")

# -------------------------------
# FILE DI SALVATAGGIO
# -------------------------------
FILE_DATI = "finanze.json"

# -------------------------------
# FUNZIONI DI SALVATAGGIO
# -------------------------------
def carica_dati():
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r") as f:
            return json.load(f)
    # Se non esiste, inizializza i dati
    return {"cassa": 0, "fondo_cassa": 0, "soldi_sporchi": 0, "movimenti": []}

def salva_dati(dati):
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f, indent=4)

# -------------------------------
# STATO IN STREAMLIT
# -------------------------------
if "dati" not in st.session_state:
    st.session_state.dati = carica_dati()

# -------------------------------
# FUNZIONI UTILI
# -------------------------------
def formatta(num):
    return f"{round(num):,}".replace(",", ".")

def invia_discord(msg):
    WEBHOOK_URL = st.secrets.get("WEBHOOK_URL")
    if not WEBHOOK_URL:
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": msg})
    except:
        pass

def registra_movimento(tipo, causale, valore):
    movimento = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "tipo": tipo,
        "causale": causale,
        "valore": valore
    }
    st.session_state.dati["movimenti"].append(movimento)
    salva_dati(st.session_state.dati)
    return movimento

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<h1 style='text-align:center;color:white;'>💰 Registro Finanze</h1>", unsafe_allow_html=True)
st.divider()

# ===============================
# DASHBOARD
# ===============================
col1, col2, col3 = st.columns([1,1,1], gap="large")

with col1:
    st.markdown(
        f"<div style='background-color:#1E1E1E;padding:20px;border-radius:10px;text-align:center;'><h3>💰 CASSA</h3><h2>{formatta(st.session_state.dati['cassa'])} $</h2></div>", unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"<div style='background-color:#1E1E1E;padding:20px;border-radius:10px;text-align:center;'><h3>💸 SOLDI SPORCHI</h3><h2>{formatta(st.session_state.dati['soldi_sporchi'])} $</h2></div>", unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"<div style='background-color:#1E1E1E;padding:20px;border-radius:10px;text-align:center;'><h3>💼 FONDO CASSA</h3><h2>{formatta(st.session_state.dati['fondo_cassa'])} $</h2></div>", unsafe_allow_html=True
    )

st.divider()

# ===============================
# FUNZIONE REGISTRA SEZIONE
# ===============================
def registra_sezione(titolo, key_input, tipo):
    st.subheader(titolo)
    causale = st.text_input(f"Causale {titolo}", key=f"{key_input}_causale")
    valore = st.number_input("Importo (+ / -)", value=0.0, key=f"{key_input}_valore")
    if st.button(f"Registra {titolo}", key=f"btn_{key_input}"):
        if causale.strip():
            st.session_state.dati[tipo] += valore
            movimento = registra_movimento(tipo, causale, valore)

            msg = f"""🧾 {titolo}
🕒 {movimento['data']}
📝 {movimento['causale']}
💰 Importo: {formatta(valore)} $
📊 Totale {titolo}: {formatta(st.session_state.dati[tipo])} $
"""
            invia_discord(msg)
            st.success(f"{titolo} registrato!")
            salva_dati(st.session_state.dati)

st.divider()
registra_sezione("Cassa", "cassa", "cassa")
registra_sezione("Soldi Sporchi", "sporchi", "soldi_sporchi")
registra_sezione("Fondo Cassa", "fondo", "fondo_cassa")
st.divider()

# ===============================
# REGISTRO MOVIMENTI
# ===============================
st.subheader("📋 Registro Movimenti")
movimenti = st.session_state.dati["movimenti"]
if movimenti:
    for mov in reversed(movimenti):
        st.markdown(
            f"<div style='background-color:#2C2C2C;padding:15px;border-radius:10px;margin-bottom:10px;'>"
            f"<b>🕒 {mov['data']}</b><br>"
            f"📂 <b>{mov['tipo']}</b><br>"
            f"📝 {mov['causale']}<br>"
            f"💰 Importo: {formatta(mov['valore'])} $"
            f"</div>", unsafe_allow_html=True
        )
else:
    st.info("Nessun movimento registrato")
# -------------------------------
# PULSANTE RESET REGISTRO
# -------------------------------
# st.divider()
# st.subheader("⚠️ Gestione Registro")
# if st.button("Svuota Registro"):
    # Azzera i dati
#    st.session_state.dati = {"cassa": 0, "fondo_cassa": 0, "soldi_sporchi": 0, "movimenti": []}
#    salva_dati(st.session_state.dati)
#    st.success("Registro e totali resettati!")
