import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components

# --- 1. SETUP ---
st.set_page_config(page_title="Professional AI Architect", layout="wide")

# Styling für den "Conceptual Architecture" Look (Weißer Hintergrund, klare Linien)
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stTextArea textarea { border: 1px solid #3C8CE7; }
    .stButton>button { background-color: #3C8CE7; color: white; border-radius: 5px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH ---
api_key = st.secrets.get("OPENAI_API_KEY")
password = st.secrets.get("APP_PASSWORD", "admin")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔒 Login")
    pw_input = st.text_input("Passwort:", type="password")
    if pw_input == password:
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- 3. APP ---
client = OpenAI(api_key=api_key)
st.title("🏗️ Professional Architecture Designer")

col1, col2 = st.columns([1, 2])

with col1:
    prompt = st.text_area("System beschreiben:", height=300, 
                         placeholder="Z.B. Webshop für Trikots. Nutze Schichten für Frontend, Backend und Datenbanken.")
    generate = st.button("Architektur generieren")

if generate and prompt:
    with st.spinner("Visualisiere Architektur..."):
        try:
            # Der Prompt ist jetzt extrem spezifisch für den Layer-Look (Bild 14)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "system", 
                    "content": """Du bist ein Senior Architekt. Erstelle NUR Mermaid.js Code (graph LR).
                    WICHTIG: 
                    1. Gruppiere ALLES in subgraphs: 'subgraph "Specification and Execution Layer"', 'subgraph "Data Layer"', etc.
                    2. Nutze Icons: 'User[fa:fa-user User]' oder 'DB[(fa:fa-database Database)]'.
                    3. Farbe: Nutze 'linkStyle default stroke:#00a896,stroke-width:3px;' für die Linien.
                    4. Antworte NUR mit dem Code, ohne Backticks oder Text."""
                }, {"role": "user", "content": prompt}]
            )
            
            clean_code = response.choices[0].message.content.strip().replace("```mermaid", "").replace("```", "")

            with col2:
                st.subheader("Ihre Architektur-Visualisierung:")
                
                # DER FIX FÜR DEN FEHLER (html_code entfernt):
                html_template = f"""
                <div class="mermaid" style="background-color: white; border: 1px solid #ddd; padding: 20px;">
                {clean_code}
                </div>
                <script type="module">
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                    mermaid.initialize({{ 
                        startOnLoad: true, 
                        theme: 'base',
                        themeVariables: {{
                            'primaryColor': '#ffffff',
                            'primaryTextColor': '#333',
                            'primaryBorderColor': '#333',
                            'lineColor': '#00a896',
                            'secondaryColor': '#f4f4f4',
                            'tertiaryColor': '#fff'
                        }},
                        flowchart: {{ htmlLabels: true, curve: 'basis' }}
                    }});
                </script>
                """
                # Hier lag der Fehler: Das Argument heißt 'html', nicht 'html_code'
                components.html(html_template, height=800, scrolling=True)
                
        except Exception as e:
            st.error(f"Fehler: {e}")
