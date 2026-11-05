from uuid import uuid4
from textwrap import dedent, indent

import streamlit as st

from lead_qualification_workflow import graph
from qualifying import (
    VISITOR_FIELDS,
    get_missing_fields,
    initial_state,
    is_valid_contact,
)

WELCOME_MESSAGE = (
    "Hi! I’m TechNova’s virtual assistant. Tell me what you’re looking to build, "
    "and I’ll guide you through a few details."
)


def reset_conversation():
    st.session_state.thread_id = str(uuid4())
    st.session_state.started = False
    st.session_state.chat_history = [
        {"role": "assistant", "content": WELCOME_MESSAGE}
    ]
    st.session_state.lead = {field: None for field in VISITOR_FIELDS}
    st.session_state.deferred_fields = []


st.set_page_config(
    page_title="Nova | TechNova Project Assistant",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "thread_id" not in st.session_state:
    reset_conversation()

hero_html = ""
if not st.session_state.started:
    hero_html = """
    <section class="nova-hero">
      <div class="nova-hero-content">
        <div class="nova-eyebrow">Project consultation</div>
        <h1>Turn your idea into a clear next step.</h1>
        <p>Tell Nova what you're trying to build. I’ll help you explore the right service and next steps.</p>
        <div class="nova-hero-actions">
          <span class="nova-pill">✦ Explore services</span>
          <span class="nova-pill">✦ Discuss your project</span>
          <span class="nova-pill">✦ Talk to our team</span>
        </div>
      </div>
      <div class="nova-hero-art" aria-hidden="true">
        <svg width="76" height="76" viewBox="0 0 82 82" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M41 5L49.7 32.3L77 41L49.7 49.7L41 77L32.3 49.7L5 41L32.3 32.3L41 5Z" fill="url(#novaGradient)"/>
          <circle cx="65" cy="18" r="5" fill="#fff" fill-opacity="0.9"/>
          <circle cx="18" cy="63" r="4" fill="#C7D2FE"/>
          <defs>
            <linearGradient id="novaGradient" x1="18" y1="10" x2="66" y2="71" gradientUnits="userSpaceOnUse">
              <stop stop-color="#FFFFFF"/>
              <stop offset="1" stop-color="#A5B4FC"/>
            </linearGradient>
          </defs>
        </svg>
      </div>
    </section>
    """

theme_palette = {
    "bg": "#070b14",
    "bg_alt": "#0f172a",
    "surface": "#111b2e",
    "surface_soft": "#1a243b",
    "panel": "#0c1322",
    "text": "#edf4ff",
    "muted": "#94a3b8",
    "primary": "#7c6cff",
    "primary_soft": "rgba(124, 108, 255, 0.14)",
    "accent": "#38bdf8",
    "success": "#34d399",
    "shadow": "rgba(15, 23, 42, 0.45)",
}
theme_css_override = f"""
:root, .stApp, [data-testid="stAppViewContainer"] {{
    color-scheme: dark;
    --bg: {theme_palette['bg']} !important;
    --bg-alt: {theme_palette['bg_alt']} !important;
    --surface: {theme_palette['surface']} !important;
    --surface-soft: {theme_palette['surface_soft']} !important;
    --panel: {theme_palette['panel']} !important;
    --text: {theme_palette['text']} !important;
    --muted: {theme_palette['muted']} !important;
    --primary: {theme_palette['primary']} !important;
    --primary-soft: {theme_palette['primary_soft']} !important;
    --accent: {theme_palette['accent']} !important;
    --success: {theme_palette['success']} !important;
    --shadow: {theme_palette['shadow']} !important;
}}
"""
theme_css_override = indent(theme_css_override.strip(), "    ")

# Custom CSS for the dark theme, hidden headers/footers, and creative styling
st.markdown(
    dedent(f"""
    <style>
    {theme_css_override}

    #MainMenu, header[data-testid="stHeader"], footer,
    [data-testid="stDecoration"], [data-testid="stToolbar"],
    [data-testid="stStatusWidget"] {{
        display:none !important; visibility:hidden !important;
    }}
    .block-container {{
        max-width: 1040px;
        padding: 1rem 1.25rem 6rem !important;
    }}
    .stApp, [data-testid="stAppViewContainer"] {{
        color: var(--text);
        background: radial-gradient(circle at top left, rgba(124, 108, 255, 0.18), transparent 28%),
                    radial-gradient(circle at bottom right, rgba(56, 189, 248, 0.18), transparent 32%),
                    var(--bg);
    }}
    .nova-topbar {{
        display: flex; align-items: center; justify-content: space-between;
        gap: 1rem; padding: 0.2rem 0 0.75rem; margin-bottom: 0.75rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.18);
    }}
    .nova-brand {{ display: flex; align-items: center; gap: 0.8rem; }}
    .nova-logo {{
        width: 42px; height: 42px; display: grid; place-items: center;
        border-radius: 14px; color: white; font-weight: 800;
        background: linear-gradient(135deg, #7c6cff 0%, #38bdf8 100%);
        box-shadow: 0 14px 26px rgba(124, 108, 255, 0.3);
    }}
    .nova-brand-name {{ font-size: 1.08rem; font-weight: 800; color: var(--text); }}
    .nova-brand-sub {{ font-size: 0.72rem; color: var(--muted); }}
    .nova-online {{
        display: inline-flex; align-items: center; gap: 0.55rem;
        padding: 0.42rem 0.8rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700;
        background: rgba(52, 211, 153, 0.12); color: var(--success);
        border: 1px solid rgba(52, 211, 153, 0.22);
    }}
    .nova-online-dot {{ width: 7px; height: 7px; border-radius: 50%; background: var(--success); }}

    .nova-hero {{
        position: relative; overflow: hidden; display: flex; align-items: center; justify-content: space-between;
        gap: 1.25rem; min-height: 180px; padding: 1.5rem 1.8rem; margin-bottom: 1rem;
        border-radius: 28px; border: 1px solid rgba(148, 163, 184, 0.18);
        background: linear-gradient(135deg, #0b1429 0%, #16213c 32%, #1d1b40 100%);
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.28);
    }}
    .nova-hero::before,
    .nova-hero::after {{
        content: ""; position: absolute; border-radius: 50%;
        background: rgba(255, 255, 255, 0.06); filter: blur(10px);
    }}
    .nova-hero::before {{ width: 190px; height: 190px; top: -45px; right: 14%; }}
    .nova-hero::after {{ width: 240px; height: 240px; bottom: -90px; right: 3%; }}
    .nova-hero-content {{ position: relative; z-index: 2; max-width: 760px; }}
    .nova-eyebrow {{
        margin-bottom: 0.65rem; color: #c7d2fe; text-transform: uppercase; letter-spacing: 0.18em;
        font-size: 0.66rem; font-weight: 800;
    }}
    .nova-hero h1 {{
        margin: 0; color: #f8fbff !important; font-size: clamp(2rem, 4vw, 3rem);
        line-height: 1.05; letter-spacing: -0.06em; font-weight: 900;
    }}
    .nova-hero p {{
        margin: 0.9rem 0 0; max-width: 640px; color: #d4deef; font-size: 0.97rem; line-height: 1.7;
    }}
    .nova-hero-actions {{ display: flex; flex-wrap: wrap; gap: 0.7rem; margin-top: 1.2rem; }}
    .nova-pill {{
        display: inline-flex; align-items: center; gap: 0.5rem; border-radius: 999px; padding: 0.5rem 0.8rem;
        font-size: 0.74rem; font-weight: 700; color: white; border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.06); backdrop-filter: blur(8px);
    }}
    .nova-hero-art {{
        position: relative; z-index: 2; display: grid; place-items: center; width: 170px; height: 170px;
        flex-shrink: 0; border-radius: 32px; background: linear-gradient(135deg, rgba(124,108,255,.18), rgba(56,189,248,.14));
        border: 1px solid rgba(255,255,255,.12); box-shadow: inset 0 1px 0 rgba(255,255,255,.18);
    }}
    .nova-section-head {{ margin: 0.8rem 0 0.65rem; }}
    .nova-kicker {{
        color: var(--primary); font-size: 0.66rem; font-weight: 800; letter-spacing: 0.16em;
        text-transform: uppercase;
    }}
    .nova-section-title {{ font-size: 1.05rem; font-weight: 800; color: var(--text); margin-top: 0.32rem; }}
    .nova-card {{
        min-height: 118px; padding: 0.9rem 0.9rem; border-radius: 18px; border: 1px solid rgba(148,163,184,.15);
        background: linear-gradient(180deg, var(--surface) 0%, color-mix(in srgb, var(--surface) 92%, var(--bg)) 100%);
        box-shadow: 0 10px 26px var(--shadow); transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
    }}
    .nova-card:hover {{ transform: translateY(-2px); border-color: rgba(124,108,255,.4); box-shadow: 0 14px 32px var(--shadow); }}
    .nova-card-icon {{
        width: 38px; height: 38px; display: grid; place-items: center; border-radius: 12px;
        background: var(--primary-soft); color: var(--primary); margin-bottom: 0.8rem;
    }}
    .nova-card-icon svg {{ width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }}
    .nova-card strong {{ display: block; margin-bottom: 0.35rem; font-size: 0.92rem; color: var(--text); }}
    .nova-card span {{ font-size: 0.77rem; line-height: 1.55; color: var(--muted); }}

    [data-testid="stChatMessage"] {{
        align-items: center !important;
        border-radius: 18px !important; padding: 0.95rem 1rem !important; margin-bottom: 0.8rem !important;
        border: 1px solid rgba(148, 163, 184, 0.16) !important; background: var(--surface) !important;
        box-shadow: 0 8px 20px var(--shadow);
    }}
    [data-testid="stChatMessageContent"] {{
        align-self: stretch !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        min-width: 0;
    }}
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {{
        margin: 0 !important;
    }}
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {{
        margin: 0 !important; color: var(--text) !important; font-size: 0.92rem; line-height: 1.65;
    }}
    [data-testid="stChatMessage"][data-testid="chatMessageUser"] {{
        background: rgba(124,108,255,0.08) !important; border-left: 3px solid var(--primary) !important;
    }}
    [data-testid="stChatMessage"][data-testid="chatMessageAssistant"] {{
        background: rgba(56,189,248,0.06) !important; border-left: 3px solid var(--accent) !important;
    }}
    [data-testid="stChatInput"] {{
        border-radius: 18px !important; border: 1px solid rgba(148,163,184,.18) !important;
        background: var(--surface) !important; box-shadow: 0 8px 26px var(--shadow) !important;
    }}
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] textarea:focus {{
        background: var(--surface) !important; color: var(--text) !important;
    }}
    [data-testid="stChatInput"]:focus-within {{ border-color: var(--primary) !important; box-shadow: 0 0 0 4px rgba(124,108,255,.12) !important; }}
    [data-testid="stChatInput"] textarea {{ font-size: 0.92rem; }}
    div[data-testid="stBottom"], div[data-testid="stBottom"] > div {{ background: transparent !important; }}

    .stButton > button {{
        background: var(--surface-soft); color: var(--text); border: 1px solid rgba(148,163,184,.2);
        border-radius: 12px; font-weight: 700; box-shadow: none; transition: background .2s ease, border-color .2s ease;
    }}
    .stButton > button:hover {{ background: var(--surface); border-color: var(--primary); color: var(--text); }}
    .chat-heading {{ font-size: 1.05rem; font-weight: 800; color: var(--text); }}
    .chat-subheading {{ color: var(--muted); font-size: 0.82rem; margin-top: 0.15rem; }}
    @media (max-width: 640px) {{
        .block-container {{ padding: 1rem 0.8rem 5rem !important; }}
        .nova-hero {{ padding: 1.2rem 1.1rem; min-height: 150px; }}
        .nova-hero-art {{ display: none; }}
        .nova-topbar {{ flex-wrap: wrap; }}
        .nova-brand-sub {{ display: none; }}
    }}
    </style>

    <div class="nova-topbar">
      <div class="nova-brand">
        <div class="nova-logo">N</div>
        <div>
          <div class="nova-brand-name">TechNova</div>
          <div class="nova-brand-sub">AI project consultation</div>
        </div>
      </div>
      <div class="nova-online"><span class="nova-online-dot"></span>Nova is online</div>
    </div>

    {hero_html}
    """),
    unsafe_allow_html=True,
)

# Starter Suggestion Cards shown before conversation initiates
if not st.session_state.started:
    st.markdown(
        """
        <div class="nova-section-head">
            <div class="nova-kicker">GET STARTED</div>
            <div class="nova-section-title">You can start with anything about your project</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    help_columns = st.columns(3)
    help_cards = [
        (
            '<svg viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="14" rx="2.5"/><path d="M3.5 9h17M8 5v4m8-4v4"/></svg>',
            "Explore services",
            "Ask which service fits your idea, such as websites, apps, software, or automation.",
        ),
        (
            '<svg viewBox="0 0 24 24"><path d="M12 3.5a6.5 6.5 0 0 0-3.8 11.8c.7.5 1.1 1.2 1.2 2h5.2c.1-.8.5-1.5 1.2-2A6.5 6.5 0 0 0 12 3.5Z"/><path d="M9.5 20.5h5"/></svg>',
            "Shape your idea",
            "Describe what you want to build or improve, even if the requirements are not final yet.",
        ),
        (
            '<svg viewBox="0 0 24 24"><path d="M4 5.5h16v13H4z"/><path d="m8 10 2.5 2L8 14m5-4h3"/></svg>',
            "Get a project estimate",
            "Share your budget and timeline when you’re ready, and Nova will capture them.",
        ),
    ]
    for column, (icon, title, description) in zip(help_columns, help_cards):
        with column:
            st.markdown(
                f'<div class="nova-card"><div class="nova-card-icon">{icon}</div>'
                f'<strong>{title}</strong><span>{description}</span></div>',
                unsafe_allow_html=True,
            )
    st.markdown('<div style="height:.8rem"></div>', unsafe_allow_html=True)

if st.session_state.started:
    heading, action = st.columns([5, 1])
    with heading:
        st.markdown(
            '<div class="chat-heading">Your conversation</div>'
            '<div class="chat-subheading">Ask a question or tell us about your project.</div>',
            unsafe_allow_html=True,
        )
    with action:
        st.button("New chat", on_click=reset_conversation, use_container_width=True)
else:
    st.markdown(
        '<div class="chat-heading">Chat with Nova</div>'
        '<div class="chat-subheading">Ask a question or tell us about your project.</div>',
        unsafe_allow_html=True,
    )

# Chat conversation display
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input Handling
missing_fields = get_missing_fields(
    {
        **st.session_state.lead,
        "deferred_fields": st.session_state.deferred_fields,
    }
)
waiting_for_contact = bool(missing_fields and missing_fields[0] == "contact")
placeholder = (
    "Enter an email address or phone number"
    if waiting_for_contact
    else "Message TechNova..."
)

prompt = st.chat_input(placeholder)
if prompt:
    if waiting_for_contact and "?" not in prompt and not is_valid_contact(prompt):
        st.error("Enter a valid email address or phone number (7–15 digits).")
    else:
        is_first_message = not st.session_state.started
        graph_input = (
            {**initial_state, "messages": [("human", prompt)]}
            if is_first_message
            else {"messages": [("human", prompt)]}
        )
        result = graph.invoke(
            graph_input,
            {"configurable": {"thread_id": st.session_state.thread_id}},
        )

        assistant_reply = result["messages"][-1].content
        st.session_state.chat_history.extend(
            [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": assistant_reply},
            ]
        )
        st.session_state.started = True
        st.session_state.lead = {
            field: result[field] for field in VISITOR_FIELDS
        }
        st.session_state.deferred_fields = result["deferred_fields"]
        st.rerun()