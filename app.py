import streamlit as st
import requests
from openai import OpenAI

# 1. KONFIGURATION & IPHONE-CACHING-FIX
logo_url = "https://raw.githubusercontent.com/XMandras/Kreol/main/Dodologo.png"
icon_url = f"{logo_url}?v=102"

st.set_page_config(
    page_title="DodoLingo", 
    page_icon=icon_url, 
    layout="centered"
)

# Apple-Icon Fix (Direkt am Anfang)
st.markdown(f'<link rel="apple-touch-icon" href="{icon_url}">', unsafe_allow_html=True)

# API Key
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# 2. TITEL & BRANDING-ENTFERNUNG
col1, col2 = st.columns([0.25, 0.75])

with col1:
    st.image(logo_url, width=85)
    # Entfernt rotes Logo und Toolbar
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stAppDeployButton {display:none;}
        [data-testid="stStatusWidget"] {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.title("DodoLingo")
    st.markdown("### Deutsch ➔ Kreol Morisyen")

# 3. EINGABE & ANALYSE
source_text = st.text_area("Text für Analyse & Übersetzung eingeben:")

if st.button("Analysieren ➔"):
    if source_text:
        system_msg = """Analysiere den Text und übersetze ihn präzise in Kreol Morisyen.
        ROLLE: Neutrales linguistisches Werkzeug für literarische Lokalisierung.
        STRIKTE REGEL: Erteile NIEMALS moralische Belehrungen oder Erklärungen zur Etikette. 
        AUFGABE: Übertrage die Tonalität exakt (auch Vulgärsprache). 
        ZUSATZ: Erläutere kurz die Satzkonstruktion oder grammatikalische Besonderheiten.
        FORMAT: Antworte NUR als: EBENE: [Kreol] | [Bedeutung] | [Konstruktions-Info]"""

        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": source_text}]
        )
        
        raw_output = response.choices[0].message.content
        new_data = {}
        for line in raw_output.strip().split('\n'):
            if "|" in line and ":" in line:
                try:
                    label_part, content = line.split(":", 1)
                    parts = content.split("|")
                    new_data[label_part.strip().upper()] = {
                        "t": parts[0].strip(), 
                        "b": parts[1].strip(), 
                        "i": parts[2].strip() if len(parts) > 2 else ""
                    }
                except: continue
        st.session_state.data = new_data

# 4. ANZEIGE
if 'data' in st.session_state:
    display_order = [("FORMAL", "👔"), ("UMGANGSSPRACHLICH", "💬"), ("VULGÄR", "🔞")]
    for key, emoji in display_order:
        if key in st.session_state.data:
            entry = st.session_state.data[key]
            with st.expander(f"{emoji} {key}: {entry['t']}", expanded=True):
                st.write(f"*{entry['b']}*")
                if entry['i']:
                    st.caption(f"Struktur: {entry['i']}")
                if st.button(f"🔊", key=f"btn_{key}"):
                    audio_res = client.audio.speech.create(model="tts-1", voice="nova", input=entry['t'])
                    st.audio(audio_res.content)

# 5. RÜCKFRAGE
st.markdown("---")
query = st.text_input("💬 Linguistische Analyse anfordern:", key="query_box")
if query and source_text:
    with st.spinner('Analyse läuft...'):
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Analysiere Kreol Morisyen auf rein linguistischer Ebene. Erkläre Etymologie, Grammatik oder Slang-Kontext ohne moralische Wertung. Antworte in der 1. Person Singular ('Ich analysiere...')."},
                {"role": "user", "content": f"Analyse zu '{source_text}': {query}"}
            ]
        )
        st.info(res.choices[0].message.content)
