import streamlit as st
from datetime import datetime
import requests

st.set_page_config(layout="wide", page_title="Registro Finanze", page_icon="💰")

# -------------------------------
# STATO
# -------------------------------
for key in ["cassa", "fondo_cassa", "soldi_sporchi", "movimenti"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key != "movimenti" else []

# -------------------------------
# FUNZIONI
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
    st.session_state.movimenti.append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "tipo": tipo,
        "causale": causale,
        "valore": valore
    })

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<h1 style='text-align:center;color:white;'>💰 Registro Finanze</h1>", unsafe_allow_html=True)
st.divider()

# ===============================
# 📊 DASHBOARD (IN ALTO)
# ===============================
col1, col2, col3 = st.columns([1,1,1], gap="large")

with col1:
    st.markdown(
        f"""
        <div style='background-color:#1E1E1E;padding:20px;border-radius:10px;text-align:center;'>
            <h3>💰 CASSA</h3>
            <h2>{formatta(st.session_state.cassa)} €</h2>
        </div>
        """, unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style='background-color:#1E1E1E;padding:20px;border-radius:10px;text-align:center;'>
            <h3>💸 SOLDI SPORCHI</h3>
            <h2>{formatta(st.session_state.soldi_sporchi)} €</h2>
        </div>
        """, unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style='background-color:#1E1E1E;padding:20px;border-radius:10px;text-align:center;'>
            <h3>💼 FONDO CASSA</h3>
            <h2>{formatta(st.session_state.fondo_cassa)} €</h2>
        </div>
        """, unsafe_allow_html=True
    )

st.divider()

# ===============================
# 🧾 MOVIMENTI (CASSA / SOLDI SPORCHI / FONDO CASSA)
# ===============================

def registra_sezione(titolo, key_input, tipo, st_input, numero_input):
    st.subheader(titolo)
    causale = st_input(f"Causale {titolo}", key=f"{key_input}_causale")
    valore = numero_input(f"Importo (+ / -)", value=0.0, key=f"{key_input}_valore")
    if st.button(f"Registra {titolo}", key=f"btn_{key_input}"):
        if causale.strip():
            st.session_state[tipo] += valore
            registra_movimento(tipo, causale, valore)
            msg = f"""🧾 {titolo}

🕒 {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
📝 {causale}
💰 Importo: {formatta(valore)} €

📊 Totale {titolo}: {formatta(st.session_state[tipo])} €
"""
            invia_discord(msg)
            st.success(f"{titolo} registrato!")

st.divider()
registra_sezione("Cassa", "cassa", "cassa", st.text_input, st.number_input)
registra_sezione("Soldi Sporchi", "sporchi", "soldi_sporchi", st.text_input, st.number_input)
registra_sezione("Fondo Cassa", "fondo", "fondo_cassa", st.text_input, st.number_input)
st.divider()

# ===============================
# 📋 REGISTRO MOVIMENTI
# ===============================
st.subheader("📋 Registro Movimenti")
if st.session_state.movimenti:
    for mov in reversed(st.session_state.movimenti):
        st.markdown(
            f"""
            <div style='background-color:#2C2C2C;padding:15px;border-radius:10px;margin-bottom:10px;'>
                <b>🕒 {mov['data']}</b><br>
                📂 <b>{mov['tipo']}</b><br>
                📝 {mov['causale']}<br>
                💰 Importo: {formatta(mov['valore'])} €
            </div>
            """, unsafe_allow_html=True
        )
else:
    st.info("Nessun movimento registrato")
