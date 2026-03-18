import streamlit as st
from datetime import datetime
import requests
import json
import base64

st.set_page_config(layout="wide", page_title="Registro Finanze", page_icon="💰")

# -------------------------------
# CONFIG GITHUB
# -------------------------------
GITHUB_REPO_OWNER = st.secrets["GITHUB_OWNER"]
GITHUB_REPO_NAME  = st.secrets["GITHUB_REPO"]
GITHUB_FILE_PATH  = "finanze.json"
GITHUB_TOKEN      = st.secrets["GITHUB_PAT"]

GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/{GITHUB_FILE_PATH}"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# -------------------------------
# FUNZIONI GITHUB
# -------------------------------
def leggi_file_github():
    """Legge il file JSON da GitHub e lo restituisce come dizionario"""
    r = requests.get(GITHUB_API_URL, headers=HEADERS)
    if r.status_code == 200:
        content = r.json()["content"]
        decoded = base64.b64decode(content).decode("utf-8")
        return json.loads(decoded)
    else:
        # struttura vuota se il file non esiste
        return {"cassa": 0, "fondo_cassa": 0, "soldi_sporchi": 0, "movimenti": []}

def aggiorna_file_github(dati):
    """Aggiorna o crea il file JSON su GitHub leggendo sempre lo SHA corrente"""
    r = requests.get(GITHUB_API_URL, headers=HEADERS)
    if r.status_code == 200:
        sha = r.json()["sha"]
    else:
        sha = None

    json_str = json.dumps(dati, indent=4)
    json_base64 = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
    payload = {"message": "Aggiornamento finanze", "content": json_base64}
    if sha:
        payload["sha"] = sha

    r = requests.put(GITHUB_API_URL, headers=HEADERS, json=payload)
    if r.status_code not in [200, 201]:
        st.error(f"Errore aggiornamento GitHub: {r.json()}")

# -------------------------------
# STATO STREAMLIT
# -------------------------------
if "dati" not in st.session_state:
    st.session_state.dati = leggi_file_github()

# -------------------------------
# UTILI
# -------------------------------
def formatta(num):
    return f"{round(num):,}".replace(",", ".")

def registra_movimento(tipo, causale, valore):
    """Aggiorna session_state e GitHub senza rerun"""
    st.session_state.dati["movimenti"].append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "tipo": tipo,
        "causale": causale,
        "valore": valore
    })
    st.session_state.dati[tipo] += valore
    aggiorna_file_github(st.session_state.dati)

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
    st.markdown(f"<div style='background-color:#1E1E1E;padding:20px;border-radius:10px;text-align:center;'>"
                f"<h3>💰 CASSA</h3><h2>{formatta(st.session_state.dati['cassa'])} $</h2></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div style='background-color:#1E1E1E;padding:20px;border-radius:10px;text-align:center;'>"
                f"<h3>💸 SOLDI SPORCHI</h3><h2>{formatta(st.session_state.dati['soldi_sporchi'])} $</h2></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div style='background-color:#1E1E1E;padding:20px;border-radius:10px;text-align:center;'>"
                f"<h3>💼 FONDO CASSA</h3><h2>{formatta(st.session_state.dati['fondo_cassa'])} $</h2></div>", unsafe_allow_html=True)

st.divider()

# ===============================
# FUNZIONE REGISTRA SEZIONE
# ===============================
def registra_sezione(titolo, tipo):
    st.subheader(titolo)

    # ✅ Inizializza le chiavi se non esistono
    if f"{tipo}_valore" not in st.session_state:
        st.session_state[f"{tipo}_valore"] = 0.0
    if f"{tipo}_causale" not in st.session_state:
        st.session_state[f"{tipo}_causale"] = ""

    # widget legati a session_state
    causale = st.text_input(f"Causale {titolo}", key=f"{tipo}_causale")
    valore = st.number_input("Importo (+ / -)", value=st.session_state[f"{tipo}_valore"], key=f"{tipo}_valore")

    if st.button(f"Registra {titolo}", key=f"btn_{tipo}"):
        if causale.strip():
            registra_movimento(tipo, causale, valore)
            # reset input
            st.session_state[f"{tipo}_valore"] = 0.0
            st.session_state[f"{tipo}_causale"] = ""

registra_sezione("Cassa", "cassa")
registra_sezione("Soldi Sporchi", "soldi_sporchi")
registra_sezione("Fondo Cassa", "fondo_cassa")

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

# ===============================
# PULSANTE RESET REGISTRO
# ===============================
st.divider()
st.subheader("⚠️ Gestione Registro")
if st.button("Svuota Registro"):
    st.session_state.dati = {"cassa": 0, "fondo_cassa": 0, "soldi_sporchi": 0, "movimenti": []}
    aggiorna_file_github(st.session_state.dati)
