import streamlit as st

st.set_page_config(
    page_title="Constellation · AI Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

import os, html, requests, json

# ─────────────────────────────────────────────────────────────────────────────
# MODEL REGISTRY
# tier: "paid" | "free" | "local"
# ─────────────────────────────────────────────────────────────────────────────
MODELS = {
    # ── PAID ──────────────────────────────────────────────────────────────
    "oracle":    {"label":"Oracle",      "tagline":"Ancient wisdom, crystalline clarity",         "provider":"anthropic", "model_id":"claude-opus-4-5",                "color":"#a78bfa","glyph":"◈","key_env":"ANTHROPIC_API_KEY", "key_session":"anthropic_key",  "tier":"paid"},
    "echo":      {"label":"Echo",        "tagline":"Swift replies from the mountain",              "provider":"anthropic", "model_id":"claude-sonnet-4-5",               "color":"#818cf8","glyph":"◇","key_env":"ANTHROPIC_API_KEY", "key_session":"anthropic_key",  "tier":"paid"},
    "luminary":  {"label":"Luminary",    "tagline":"Radiant reasoning, sovereign intelligence",   "provider":"openai",    "model_id":"gpt-4o",                          "color":"#34d399","glyph":"✦","key_env":"OPENAI_API_KEY",    "key_session":"openai_key",     "tier":"paid"},
    "spark":     {"label":"Spark",       "tagline":"Quick fire, bright ideas",                    "provider":"openai",    "model_id":"gpt-4o-mini",                     "color":"#6ee7b7","glyph":"⚡","key_env":"OPENAI_API_KEY",    "key_session":"openai_key",     "tier":"paid"},
    "cosmos":    {"label":"Cosmos",      "tagline":"Vast as the universe, endlessly curious",     "provider":"google",    "model_id":"gemini-1.5-pro",                  "color":"#fb923c","glyph":"◉","key_env":"GOOGLE_API_KEY",    "key_session":"google_key",     "tier":"paid"},
    "nova":      {"label":"Nova",        "tagline":"Born from starlight, fleet of thought",       "provider":"google",    "model_id":"gemini-1.5-flash",                "color":"#fdba74","glyph":"★","key_env":"GOOGLE_API_KEY",    "key_session":"google_key",     "tier":"paid"},
    "mistral":   {"label":"Mistral",     "tagline":"A wild wind carrying secrets",                "provider":"mistral",   "model_id":"mistral-large-latest",            "color":"#f472b6","glyph":"〜","key_env":"MISTRAL_API_KEY",   "key_session":"mistral_key",    "tier":"paid"},
    "prism":     {"label":"Prism",       "tagline":"Language refracted into insight",             "provider":"cohere",    "model_id":"command-r-plus",                  "color":"#38bdf8","glyph":"⬡","key_env":"COHERE_API_KEY",    "key_session":"cohere_key",     "tier":"paid"},
    "mercury":   {"label":"Mercury",     "tagline":"Messenger of the gods — at light speed",     "provider":"groq",      "model_id":"llama-3.3-70b-versatile",         "color":"#fbbf24","glyph":"⚙","key_env":"GROQ_API_KEY",      "key_session":"groq_key",       "tier":"paid"},

    # ── FREE (HuggingFace Inference API — no key needed for many models) ──
    "sage":      {"label":"Sage",        "tagline":"Open wisdom from the community",              "provider":"hf_free",   "model_id":"mistralai/Mistral-7B-Instruct-v0.3","color":"#e879f9","glyph":"❋","key_env":"HF_TOKEN",          "key_session":"hf_key",         "tier":"free"},
    "phantom":   {"label":"Phantom",     "tagline":"Unseen intelligence, freely given",           "provider":"hf_free",   "model_id":"microsoft/Phi-3.5-mini-instruct",  "color":"#c084fc","glyph":"◐","key_env":"HF_TOKEN",          "key_session":"hf_key",         "tier":"free"},
    "zephyr":    {"label":"Zephyr",      "tagline":"A gentle breeze of open-source thought",     "provider":"hf_free",   "model_id":"HuggingFaceH4/zephyr-7b-beta",     "color":"#67e8f9","glyph":"≋","key_env":"HF_TOKEN",          "key_session":"hf_key",         "tier":"free"},
    "titan":     {"label":"Titan",       "tagline":"Colossal open model, raw and powerful",      "provider":"hf_free",   "model_id":"meta-llama/Meta-Llama-3-8B-Instruct","color":"#86efac","glyph":"▲","key_env":"HF_TOKEN",         "key_session":"hf_key",         "tier":"free"},

    # ── LOCAL (Ollama — runs on your machine) ─────────────────────────────
    "forge":     {"label":"Forge",       "tagline":"Crafted locally, owned entirely",             "provider":"ollama",    "model_id":"llama3.2",                        "color":"#fda4af","glyph":"⬟","key_env":"",                  "key_session":"",               "tier":"local"},
    "raven":     {"label":"Raven",       "tagline":"Dark, clever, completely private",            "provider":"ollama",    "model_id":"mistral",                         "color":"#94a3b8","glyph":"◆","key_env":"",                  "key_session":"",               "tier":"local"},
    "ember":     {"label":"Ember",       "tagline":"Small but fierce — runs on anything",        "provider":"ollama",    "model_id":"phi3",                            "color":"#fb7185","glyph":"◇","key_env":"",                  "key_session":"",               "tier":"local"},
    "atlas":     {"label":"Atlas",       "tagline":"Carries the weight of open knowledge",       "provider":"ollama",    "model_id":"gemma2",                          "color":"#4ade80","glyph":"⬡","key_env":"",                  "key_session":"",               "tier":"local"},
}

PROVIDER_LABELS = {
    "anthropic":"Anthropic","openai":"OpenAI","google":"Google Gemini",
    "mistral":"Mistral AI","cohere":"Cohere","groq":"Groq",
    "hf_free":"HuggingFace (Free)","ollama":"Ollama (Local)",
}

TIER_META = {
    "paid":  {"label":"Paid APIs",        "badge":"💳 API Key",  "badge_color":"rgba(251,191,36,.15)",  "badge_text":"#fbbf24"},
    "free":  {"label":"Free — HuggingFace","badge":"🆓 Free",    "badge_color":"rgba(74,222,128,.12)",  "badge_text":"#4ade80"},
    "local": {"label":"Local — Ollama",   "badge":"🏠 Local",   "badge_color":"rgba(251,113,133,.12)", "badge_text":"#fb7185"},
}

OLLAMA_BASE = "http://localhost:11434"

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=JetBrains+Mono:wght@300;400;500&display=swap');

html,body,[data-testid="stAppViewContainer"]{background:#06060e;font-family:'JetBrains Mono',monospace;}
[data-testid="stAppViewContainer"]{
    background:
        radial-gradient(ellipse 55% 40% at 15% 5%,  rgba(120,80,255,.13) 0%,transparent 65%),
        radial-gradient(ellipse 45% 35% at 85% 95%, rgba(251,146,60,.09) 0%,transparent 60%),
        radial-gradient(ellipse 30% 30% at 50% 50%, rgba(74,222,128,.04) 0%,transparent 70%),
        #06060e;
    color:#e2ddd6;
}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important}

/* Sidebar */
[data-testid="stSidebar"]{background:rgba(6,6,14,.97)!important;border-right:1px solid rgba(255,255,255,.06)!important;}
[data-testid="stSidebar"]>div{padding-top:1.5rem;}
[data-testid="stSidebar"] *{color:#e2ddd6!important;}
.sidebar-brand{font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:300;letter-spacing:.08em;text-align:center;padding:.5rem 1rem 1.2rem;border-bottom:1px solid rgba(255,255,255,.07);margin-bottom:.8rem;}
.sidebar-brand span{color:#a78bfa;}
.provider-label{font-size:.56rem;letter-spacing:.18em;text-transform:uppercase;opacity:.28;padding:.7rem .4rem .15rem;}

/* Tier section headers */
.tier-header{display:flex;align-items:center;gap:.5rem;padding:.9rem .4rem .3rem;border-top:1px solid rgba(255,255,255,.05);margin-top:.3rem;}
.tier-header .tier-name{font-size:.6rem;letter-spacing:.15em;text-transform:uppercase;opacity:.4;}
.tier-badge{font-size:.55rem;padding:.15rem .5rem;border-radius:20px;letter-spacing:.05em;}

/* Main */
.block-container{max-width:1100px!important;padding:0 1.5rem 7rem!important;margin:0 auto;}

/* Page header */
.page-header{display:flex;align-items:center;gap:1rem;padding:2rem 0 1.6rem;border-bottom:1px solid rgba(255,255,255,.06);margin-bottom:2rem;}
.page-header .ai-glyph{font-size:2.2rem;line-height:1;}
.page-header .ai-name{font-family:'Cormorant Garamond',serif;font-size:2.1rem;font-weight:300;letter-spacing:.04em;line-height:1;}
.page-header .ai-tagline{font-size:.68rem;opacity:.38;letter-spacing:.12em;text-transform:uppercase;margin-top:.3rem;}
.page-header .provider-badge{margin-left:auto;font-size:.6rem;letter-spacing:.15em;text-transform:uppercase;border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:.3rem .8rem;opacity:.5;}
.page-header .tier-pill{font-size:.58rem;padding:.25rem .7rem;border-radius:20px;margin-left:.4rem;}

/* Messages */
.msg{display:flex;gap:.85rem;align-items:flex-start;animation:riseUp .3s ease both;margin-bottom:1.4rem;}
@keyframes riseUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.msg-avatar{width:30px;height:30px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:.9rem;flex-shrink:0;margin-top:3px;}
.msg.user .msg-avatar{background:rgba(160,139,255,.15);border:1px solid rgba(160,139,255,.25);}
.msg.ai   .msg-avatar{border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.04);}
.msg-body{flex:1;}
.msg-role{font-size:.58rem;letter-spacing:.16em;text-transform:uppercase;opacity:.3;margin-bottom:.35rem;}
.msg-text{font-size:.875rem;line-height:1.75;padding:.8rem 1rem;border-radius:10px;border:1px solid rgba(255,255,255,.06);white-space:pre-wrap;word-break:break-word;}
.msg.user .msg-text{background:rgba(120,80,255,.09);border-color:rgba(120,80,255,.18);color:#ccc8f0;}
.msg.ai   .msg-text{background:rgba(255,255,255,.03);color:#e2ddd6;}
.cursor{display:inline-block;width:7px;height:14px;background:currentColor;margin-left:2px;vertical-align:middle;animation:blink .8s step-end infinite;opacity:.7;border-radius:1px;}
@keyframes blink{50%{opacity:0}}
.err-box{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.25);border-radius:8px;padding:.8rem 1rem;font-size:.8rem;color:#fca5a5;margin:.5rem 0;}
.warn-box{background:rgba(251,191,36,.07);border:1px solid rgba(251,191,36,.2);border-radius:8px;padding:.8rem 1rem;font-size:.8rem;color:#fcd34d;margin-bottom:1rem;}
.info-box{background:rgba(74,222,128,.06);border:1px solid rgba(74,222,128,.18);border-radius:8px;padding:.8rem 1rem;font-size:.8rem;color:#86efac;margin-bottom:1rem;line-height:1.7;}

/* Ollama status dot */
.status-dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px;vertical-align:middle;}
.dot-green{background:#4ade80;box-shadow:0 0 6px #4ade80;}
.dot-red{background:#f87171;}
.dot-gray{background:#64748b;}

/* Panel */
.panel-header{text-align:center;padding:1.5rem 0 1.5rem;}
.panel-title{font-family:'Cormorant Garamond',serif;font-size:2.4rem;font-weight:300;letter-spacing:.06em;}
.panel-title span{color:#a78bfa;}
.panel-subtitle{font-size:.65rem;letter-spacing:.2em;text-transform:uppercase;opacity:.3;margin-top:.4rem;}
.panel-section-label{font-size:.6rem;letter-spacing:.2em;text-transform:uppercase;opacity:.35;margin:1.8rem 0 .8rem;padding-bottom:.4rem;border-bottom:1px solid rgba(255,255,255,.05);}
.panel-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.5rem;}
.panel-card{border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:1rem 1.1rem;background:rgba(255,255,255,.02);position:relative;overflow:hidden;}
.panel-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--cc);opacity:.6;}
.panel-card .pc-header{display:flex;align-items:center;gap:.5rem;margin-bottom:.7rem;}
.panel-card .pc-glyph{font-size:1.1rem;}
.panel-card .pc-name{font-family:'Cormorant Garamond',serif;font-size:1rem;font-weight:600;}
.panel-card .pc-model{font-size:.5rem;opacity:.25;margin-left:auto;text-align:right;max-width:100px;overflow:hidden;text-overflow:ellipsis;}
.panel-card .pc-text{font-size:.8rem;line-height:1.7;color:#d8d4e8;white-space:pre-wrap;word-break:break-word;min-height:2rem;}
.panel-card .pc-status{font-size:.62rem;opacity:.35;margin-top:.5rem;font-style:italic;}
.critique-card{border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:1rem 1.2rem;background:rgba(255,255,255,.015);margin-bottom:.8rem;position:relative;overflow:hidden;}
.critique-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--cc);opacity:.4;}
.critique-card .crit-header{display:flex;align-items:center;gap:.6rem;margin-bottom:.6rem;}
.critique-card .crit-glyph{font-size:1rem;}
.critique-card .crit-name{font-family:'Cormorant Garamond',serif;font-size:.95rem;font-weight:600;}
.critique-card .crit-label{font-size:.58rem;opacity:.3;letter-spacing:.1em;text-transform:uppercase;margin-left:.3rem;}
.critique-card .crit-text{font-size:.8rem;line-height:1.7;color:#d0cce6;white-space:pre-wrap;word-break:break-word;}
.progress-wrap{background:rgba(255,255,255,.05);border-radius:4px;height:3px;margin-bottom:1.2rem;overflow:hidden;}
.progress-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,#a78bfa,#34d399,#fb923c,#f472b6);transition:width .4s ease;}
.session-divider{border:none;border-top:1px solid rgba(255,255,255,.05);margin:2.5rem 0;}

/* Input */
[data-testid="stChatInput"]>div{border:1px solid rgba(255,255,255,.1)!important;border-radius:12px!important;background:rgba(255,255,255,.03)!important;backdrop-filter:blur(10px);}
[data-testid="stChatInput"]>div:focus-within{border-color:rgba(167,139,250,.5)!important;box-shadow:0 0 0 3px rgba(167,139,250,.08);}
[data-testid="stChatInput"] textarea{color:#e2ddd6!important;font-family:'JetBrains Mono',monospace!important;font-size:.84rem!important;background:transparent!important;}
[data-testid="stChatInput"] textarea::placeholder{color:rgba(226,221,214,.25)!important;}
[data-testid="stChatInputSubmitButton"] button{background:rgba(120,80,255,.6)!important;border-radius:8px!important;}
[data-testid="stTextInput"] input{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.09)!important;border-radius:8px!important;color:#e2ddd6!important;font-family:'JetBrains Mono',monospace!important;font-size:.78rem!important;}
[data-testid="stTextInput"] label{font-size:.7rem!important;opacity:.5;}
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:4px;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def check_ollama():
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=2)
        if r.status_code == 200:
            tags = r.json().get("models", [])
            return True, [t["name"].split(":")[0] for t in tags]
    except:
        pass
    return False, []

def model_available(key, meta):
    tier = meta["tier"]
    if tier == "paid":
        return bool(st.session_state.get(meta["key_session"], ""))
    elif tier == "free":
        return True  # HF free inference works without key (rate limited)
    elif tier == "local":
        if not st.session_state.get("ollama_running"):
            return False
        installed = st.session_state.get("ollama_models", [])
        return any(meta["model_id"].startswith(m) or m.startswith(meta["model_id"]) for m in installed)
    return False

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "active_model"    not in st.session_state: st.session_state.active_model    = "oracle"
if "app_mode"        not in st.session_state: st.session_state.app_mode        = "solo"
if "histories"       not in st.session_state: st.session_state.histories       = {k:[] for k in MODELS}
if "panel_sessions"  not in st.session_state: st.session_state.panel_sessions  = []
if "ollama_running"  not in st.session_state: st.session_state.ollama_running  = False
if "ollama_models"   not in st.session_state: st.session_state.ollama_models   = []

for m in MODELS.values():
    sk = m["key_session"]
    if sk and sk not in st.session_state:
        st.session_state[sk] = os.environ.get(m["key_env"], "")

# Check Ollama on every load
ollama_ok, ollama_models = check_ollama()
st.session_state.ollama_running = ollama_ok
st.session_state.ollama_models  = ollama_models

# ─────────────────────────────────────────────────────────────────────────────
# INFERENCE — non-streaming
# ─────────────────────────────────────────────────────────────────────────────
def infer(meta, messages_list, system_prompt=None):
    prov = meta["provider"]
    key  = st.session_state.get(meta["key_session"], "") if meta["key_session"] else ""

    try:
        # ── Paid providers ──────────────────────────────────────────────────
        if prov == "anthropic":
            import anthropic as _ant
            client = _ant.Anthropic(api_key=key)
            kwargs = dict(model=meta["model_id"], max_tokens=1024, messages=messages_list)
            if system_prompt: kwargs["system"] = system_prompt
            return client.messages.create(**kwargs).content[0].text

        elif prov == "openai":
            from openai import OpenAI
            msgs = ([{"role":"system","content":system_prompt}] if system_prompt else []) + messages_list
            return OpenAI(api_key=key).chat.completions.create(model=meta["model_id"],messages=msgs,max_tokens=1024).choices[0].message.content

        elif prov == "google":
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=key)
            contents = [types.Content(role="user" if m["role"]=="user" else "model",parts=[types.Part(text=m["content"])]) for m in messages_list]
            cfg = types.GenerateContentConfig(max_output_tokens=1024,**({"system_instruction":system_prompt} if system_prompt else {}))
            return client.models.generate_content(model=meta["model_id"],contents=contents,config=cfg).text

        elif prov == "mistral":
            from mistralai import Mistral
            msgs = ([{"role":"system","content":system_prompt}] if system_prompt else []) + messages_list
            return Mistral(api_key=key).chat.complete(model=meta["model_id"],messages=msgs,max_tokens=1024).choices[0].message.content

        elif prov == "cohere":
            import cohere
            hist = [{"role":"USER" if m["role"]=="user" else "CHATBOT","message":m["content"]} for m in messages_list[:-1]]
            return cohere.Client(api_key=key).chat(model=meta["model_id"],message=messages_list[-1]["content"],chat_history=hist,preamble=system_prompt or "",max_tokens=1024).text

        elif prov == "groq":
            from groq import Groq
            msgs = ([{"role":"system","content":system_prompt}] if system_prompt else []) + messages_list
            return Groq(api_key=key).chat.completions.create(model=meta["model_id"],messages=msgs,max_tokens=1024).choices[0].message.content

        # ── HuggingFace Free Inference API ──────────────────────────────────
        elif prov == "hf_free":
            hf_token = st.session_state.get("hf_key", "")
            headers = {"Content-Type": "application/json"}
            if hf_token:
                headers["Authorization"] = f"Bearer {hf_token}"

            # Build prompt from messages
            prompt = ""
            if system_prompt:
                prompt += f"<|system|>\n{system_prompt}</s>\n"
            for m in messages_list:
                role_tag = "<|user|>" if m["role"] == "user" else "<|assistant|>"
                prompt += f"{role_tag}\n{m['content']}</s>\n"
            prompt += "<|assistant|>\n"

            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 512, "temperature": 0.7, "return_full_text": False}}
            url = f"https://api-inference.huggingface.co/models/{meta['model_id']}"
            r = requests.post(url, headers=headers, json=payload, timeout=60)

            if r.status_code == 503:
                return "[Model is loading on HuggingFace, please try again in 20 seconds]"
            if r.status_code != 200:
                return f"[HuggingFace error {r.status_code}: {r.text[:200]}]"

            data = r.json()
            if isinstance(data, list) and data:
                return data[0].get("generated_text", str(data))
            return str(data)

        # ── Ollama Local ────────────────────────────────────────────────────
        elif prov == "ollama":
            msgs = []
            if system_prompt:
                msgs.append({"role": "system", "content": system_prompt})
            msgs.extend(messages_list)

            payload = {"model": meta["model_id"], "messages": msgs, "stream": False,
                       "options": {"num_predict": 1024}}
            r = requests.post(f"{OLLAMA_BASE}/api/chat", json=payload, timeout=120)
            if r.status_code != 200:
                return f"[Ollama error {r.status_code}: {r.text[:200]}]"
            return r.json()["message"]["content"]

    except Exception as e:
        return f"[Error: {e}]"

# ─────────────────────────────────────────────────────────────────────────────
# STREAMING — solo chat
# ─────────────────────────────────────────────────────────────────────────────
def stream_infer(meta, messages_list):
    prov = meta["provider"]
    key  = st.session_state.get(meta["key_session"], "") if meta["key_session"] else ""

    try:
        if prov == "anthropic":
            import anthropic as _ant
            with _ant.Anthropic(api_key=key).messages.stream(model=meta["model_id"],max_tokens=1024,messages=messages_list) as s:
                for t in s.text_stream: yield t

        elif prov == "openai":
            from openai import OpenAI
            for chunk in OpenAI(api_key=key).chat.completions.create(model=meta["model_id"],messages=messages_list,max_tokens=1024,stream=True):
                yield chunk.choices[0].delta.content or ""

        elif prov == "google":
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=key)
            contents = [types.Content(role="user" if m["role"]=="user" else "model",parts=[types.Part(text=m["content"])]) for m in messages_list]
            for chunk in client.models.generate_content_stream(model=meta["model_id"],contents=contents):
                if chunk.text: yield chunk.text

        elif prov == "mistral":
            from mistralai import Mistral
            for chunk in Mistral(api_key=key).chat.stream(model=meta["model_id"],messages=messages_list,max_tokens=1024):
                yield chunk.data.choices[0].delta.content or ""

        elif prov == "cohere":
            import cohere
            hist = [{"role":"USER" if m["role"]=="user" else "CHATBOT","message":m["content"]} for m in messages_list[:-1]]
            for event in cohere.Client(api_key=key).chat_stream(model=meta["model_id"],message=messages_list[-1]["content"],chat_history=hist,max_tokens=1024):
                if event.event_type=="text-generation": yield event.text

        elif prov == "groq":
            from groq import Groq
            for chunk in Groq(api_key=key).chat.completions.create(model=meta["model_id"],messages=messages_list,max_tokens=1024,stream=True):
                yield chunk.choices[0].delta.content or ""

        elif prov == "hf_free":
            # HF free doesn't support streaming well, use non-stream
            yield infer(meta, messages_list)

        elif prov == "ollama":
            msgs = list(messages_list)
            payload = {"model": meta["model_id"], "messages": msgs, "stream": True, "options": {"num_predict": 1024}}
            with requests.post(f"{OLLAMA_BASE}/api/chat", json=payload, stream=True, timeout=120) as r:
                for line in r.iter_lines():
                    if line:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content: yield content
                        if data.get("done"): break

    except Exception as e:
        yield f"[Error: {e}]"

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">✦ <span>Constellation</span></div>', unsafe_allow_html=True)

    for tier_key, tier_info in TIER_META.items():
        tier_models = {k:m for k,m in MODELS.items() if m["tier"]==tier_key}
        if not tier_models: continue

        st.markdown(f"""
        <div class="tier-header">
          <span class="tier-name">{tier_info['label']}</span>
          <span class="tier-badge" style="background:{tier_info['badge_color']};color:{tier_info['badge_text']}">{tier_info['badge']}</span>
        </div>""", unsafe_allow_html=True)

        # Group by provider within tier
        providers_seen = list(dict.fromkeys(m["provider"] for m in tier_models.values()))
        for prov in providers_seen:
            prov_models = {k:m for k,m in tier_models.items() if m["provider"]==prov}
            st.markdown(f'<div class="provider-label">{PROVIDER_LABELS[prov]}</div>', unsafe_allow_html=True)
            for key, meta in prov_models.items():
                avail = model_available(key, meta)
                is_active = st.session_state.active_model == key and st.session_state.app_mode == "solo"

                # Status indicator for local models
                if meta["tier"] == "local":
                    dot = "dot-green" if avail else ("dot-red" if st.session_state.ollama_running else "dot-gray")
                    extra = f'<span class="status-dot {dot}"></span>'
                else:
                    extra = ""

                c1, c2 = st.columns([0.15, 0.85])
                with c1:
                    opacity = "1" if avail else "0.35"
                    st.markdown(f"<span style='color:{meta['color']};font-size:1.1rem;opacity:{opacity}'>{meta['glyph']}</span>", unsafe_allow_html=True)
                with c2:
                    if st.button(
                        f"**{meta['label']}**  \n_{meta['tagline']}_",
                        key=f"btn_{key}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary",
                        disabled=not avail,
                    ):
                        st.session_state.active_model = key
                        st.session_state.app_mode = "solo"
                        st.rerun()

    # ── API Keys section ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="provider-label">💳 Paid API Keys</div>', unsafe_allow_html=True)
    keys_done = set()
    for key, meta in MODELS.items():
        if meta["tier"] != "paid": continue
        sk = meta["key_session"]
        if sk in keys_done: continue
        keys_done.add(sk)
        val = st.text_input(PROVIDER_LABELS[meta["provider"]], value=st.session_state.get(sk,""), type="password", key=f"input_{sk}")
        st.session_state[sk] = val

    st.markdown('<div class="provider-label" style="margin-top:.5rem">🆓 HuggingFace Token (optional)</div>', unsafe_allow_html=True)
    hf_val = st.text_input("HuggingFace Token", value=st.session_state.get("hf_key",""), type="password", key="input_hf_key", help="Optional — higher rate limits with a free HF account token")
    st.session_state["hf_key"] = hf_val

    # Ollama status
    st.markdown("---")
    dot_cls = "dot-green" if ollama_ok else "dot-red"
    dot_label = f"Running · {len(ollama_models)} model(s)" if ollama_ok else "Not running"
    st.markdown(f'<div style="font-size:.7rem;opacity:.5;padding:.3rem .2rem"><span class="status-dot {dot_cls}"></span>Ollama: {dot_label}</div>', unsafe_allow_html=True)
    if not ollama_ok:
        st.markdown('<div style="font-size:.62rem;opacity:.35;padding:.2rem .2rem .5rem;line-height:1.6">Install: <code>brew install ollama</code><br>Start: <code>ollama serve</code><br>Pull: <code>ollama pull llama3.2</code></div>', unsafe_allow_html=True)
    elif ollama_models:
        st.markdown(f'<div style="font-size:.62rem;opacity:.3;padding:.1rem .2rem .5rem">{" · ".join(ollama_models[:6])}</div>', unsafe_allow_html=True)

    if st.button("🔄  Refresh Ollama", use_container_width=True):
        st.rerun()

    st.markdown("---")
    lbl = "🗑  Clear conversation" if st.session_state.app_mode=="solo" else "🗑  Clear panel"
    if st.button(lbl, use_container_width=True):
        if st.session_state.app_mode == "solo":
            st.session_state.histories[st.session_state.active_model] = []
        else:
            st.session_state.panel_sessions = []
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# MODE TOGGLE
# ─────────────────────────────────────────────────────────────────────────────
mode = st.session_state.app_mode
c1, c2, _ = st.columns([1.1, 1.1, 5])
with c1:
    if st.button("💬  Solo Chat", type="primary" if mode=="solo" else "secondary", use_container_width=True):
        st.session_state.app_mode = "solo"; st.rerun()
with c2:
    if st.button("✦  Panel", type="primary" if mode=="panel" else "secondary", use_container_width=True):
        st.session_state.app_mode = "panel"; st.rerun()
st.markdown("<div style='border-bottom:1px solid rgba(255,255,255,.06);margin-bottom:1.8rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FREE MODELS INFO BANNER
# ─────────────────────────────────────────────────────────────────────────────
if mode == "solo":
    active_key  = st.session_state.active_model
    active_meta = MODELS[active_key]
    if active_meta["tier"] == "free":
        st.markdown("""<div class="info-box">
        🆓 <strong>HuggingFace Free Inference</strong> — No API key required. 
        Uses the public inference API (rate limited). For higher limits, add a free 
        <a href="https://huggingface.co/settings/tokens" target="_blank" style="color:#86efac">HuggingFace token</a> in the sidebar.
        Models may take ~20s to warm up on first call.
        </div>""", unsafe_allow_html=True)
    elif active_meta["tier"] == "local":
        if not ollama_ok:
            st.markdown("""<div class="info-box">
            🏠 <strong>Ollama Local</strong> — Run AI completely offline on your machine.<br>
            1. Install: <code>brew install ollama</code> (Mac) or <a href="https://ollama.com/download" target="_blank" style="color:#86efac">ollama.com/download</a><br>
            2. Start: <code>ollama serve</code><br>
            3. Pull a model: <code>ollama pull llama3.2</code><br>
            4. Click <strong>Refresh Ollama</strong> in sidebar.
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SOLO CHAT
# ─────────────────────────────────────────────────────────────────────────────
if mode == "solo":
    active_key = st.session_state.active_model
    meta = MODELS[active_key]
    history = st.session_state.histories[active_key]
    tier_info = TIER_META[meta["tier"]]
    avail = model_available(active_key, meta)

    st.markdown(f"""
    <div class="page-header">
      <div class="ai-glyph" style="color:{meta['color']};filter:drop-shadow(0 0 10px {meta['color']})">{meta['glyph']}</div>
      <div>
        <div class="ai-name" style="color:{meta['color']}">{meta['label']}</div>
        <div class="ai-tagline">{meta['tagline']}</div>
      </div>
      <span class="tier-pill" style="background:{tier_info['badge_color']};color:{tier_info['badge_text']}">{tier_info['badge']}</span>
      <div class="provider-badge">{PROVIDER_LABELS[meta['provider']]} · {meta['model_id']}</div>
    </div>""", unsafe_allow_html=True)

    for msg in history:
        role_cls = "user" if msg["role"]=="user" else "ai"
        label = "You" if msg["role"]=="user" else meta["label"]
        glyph = "▸" if msg["role"]=="user" else meta["glyph"]
        color = "#a78bfa" if msg["role"]=="user" else meta["color"]
        st.markdown(f"""
        <div class="msg {role_cls}">
          <div class="msg-avatar" style="color:{color}">{glyph}</div>
          <div class="msg-body"><div class="msg-role">{label}</div>
          <div class="msg-text">{html.escape(msg['content'])}</div></div>
        </div>""", unsafe_allow_html=True)

    prompt = st.chat_input(f"Speak to {meta['label']}…", disabled=not avail)
    if prompt:
        st.markdown(f"""
        <div class="msg user">
          <div class="msg-avatar" style="color:#a78bfa">▸</div>
          <div class="msg-body"><div class="msg-role">You</div>
          <div class="msg-text">{html.escape(prompt)}</div></div>
        </div>""", unsafe_allow_html=True)
        ph = st.empty(); full = ""
        msgs = [{"role":m["role"],"content":m["content"]} for m in history] + [{"role":"user","content":prompt}]
        for chunk in stream_infer(meta, msgs):
            full += chunk
            ph.markdown(f"""
            <div class="msg ai">
              <div class="msg-avatar" style="color:{meta['color']}">{meta['glyph']}</div>
              <div class="msg-body"><div class="msg-role">{meta['label']}</div>
              <div class="msg-text">{html.escape(full)}<span class="cursor"></span></div></div>
            </div>""", unsafe_allow_html=True)
        if full:
            ph.markdown(f"""
            <div class="msg ai">
              <div class="msg-avatar" style="color:{meta['color']}">{meta['glyph']}</div>
              <div class="msg-body"><div class="msg-role">{meta['label']}</div>
              <div class="msg-text">{html.escape(full)}</div></div>
            </div>""", unsafe_allow_html=True)
            history.append({"role":"user","content":prompt})
            history.append({"role":"assistant","content":full})
            st.session_state.histories[active_key] = history

# ─────────────────────────────────────────────────────────────────────────────
# PANEL MODE
# ─────────────────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div class="panel-header">
      <div class="panel-title">The <span>Panel</span></div>
      <div class="panel-subtitle">Round 1: all minds answer &nbsp;·&nbsp; Round 2: they critique each other</div>
    </div>""", unsafe_allow_html=True)

    available   = {k:m for k,m in MODELS.items() if model_available(k,m)}
    unavailable = {k:m for k,m in MODELS.items() if not model_available(k,m)}

    if not available:
        st.markdown('<div class="err-box">⚠ No models available. Add API keys, connect HuggingFace, or start Ollama.</div>', unsafe_allow_html=True)
    else:
        by_tier = {}
        for k,m in available.items():
            by_tier.setdefault(m["tier"],[]).append(m["label"])
        summary = " · ".join(f"{TIER_META[t]['badge']} {', '.join(names)}" for t,names in by_tier.items())
        st.markdown(f'<div style="font-size:.68rem;opacity:.4;margin-bottom:1rem;line-height:1.8">{summary}</div>', unsafe_allow_html=True)

    # Past sessions
    for idx, session in enumerate(st.session_state.panel_sessions):
        if idx > 0: st.markdown('<hr class="session-divider">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="msg user" style="margin-bottom:1rem">
          <div class="msg-avatar" style="color:#a78bfa">▸</div>
          <div class="msg-body"><div class="msg-role">You asked the panel</div>
          <div class="msg-text">{html.escape(session['question'])}</div></div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="panel-section-label">Round 1 — Initial Responses</div>', unsafe_allow_html=True)
        cards = "".join(f"""
        <div class="panel-card" style="--cc:{MODELS[k]['color']}">
          <div class="pc-header">
            <span class="pc-glyph" style="color:{MODELS[k]['color']}">{MODELS[k]['glyph']}</span>
            <span class="pc-name">{MODELS[k]['label']}</span>
            <span class="pc-model">{MODELS[k]['model_id']}</span>
          </div>
          <div class="pc-text">{html.escape(resp)}</div>
        </div>""" for k,resp in session["responses"].items())
        st.markdown(f'<div class="panel-grid">{cards}</div>', unsafe_allow_html=True)

        if session.get("critiques"):
            st.markdown('<div class="panel-section-label">Round 2 — Cross-Critiques & Synthesis</div>', unsafe_allow_html=True)
            for k,crit in session["critiques"].items():
                m = MODELS[k]
                st.markdown(f"""
                <div class="critique-card" style="--cc:{m['color']}">
                  <div class="crit-header">
                    <span class="crit-glyph" style="color:{m['color']}">{m['glyph']}</span>
                    <span class="crit-name">{m['label']}</span>
                    <span class="crit-label">critiques the panel</span>
                  </div>
                  <div class="crit-text">{html.escape(crit)}</div>
                </div>""", unsafe_allow_html=True)

    panel_prompt = st.chat_input("Pose a question to the full panel…", disabled=not available)

    if panel_prompt and available:
        st.markdown(f"""
        <div class="msg user">
          <div class="msg-avatar" style="color:#a78bfa">▸</div>
          <div class="msg-body"><div class="msg-role">You asked the panel</div>
          <div class="msg-text">{html.escape(panel_prompt)}</div></div>
        </div>""", unsafe_allow_html=True)

        n = len(available)
        model_keys = list(available.keys())

        st.markdown('<div class="panel-section-label">Round 1 — Gathering initial responses…</div>', unsafe_allow_html=True)
        progress_ph = st.empty()
        grid_ph = st.empty()
        responses = {}

        def render_grid(done, current=None):
            cards = ""
            for k in model_keys:
                m = MODELS[k]
                tier_badge = TIER_META[m["tier"]]["badge"]
                if k in done:
                    body = f'<div class="pc-text">{html.escape(done[k])}</div>'
                elif k == current:
                    body = '<div class="pc-text"><span class="cursor"></span></div><div class="pc-status">thinking…</div>'
                else:
                    body = '<div class="pc-text"></div><div class="pc-status">waiting…</div>'
                cards += f'<div class="panel-card" style="--cc:{m["color"]}"><div class="pc-header"><span class="pc-glyph" style="color:{m["color"]}">{m["glyph"]}</span><span class="pc-name">{m["label"]}</span><span class="pc-model">{tier_badge} {m["model_id"]}</span></div>{body}</div>'
            return f'<div class="panel-grid">{cards}</div>'

        for i,(k,m) in enumerate(available.items()):
            pct = int(i/n*100)
            progress_ph.markdown(f'<div class="progress-wrap"><div class="progress-fill" style="width:{pct}%"></div></div>',unsafe_allow_html=True)
            grid_ph.markdown(render_grid(responses,current=k),unsafe_allow_html=True)
            responses[k] = infer(m,[{"role":"user","content":panel_prompt}])

        progress_ph.markdown('<div class="progress-wrap"><div class="progress-fill" style="width:100%"></div></div>',unsafe_allow_html=True)
        grid_ph.markdown(render_grid(responses),unsafe_allow_html=True)
        progress_ph.empty()

        st.markdown('<div class="panel-section-label">Round 2 — Each mind reads the others and critiques…</div>',unsafe_allow_html=True)
        panel_context = f'The question was:\n"{panel_prompt}"\n\nPanel responses:\n\n'
        for k,resp in responses.items():
            panel_context += f"— {MODELS[k]['label']} ({MODELS[k]['model_id']}):\n{resp}\n\n"

        critiques = {}
        crit_phs = {k:st.empty() for k in available}

        for k,m in available.items():
            crit_phs[k].markdown(f"""
            <div class="critique-card" style="--cc:{m['color']}">
              <div class="crit-header">
                <span class="crit-glyph" style="color:{m['color']}">{m['glyph']}</span>
                <span class="crit-name">{m['label']}</span>
                <span class="crit-label">is reflecting…</span>
              </div>
              <div class="crit-text"><span class="cursor"></span></div>
            </div>""",unsafe_allow_html=True)

            sys_p = (f"You are {m['label']}, an AI with this character: \"{m['tagline']}\". "
                     "You are in a multi-AI panel. Read all responses carefully. "
                     "Write a sharp critique: point out where others are wrong, incomplete, or insightful. "
                     "Reference others by name. End with a synthesis. 3-4 paragraphs max.")
            crit = infer(m,[{"role":"user","content":panel_context+f"\nAs {m['label']}, write your critique and synthesis."}],system_prompt=sys_p)
            critiques[k] = crit

            crit_phs[k].markdown(f"""
            <div class="critique-card" style="--cc:{m['color']}">
              <div class="crit-header">
                <span class="crit-glyph" style="color:{m['color']}">{m['glyph']}</span>
                <span class="crit-name">{m['label']}</span>
                <span class="crit-label">critiques the panel</span>
              </div>
              <div class="crit-text">{html.escape(crit)}</div>
            </div>""",unsafe_allow_html=True)

        st.session_state.panel_sessions.append({"question":panel_prompt,"responses":responses,"critiques":critiques})
