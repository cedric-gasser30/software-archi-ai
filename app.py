import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components

# --- 1. SETUP ---
st.set_page_config(page_title="Professional AI Architect", layout="wide")

# Styling für die App (Heller Hintergrund, sauberer Look)
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stTextArea textarea { border: 2px solid #3C8CE7; border-radius: 10px; }
    .stButton>button { background-color: #3C8CE7; color: white; font-weight: bold; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH ---
api_key = st.secrets.get("OPENAI_API_KEY")
password = st.secrets.get("APP_PASSWORD", "admin")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    pw_input = st.text_input("Passwort eingeben:", type="password")
    if pw_input == password:
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- 3. APP ---
client = OpenAI(api_key=api_key)
st.title("🏗️ Professional Architecture Designer")

col1, col2 = st.columns([1, 2])

with col1:
    prompt = st.text_area("System beschreiben:", height=200, placeholder="Trikot-Shop mit Frontend, Backend und Datenbanken...")
    generate = st.button("Architektur generieren")

if generate and prompt:
    with st.spinner("Visualisiere..."):
        try:
            # Der Prompt zwingt die KI, Subgraphs (Boxen) zu bauen
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "system", 
                    "content": "Du bist ein Top-Architekt. Erstelle NUR Mermaid.js Code (graph LR). "
                               "Nutze 'subgraph' um Komponenten in Boxen wie 'Frontend', 'Backend' und 'Daten' zu gruppieren. "
                               "Nutze Farben für Pfeile: linkStyle default stroke:#3C8CE7,stroke-width:2px; "
                               "Gib NUR den Code ohne Backticks aus."
                }, {"role": "user", "content": prompt}]
            )
            
            clean_code = response.choices[0].message.content.strip().replace("```mermaid", "").replace("```", "")

            with col2:
                st.subheader("Ihre Architektur-Visualisierung:")
                
                # DER FIX: Dieses HTML-Snippet sorgt für das richtige Zeichnen
                html_template = f"""
                <div class="mermaid">
                {clean_code}
                </div>
                <script type="module">
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                    mermaid.initialize({{ 
                        startOnLoad: true, 
                        theme: 'base',
                        themeVariables: {{
                            'primaryColor': '#ffffff',
                            'edgeColor': '#3C8CE7',
                            'fontFamily': 'arial'
                        }},
                        flowchart: {{ htmlLabels: true, curve: 'basis' }}
                    }});
                    // Erzwinge das Rendern
                    mermaid.contentLoaded();
                </script>
                """
                components.html(html_code=html_template, height=800, scrolling=True)
                
        except Exception as e:
            st.error(f"Fehler: {e}")
