import streamlit as st
from openai import OpenAI

# 1. Setup
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

st.title("🇲🇺 Deutsch ➔ Kreol")

if 'data' not in st.session_state:
    st.session_state.data = None
if 'last_text' not in st.session_state:
    st.session_state.last_text = ""

# 2. Eingabe & Checkboxen
source_text = st.text_input("Was möchtest du übersetzen?", placeholder="z.B. Gute Besserung")
cols = st.columns(5)
show_formal = cols[0].checkbox("🔵 Geh.", value=True)
show_neutral = cols[1].checkbox("🟢 Neu.", value=True)
show_popular = cols[2].checkbox("⭐ Pop.", value=True)
show_slang = cols[3].checkbox("🟠 Umg.", value=True)
show_vulgar = cols[4].checkbox("🔴 Vul.", value=True)

# 3. Übersetzungsprozess
if source_text and source_text != st.session_state.last_text:
    with st.spinner('GPT-5.2 generiert...'):
        system_msg = """Du bist ein mauritischer Sprachexperte. 
        Übersetze in 5 Ebenen. Format: LABEL: [Kreolisch] | [Rückübersetzung]
        Labels: GEHOBEN, NEUTRAL, POPULÄR, UMGANG, VULGÄR."""

        response = client.chat.completions.create(
            model="gpt-5.2", 
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": source_text}]
        )
        
        raw_output = response.choices[0].message.content
        new_data = {}
        # Stabilerer Split-Mechanismus
        for line in raw_output.strip().split('\n'):
            if ":" in line:
                label_part, content_part = line.split(":", 1)
                clean_label = label_part.strip().upper()
                if "|" in content_part:
                    t, b = content_part.split("|", 1)
                    new_data[clean_label] = {"t": t.strip(), "b": b.strip()}
                else:
                    new_data[clean_label] = {"t": content_part.strip(), "b": "Keine Rückübersetzung verfügbar"}
        
        st.session_state.data = new_data
        st.session_state.last_text = source_text

# 4. Anzeige (Korrektur für Rückübersetzung & Audio)
if st.session_state.data:
    display_logic = [
        (show_formal, "GEHOBEN", "🔵"),
        (show_neutral, "NEUTRAL", "🟢"), 
        (show_popular, "POPULÄR", "⭐"), 
        (show_slang, "UMGANG", "🟠"), 
        (show_vulgar, "VULGÄR", "🔴")
    ]

    for active, key, emoji in display_logic:
        if active:
            # Sucht den passenden Eintrag im Datensatz
            actual_key = next((k for k in st.session_state.data if key in k), None)
            if actual_key:
                entry = st.session_state.data[actual_key]
                with st.expander(f"{emoji} {key}: {entry['t']}", expanded=False):
                    # ZEIGT DIE RÜCKÜBERSETZUNG AN
                    st.write(f"**Rückübersetzung:** _{entry['b']}_")
                    st.info(f"Stilebene: {key.lower()}")
                    
                    # AUDIO BUTTON
                    if st.button(f"🔊 Anhören ({key})", key=f"btn_{key}"):
                        audio_res = client.audio.speech.create(
                            model="tts-1",
                            voice="nova",
                            input=entry['t']
                        )
                        st.audio(audio_res.content)

# 5. Rückfrage
st.markdown("---")
query = st.text_input("💬 Rückfrage an den Lehrer:")
if query and source_text:
    res = client.chat.completions.create(
        model="gpt-5.2",
        messages=[{"role": "system", "content": "Du bist Lehrer für Mauritisches Kreol."},
                  {"role": "user", "content": f"Im Kontext von '{source_text}' frage ich mich: {query}"}]
    )
    st.success(res.choices[0].message.content)
