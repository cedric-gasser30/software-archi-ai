import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components

# 1. Konfiguration
st.set_page_config(page_title="AI Software Architect", page_icon="🏗️", layout="wide")

# 2. Key aus den Streamlit Secrets laden
api_key = st.secrets.get("OPENAI_API_KEY")

st.title("🏗️ AI Software Architecture Designer")
st.write("Generiere saubere Mermaid.js Diagramme aus deiner Beschreibung.")

if not api_key:
    st.error("❌ Fehler: Kein API-Key gefunden. Bitte füge 'OPENAI_API_KEY' in den Streamlit Secrets hinzu.")
else:
    client = OpenAI(api_key=api_key)
    
    # Eingabebereich
    user_input = st.text_area(
        "Systembeschreibung (z.B. Trikot-Webshop):", 
        height=200,
        placeholder="Beschreibe Services, Datenbanken und Verbindungen..."
    )
    
    if st.button("🚀 Architektur generieren"):
        if not user_input:
            st.warning("Bitte gib zuerst eine Beschreibung ein.")
        else:
            with st.spinner("KI generiert das Diagramm..."):
                try:
                    # Der Prompt zwingt die KI zur Reinheit des Codes
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Du bist ein Senior Software Architekt. Erstelle NUR Mermaid.js Code (startend mit graph TD). Gib KEINEN Text davor oder danach aus. Benutze keine Markdown-Code-Blocks (```)."},
                            {"role": "user", "content": user_input}
                        ],
                        temperature=0.1
                    )
                    
                    # Code säubern: Falls die KI doch Backticks liefert, werden sie hier entfernt
                    mermaid_code = response.choices[0].message.content.strip()
                    mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()

                    # Validierung
                    if not mermaid_code.startswith(("graph", "sequenceDiagram", "classDiagram", "erDiagram")):
                        st.error("Die KI hat keinen gültigen Diagramm-Code geliefert. Versuche es mit einer genaueren Beschreibung.")
                    else:
                        st.subheader("Visualisierung:")
                        
                        # Das HTML-Template für das Rendering
                        html_code = f"""
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
                        components.html(html_code, height=600, scrolling=True)
                        
                        with st.expander("Mermaid Quellcode anzeigen (für Notion/GitHub)"):
                            st.code(mermaid_code, language="mermaid")

                except Exception as e:
                    st.error(f"Ein technischer Fehler ist aufgetreten: {e}")
