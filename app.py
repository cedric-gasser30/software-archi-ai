import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components
import re

# --- SETUP & DESIGN ---
st.set_page_config(page_title="Pro Architekt AI", page_icon="💡", layout="wide")

# CSS für ein professionelles, sauberes Design und Anpassung an den Wunschstil
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; } /* Hellerer, neutraler Hintergrund */
    .stButton > button { 
        width: 100%; border-radius: 8px; height: 3.5em; 
        background-color: #4CAF50; /* Grüner Button, wie "Deploy" */ 
        color: white; font-size: 1.1em; font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stTextArea textarea {
        font-size: 1.05em;
        border-radius: 8px;
        border: 1px solid #ced4da;
    }
    h1, h2, h3, h4, h5, h6 { color: #333333; }
    .stAlert { border-radius: 8px; }

    /* Mermaid Style-Anpassungen */
    .mermaid {
        background-color: white !important; /* Weißer Hintergrund für das Diagramm */
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1); /* Tieferer Schatten */
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN LOGIK ---
def check_password():
    if "password_correct" not in st.session_state:
        st.subheader("Login für AI Architecture Designer")
        st.text_input("Bitte gib das Passwort ein:", type="password", key="password", 
                     on_change=lambda: st.session_state.update({"password_correct": st.session_state.password == st.secrets.get("APP_PASSWORD", "admin")}))
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Passwort falsch. Bitte erneut versuchen:", type="password", key="password_retry", 
                     on_change=lambda: st.session_state.update({"password_correct": st.session_state.password_retry == st.secrets.get("APP_PASSWORD", "admin")}))
        st.error("😕 Zugriff verweigert. Bitte gib das korrekte Passwort ein.")
        return False
    else:
        return True

# --- HAUPTAPP nach erfolgreichem Login ---
if check_password():
    api_key = st.secrets.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) if api_key else None

    st.title("💡 Professioneller Software Architektur Designer")
    st.markdown("Beschreibe dein System und die KI generiert ein **klares, strukturiertes Architekturdiagramm**.")

    # Sidebar für den Logout und Einstellungen
    with st.sidebar:
        if st.button("🔒 Logout"):
            st.session_state["password_correct"] = False
            st.rerun()
        st.markdown("---")
        st.subheader("Einstellungen")
        if not api_key:
            st.warning("Kein OpenAI API Key in Secrets gefunden.")
        else:
            st.success("✅ Erfolgreich angemeldet.")
        
        # Beispielprompts zur Orientierung
        st.markdown("#### Beispiel-Prompts:")
        st.markdown("""
        - "Microservice-Architektur für einen E-Commerce-Shop mit React Frontend, Python Backend (Django), PostgreSQL und Redis Cache. Füge einen Payment Service (Stripe) und einen E-Mail-Notification Service hinzu."
        - "Drei-Schichten-Architektur für eine mobile Banking App: Präsentationsschicht (Swift/Kotlin), Business-Logik-Schicht (Java Spring Boot) und Datenschicht (MySQL)."
        """)

    col1, col2 = st.columns([1, 2]) # Eingabe links, Diagramm rechts

    with col1:
        user_input = st.text_area(
            "Deine Systembeschreibung (detailliert!):", 
            height=300,
            placeholder="Beschreibe die Komponenten, Datenbanken, APIs und deren Beziehungen. Füge auch 'Layer' wie 'Frontend-Schicht', 'Business-Logik' oder 'Datenbank-Schicht' hinzu, um die Struktur zu verbessern."
        )
        
        diagram_type = st.selectbox(
            "Gewünschter Diagramm-Typ:",
            ["Flowchart (Flussdiagramm)", "C4-Model (Context/Container/Component)", "Sequence Diagram (Ablauf)"],
            help="C4-Modell ist ideal für Software-Architektur, Flowchart für allgemeine Abläufe."
        )
        
        if diagram_type == "C4-Model (Context/Container/Component)":
            st.info("Für C4-Modelle kann die KI am besten Komponenten und deren Schichten darstellen.")

        generate_btn = st.button("🚀 Architektur generieren", use_container_width=True)

    with col2: # Hier wird das Diagramm erscheinen
        if generate_btn:
            if not user_input:
                st.warning("⚠️ Bitte gib zuerst eine Systembeschreibung ein.")
            else:
                with st.spinner("KI entwirft deine Architektur... dies kann einen Moment dauern."):
                    try:
                        # Verbesserter Prompt für mehr Struktur und Farbe
                        system_prompt = f"""
                        Du bist ein Senior Software Architekt. Erstelle ein {diagram_type} basierend auf der Nutzerbeschreibung.
                        Deine Antwort MUSS NUR den Mermaid.js Code enthalten. KEINE Erklärungen, kein '```mermaid', kein 'Hier ist das Diagramm'.
                        Strukturiere das Diagramm klar in logische Schichten (z.B. Frontend, Backend, Data Layer, Analytics Layer) wie im professionellen Beispielbild.
                        Nutze Subgraphs um Schichten zu gruppieren. Verwende farbige Pfeile (z.B. style fill:#fff,stroke:#3C8CE7,stroke-width:2px;) um verschiedene Datenflüsse zu kennzeichnen.
                        Vermeide Bindestriche in den Knoten-IDs (z.B. 'UserService' statt 'User-Service'). Labels dürfen Leerzeichen enthalten.
                        Priorisiere die Lesbarkeit und professionelle Ästhetik. Verwende 'graph LR' für links-nach-rechts-Layout.
                        """
                        
                        response = client.chat.completions.create(
                            model="gpt-4o", # GPT-4o ist besser für komplexe Anweisungen
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_input}
                            ],
                            temperature=0.4 # Etwas kreativer, um den Stil zu treffen
                        )
                        
                        raw_mermaid_code = response.choices[0].message.content.strip()
                        
                        # Aggressive Reinigung, um Syntaxfehler zu vermeiden
                        clean_mermaid_code = raw_mermaid_code.replace("```mermaid", "").replace("```", "").strip()
                        # Entferne auch überflüssige Anführungszeichen, die Mermaid manchmal stören
                        clean_mermaid_code = re.sub(r'\"([A-Za-z0-9_]+)\"\[', r'\1[', clean_mermaid_code) # Entfernt "ID"[Label]
                        clean_mermaid_code = re.sub(r'\"([A-Za-z0-9_]+)\"-->', r'\1-->', clean_mermaid_code) # Entfernt "ID"-->
                        clean_mermaid_code = re.sub(r'([A-Za-z0-9_]+)\[\"([^\"]+)\"\]', r'\1[\2]', clean_mermaid_code) # Entfernt ID["Label"]

                        # Validierung des Codes
                        if not clean_mermaid_code.startswith(("graph", "sequenceDiagram", "classDiagram", "erDiagram")):
                            st.error("❌ Die KI konnte keinen gültigen Mermaid-Code erstellen. Versuche eine detailliertere oder andere Beschreibung.")
                            st.code(clean_mermaid_code, language="text") # Zeigt den Roh-Output der KI
                        else:
                            st.subheader("Ihre Architektur-Visualisierung:")
                            
                            # HTML/JS Code für Mermaid Rendering
                            mermaid_html = f"""
                            <div class="mermaid" style="background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1); width: 100%; height: auto; overflow: visible;">
                            {clean_mermaid_code}
                            </div>
                            <script type="module">
                                import mermaid from '[https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs](https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs)';
                                mermaid.initialize({{ 
                                    startOnLoad: true, 
                                    theme: 'base', // 'base' ist neutral und lässt mehr Freiheit für eigene Styles
                                    securityLevel: 'loose',
                                    flowchart: {{ useMaxWidth: true, htmlLabels: true, curve: 'linear' }}, // 'linear' für geradere Linien
                                    sequence: {{ use  MaxWidth: true, htmlLabels: true }},
                                    class: {{ useMaxWidth: true, htmlLabels: true }},
                                    er: {{ useMaxWidth: true, htmlLabels: true }}
                                }});
                            </script>
                            """
                            components.html(mermaid_html, height=800, scrolling=True) # Größere Standardhöhe
                            
                            with st.expander("Mermaid Quellcode anzeigen & kopieren"):
                                st.code(clean_mermaid_code, language="mermaid")
                                st.download_button(
                                    label="Mermaid Code herunterladen",
                                    data=clean_mermaid_code,
                                    file_name="architektur.mmd",
                                    mime="text/plain"
                                )

                    except Exception as e:
                        st.error(f"Ein Fehler ist aufgetreten: {e}")
