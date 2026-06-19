from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from support_agent.agent import SupportAgent
from support_agent.config import Settings

# Page configuration
st.set_page_config(page_title="Northstar Support Copilot", page_icon="✦", layout="wide")

# Custom premium CSS styling and font embedding
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    .main .block-container {
        font-family: 'Outfit', sans-serif;
    }
    
    h1 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d0e15;
        border-right: 1px solid #1f2335;
    }
    
    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #1a1b26;
        border: 1px solid #292e42;
        border-radius: 12px;
        padding: 12px;
    }
    
    div[data-testid="stMetricValue"] {
        color: #7aa2f7 !important;
        font-weight: 700;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #7aa2f7, #bb9af7);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(122, 162, 247, 0.4);
        color: #ffffff;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

st.title("Northstar Support Copilot")
st.caption("Persona-aware answers grounded in the product knowledge base")


@st.cache_resource
def get_agent() -> SupportAgent:
    from dotenv import load_dotenv
    import os
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env", override=True)
    settings = Settings.from_env(root)
    settings.llm_provider = "gemini"  # FORCE GEMINI
    agent = SupportAgent(settings)
    if agent.store.count() == 0:
        agent.ingest()
    return agent


agent = get_agent()

# Correctly persist conversation history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []


def render_assistant_message(msg: dict):
    # Main LLM Text response
    st.markdown(msg["response"])
    
    # Metadata columns
    c1, c2 = st.columns(2)
    
    persona = msg["persona"]
    conf = msg["persona_confidence"]
    
    # Style persona tag color
    if persona == "Technical Expert":
        badge_bg = "rgba(66, 135, 245, 0.15)"
        badge_border = "rgba(66, 135, 245, 0.4)"
        badge_text = "#4287f5"
    elif persona == "Frustrated User":
        badge_bg = "rgba(239, 68, 68, 0.15)"
        badge_border = "rgba(239, 68, 68, 0.4)"
        badge_text = "#ef4444"
    else: # Business Executive
        badge_bg = "rgba(139, 92, 246, 0.15)"
        badge_border = "rgba(139, 92, 246, 0.4)"
        badge_text = "#8b5cf6"
        
    c1.markdown(
        f'<div style="background-color: {badge_bg}; color: {badge_text}; border: 1px solid {badge_border}; '
        f'padding: 6px 12px; border-radius: 12px; font-weight: 600; text-align: center; font-size: 0.85rem; line-height: 1.2; display: inline-block; width: 100%;">'
        f'👤 Persona: {persona} ({conf:.0%})</div>',
        unsafe_allow_html=True
    )
    
    if msg["escalation_status"]:
        c2.markdown(
            f'<div style="background-color: rgba(249, 115, 22, 0.15); color: #f97316; border: 1px solid rgba(249, 115, 22, 0.4); '
            f'padding: 6px 12px; border-radius: 12px; font-weight: 600; text-align: center; font-size: 0.85rem; line-height: 1.2; display: inline-block; width: 100%;">'
            f'🚨 Escalated to Human</div>',
            unsafe_allow_html=True
        )
    else:
        c2.markdown(
            f'<div style="background-color: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.4); '
            f'padding: 6px 12px; border-radius: 12px; font-weight: 600; text-align: center; font-size: 0.85rem; line-height: 1.2; display: inline-block; width: 100%;">'
            f'✅ Auto-Resolved</div>',
            unsafe_allow_html=True
        )

    # Retrieved sources
    if msg.get("retrieved"):
        with st.expander("🔍 Retrieved sources"):
            for item in msg["retrieved"]:
                st.markdown(f"- **{item['citation']}** — score `{item['score']:.3f}`")
                
    # Human Handoff Summary
    handoff = msg.get("handoff_summary")
    if handoff:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        reasons_list = "".join(f"<li>{r}</li>" for r in handoff.get("escalation_reasons", []))
        docs_list = "".join(f"<li>{d}</li>" for d in handoff.get("documents_used", []))
        
        handoff_html = f"""
        <div style="background: linear-gradient(145deg, #161821, #0f111a); border: 1px solid rgba(249, 115, 22, 0.5); 
                    border-radius: 16px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.4); color: #c0caf5; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; border-bottom: 1px solid rgba(249, 115, 22, 0.2); padding-bottom: 12px; margin-bottom: 15px;">
                <span style="font-size: 1.4rem; margin-right: 10px;">🚨</span>
                <h4 style="margin: 0; color: #f97316; font-size: 1.1rem; font-weight: 700; letter-spacing: 0.5px; font-family: 'Outfit', sans-serif;">HUMAN HANDOFF TICKET</h4>
            </div>
            
            <div style="margin-bottom: 14px;">
                <strong style="color: #565f89; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;">Customer Issue:</strong>
                <p style="margin: 4px 0 0 0; font-size: 0.95rem; color: #bb9af7; font-style: italic;">"{handoff.get('issue')}"</p>
            </div>
            
            <div style="margin-bottom: 14px; background-color: rgba(247, 118, 142, 0.1); border-left: 4px solid #f7768e; padding: 8px 12px; border-radius: 4px;">
                <strong style="color: #f7768e; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;">Escalation Reasons:</strong>
                <ul style="margin: 4px 0 0 0; padding-left: 20px; font-size: 0.9rem; color: #f7768e; line-height: 1.4;">
                    {reasons_list}
                </ul>
            </div>
            
            <div style="margin-bottom: 14px;">
                <strong style="color: #565f89; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;">Retrieved Reference Material:</strong>
                <ul style="margin: 4px 0 0 0; padding-left: 20px; font-size: 0.9rem; color: #7aa2f7; line-height: 1.4;">
                    {docs_list}
                </ul>
            </div>
            
            <div style="margin-bottom: 5px;">
                <strong style="color: #565f89; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;">Recommended Next Steps:</strong>
                <p style="margin: 4px 0 0 0; font-size: 0.95rem; color: #9ece6a; font-weight: 500;">
                    👉 {handoff.get('recommended_next_steps')}
                </p>
            </div>
        </div>
        """
        st.markdown(handoff_html, unsafe_allow_html=True)
        with st.expander("📋 Copy raw handoff JSON data"):
            st.json(handoff)


with st.sidebar:
    st.header("System")
    st.metric("Indexed chunks", agent.store.count())
    
    options = ["openai", "gemini", "template", "ollama"]
    current_index = options.index(agent.settings.llm_provider) if agent.settings.llm_provider in options else 0
    provider = st.selectbox("LLM Provider", options, index=current_index)
    if provider != agent.settings.llm_provider:
        agent.update_generator(provider)
        st.rerun()

    if st.button("Reset conversation", use_container_width=True):
        agent.reset()
        st.session_state.messages = []
        st.rerun()

# Render all messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            render_assistant_message(message)

# Handle new user input
if prompt := st.chat_input("Describe the support issue…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        result = agent.ask(prompt)
        msg_dict = {
            "role": "assistant",
            "response": result.response,
            "persona": result.persona.value,
            "persona_confidence": result.persona_confidence,
            "escalation_status": result.escalation_status,
            "escalation_reasons": result.escalation_reasons,
            "retrieved": [{"citation": item.chunk.citation, "score": item.score} for item in result.retrieved],
            "handoff_summary": result.handoff_summary,
        }
        render_assistant_message(msg_dict)
    st.session_state.messages.append(msg_dict)

