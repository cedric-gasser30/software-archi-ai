import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components
import re

# --- SETUP ---
st.set_page_config(page_title="AI Architecture Designer", page_icon="🏗️", layout="wide")

# Login Logik (Passwort aus Secrets)
def check_password():
    if "password_correct" not in st.session_state:
        st.text_input("Passwort:", type="password", key="password", 
                     on_change=lambda: st.session_state.update({"password_correct": st.session_state.password == st.secrets.get("APP_PASSWORD", "admin")}))
        return False
    return st.session_state["password_correct"]

if check_password():
    api_key = st.secrets.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) if api_key else None

    st.title("🏗️ AI Software Architecture Designer")

    user_input = st.text_area("Systembeschreibung:", height=200, placeholder="Trikot-Shop...")

    if st.button("🚀 Architektur generieren"):
        if not client:
            st.error("API Key fehlt!")
        else:
            with st.spinner("KI generiert Architektur..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Du bist ein Software-Architekt. Erstelle NUR Mermaid.js Code (graph TD). Benutze KEINE Sonderzeichen wie ' oder - in den IDs. Nutze einfache Namen wie OrderService statt Order-Service. Antworte NUR mit dem Code."},
                            {"role": "user", "content": user_input}
                        ]
                    )
                    
                    # 1. Rohcode holen
                    code = response.choices[0].message.content.strip()
                    
                    # 2. Markdown-Boxen entfernen
                    code = code.replace("```mermaid", "").replace("```", "").strip()
                    
                    # 3. Aggressive Reinigung für Mermaid-Syntax (Verhindert den Syntax Error)
                    # Wir entfernen Bindestriche in den IDs, da Mermaid diese oft nicht mag
                    code = re.sub(r'([a-zA-Z0-9]+)-([a-zA-Z0-9]+)', r'\1\2', code)

                    # HTML Template mit Fehler-Fallback
                    html_code = f"""
                    <div class="mermaid">
                    {code}
                    </div>
                    <script type="module">
                        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                        try {{
                            mermaid.initialize({{ startOnLoad: true, theme: 'neutral', securityLevel: 'loose' }});
                        }} catch (e) {{
                            document.write("Fehler beim Zeichnen: " + e.message);
                        }}
                    </script>
                    """
                    
                    st.subheader("Visualisierung")
                    components.html(html_code, height=800, scrolling=True)
                    
                    with st.expander("Mermaid Code kopieren"):
                        st.code(code)

                except Exception as e:
                    st.error(f"Technischer Fehler: {e}")
