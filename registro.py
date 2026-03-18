import streamlit as st
from datetime import datetime
import requests

# -------------------------------
# CONFIG
# -------------------------------
WEBHOOK_URL = st.secrets.get("WEBHOOK_URL")

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
st.title("💰 Registro Finanze")

# ===============================
# 📊 DASHBOARD (IN ALTO)
# ===============================
col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.subheader("💰 CASSA")
        st.metric("", f"{formatta(st.session_state.cassa)} €")

with col2:
    with st.container():
        st.subheader("💸 SOLDI SPORCHI")
        st.metric("", f"{formatta(st.session_state.soldi_sporchi)} €")

with col3:
    with st.container():
        st.subheader("💼 FONDO CASSA")
        st.metric("", f"{formatta(st.session_state.fondo_cassa)} €")

st.divider()

# ===============================
# 🧾 MOVIMENTO CASSA
# ===============================
st.subheader("🧾 Movimento Cassa")

causale_cassa = st.text_input("Causale Cassa")
valore_cassa = st.number_input("Importo Cassa (+ / -)", value=0.0, key="cassa_input")

if st.button("Registra Movimento Cassa"):
    if causale_cassa.strip():
        st.session_state.cassa += valore_cassa
        registra_movimento("CASSA", causale_cassa, valore_cassa)

        msg = f"""🧾 Movimento Cassa

🕒 {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
📝 {causale_cassa}
💰 Importo: {formatta(valore_cassa)} €

📊 Totale Cassa: {formatta(st.session_state.cassa)} €
"""
        invia_discord(msg)

        st.success("Movimento cassa registrato")

st.divider()

# ===============================
# 💸 SOLDI SPORCHI
# ===============================
st.subheader("💸 Soldi Sporchi")

causale_sporchi = st.text_input("Causale Soldi Sporchi")
valore_sporchi = st.number_input("Importo (+ / -)", value=0.0, key="sporchi_input")

if st.button("Registra Soldi Sporchi"):
    if causale_sporchi.strip():
        st.session_state.soldi_sporchi += valore_sporchi
        registra_movimento("SOLDI SPORCHI", causale_sporchi, valore_sporchi)

        msg = f"""💸 Soldi Sporchi

🕒 {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
📝 {causale_sporchi}
💰 Importo: {formatta(valore_sporchi)} €

📊 Totale: {formatta(st.session_state.soldi_sporchi)} €
"""
        invia_discord(msg)

        st.success("Movimento soldi sporchi registrato")

st.divider()

# ===============================
# 💼 FONDO CASSA
# ===============================
st.subheader("💼 Fondo Cassa")

causale_fondo = st.text_input("Causale Fondo Cassa")
valore_fondo = st.number_input("Importo (+ / -)", value=0.0, key="fondo_input")

if st.button("Registra Fondo Cassa"):
    if causale_fondo.strip():
        st.session_state.fondo_cassa += valore_fondo
        registra_movimento("FONDO CASSA", causale_fondo, valore_fondo)

        msg = f"""💼 Fondo Cassa

🕒 {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
📝 {causale_fondo}
💰 Importo: {formatta(valore_fondo)} €

📊 Totale: {formatta(st.session_state.fondo_cassa)} €
"""
        invia_discord(msg)

        st.success("Fondo cassa aggiornato")

st.divider()

# ===============================
# 📋 REGISTRO MOVIMENTI
# ===============================
st.subheader("📋 Registro Movimenti")

if st.session_state.movimenti:
    for mov in reversed(st.session_state.movimenti):
        st.write(f"""
🕒 {mov['data']}  
📂 {mov['tipo']}  
📝 {mov['causale']}  
💰 Importo: {formatta(mov['valore'])} €  
""")
        st.divider()
else:
    st.info("Nessun movimento registrato")
