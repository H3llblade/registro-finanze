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
# CONFIG DISCORD
# -------------------------------
WEBHOOK_URL = st.secrets.get("DISCORD_WEBHOOK_URL")  # il tuo webhook Discord

# -------------------------------
# FUNZIONI GITHUB
# -------------------------------
def leggi_file_github():
    r = requests.get(GITHUB_API_URL, headers=HEADERS)
    if r.status_code == 200:
        content = r.json()["content"]
        decoded = base64.b64decode(content).decode("utf-8")
        return json.loads(decoded)
    else:
        return {"cassa": 0, "fondo_cassa": 0, "soldi_sporchi": 0, "movimenti": []}

def aggiorna_file_github(dati):
    r = requests.get(GITHUB_API_URL, headers=HEADERS)
    sha = r.json()["sha"] if r.status_code == 200 else None

    json_str = json.dumps(dati, indent=4)
    json_base64 = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
    payload = {"message": "Aggiornamento finanze", "content": json_base64}
    if sha:
        payload["sha"] = sha

    r = requests.put(GITHUB_API_URL, headers=HEADERS, json=payload)
    if r.status_code not in [200, 201]:
        st.error(f"Errore aggiornamento GitHub: {r.json()}")

# -------------------------------
# INVIO DISCORD                 
# -------------------------------
def invia_discord(tipo, causale, valore, totale):
    if not WEBHOOK_URL:
        st.warning("Webhook Discord non impostato!")
        return
    try:
        # Aggiunta di emoji per rendere il messaggio più leggibile
        emoji_tipo = "💰" if tipo == "cassa" else "💸" if tipo == "soldi_sporchi" else "💼"
        msg = (
            f"{emoji_tipo} **{tipo.upper()} registrato!**\n"
            f"📝 Causale: {causale}\n"
            f"💵 Importo: {round(valore)} $\n"
            f"📊 Totale {tipo}: {round(totale)} $\n"
            f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )
        r = requests.post(WEBHOOK_URL, json={"content": msg}, timeout=5)
        if r.status_code == 204:
            st.success(f"Messaggio Discord inviato correttamente per {tipo}")
        else:
            st.error(f"Errore invio Discord: status {r.status_code} - {r.text}")
    except Exception as e:
        st.error(f"Eccezione invio Discord: {e}")

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
    st.session_state.dati["movimenti"].append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "tipo": tipo,
        "causale": causale,
        "valore": valore
    })
    st.session_state.dati[tipo] += valore
    aggiorna_file_github(st.session_state.dati)
    invia_discord(tipo, causale, valore, st.session_state.dati[tipo])

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

    if f"{tipo}_valore" not in st.session_state:
        st.session_state[f"{tipo}_valore"] = 0.0
    if f"{tipo}_causale" not in st.session_state:
        st.session_state[f"{tipo}_causale"] = ""

    causale = st.text_input(f"Causale {titolo}", key=f"{tipo}_causale")
    valore = st.number_input("Importo (+ / -)", value=st.session_state[f"{tipo}_valore"], key=f"{tipo}_valore")

    def registra_callback():
        if causale.strip():
            registra_movimento(tipo, causale, valore)
            st.session_state[f"{tipo}_valore"] = 0.0
            st.session_state[f"{tipo}_causale"] = ""

    st.button(f"Registra {titolo}", key=f"btn_{tipo}", on_click=registra_callback)

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
# PULSANTE RESET
# ===============================
def reset_registro():
    if st.button("🗑️ Svuota Registro"):
        st.session_state.dati = {
            "cassa": 0,
            "fondo_cassa": 0,
            "soldi_sporchi": 0,
            "movimenti": []
        }
        aggiorna_file_github(st.session_state.dati)
        st.success("Registro svuotato correttamente!")
reset_registro()
