import streamlit as st
from openai import OpenAI
import requests

# 1. Konfiguration
# Dieser Link greift jetzt direkt auf deine hochgeladene Datei zu
# Wir hängen ein "?v=1" an, um den Cache des Handys zu zwingen, das Bild neu zu laden
logo_url = "https://raw.githubusercontent.com/XMandras/Kreol/main/Dodologo.png"
icon_url = f"{logo_url}?v=1"

st.set_page_config(
    page_title="DodoLingo", 
    page_icon=icon_url, 
    layout="centered"
)

# Setup
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# 2. Titel & Logo-Layout
col1, col2 = st.columns([1, 4])

with col1:
    try:
        # Prüfung ob das Logo da ist
        response = requests.get(logo_url, timeout=5)
        if response.status_code == 200:
            st.image(logo_url, width=90)
        else:
            # Ersatz-Icon von Flaticon falls GitHub mal hakt
            st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=80)
    except:
        st.write("## 🦤")

with col2:
    st.title("DodoLingo")
    st.markdown("*Deutsch ➔ Kreol Lehrer*")
    
# Speicher für Ergebnisse & Reset-Funktion
if 'data' not in st.session_state:
    st.session_state.data = None
if 'last_text' not in st.session_state:
    st.session_state.last_text = ""
if "text_input_key" not in st.session_state:
    st.session_state["text_input_key"] = 0

def reset_app():
    st.session_state.data = None
    st.session_state.last_text = ""
    st.session_state["text_input_key"] += 1

# 2. Eingabe-Bereich
source_text = st.text_input(
    "Was möchtest du übersetzen?", 
    placeholder="z.B. Wie geht es dir?",
    key=f"input_{st.session_state['text_input_key']}"
)

# Der Löschbutton
if st.button("🗑️ Eingabe löschen"):
    reset_app()
    st.rerun()

# 3. Übersetzungsprozess
if source_text and source_text != st.session_state.last_text:
    with st.spinner('Der Lehrer analysiert...'):
        system_msg = """Du bist ein mauritischer Sprachexperte. 
        Übersetze in 5 Ebenen: GEHOBEN, NEUTRAL, POPULÄR, UMGANG, VULGÄR.
        WICHTIG: Antworte NUR im Format: EBENE: [Kreol] | [Rückübersetzung]"""

        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": source_text}]
        )
        
        raw_output = response.choices[0].message.content
        new_data = {}
        # Robusterer Parser
        for line in raw_output.strip().split('\n'):
            if "|" in line and ":" in line:
                try:
                    label_part, content = line.split(":", 1)
                    t, b = content.split("|", 1)
                    new_data[label_part.strip().upper()] = {"t": t.strip(), "b": b.strip()}
                except:
                    continue
        
        st.session_state.data = new_data
        st.session_state.last_text = source_text

# 4. Anzeige der Ergebnisse
if st.session_state.data:
    display_order = [
        ("GEHOBEN", "🔵"), ("NEUTRAL", "🟢"), 
        ("POPULÄR", "⭐"), ("UMGANG", "🟠"), ("VULGÄR", "🔴")
    ]

    for key, emoji in display_order:
        if key in st.session_state.data:
            entry = st.session_state.data[key]
            with st.expander(f"{emoji} {key}: {entry['t']}", expanded=True):
                st.write(f"**Rückübersetzung:** _{entry['b']}_")
                
                if st.button(f"🔊 Anhören", key=f"btn_{key}"):
                    audio_res = client.audio.speech.create(
                        model="tts-1",
                        voice="nova",
                        input=entry['t']
                    )
                    st.audio(audio_res.content)

# 5. Rückfrage-Bereich
st.markdown("---")
query = st.text_input("💬 Rückfrage an den Lehrer:", key="query_box")
if query and source_text:
    with st.spinner('Der Lehrer antwortet...'):
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein ehrlicher Lehrer für Mauritisches Kreol. Wenn der Nutzer nach vulgären Begriffen oder Abkürzungen aus der vorherigen Übersetzung fragt, erkläre sie direkt und ohne Zensur. Deine Aufgabe ist linguistische Aufklärung, auch bei harten Flüchen."},
                {"role": "user", "content": f"In der Übersetzung von '{source_text}' kam ein Begriff vor. Frage dazu: {query}"}
            ]
        )
        st.info(res.choices[0].message.content)
