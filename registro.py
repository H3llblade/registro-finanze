import streamlit as st
from datetime import datetime
import requests

# -------------------------------
# CONFIG
# -------------------------------
WEBHOOK_URL = st.secrets["WEBHOOK_URL"]

# -------------------------------
# STATO INIZIALE
# -------------------------------
if "cassa" not in st.session_state:
    st.session_state.cassa = 0

if "fondo_cassa" not in st.session_state:
    st.session_state.fondo_cassa = 0

if "soldi_sporchi" not in st.session_state:
    st.session_state.soldi_sporchi = 0

if "movimenti" not in st.session_state:
    st.session_state.movimenti = []

# -------------------------------
# FUNZIONI UTILI
# -------------------------------
def formatta(numero):
    return f"{round(numero):,}".replace(",", ".")

def invia_discord(messaggio):
    payload = {"content": messaggio}
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code != 204:
            st.warning(f"Errore Discord: {response.status_code}")
    except Exception as e:
        st.error(f"Errore webhook: {e}")

def aggiungi_movimento(tipo, causale, uscita, ingresso):
    st.session_state.movimenti.append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "tipo": tipo,
        "causale": causale,
        "uscita": uscita,
        "ingresso": ingresso
    })

# -------------------------------
# HEADER
# -------------------------------
st.title("💰 Registro Finanze")

# ===============================
# 🧾 MOVIMENTO CASSA
# ===============================
st.subheader("🧾 Movimento Cassa")
st.divider()

causale = st.text_input("Causale")
prelievo = st.number_input("Prelievo", value=0.0)
deposito = st.number_input("Deposito (può essere negativo)", value=0.0)

if st.button("Registra Movimento"):
    if causale.strip() == "":
        st.error("Inserisci una causale valida")
    else:
        # Logica
        st.session_state.cassa += deposito
        st.session_state.soldi_sporchi -= prelievo

        aggiungi_movimento("CASSA", causale, prelievo, deposito)

        # Discord
        data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        messaggio = f"""🧾 Nuovo movimento registrato

🕒 {data}
📝 Causale: {causale}
💸 Prelievo: {formatta(prelievo)} €
💰 Deposito: {formatta(deposito)} €
📂 Destinazione: CASSA

📊 Situazione aggiornata:

💰 CASSA: {formatta(st.session_state.cassa)} €
💼 FONDO CASSA: {formatta(st.session_state.fondo_cassa)} €
💸 SOLDI SPORCHI: {formatta(st.session_state.soldi_sporchi)} €
"""
        invia_discord(messaggio)

        st.success("Movimento registrato!")

# ===============================
# 💼 FONDO CASSA
# ===============================
st.subheader("💼 Fondo Cassa")
st.divider()

valore_fondo = st.number_input("Importo da aggiungere", value=0.0, key="fondo")

if st.button("Aggiorna Fondo Cassa"):
    st.session_state.fondo_cassa += valore_fondo

    aggiungi_movimento("FONDO CASSA", "Fondo Cassa", 0, valore_fondo)

    # Discord
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    messaggio = f"""💼 Fondo Cassa aggiornato

🕒 {data}
💰 Importo aggiunto: {formatta(valore_fondo)} €
📈 Totale Fondo Cassa: {formatta(st.session_state.fondo_cassa)} €
"""
    invia_discord(messaggio)

    st.success("Fondo cassa aggiornato!")

# ===============================
# 💸 SOLDI SPORCHI
# ===============================
st.subheader("💸 Soldi Sporchi")
st.divider()

valore_sporchi = st.number_input("Importo da aggiungere", value=0.0, key="sporchi")

if st.button("Aggiungi Soldi Sporchi"):
    st.session_state.soldi_sporchi += valore_sporchi

    aggiungi_movimento("FONDO CASSA", "Aggiunta Soldi Sporchi", 0, valore_sporchi)

    # Discord
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    messaggio = f"""💸 Soldi Sporchi aggiornati

🕒 {data}
💰 Importo aggiunto: {formatta(valore_sporchi)} €
📊 Totale: {formatta(st.session_state.soldi_sporchi)} €
"""
    invia_discord(messaggio)

    st.success("Soldi sporchi aggiornati!")

# ===============================
# 📊 DASHBOARD
# ===============================
st.subheader("📊 Situazione Attuale")
st.divider()

st.write(f"💰 CASSA: {formatta(st.session_state.cassa)} €")
st.write(f"💼 FONDO CASSA: {formatta(st.session_state.fondo_cassa)} €")
st.write(f"💸 SOLDI SPORCHI: {formatta(st.session_state.soldi_sporchi)} €")

# ===============================
# 📋 STORICO
# ===============================
st.subheader("📋 Storico Movimenti")
st.divider()

for mov in reversed(st.session_state.movimenti):
    st.write(f"""
🕒 {mov['data']}  
📂 {mov['tipo']}  
📝 {mov['causale']}  
💸 Uscita: {formatta(mov['uscita'])} €  
💰 Entrata: {formatta(mov['ingresso'])} €  
""")
    st.divider()
