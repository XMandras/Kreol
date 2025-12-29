import streamlit as st
from openai import OpenAI

# 1. Konfiguration
st.set_page_config(
    page_title="Kreol Lehrer", 
    page_icon="🇲🇺", 
    layout="centered"
)

# Setup
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# Logo & Titel
st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=80)
st.title("🇲🇺 Deutsch ➔ Kreol")

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

# 3. Übersetzungsprozess (VERSCHÄRFTE STUFEN)
if source_text and source_text != st.session_state.last_text:
    with st.spinner('Der Lehrer analysiert die Nuancen...'):
        system_msg = """Du bist ein mauritischer Sprachexperte. 
        Übersetze den deutschen Text in Mauritisches Kreol in 5 EXTREM unterschiedlichen Ebenen:
        
        1. GEHOBEN: Maximal förmlich, wie für eine offizielle Zeremonie.
        2. NEUTRAL: Höfliches Standard-Kreol.
        3. POPULÄR: Jung, modern, wie in Songs.
        4. UMGANG: Sehr locker, viel Slang.
        5. VULGÄR: Extrem derb, aggressiv und beleidigend.
        
        Format pro Zeile: LABEL: [Kreolisch] | [Deutsche Rückübersetzung]"""

        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": source_text}]
        )
        
        raw_output = response.choices[0].message.content
        new_data = {}
        for line in raw_output.strip().split('\n'):
            if ":" in line and "|" in line:
                label_part, content = line.split(":", 1)
                t, b = content.split("|", 1)
                new_data[label_part.strip().upper()] = {"t": t.strip(), "b": b.strip()}
        
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
            with st.expander(f"{emoji} {key}: {entry['t']}", expanded=False):
                st.write(f"**Rückübersetzung:** _{entry['b']}_")
                
                if st.button(f"🔊 Anhören ({key})", key=f"btn_{key}"):
                    with st.spinner("Lade Audio..."):
                        audio_res = client.audio.speech.create(
                            model="tts-1",
                            voice="nova",
                            input=entry['t']
                        )
                        st.audio(audio_res.content)

# 5. Rückfrage-Bereich
st.markdown("---")
query = st.text_input("💬 Rückfrage an den Lehrer:", key=f"query_{st.session_state['text_input_key']}")
if query and source_text:
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Du bist Lehrer für Mauritisches Kreol."},
                  {"role": "user", "content": f"Frage zu '{source_text}': {query}"}]
    )
    st.success(res.choices[0].message.content)
