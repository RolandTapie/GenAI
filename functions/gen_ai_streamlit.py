import streamlit as st
from datetime import datetime
import html as pyhtml
import requests


from llm import model
from rag import RagModel

document= r"C:\Users\tallar\Downloads\Famille bamendjou de liege-20250801T201343Z-1-001\Famille bamendjou de liege\ARESBAL_ ROI et statut.pdf"

def rag_api(host,port,root,question):
    print(f"http://{host}:{port}/{root}?request={question}")
    response = requests.post(f"http://{host}:{port}/{root}?request={question}")
    print(response.text)
    return response.text

# --- Initialisation unique des modèles ---
if "gen_model" not in st.session_state:
    with st.spinner("Initialisation du modèle génératif..."):
        st.session_state.gen_model = model("openai")
    st.success("Modèle génératif ✅")

# if "rag" not in st.session_state:
#     with st.spinner("Initialisation du modèle RAG..."):
#         st.session_state.rag = RagModel(
#             document,
#             "Mistral",
#             "text-embedding-3-small"
#         )
#     st.success("Modèle RAG prêt ✅")

gen_model = st.session_state.gen_model
#rag = st.session_state.rag

st.set_page_config(page_title="Chatbot RAG - Ville de Liège", page_icon="💬", layout="centered")

CSS = """
<style>
/* Background gradient */
.stApp {
    min-height: 100vh;
    background: linear-gradient(135deg, #004e92 0%, #004e92 60%, #c0c0c0 85%, #ffd700 100%);
    background-attachment: fixed;
    font-family: 'Inter', 'Arial', sans-serif;
}

/* Wrapper that centers the chat */
.chat-wrapper{
    width: 85%;
    max-width: 1100px;
    margin: 30px auto;
}

/* Header */
.chat-header {
    text-align: center;
    color: #ffffff;
    margin-bottom: 10px;
}

/* Chat area: scrollable box */
.chat-area {
    background: rgba(255,255,255,0.06);
    padding: 20px;
    border-radius: 14px;
    max-height: 64vh;
    overflow-y: auto;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}

/* Message row */
.message-row {
    display: flex;
    margin: 12px 0;
    align-items: flex-end;
}
.message-row.bot { justify-content: flex-start; }
.message-row.user { justify-content: flex-end; }

/* Avatar (optional small circle) */
.avatar {
    width:36px;
    height:36px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    margin: 0 10px;
    font-size:18px;
}

/* Bubble */
.bubble {
    padding: 12px 16px;
    border-radius: 16px;
    max-width: 70%;
    box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    line-height: 1.4;
    word-wrap: break-word;
}
.bubble.bot {
    background: #fff3cd;
    color: #222;
    border-bottom-left-radius: 4px;
}
.bubble.user {
    background: #d1e7ff;
    color: #02203a;
    border-bottom-right-radius: 4px;
}

/* Input card area */
.input-card {
    margin-top: 16px;
    padding: 16px;
    border-radius: 10px;
    background: rgba(255,255,255,0.9);
}

/* Make sure streamlit internal paddings don't break layout */
.block-container {
    padding-top: 10px;
    padding-bottom: 30px;
}

/* Responsive */
@media (max-width: 700px) {
    .chat-wrapper { width: 95%; }
    .bubble { max-width: 85%; }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# --- Session state pour l'historique
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "content": "Bonjour 👋 — je suis un chatbot, comment puis je vous aider?"}
    ]


def render_chat_html(messages):
    """Construit un unique bloc HTML pour la zone de chat."""
    html_parts = []
    html_parts.append("<div class='chat-wrapper'>")
    html_parts.append(f"<div class='chat-header'><h2 style='margin:6px 0 0 0;'>💬 Chatbot RAG - {document}Frontend</h2>")
    html_parts.append("<div style='color:rgba(255,255,255,0.9); font-size:14px;'>Prototype (sans LLM) — réponses = question pour tests</div></div>")
    html_parts.append("<div class='chat-area'>")

    for msg in messages:
        safe = pyhtml.escape(msg["content"]).replace("\n", "<br>")
        if msg["role"] == "user":
            # bulle à droite
            html_parts.append(
                f"<div class='message-row user'>"
                f"<div class='bubble user'>🧑‍&nbsp;&nbsp;{safe}</div>"
                f"</div>"
            )
        else:
            # bulle à gauche
            html_parts.append(
                f"<div class='message-row bot'>"
                f"<div class='bubble bot'>🤖&nbsp;&nbsp;{safe}</div>"
                f"</div>"
            )

    html_parts.append("</div>")  # fin chat-area
    html_parts.append("</div>")  # fin wrapper
    return "\n".join(html_parts)

# --- Affiche l'historique dans un seul st.markdown
chat_html = render_chat_html(st.session_state.messages)
st.markdown(chat_html, unsafe_allow_html=True)

# --- Formulaire d'entrée (centré)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Votre message :")
    submitted = st.form_submit_button("Envoyer")

    if submitted and user_input and user_input.strip():
        # Ajouter message utilisateur
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        # Simuler réponse identique à la question (pour test)
        with st.spinner("Le bot réfléchit... 🧠💭"):
            query=user_input.strip()
            context = rag_api("localhost",8000,"/query",query)
            print(context)
            gen_model.set_context(context)
        st.session_state.messages.append({"role": "bot", "content": gen_model.ask(query,"Mistral")})
        # relancer pour rafraîchir (nouvelle méthode)
        st.rerun()

# --- Footer
st.markdown("---")
st.caption(f"Prototype d'interface - {datetime.now().strftime('%d/%m/%Y')}")
