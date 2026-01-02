import streamlit as st
from openai import OpenAI

# 1. Grundkonfiguration
st.set_page_config(page_title="DodoLingo", layout="centered")

# API Key Prüfung
if "OPENAI_API_KEY" not in st.secrets:
    st.error("API Key fehlt in den Secrets!")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 2. Titel & Logo
logo_url = "https://raw.githubusercontent.com/XMandras/Kreol/main/Dodologo.png"
col1, col2 = st.columns([0.25, 0.75])
with col1:
    st.image(logo_url, width=85)
with col2:
    st.title("DodoLingo")
    st.markdown("### Deutsch ➔ Kreol Morisyen")

# 3. Eingabebereich
source_text = st.text_area("Text für Übersetzung eingeben:", height=150)

if st.button("Übersetzen in 5 Sprachebenen"):
    if source_text:
        with st.spinner('Wird übersetzt...'):
            try:
                # System-Prompt mit Fokus auf wörtliche Rückübersetzung und linguistische Feinheiten
                system_msg = """Du bist ein Experte für Kreol Morisyen. Übersetze den Quelltext in 5 Ebenen.
                
                ANWEISUNGEN FÜR DIE RÜCKÜBERSETZUNG:
                1. Gib eine dezidierte, wörtliche Rückübersetzung ins Deutsche an.
                2. Erwähne IMMER, wenn und warum eine ungewöhnliche Satzkonstruktion oder ein bestimmtes Wort zur semantischen Verformung oder Verstärkung benutzt wird (z.B. Reduplikation, spezielle Partikel).
                3. Erkläre idiomatische Wendungen detailliert.
                
                FORMAT (Antworte NUR so):
                FORMAL: [Kreol] | [Wörtliche Rückübersetzung & Erklärung der Konstruktion/Verstärkung] | [Zusatz-Info]
                NEUTRAL: [Kreol] | [Wörtliche Rückübersetzung & Erklärung der Konstruktion/Verstärkung] | [Zusatz-Info]
                UMGANGSSPRACHLICH: [Kreol] | [Wörtliche Rückübersetzung & Erklärung der Konstruktion/Verstärkung] | [Zusatz-Info]
                SLANG: [Kreol] | [Wörtliche Rückübersetzung & Erklärung der Konstruktion/Verstärkung] | [Zusatz-Info]
                VULGÄR: [Kreol] | [Wörtliche Rückübersetzung & Erklärung der Konstruktion/Verstärkung] | [Zusatz-Info]"""

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": source_text}
                    ]
                )
                
                raw_output = response.choices[0].message.content
                data = {}
                for line in raw_output.strip().split('\n'):
                    if ":" in line and "|" in line:
                        label, rest = line.split(":", 1)
                        parts = rest.split("|")
                        if len(parts) >= 2:
                            data[label.strip().upper()] = {
                                "t": parts[0].strip(),
                                "b": parts[1].strip(),
                                "i": parts[2].strip() if len(parts) > 2 else ""
                            }
                st.session_state.data = data
            except Exception as e:
                st.error(f"Fehler: {e}")

# 4. Anzeige der 5 Ebenen (Eingeklappt)
if 'data' in st.session_state:
    display_order = [
        ("FORMAL", "👔"), 
        ("NEUTRAL", "⚖️"), 
        ("UMGANGSSPRACHLICH", "💬"), 
        ("SLANG", "🛹"), 
        ("VULGÄR", "🔞")
    ]
    for key, emoji in display_order:
        if key in st.session_state.data:
            entry = st.session_state.data[key]
            # Expander ist standardmäßig zu (expanded=False)
            with st.expander(f"{emoji} {key}: {entry['t']}", expanded=False):
                # Direkte Anzeige der Rückübersetzung/Analyse ohne einleitenden Text
                st.write(entry['b'])
                if entry['i']:
                    st.caption(f"Info: {entry['i']}")
                if st.button(f"🔊 Audio abspielen", key=f"audio_{key}"):
                    audio_res = client.audio.speech.create(model="tts-1", voice="nova", input=entry['t'])
                    st.audio(audio_res.content)

# 5. Rückfrage-Bereich
st.markdown("---")
query = st.text_input("💬 Linguistische Analyse anfordern:")
if query and source_text:
    with st.spinner('Analysiere...'):
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Analysiere rein linguistisch ohne moralische Wertung."},
                {"role": "user", "content": f"Text: {source_text}\nFrage: {query}"}
            ]
        )
        st.info(res.choices[0].message.content)
