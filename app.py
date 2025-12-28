import streamlit as st
from openai import OpenAI

api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=api_key)

# App-Konfiguration mit dem neuen Namen
st.set_page_config(page_title="Kreol", page_icon="🇲🇺")
st.title("🇲🇺 Deutsch ➔ Kreol")

# Speicher für die Ergebnisse (Session State)
if 'data' not in st.session_state:
    st.session_state.data = None
if 'last_text' not in st.session_state:
    st.session_state.last_text = ""

# 2. Eingabe
source_text = st.text_input("Was möchtest du übersetzen?", placeholder="z.B. Gute Besserung")

# 3. Checkboxen
cols = st.columns(5)
show_formal = cols[0].checkbox("🔵 Geh.", value=True)
show_neutral = cols[1].checkbox("🟢 Neu.", value=True)
show_popular = cols[2].checkbox("⭐ Pop.", value=True)
show_slang = cols[3].checkbox("🟠 Umg.", value=True)
show_vulgar = cols[4].checkbox("🔴 Vul.", value=True)

# 4. Übersetzungsprozess
if source_text and source_text != st.session_state.last_text:
    with st.spinner('GPT-5.2 generiert Übersetzungen...'):
        system_msg = """Du bist ein mauritischer Sprachexperte. 
        Deine Aufgabe: Übersetze den deutschen Text in Mauritisches Kreol in 5 Ebenen.
        Format pro Zeile: LABEL: [Kreolische Übersetzung] | [Deutsche Rückübersetzung]
        
        BEISPIEL:
        GEHOBEN: Mo swet ou enn rapid gerizon | Ich wünsche Ihnen eine schnelle Genesung
        POPULÄR: Gerizon vit vit | Schnelle Heilung (Kurzform)
        
        Benutze EXAKT diese 5 Labels: GEHOBEN, NEUTRAL, POPULÄR, UMGANG, VULGÄR.
        Schreibe in der Übersetzung (vor dem |) NIEMALS Deutsch, sondern immer nur Kreol!"""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": source_text}]
        )
        
        raw_output = response.choices[0].message.content
        new_data = {}
        for line in raw_output.strip().split('\n'):
            if ":" in line and "|" in line:
                label, content = line.split(":", 1)
                t, b = content.split("|", 1)
                clean_label = label.strip().upper()
                new_data[clean_label] = {"t": t.strip(), "b": b.strip()}
        
        st.session_state.data = new_data
        st.session_state.last_text = source_text

# 5. Anzeige (Eingeklappt per Default)
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
            actual_key = next((k for k in st.session_state.data if k.startswith(key)), None)
            
            if actual_key:
                entry = st.session_state.data[actual_key]
                with st.expander(f"{emoji} {key}: {entry['t']}", expanded=False):
                    
                    # 1. Rückübersetzung & Erklärung (Jetzt fest im Expander)
                    st.write(f"**Rückübersetzung:** _{entry['b']}_")
                    
                    # Kleiner Zusatz-Text für die Nuance
                    st.info(f"Dies ist die {key.lower()}e Form der Ausdrucksweise im Mauritischen.")
                    
                    # 2. Audio Button
                    if st.button(f"🔊 Anhören ({key})", key=f"btn_{key}"):
                        with st.spinner("Lade Audio..."):
                            audio_input = entry['t'] if entry['t'].endswith(('.', '!', '?')) else entry['t'] + "."
                            audio_res = client.audio.speech.create(
                                model="tts-1",
                                voice="nova",
                                input=audio_input
                            )
                            st.audio(audio_res.content)

# 6. Rückfrage-Bereich (Hier bleibt alles wie gehabt)
st.markdown("---")
query = st.text_input("💬 Rückfrage an den Lehrer:")
if query and source_text:
    res = client.chat.completions.create(
        model="gpt-5.2",
        messages=[{"role": "system", "content": "Du bist Lehrer für Mauritisches Kreol."},
                  {"role": "user", "content": f"Im Kontext von '{source_text}' frage ich mich: {query}"}]
    )
    st.success(res.choices[0].message.content)

# 6. Rückfrage-Bereich
st.markdown("---")
query = st.text_input("💬 Rückfrage an den Lehrer:")
if query and source_text:
    res = client.chat.completions.create(
        model="gpt-5.2",
        messages=[{"role": "system", "content": "Du bist Lehrer für Mauritisches Kreol."},
                  {"role": "user", "content": f"Im Kontext von '{source_text}' frage ich mich: {query}"}]
    )
    st.success(res.choices[0].message.content)
