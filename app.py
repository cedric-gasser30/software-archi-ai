import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components

# --- Konfiguration ---
st.set_page_config(
    page_title="AI Software Architect",
    page_icon="🏗️",
    layout="wide"
)

# --- Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stTextArea textarea {
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar: API-Konfiguration ---
st.sidebar.title("⚙️ Einstellungen")
# Versucht den Key aus den Streamlit Secrets zu laden, sonst manuelles Feld
api_key = st.sidebar.text_input("OpenAI API Key", 
                                value=st.secrets.get("OPENAI_API_KEY", ""), 
                                type="password",
                                help="Hinterlege deinen Key in den Streamlit Secrets oder gib ihn hier ein.")

model_choice = st.sidebar.selectbox("KI Modell", ["gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"])

st.sidebar.info("""
**Anleitung:**
1. Gib eine Systembeschreibung ein.
2. Wähle den Diagrammtyp.
3. Klicke auf 'Generieren'.
""")

# --- Hauptbereich ---
st.title("🏗️ AI Software Architecture Designer")
st.subheader("Visualisiere komplexe Systeme in Sekunden")

col_in, col_out = st.columns([1, 2])

with col_in:
    user_input = st.text_area(
        "Systembeschreibung:", 
        height=300,
        placeholder="Beispiel: Ein E-Commerce System mit einem React Frontend, einem Node.js API-Gateway, Microservices für Produkte und Nutzer, sowie einer MongoDB Datenbank."
    )
    
    diagram_type = st.selectbox(
        "Diagramm-Typ:", 
        ["Flowchart (Flussdiagramm)", "Sequence Diagram (Ablauf)", "Class Diagram (Struktur)", "Entity Relationship (Datenbank)"]
    )
    
    generate_btn = st.button("🚀 Architektur generieren", use_container_width=True)

# --- Logik & KI-Abfrage ---
if generate_btn:
    if not api_key:
        st.error("❌ Bitte gib einen OpenAI API Key an!")
    elif not user_input:
        st.warning("⚠️ Bitte beschreibe zuerst dein System.")
    else:
        client = OpenAI(api_key=api_key)
        
        with st.spinner("KI entwirft die Architektur..."):
            try:
                # System-Prompt für präzisen Mermaid-Code
                prompt = f"""
                Du bist ein Senior Software Architekt. Erstelle ein {diagram_type} für das folgende System:
                '{user_input}'
                
                ANTWORTE NUR MIT DEM MERMAID.JS CODE. 
                Beginne direkt mit 'graph TD', 'sequenceDiagram' oder dem entsprechenden Start-Tag.
                Verwende keine Code-Blöcke (```) in deiner Antwort.
                Nutze aussagekräftige Labels und moderne Formatierung.
                """
                
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                
                mermaid_code = response.choices[0].message.content.strip()
                
                # Bereinigung falls die KI doch Backticks liefert
                mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "")

                with col_out:
                    st.success("Architektur erfolgreich generiert!")
                    
                    # HTML/JS Code zum Rendern von Mermaid
                    mermaid_html = f"""
                    <div class="mermaid" style="display: flex; justify-content: center;">
                    {mermaid_code}
                    </div>
                    <script type="module">
                        import mermaid from '[https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs](https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs)';
                        mermaid.initialize({{ 
                            startOnLoad: true,
                            theme: 'neutral',
                            securityLevel: 'loose'
                        }});
                    </script>
                    """
                    
                    # Rendern des Diagramms
                    components.html(mermaid_html, height=600, scrolling=True)
                    
                    # Download & Quellcode Bereich
                    with st.expander("Mermaid Quellcode anzeigen"):
                        st.code(mermaid_code, language="mermaid")
                        st.info("Diesen Code kannst du direkt in GitHub oder Notion einfügen.")

            except Exception as e:
                st.error(f"Ein Fehler ist aufgetreten: {str(e)}")