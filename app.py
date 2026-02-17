import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components

# 1. Konfiguration (Muss ganz oben stehen)
st.set_page_config(page_title="AI Architect", layout="wide")

# 2. Key aus den Secrets laden
api_key = st.secrets.get("OPENAI_API_KEY")

st.title("🏗️ AI Software Architecture Designer")

if not api_key:
    st.error("Bitte OPENAI_API_KEY in den Streamlit Secrets hinterlegen!")
else:
    client = OpenAI(api_key=api_key)
    
    user_input = st.text_area("Beschreibung:", placeholder="Z.B. Webshop mit SQL Datenbank...")
    
    if st.button("🚀 Architektur generieren"):
        with st.spinner("KI arbeitet..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Erstelle NUR Mermaid.js Code (graph TD...). Kein Text davor/danach."},
                        {"role": "user", "content": user_input}
                    ]
                )
                mermaid_code = response.choices[0].message.content.strip().replace("```mermaid", "").replace("```", "")
                
                # Sichereres Rendering-Format
                html_layout = f"""
                <pre class="mermaid">
                    {mermaid_code}
                </pre>
                <script type="module">
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                    mermaid.initialize({{ startOnLoad: true, theme: 'forest' }});
                </script>
                """
                components.html(html_layout, height=600, scrolling=True)
                
            except Exception as e:
                st.error(f"Fehler: {e}")
