import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components

# --- 1. SETUP ---
st.set_page_config(page_title="Secure AI Architect", page_icon="🔒", layout="wide")

# --- 2. LOGIN LOGIK ---
def check_password():
    """Gibt True zurück, wenn das Passwort korrekt ist."""
    def password_entered():
        if st.session_state["password"] == st.secrets.get("APP_PASSWORD", "admin"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Passwort nicht im State lassen
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Erstes Mal: Passwort abfragen
        st.text_input("Bitte gib das Passwort ein, um die Architektur-KI zu nutzen:", 
                     type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Falsches Passwort
        st.text_input("Passwort falsch. Bitte erneut versuchen:", 
                     type="password", on_change=password_entered, key="password")
        st.error("😕 Zugriff verweigert.")
        return False
    else:
        # Passwort korrekt
        return True

# Nur fortfahren, wenn der Login erfolgreich war
if check_password():
    
    # --- 3. DIE EIGENTLICHE APP ---
    api_key = st.secrets.get("OPENAI_API_KEY")
    
    st.title("🏗️ AI Software Architecture Designer")
    st.sidebar.success("🔒 Du bist eingeloggt")
    
    if st.sidebar.button("Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

    if not api_key:
        st.error("❌ API-Key fehlt in den Secrets!")
    else:
        client = OpenAI(api_key=api_key)
        
        user_input = st.text_area("Systembeschreibung:", placeholder="z.B. Webshop Architektur...")
        
        if st.button("🚀 Architektur generieren"):
            with st.spinner("KI generiert Architektur..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Erstelle NUR Mermaid.js Code (graph TD...). Kein Text drumherum."},
                            {"role": "user", "content": user_input}
                        ]
                    )
                    mermaid_code = response.choices[0].message.content.strip().replace("```mermaid", "").replace("```", "")
                    
                    html_code = f"""
                    <div class="mermaid" style="display: flex; justify-content: center;">{mermaid_code}</div>
                    <script type="module">
                        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                        mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
                    </script>
                    """
                    components.html(html_code, height=600, scrolling=True)
                except Exception as e:
                    st.error(f"Fehler: {e}")
