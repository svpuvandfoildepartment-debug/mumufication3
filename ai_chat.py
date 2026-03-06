import streamlit as st

# ── Page config (must be first) ───────────────────────────────────────────────
st.set_page_config(
    page_title="Constellation · AI Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

import os, time, importlib

# ─────────────────────────────────────────────────────────────────────────────
# AI MODEL REGISTRY  – beautiful names + metadata
# ─────────────────────────────────────────────────────────────────────────────
MODELS = {
    # ── Anthropic ──────────────────────────────────────────────────────────
    "oracle": {
        "label": "Oracle",
        "tagline": "Ancient wisdom, crystalline clarity",
        "provider": "anthropic",
        "model_id": "claude-opus-4-5",
        "color": "#a78bfa",
        "glyph": "◈",
        "key_env": "ANTHROPIC_API_KEY",
        "key_session": "anthropic_key",
    },
    "echo": {
        "label": "Echo",
        "tagline": "Swift replies from the mountain",
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-5",
        "color": "#818cf8",
        "glyph": "◇",
        "key_env": "ANTHROPIC_API_KEY",
        "key_session": "anthropic_key",
    },
    # ── OpenAI ─────────────────────────────────────────────────────────────
    "luminary": {
        "label": "Luminary",
        "tagline": "Radiant reasoning, sovereign intelligence",
        "provider": "openai",
        "model_id": "gpt-4o",
        "color": "#34d399",
        "glyph": "✦",
        "key_env": "OPENAI_API_KEY",
        "key_session": "openai_key",
    },
    "spark": {
        "label": "Spark",
        "tagline": "Quick fire, bright ideas",
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "color": "#6ee7b7",
        "glyph": "⚡",
        "key_env": "OPENAI_API_KEY",
        "key_session": "openai_key",
    },
    # ── Google Gemini ──────────────────────────────────────────────────────
    "cosmos": {
        "label": "Cosmos",
        "tagline": "Vast as the universe, endlessly curious",
        "provider": "google",
        "model_id": "gemini-1.5-pro",
        "color": "#fb923c",
        "glyph": "◉",
        "key_env": "GOOGLE_API_KEY",
        "key_session": "google_key",
    },
    "nova": {
        "label": "Nova",
        "tagline": "Born from starlight, fleet of thought",
        "provider": "google",
        "model_id": "gemini-1.5-flash",
        "color": "#fdba74",
        "glyph": "★",
        "key_env": "GOOGLE_API_KEY",
        "key_session": "google_key",
    },
    # ── Mistral ────────────────────────────────────────────────────────────
    "mistral": {
        "label": "Mistral",
        "tagline": "A wild wind carrying secrets",
        "provider": "mistral",
        "model_id": "mistral-large-latest",
        "color": "#f472b6",
        "glyph": "〜",
        "key_env": "MISTRAL_API_KEY",
        "key_session": "mistral_key",
    },
    # ── Cohere ─────────────────────────────────────────────────────────────
    "prism": {
        "label": "Prism",
        "tagline": "Language refracted into insight",
        "provider": "cohere",
        "model_id": "command-r-plus",
        "color": "#38bdf8",
        "glyph": "⬡",
        "key_env": "COHERE_API_KEY",
        "key_session": "cohere_key",
    },
    # ── Groq (fast inference) ──────────────────────────────────────────────
    "mercury": {
        "label": "Mercury",
        "tagline": "Messenger of the gods — at light speed",
        "provider": "groq",
        "model_id": "llama-3.3-70b-versatile",
        "color": "#fbbf24",
        "glyph": "⚙",
        "key_env": "GROQ_API_KEY",
        "key_session": "groq_key",
    },
}

PROVIDER_LABELS = {
    "anthropic": "Anthropic",
    "openai": "OpenAI",
    "google": "Google Gemini",
    "mistral": "Mistral AI",
    "cohere": "Cohere",
    "groq": "Groq",
}

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── Root & base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #06060e;
    font-family: 'JetBrains Mono', monospace;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 55% 40% at 15% 5%,  rgba(120,80,255,.14) 0%, transparent 65%),
        radial-gradient(ellipse 45% 35% at 85% 95%, rgba(251,146,60,.10) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 50% 50%, rgba(52,211,153,.05) 0%, transparent 70%),
        #06060e;
    color: #e2ddd6;
}

/* hide streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(6,6,14,.97) !important;
    border-right: 1px solid rgba(255,255,255,.06) !important;
}
[data-testid="stSidebar"] > div { padding-top: 1.5rem; }
[data-testid="stSidebar"] * { color: #e2ddd6 !important; }

/* sidebar header */
.sidebar-brand {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.5rem;
    font-weight: 300;
    letter-spacing: .08em;
    text-align: center;
    padding: .5rem 1rem 1.4rem;
    border-bottom: 1px solid rgba(255,255,255,.07);
    margin-bottom: 1.2rem;
    color: #e2ddd6;
}
.sidebar-brand span { color: #a78bfa; }

/* model card in sidebar */
.model-card {
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 10px;
    padding: .65rem .9rem;
    margin: .35rem .2rem;
    cursor: pointer;
    transition: border-color .2s, background .2s;
}
.model-card:hover { background: rgba(255,255,255,.04); }
.model-card.active { border-color: var(--mc); background: rgba(255,255,255,.05); }
.model-card .mc-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.05rem;
    font-weight: 600;
}
.model-card .mc-tag {
    font-size: .62rem;
    opacity: .45;
    letter-spacing: .05em;
    margin-top: 1px;
}

/* provider section label */
.provider-label {
    font-size: .58rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    opacity: .3;
    padding: .8rem .4rem .2rem;
}

/* ── Main layout ── */
.block-container {
    max-width: 820px !important;
    padding: 0 1.5rem 7rem !important;
    margin: 0 auto;
}

/* ── Page header ── */
.page-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 2.2rem 0 1.8rem;
    border-bottom: 1px solid rgba(255,255,255,.06);
    margin-bottom: 2rem;
}
.page-header .ai-glyph {
    font-size: 2.2rem;
    line-height: 1;
    filter: drop-shadow(0 0 12px var(--active-color, #a78bfa));
}
.page-header .ai-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.1rem;
    font-weight: 300;
    letter-spacing: .04em;
    line-height: 1;
    color: var(--active-color, #a78bfa);
}
.page-header .ai-tagline {
    font-size: .68rem;
    opacity: .38;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-top: .3rem;
}
.page-header .provider-badge {
    margin-left: auto;
    font-size: .6rem;
    letter-spacing: .15em;
    text-transform: uppercase;
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 20px;
    padding: .3rem .8rem;
    opacity: .5;
}

/* ── Chat messages ── */
.chat-feed { display: flex; flex-direction: column; gap: 1.5rem; }

.msg { display: flex; gap: .85rem; align-items: flex-start; animation: riseUp .3s ease both; }
@keyframes riseUp { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform:none; } }

.msg-avatar {
    width: 30px; height: 30px; border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: .9rem; flex-shrink: 0; margin-top: 3px;
}
.msg.user   .msg-avatar { background: rgba(160,139,255,.15); border: 1px solid rgba(160,139,255,.25); }
.msg.ai     .msg-avatar { border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.04); }

.msg-body { flex: 1; }
.msg-role {
    font-size: .58rem;
    letter-spacing: .16em;
    text-transform: uppercase;
    opacity: .3;
    margin-bottom: .35rem;
}
.msg-text {
    font-size: .875rem;
    line-height: 1.75;
    padding: .8rem 1rem;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,.06);
    white-space: pre-wrap;
    word-break: break-word;
}
.msg.user .msg-text {
    background: rgba(120,80,255,.09);
    border-color: rgba(120,80,255,.18);
    color: #ccc8f0;
}
.msg.ai .msg-text {
    background: rgba(255,255,255,.03);
    color: #e2ddd6;
}

/* streaming cursor */
.cursor { display: inline-block; width: 7px; height: 14px;
          background: currentColor; margin-left: 2px; vertical-align: middle;
          animation: blink .8s step-end infinite; opacity: .7; border-radius: 1px; }
@keyframes blink { 50% { opacity: 0; } }

/* error banner */
.err-box {
    background: rgba(239,68,68,.1);
    border: 1px solid rgba(239,68,68,.25);
    border-radius: 8px;
    padding: .8rem 1rem;
    font-size: .8rem;
    color: #fca5a5;
    margin-top: .5rem;
}

/* ── Input ── */
[data-testid="stChatInput"] > div {
    border: 1px solid rgba(255,255,255,.1) !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,.03) !important;
    backdrop-filter: blur(10px);
    transition: border-color .2s, box-shadow .2s;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: rgba(167,139,250,.5) !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,.08);
}
[data-testid="stChatInput"] textarea {
    color: #e2ddd6 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: .84rem !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: rgba(226,221,214,.25) !important; }
[data-testid="stChatInputSubmitButton"] button {
    background: rgba(120,80,255,.6) !important;
    border-radius: 8px !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
    background: rgba(120,80,255,.9) !important;
}

/* ── API key inputs ── */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(255,255,255,.09) !important;
    border-radius: 8px !important;
    color: #e2ddd6 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: .78rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(167,139,250,.4) !important;
    box-shadow: 0 0 0 2px rgba(167,139,250,.08) !important;
}
[data-testid="stTextInput"] label { font-size: .7rem !important; opacity: .5; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.1); border-radius: 4px; }

/* ── Selectbox (for radio-like selector) ── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(255,255,255,.09) !important;
    border-radius: 8px !important;
    color: #e2ddd6 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "active_model" not in st.session_state:
    st.session_state.active_model = "oracle"
if "histories" not in st.session_state:
    st.session_state.histories = {k: [] for k in MODELS}

# API keys (pulled from env or session)
for m in MODELS.values():
    sk = m["key_session"]
    if sk not in st.session_state:
        st.session_state[sk] = os.environ.get(m["key_env"], "")

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">✦ <span>Constellation</span></div>', unsafe_allow_html=True)

    # Group models by provider
    providers_seen = []
    for key, meta in MODELS.items():
        prov = meta["provider"]
        if prov not in providers_seen:
            providers_seen.append(prov)

    for prov in providers_seen:
        st.markdown(f'<div class="provider-label">{PROVIDER_LABELS[prov]}</div>', unsafe_allow_html=True)
        for key, meta in MODELS.items():
            if meta["provider"] != prov:
                continue
            is_active = st.session_state.active_model == key
            active_class = "active" if is_active else ""
            col1, col2 = st.columns([0.15, 0.85])
            with col1:
                st.markdown(f"<span style='color:{meta['color']};font-size:1.1rem'>{meta['glyph']}</span>", unsafe_allow_html=True)
            with col2:
                if st.button(
                    f"**{meta['label']}**  \n_{meta['tagline']}_",
                    key=f"btn_{key}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    st.session_state.active_model = key
                    st.rerun()

    st.markdown("---")
    st.markdown('<div class="provider-label">API Keys</div>', unsafe_allow_html=True)

    # Collect unique key slots
    keys_done = set()
    for key, meta in MODELS.items():
        sk = meta["key_session"]
        if sk in keys_done:
            continue
        keys_done.add(sk)
        val = st.text_input(
            f"{PROVIDER_LABELS[meta['provider']]}",
            value=st.session_state[sk],
            type="password",
            key=f"input_{sk}",
        )
        st.session_state[sk] = val

    st.markdown("---")
    if st.button("🗑  Clear conversation", use_container_width=True):
        st.session_state.histories[st.session_state.active_model] = []
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# INFERENCE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def call_anthropic(meta, history, user_msg):
    import anthropic as _ant
    client = _ant.Anthropic(api_key=st.session_state[meta["key_session"]])
    msgs = [{"role": m["role"], "content": m["content"]} for m in history]
    msgs.append({"role": "user", "content": user_msg})
    full = ""
    with client.messages.stream(
        model=meta["model_id"], max_tokens=2048, messages=msgs
    ) as stream:
        for text in stream.text_stream:
            full += text
            yield text
    return full


def call_openai(meta, history, user_msg):
    from openai import OpenAI
    client = OpenAI(api_key=st.session_state[meta["key_session"]])
    msgs = [{"role": m["role"], "content": m["content"]} for m in history]
    msgs.append({"role": "user", "content": user_msg})
    stream = client.chat.completions.create(
        model=meta["model_id"], messages=msgs, max_tokens=2048, stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            yield delta


def call_google(meta, history, user_msg):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=st.session_state[meta["key_session"]])
    contents = []
    for m in history:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=user_msg)]))
    for chunk in client.models.generate_content_stream(
        model=meta["model_id"], contents=contents
    ):
        if chunk.text:
            yield chunk.text


def call_mistral(meta, history, user_msg):
    from mistralai import Mistral
    client = Mistral(api_key=st.session_state[meta["key_session"]])
    msgs = [{"role": m["role"], "content": m["content"]} for m in history]
    msgs.append({"role": "user", "content": user_msg})
    stream = client.chat.stream(model=meta["model_id"], messages=msgs, max_tokens=2048)
    for chunk in stream:
        delta = chunk.data.choices[0].delta.content or ""
        if delta:
            yield delta


def call_cohere(meta, history, user_msg):
    import cohere
    client = cohere.Client(api_key=st.session_state[meta["key_session"]])
    chat_history = []
    for m in history:
        role = "USER" if m["role"] == "user" else "CHATBOT"
        chat_history.append({"role": role, "message": m["content"]})
    stream = client.chat_stream(
        model=meta["model_id"],
        message=user_msg,
        chat_history=chat_history,
        max_tokens=2048,
    )
    for event in stream:
        if event.event_type == "text-generation":
            yield event.text


def call_groq(meta, history, user_msg):
    from groq import Groq
    client = Groq(api_key=st.session_state[meta["key_session"]])
    msgs = [{"role": m["role"], "content": m["content"]} for m in history]
    msgs.append({"role": "user", "content": user_msg})
    stream = client.chat.completions.create(
        model=meta["model_id"], messages=msgs, max_tokens=2048, stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            yield delta


PROVIDER_FN = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "google": call_google,
    "mistral": call_mistral,
    "cohere": call_cohere,
    "groq": call_groq,
}

# ─────────────────────────────────────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────────────────────────────────────
active_key = st.session_state.active_model
meta = MODELS[active_key]
history = st.session_state.histories[active_key]

# Page header
st.markdown(f"""
<div class="page-header" style="--active-color:{meta['color']}">
  <div class="ai-glyph" style="color:{meta['color']}">{meta['glyph']}</div>
  <div>
    <div class="ai-name">{meta['label']}</div>
    <div class="ai-tagline">{meta['tagline']}</div>
  </div>
  <div class="provider-badge">{PROVIDER_LABELS[meta['provider']]} · {meta['model_id']}</div>
</div>
""", unsafe_allow_html=True)

# Check API key
api_key = st.session_state[meta["key_session"]]
if not api_key:
    st.markdown(f"""<div class="err-box">
        ⚠ No API key for <strong>{PROVIDER_LABELS[meta['provider']]}</strong>. 
        Enter it in the sidebar to begin conversing with <em>{meta['label']}</em>.
    </div>""", unsafe_allow_html=True)

# Render chat history
st.markdown('<div class="chat-feed">', unsafe_allow_html=True)
for msg in history:
    role_cls = "user" if msg["role"] == "user" else "ai"
    role_label = "You" if msg["role"] == "user" else meta["label"]
    glyph = "▸" if msg["role"] == "user" else meta["glyph"]
    avatar_color = "#a78bfa" if msg["role"] == "user" else meta["color"]
    st.markdown(f"""
    <div class="msg {role_cls}">
      <div class="msg-avatar" style="color:{avatar_color}">{glyph}</div>
      <div class="msg-body">
        <div class="msg-role">{role_label}</div>
        <div class="msg-text">{msg['content']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────────────────────────────────────
prompt = st.chat_input(f"Speak to {meta['label']}…", disabled=not api_key)

if prompt:
    # Show user message immediately
    st.markdown(f"""
    <div class="msg user">
      <div class="msg-avatar" style="color:#a78bfa">▸</div>
      <div class="msg-body">
        <div class="msg-role">You</div>
        <div class="msg-text">{prompt}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Stream AI response
    ai_placeholder = st.empty()
    full_response = ""
    error_msg = None

    try:
        fn = PROVIDER_FN[meta["provider"]]
        for chunk in fn(meta, history, prompt):
            full_response += chunk
            ai_placeholder.markdown(f"""
            <div class="msg ai">
              <div class="msg-avatar" style="color:{meta['color']}">{meta['glyph']}</div>
              <div class="msg-body">
                <div class="msg-role">{meta['label']}</div>
                <div class="msg-text">{full_response}<span class="cursor"></span></div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        error_msg = str(e)
        ai_placeholder.markdown(f'<div class="err-box">⚠ {error_msg}</div>', unsafe_allow_html=True)

    if full_response:
        # Final render without cursor
        ai_placeholder.markdown(f"""
        <div class="msg ai">
          <div class="msg-avatar" style="color:{meta['color']}">{meta['glyph']}</div>
          <div class="msg-body">
            <div class="msg-role">{meta['label']}</div>
            <div class="msg-text">{full_response}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Persist to history
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": full_response})
        st.session_state.histories[active_key] = history
