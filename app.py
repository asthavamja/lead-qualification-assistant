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

FIELD_LABELS = {
    "service_name": "Service",
    "summary_of_product": "Project",
    "budget": "Budget",
    "timeline_months": "Timeline",
    "decision_maker": "Decision-maker",
    "name": "Name",
    "contact": "Contact",
}


def reset_conversation():
    st.session_state.thread_id = str(uuid4())
    st.session_state.started = False
    st.session_state.chat_history = [
        {"role": "assistant", "content": WELCOME_MESSAGE}
    ]
    st.session_state.lead = {field: None for field in VISITOR_FIELDS}
    st.session_state.deferred_fields = []
    st.session_state.score = None
    st.session_state.handoff_flag = False


st.set_page_config(
    page_title="Nova | TechNova Project Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "thread_id" not in st.session_state:
    reset_conversation()

# Theme-specific variable overrides based on user choice

def get_theme_palette(theme_mode):
    if theme_mode == "Dark":
        return {
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
    if theme_mode == "Light":
        return {
            "bg": "#f4f7ff",
            "bg_alt": "#eef2ff",
            "surface": "#ffffff",
            "surface_soft": "#f3f6ff",
            "panel": "#f8faff",
            "text": "#111827",
            "muted": "#5b6475",
            "primary": "#4f46e5",
            "primary_soft": "rgba(79, 70, 229, 0.12)",
            "accent": "#0ea5e9",
            "success": "#10b981",
            "shadow": "rgba(99, 102, 241, 0.12)",
        }
    return {
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


theme_palette = get_theme_palette("Dark")
theme_css_override = f"""
:root, .stApp, [data-testid="stAppViewContainer"] {{
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
section[data-testid="stSidebar"] {{ background: var(--panel) !important; }}
@media (prefers-color-scheme: light) {{
    .stApp, [data-testid="stAppViewContainer"] {{
        --bg: {get_theme_palette('Light')['bg']} !important;
        --bg-alt: {get_theme_palette('Light')['bg_alt']} !important;
        --surface: {get_theme_palette('Light')['surface']} !important;
        --surface-soft: {get_theme_palette('Light')['surface_soft']} !important;
        --panel: {get_theme_palette('Light')['panel']} !important;
        --text: {get_theme_palette('Light')['text']} !important;
        --muted: {get_theme_palette('Light')['muted']} !important;
        --primary: {get_theme_palette('Light')['primary']} !important;
        --primary-soft: {get_theme_palette('Light')['primary_soft']} !important;
        --accent: {get_theme_palette('Light')['accent']} !important;
        --success: {get_theme_palette('Light')['success']} !important;
        --shadow: {get_theme_palette('Light')['shadow']} !important;
    }}
}}
@media (prefers-color-scheme: dark) {{
    .stApp, [data-testid="stAppViewContainer"] {{
        --bg: {get_theme_palette('Dark')['bg']} !important;
        --bg-alt: {get_theme_palette('Dark')['bg_alt']} !important;
        --surface: {get_theme_palette('Dark')['surface']} !important;
        --surface-soft: {get_theme_palette('Dark')['surface_soft']} !important;
        --panel: {get_theme_palette('Dark')['panel']} !important;
        --text: {get_theme_palette('Dark')['text']} !important;
        --muted: {get_theme_palette('Dark')['muted']} !important;
        --primary: {get_theme_palette('Dark')['primary']} !important;
        --primary-soft: {get_theme_palette('Dark')['primary_soft']} !important;
        --accent: {get_theme_palette('Dark')['accent']} !important;
        --success: {get_theme_palette('Dark')['success']} !important;
        --shadow: {get_theme_palette('Dark')['shadow']} !important;
    }}
}}
"""
theme_css_override = indent(theme_css_override.strip(), "    ")

# Custom CSS for theme switching, hidden headers/footers, and creative styling
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
        max-width: 1280px;
        padding: 1.2rem 1.4rem 6rem !important;
    }}
    .stApp, [data-testid="stAppViewContainer"] {{
        color: var(--text);
        background: radial-gradient(circle at top left, rgba(124, 108, 255, 0.18), transparent 28%),
                    radial-gradient(circle at bottom right, rgba(56, 189, 248, 0.18), transparent 32%),
                    var(--bg);
    }}
    .nova-topbar {{
        display: flex; align-items: center; justify-content: space-between;
        gap: 1rem; padding: 0.2rem 0 1rem; margin-bottom: 1rem;
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
        gap: 1.25rem; min-height: 220px; padding: 2rem 2.25rem; margin-bottom: 1.5rem;
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
    .nova-section-head {{ margin: 1.1rem 0 0.9rem; }}
    .nova-kicker {{
        color: var(--primary); font-size: 0.66rem; font-weight: 800; letter-spacing: 0.16em;
        text-transform: uppercase;
    }}
    .nova-section-title {{ font-size: 1.05rem; font-weight: 800; color: var(--text); margin-top: 0.32rem; }}
    .nova-card {{
        min-height: 134px; padding: 1.15rem 1rem; border-radius: 20px; border: 1px solid rgba(148,163,184,.15);
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
        border-radius: 18px !important; padding: 0.95rem 1rem !important; margin-bottom: 0.8rem !important;
        border: 1px solid rgba(148, 163, 184, 0.16) !important; background: var(--surface) !important;
        box-shadow: 0 8px 20px var(--shadow);
    }}
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {{
        margin: 0; color: var(--text) !important; font-size: 0.92rem; line-height: 1.65;
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
    [data-testid="stChatInput"]:focus-within {{ border-color: var(--primary) !important; box-shadow: 0 0 0 4px rgba(124,108,255,.12) !important; }}
    [data-testid="stChatInput"] textarea {{ color: var(--text) !important; font-size: 0.92rem; }}
    div[data-testid="stBottom"], div[data-testid="stBottom"] > div {{ background: transparent !important; }}

    section[data-testid="stSidebar"] {{
        background: var(--panel) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.14) !important;
    }}
    section[data-testid="stSidebar"] > div {{ padding: 1.2rem 0.9rem 1rem !important; }}
    .side-title {{ padding-bottom: 0.8rem; margin-bottom: 1rem; border-bottom: 1px solid rgba(148, 163, 184, 0.15); }}
    .side-kicker {{ color: var(--primary); font-size: 0.64rem; letter-spacing: 0.15em; font-weight: 800; text-transform: uppercase; }}
    .side-heading {{ color: var(--text); font-size: 1.08rem; font-weight: 800; margin-top: 0.28rem; }}
    .side-sub {{ color: var(--muted); font-size: 0.72rem; line-height: 1.5; margin-top: 0.12rem; }}
    .progress-wrap {{
        background: var(--primary-soft); border: 1px solid rgba(124,108,255,.18); border-radius: 16px;
        padding: 0.75rem 0.8rem; margin-bottom: 1rem;
    }}
    .progress-head {{ display: flex; justify-content: space-between; gap: 0.5rem; align-items: center; font-size: 0.72rem; color: var(--muted); }}
    .progress-head b {{ color: var(--text); font-size: 0.78rem; }}
    .progress-track {{ height: 8px; border-radius: 999px; background: rgba(148,163,184,0.18); overflow: hidden; margin-top: 0.7rem; }}
    .progress-fill {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--primary), var(--accent)); }}
    .summary-list {{ display: flex; flex-direction: column; gap: 0.58rem; margin-top: 0.7rem; }}
    .summary-row {{ display: flex; justify-content: space-between; align-items: center; gap: 0.6rem; }}
    .summary-label-wrap {{ display: inline-flex; align-items: center; gap: 0.5rem; min-width: 0; }}
    .status-indicator {{
        width: 18px; height: 18px; border-radius: 50%; display: grid; place-items: center; font-size: 0.58rem; font-weight: 800;
    }}
    .status-indicator.filled {{ background: rgba(52,211,153,.12); color: var(--success); }}
    .status-indicator.empty {{ background: rgba(148,163,184,.14); color: var(--muted); }}
    .summary-label {{ font-size: 0.74rem; color: var(--muted); }}
    .summary-val {{
        display: inline-flex; align-items: center; max-width: 116px; min-height: 28px; padding: 0.34rem 0.52rem; border-radius: 10px;
        font-size: 0.7rem; font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}
    .summary-val.filled {{ background: rgba(124,108,255,.1); color: var(--text); border: 1px solid rgba(124,108,255,.14); }}
    .summary-val.empty {{ background: rgba(148,163,184,.08); color: var(--muted); border: 1px dashed rgba(148,163,184,.18); }}
    .score-card {{ margin-top: 1rem; border-radius: 16px; padding: 0.8rem 0.9rem; background: linear-gradient(135deg, rgba(124,108,255,.16), rgba(56,189,248,.08)); border: 1px solid rgba(124,108,255,.18); }}
    .score-label {{ display: block; font-size: 0.66rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); }}
    .score-badge {{ display: inline-block; margin-top: 0.45rem; padding: 0.38rem 0.6rem; border-radius: 999px; background: rgba(52,211,153,.12); color: var(--success); font-size: 0.72rem; font-weight: 800; }}
    .handoff-alert {{ display: flex; gap: 0.7rem; margin-top: 1rem; padding: 0.75rem 0.8rem; border-radius: 16px; background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.16); }}
    .handoff-icon {{ display: grid; place-items: center; width: 28px; height: 28px; border-radius: 10px; background: rgba(239,68,68,.08); color: #ef4444; }}
    .handoff-alert strong {{ display: block; color: var(--text); font-size: 0.8rem; }}
    .handoff-alert span {{ display: block; margin-top: 0.18rem; color: var(--muted); font-size: 0.68rem; line-height: 1.4; }}
    .sidebar-section-label {{ margin-top: 1rem; margin-bottom: 0.5rem; font-size: 0.62rem; letter-spacing: 0.14em; color: var(--muted); text-transform: uppercase; font-weight: 800; }}
    [data-testid="stRadio"] > div {{ gap: 0.45rem; }}
    .stRadio [role="radiogroup"] {{ background: var(--surface-soft); border-radius: 12px; padding: 0.2rem; border: 1px solid rgba(148,163,184,.15); }}
    .stRadio label {{ color: var(--text); font-size: 0.74rem; }}
    .stButton > button {{
        background: linear-gradient(135deg, var(--primary), #8b5cf6); color: white; border: none; border-radius: 12px;
        font-weight: 700; box-shadow: 0 10px 22px rgba(124,108,255,.18); transition: transform .2s ease; 
    }}
    .stButton > button:hover {{ transform: translateY(-1px); }}
    @media (max-width: 640px) {{
        .block-container {{ padding: 1rem 0.8rem 5rem !important; }}
        .nova-hero {{ padding: 1.35rem 1.2rem; min-height: 180px; }}
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

    <section class="nova-hero">
      <div class="nova-hero-content">
        <div class="nova-eyebrow">Project consultation</div>
        <h1>Turn your idea into a clear next step.</h1>
        <p>Tell Nova what you're trying to build. I’ll collect the right details, suggest the best-fit service, and guide your conversation toward a polished project brief.</p>
        <div class="nova-hero-actions">
          <span class="nova-pill">✦ Service fit</span>
          <span class="nova-pill">✦ Budget + timeline</span>
          <span class="nova-pill">✦ Expert handoff</span>
        </div>
      </div>
      <div class="nova-hero-art" aria-hidden="true">
        <svg width="92" height="92" viewBox="0 0 82 82" fill="none" xmlns="http://www.w3.org/2000/svg">
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

# Sidebar: Dossier, Qualification Summary & Theme Toggle
with st.sidebar:
    st.markdown(
        """
        <div class="side-title">
            <div class="side-kicker">LEAD PROFILE</div>
            <div class="side-heading">Project summary</div>
            <div class="side-sub">Details captured automatically from the conversation.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    lead = st.session_state.lead
    summary_rows_html = []
    for field in VISITOR_FIELDS:
        val = lead.get(field)
        if field == "budget" and val is not None:
            formatted_val = f"₹{val:,}"
        elif field == "timeline_months" and val is not None:
            formatted_val = f"{val} mo" if val == 1 else f"{val} mos"
        elif field == "decision_maker" and val is not None:
            formatted_val = "Yes" if val else "No"
        elif val is not None:
            formatted_val = str(val)
        else:
            formatted_val = None

        label = FIELD_LABELS.get(field, field.replace("_", " ").title())
        if formatted_val:
            badge_html = f'<span class="summary-val filled" title="{formatted_val}">{formatted_val}</span>'
            status_dot = '<span class="status-indicator filled">✓</span>'
        else:
            badge_html = '<span class="summary-val empty">Pending</span>'
            status_dot = '<span class="status-indicator empty">·</span>'

        summary_rows_html.append(
            f'<div class="summary-row">'
            f'<div class="summary-label-wrap">{status_dot}<span class="summary-label">{label}</span></div>'
            f'{badge_html}'
            f'</div>'
        )

    filled_count = sum(1 for field in VISITOR_FIELDS if lead.get(field) is not None)
    total_fields = len(VISITOR_FIELDS)
    progress_pct = int((filled_count / total_fields) * 100) if total_fields else 0

    st.markdown(
        f"""
        <div class="progress-wrap">
            <div class="progress-head">
                <span>Qualification progress</span>
                <b>{filled_count}/{total_fields}</b>
            </div>
            <div class="progress-track"><div class="progress-fill" style="width:{progress_pct}%"></div></div>
        </div>
        <div class="summary-list">{"".join(summary_rows_html)}</div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.score:
        score_val = st.session_state.score.title()
        st.markdown(
            f"""
            <div class="score-card">
                <span class="score-label">Lead Qualification</span>
                <span class="score-badge">{score_val}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.handoff_flag:
        st.markdown(
            """
            <div class="handoff-alert">
                <div class="handoff-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                    </svg>
                </div>
                <div>
                    <strong>Team Handoff Ready</strong>
                    <span>A member of our team will follow up with you shortly.</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height: 0.6rem"></div>', unsafe_allow_html=True)
    st.button("Start a new conversation", on_click=reset_conversation, use_container_width=True)

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
        st.session_state.score = result["score"]
        st.session_state.handoff_flag = result["handoff_flag"]
        st.rerun()