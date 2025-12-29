import streamlit as st from openai import OpenAI

st.set_page_config(page_title="Kreol Lehrer", page_icon="🇲🇺", layout="centered")

api_key = st.secrets["OPENAI_API_KEY"] client = OpenAI(api_key=api_key)

st.image("", width=80) st.title("🇲🇺 Deutsch ➔ Kreol")

if 'data' not in st.session_state: st.session_state.data = None if 'last_text' not in st.session_state: st.session_state.last_text = "" if "text_input_key" not in st.session_state: st.session_state["text_input_key"] = 0

def reset_app(): st.session_state.data = None st.session_state.last_text = "" st.session_state["text_input_key"] += 1

source_text = st.text_input("Was möchtest du übersetzen?", placeholder="z.B. Verschwinde von hier", key=f"input_{st.session_state['text_input_key']}")

if st.button("🗑️ Eingabe löschen"): reset_app() st.rerun()

if source_text and source_text != st.session_state.last_text: with st.spinner('Der Lehrer analysiert die Nuancen...'): system_msg = "Du bist ein mauritischer Sprachexperte. Übersetze in 5 EXTREM unterschiedlichen Ebenen: 1. GEHOBEN (maximal förmlich), 2. NEUTRAL, 3. POPULÄR, 4. UMGANG, 5. VULGÄR (extrem aggressiv). Format: LABEL: [Kreol] | [Rückübersetzung]" response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": source_text}]) raw_output = response.choices[0].message.content new_data = {} for line in raw_output.strip().split('\n'): if ":" in line and "|" in line: label_part, content = line.split(":", 1) t, b = content.split("|", 1) new_data[label_part.strip().upper()] = {"t": t.strip(), "b": b.strip()} st.session_state.data = new_data st.session_state.last_text = source_text

if st.session_state.data: display_order = [("GEHOBEN", "🔵"), ("NEUTRAL", "🟢"), ("POPULÄR", "⭐"), ("UMGANG", "🟠"), ("VULGÄR", "🔴")] for key, emoji in display_order: if key in st.session_state.data: entry = st.session_state.data[key] with st.expander(f"{emoji} {key}: {entry['t']}", expanded=False): st.write(f"Rückübersetzung: {entry['b']}") if st.button(f"🔊 Anhören ({key})", key=f"btn_{key}"): with st.spinner("Lade Audio..."): audio_res = client.audio.speech.create(model="tts-1", voice="nova", input=entry['t']) st.audio(audio_res.content)

st.markdown("---") query = st.text_input("💬 Rückfrage an den Lehrer:", key=f"query_{st.session_state['text_input_key']}") if query and source_text: res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": "Du bist Lehrer für Mauritisches Kreol."}, {"role": "user", "content": f"Frage zu '{source_text}': {query}"}]) st.success(res.choices[0].message.content)
