"""
Azure Speech Lab — Streamlit
Baseado em: mslearn-ai-fundamentals / 04a-speech
Conexão via Azure AI Foundry (Voice Live Agent)

Dependências:
    pip install streamlit streamlit-audiorecorder azure-cognitiveservices-speech requests
"""

import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import tempfile, os, io, requests, json

# ─────────────────────────────────────────────
# Página
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Azure Speech Lab",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1,h2,h3 { font-family: 'Space Mono', monospace; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #1a1a2e, #16213e);
    color: #e0e0e0;
}

.main-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00d4ff, #7b2ff7, #ff6b6b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.subtitle {
    color: #a0aec0;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

.conn-card {
    background: rgba(99,179,237,0.07);
    border: 1px solid rgba(99,179,237,0.25);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}

.conn-card label { color: #a0aec0 !important; font-size: 0.85rem; }

.service-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 600;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}
.badge-stt       { background:#1a3a5c; color:#63b3ed; border:1px solid #2b6cb0; }
.badge-tts       { background:#1a3a3a; color:#68d391; border:1px solid #2f855a; }
.badge-trans     { background:#3a1a3a; color:#d6bcfa; border:1px solid #6b46c1; }
.badge-agent     { background:#2a1a3a; color:#b794f4; border:1px solid #805ad5; }
.badge-ssml      { background:#1a3a2a; color:#9ae6b4; border:1px solid #276749; }

.result-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-top: 0.8rem;
    font-size: 1rem;
    color: #e8f4fd;
    line-height: 1.7;
}

.result-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #63b3ed;
    margin-bottom: 0.4rem;
}

.agent-msg-user {
    background: rgba(99,179,237,0.1);
    border-left: 3px solid #63b3ed;
    border-radius: 0 10px 10px 0;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.95rem;
}

.agent-msg-assistant {
    background: rgba(183,148,244,0.08);
    border-left: 3px solid #b794f4;
    border-radius: 0 10px 10px 0;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.95rem;
}

.status-dot {
    display: inline-block;
    width: 9px; height: 9px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}
.dot-ok  { background: #68d391; }
.dot-err { background: #fc8181; }
.dot-off { background: #718096; }

.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin: 1.2rem 0;
}

.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div {
    background-color: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #e0e0e0 !important;
    border-radius: 8px !important;
}

.stButton>button {
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.stButton>button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(99,179,237,0.3) !important;
}

[data-testid="stSidebar"] {
    background: rgba(8,8,28,0.9) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}
[data-testid="stSidebar"] label { color:#a0aec0 !important; font-size:0.88rem; }
[data-testid="stSidebar"] h3 {
    color:#63b3ed !important;
    font-size:0.8rem;
    text-transform:uppercase;
    letter-spacing:0.08em;
}
.stAlert { border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────
SERVICES = {
    "🤖 Agente de Voz (Voice Live)":        "agent",
    "🎤 Speech to Text (STT)":              "stt",
    "🔊 Text to Speech (TTS)":              "tts",
    "🌐 Tradução de Fala":                  "translation",
    "🎭 Síntese com SSML":                  "ssml",
}

LANGUAGES = {
    "Português (Brasil)": "pt-BR",
    "English (US)":       "en-US",
    "Español (ES)":       "es-ES",
    "Français (FR)":      "fr-FR",
    "Deutsch (DE)":       "de-DE",
    "Italiano (IT)":      "it-IT",
    "日本語":              "ja-JP",
    "中文 (简体)":         "zh-CN",
}

VOICES = {
    "pt-BR": ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural", "pt-BR-BrendaNeural"],
    "en-US": ["en-US-JennyNeural",     "en-US-GuyNeural",     "en-US-AriaNeural"],
    "es-ES": ["es-ES-ElviraNeural",    "es-ES-AlvaroNeural"],
    "fr-FR": ["fr-FR-DeniseNeural",    "fr-FR-HenriNeural"],
    "de-DE": ["de-DE-KatjaNeural",     "de-DE-ConradNeural"],
    "it-IT": ["it-IT-ElsaNeural",      "it-IT-DiegoNeural"],
    "ja-JP": ["ja-JP-NanamiNeural",    "ja-JP-KeitaNeural"],
    "zh-CN": ["zh-CN-XiaoxiaoNeural",  "zh-CN-YunxiNeural"],
}

TARGET_LANGUAGES_TRANS = {
    "English": "en", "Português": "pt", "Español": "es",
    "Français": "fr", "Deutsch": "de", "Italiano": "it",
    "日本語": "ja",   "中文": "zh-Hans",
}


# ─────────────────────────────────────────────
# Microfone
# ─────────────────────────────────────────────
def render_mic_input(label_key: str = "mic") -> bytes | None:
    try:
        from audiorecorder import audiorecorder
        st.caption("Clique em ⏺ para gravar, ⏹ para parar.")
        seg = audiorecorder(
            start_prompt="⏺ Iniciar gravação",
            stop_prompt="⏹ Parar gravação",
            pause_prompt="",
            key=label_key,
            show_visualizer=True,
        )
        if len(seg) > 0:
            buf = io.BytesIO()
            seg.export(buf, format="wav")
            return buf.getvalue()
        return None
    except ImportError:
        st.warning("Instale `streamlit-audiorecorder` para usar o microfone.\n`pip install streamlit-audiorecorder`")
        up = st.file_uploader("Ou envie um arquivo de áudio", type=["wav","mp3","webm","ogg"], key=f"fb_{label_key}")
        return up.read() if up else None


# ─────────────────────────────────────────────
# Helpers Azure Speech SDK
# ─────────────────────────────────────────────
def ensure_wav(b: bytes) -> bytes:
    if b[:4] == b"RIFF":
        return b
    try:
        import subprocess
        with tempfile.NamedTemporaryFile(suffix=".audio", delete=False) as f:
            f.write(b); src = f.name
        dst = src + ".wav"
        subprocess.run(["ffmpeg","-y","-i",src,"-ar","16000","-ac","1",dst], capture_output=True)
        wav = open(dst,"rb").read()
        os.unlink(src); os.unlink(dst)
        return wav
    except Exception:
        return b


def stt_from_bytes(key, region, lang, audio: bytes):
    try:
        audio = ensure_wav(audio)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio); p = f.name
        cfg = speechsdk.SpeechConfig(subscription=key, region=region)
        cfg.speech_recognition_language = lang
        r = speechsdk.SpeechRecognizer(cfg, speechsdk.audio.AudioConfig(filename=p))
        res = r.recognize_once_async().get()
        os.unlink(p)
        if res.reason == speechsdk.ResultReason.RecognizedSpeech:
            return res.text, None
        if res.reason == speechsdk.ResultReason.NoMatch:
            return None, "Nenhuma fala reconhecida."
        c = res.cancellation_details
        return None, f"{c.reason}: {c.error_details}"
    except Exception as e:
        return None, str(e)


def tts_to_bytes(key, region, text, voice):
    try:
        cfg = speechsdk.SpeechConfig(subscription=key, region=region)
        cfg.speech_synthesis_voice_name = voice
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            p = f.name
        s = speechsdk.SpeechSynthesizer(cfg, speechsdk.audio.AudioOutputConfig(filename=p))
        res = s.speak_text_async(text).get()
        if res.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            data = open(p,"rb").read(); os.unlink(p)
            return data, None
        c = res.cancellation_details
        return None, f"{c.reason}: {c.error_details}"
    except Exception as e:
        return None, str(e)


def ssml_to_bytes(key, region, ssml):
    try:
        cfg = speechsdk.SpeechConfig(subscription=key, region=region)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            p = f.name
        s = speechsdk.SpeechSynthesizer(cfg, speechsdk.audio.AudioOutputConfig(filename=p))
        res = s.speak_ssml_async(ssml).get()
        if res.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            data = open(p,"rb").read(); os.unlink(p)
            return data, None
        c = res.cancellation_details
        return None, f"{c.reason}: {c.error_details}"
    except Exception as e:
        return None, str(e)


def translate_from_bytes(key, region, lang_from, langs_to, audio: bytes):
    try:
        audio = ensure_wav(audio)
        cfg = speechsdk.translation.SpeechTranslationConfig(subscription=key, region=region)
        cfg.speech_recognition_language = lang_from
        for l in langs_to: cfg.add_target_language(l)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio); p = f.name
        r = speechsdk.translation.TranslationRecognizer(cfg, speechsdk.audio.AudioConfig(filename=p))
        res = r.recognize_once_async().get()
        os.unlink(p)
        if res.reason == speechsdk.ResultReason.TranslatedSpeech:
            return {"original": res.text, "translations": dict(res.translations)}, None
        if res.reason == speechsdk.ResultReason.NoMatch:
            return None, "Nenhuma fala reconhecida."
        c = res.cancellation_details
        return None, f"{c.reason}: {c.error_details}"
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────
# Azure AI Foundry — Voice Live Agent (REST)
# ─────────────────────────────────────────────
def call_agent(endpoint: str, api_key: str, agent_id: str,
               user_message: str, history: list[dict]) -> tuple[str, str | None]:
    """
    Chama o agente via API de conversação do Azure AI Foundry.
    Retorna (resposta_texto, erro_ou_None).
    """
    # Monta URL — normaliza barra final
    base = endpoint.rstrip("/")
    url = f"{base}/openai/deployments/{agent_id}/chat/completions?api-version=2025-01-01-preview"

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    messages = history + [{"role": "user", "content": user_message}]

    payload = {
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        reply = data["choices"][0]["message"]["content"]
        return reply, None
    except requests.exceptions.HTTPError as e:
        try:
            detail = resp.json().get("error", {}).get("message", str(e))
        except Exception:
            detail = str(e)
        return None, f"HTTP {resp.status_code}: {detail}"
    except Exception as e:
        return None, str(e)


def agent_tts(text: str, key: str, region: str, voice: str) -> bytes | None:
    """Sintetiza a resposta do agente em áudio."""
    data, _ = tts_to_bytes(key, region, text, voice)
    return data


# ─────────────────────────────────────────────
# Seletor de entrada de áudio reutilizável
# ─────────────────────────────────────────────
def audio_input_selector(key_prefix: str, with_text: bool = False):
    modes = ["🎙️ Microfone (navegador)", "📁 Upload de arquivo"]
    if with_text:
        modes.append("✍️ Texto direto")
    mode = st.radio("Fonte de entrada", modes, horizontal=True, key=f"{key_prefix}_mode")
    audio_bytes, text_val = None, None
    if "Microfone" in mode:
        audio_bytes = render_mic_input(f"{key_prefix}_mic")
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            st.caption("✅ Áudio capturado.")
    elif "Upload" in mode:
        up = st.file_uploader("Arquivo de áudio", type=["wav","mp3","webm","ogg"], key=f"{key_prefix}_up")
        if up:
            audio_bytes = up.read()
            st.audio(audio_bytes)
    elif "Texto" in mode:
        text_val = st.text_area("Digite o texto", placeholder="Digite aqui...", height=90, key=f"{key_prefix}_txt")
    return audio_bytes, text_val


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<h3>🔗 Conexão — Azure AI Foundry</h3>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="conn-card">', unsafe_allow_html=True)

        agent_endpoint = st.text_input(
            "🌐 Endpoint do Agente",
            placeholder="https://seu-projeto.openai.azure.com",
            help="Azure AI Foundry → Seu projeto → Endpoint",
        )
        agent_api_key = st.text_input(
            "🔑 Chave da API",
            type="password",
            placeholder="Cole sua API Key aqui",
            help="Azure AI Foundry → Seu projeto → Chaves e Endpoint",
        )
        agent_id = st.text_input(
            "🤖 Agent ID / Deployment Name",
            placeholder="ex: gpt-4o-mini  ou  meu-agente",
            help="Nome do deployment do modelo ou do agente criado no Foundry",
        )

        st.markdown('</div>', unsafe_allow_html=True)

    # Campos extras para serviços Speech SDK (STT/TTS/Tradução/SSML)
    with st.expander("⚙️ Configurações adicionais (STT / TTS / Tradução)", expanded=False):
        speech_region = st.text_input(
            "🌍 Região Speech",
            placeholder="ex: eastus, brazilsouth",
            help="Usada nos serviços STT, TTS, Tradução e SSML",
        )
        st.caption("A chave usada é a mesma do campo acima.")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<h3>🗣️ Idioma & Voz</h3>', unsafe_allow_html=True)

    selected_language_name = st.selectbox("Idioma de entrada", list(LANGUAGES.keys()), index=0)
    selected_language_code = LANGUAGES[selected_language_name]
    available_voices = VOICES.get(selected_language_code, ["pt-BR-FranciscaNeural"])
    selected_voice = st.selectbox("Voz para TTS / Agente", available_voices)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Status de conexão
    agent_ok  = bool(agent_endpoint and agent_api_key and agent_id)
    speech_ok = bool(agent_api_key and speech_region)

    st.markdown(
        f'<span class="status-dot {"dot-ok" if agent_ok else "dot-err"}"></span>'
        f'{"Agente configurado" if agent_ok else "Agente: preencha endpoint, chave e ID"}',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<span class="status-dot {"dot-ok" if speech_ok else "dot-off"}"></span>'
        f'{"Speech SDK pronto" if speech_ok else "Speech: preencha região (expander acima)"}',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.73rem; color:#718096; line-height:1.8;'>
    <b>📚 Referência</b><br>
    mslearn-ai-fundamentals — 04a-speech<br><br>
    <b>📦 Dependências:</b><br>
    <code>pip install streamlit</code><br>
    <code>pip install azure-cognitiveservices-speech</code><br>
    <code>pip install streamlit-audiorecorder</code><br>
    <code>pip install requests</code>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Cabeçalho
# ─────────────────────────────────────────────
st.markdown('<p class="main-title">🎙️ Azure Speech Lab</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Laboratório interativo — Azure AI Foundry Voice Live Agent • mslearn-ai-fundamentals / 04a-speech</p>',
    unsafe_allow_html=True,
)

st.markdown("### Selecione o Serviço")
service_label = st.selectbox("Serviço", list(SERVICES.keys()), label_visibility="collapsed")
svc = SERVICES[service_label]

badge_map = {
    "agent":       ("AGENTE VOICE LIVE", "badge-agent"),
    "stt":         ("STT",               "badge-stt"),
    "tts":         ("TTS",               "badge-tts"),
    "translation": ("TRADUÇÃO",          "badge-trans"),
    "ssml":        ("SSML",              "badge-ssml"),
}
bt, bc = badge_map[svc]
st.markdown(f'<span class="service-badge {bc}">{bt}</span>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# ── AGENTE DE VOZ (Voice Live) ───────────────
# ══════════════════════════════════════════════
if svc == "agent":
    st.markdown("#### 🤖 Agente de Voz — Azure AI Foundry Voice Live")
    st.markdown(
        "Converse com o agente via **texto** ou **voz**. "
        "A resposta é exibida em texto e também sintetizada em áudio."
    )

    # Histórico de conversa
    if "agent_history" not in st.session_state:
        st.session_state.agent_history = []

    # System prompt
    with st.expander("🛠️ System Prompt (instrução do agente)", expanded=False):
        system_prompt = st.text_area(
            "Instrução do sistema",
            value="Você é um assistente de voz inteligente e prestativo. Responda de forma clara e concisa.",
            height=100,
            key="sys_prompt",
        )
        if st.button("↺ Resetar conversa", key="reset_conv"):
            st.session_state.agent_history = []
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Entrada do usuário
    st.markdown("**Envie sua mensagem:**")
    audio_bytes, text_input = audio_input_selector(key_prefix="agent", with_text=True)

    # TTS na resposta
    tts_response = st.checkbox("🔊 Ouvir resposta do agente (TTS)", value=True)

    col1, _ = st.columns([1, 3])
    with col1:
        send_btn = st.button("▶ Enviar ao Agente", use_container_width=True, type="primary")

    if send_btn:
        if not agent_ok:
            st.error("Preencha Endpoint, Chave e Agent ID na barra lateral.")
        else:
            # 1. Transcreve áudio → texto (se vier do microfone/upload)
            user_text = text_input or ""
            if audio_bytes and not user_text:
                if not speech_ok:
                    st.error("Para transcrever voz, preencha também a **Região Speech** no expander da barra lateral.")
                    st.stop()
                with st.spinner("Transcrevendo áudio..."):
                    user_text, err = stt_from_bytes(agent_api_key, speech_region, selected_language_code, audio_bytes)
                if err:
                    st.error(f"Erro STT: {err}")
                    st.stop()

            if not user_text or not user_text.strip():
                st.warning("Digite ou grave uma mensagem antes de enviar.")
                st.stop()

            # 2. Monta histórico com system prompt
            history = []
            if system_prompt.strip():
                history.append({"role": "system", "content": system_prompt.strip()})
            history += st.session_state.agent_history

            # 3. Chama o agente
            with st.spinner("Aguardando resposta do agente..."):
                reply, err = call_agent(agent_endpoint, agent_api_key, agent_id, user_text, history)

            if err:
                st.error(f"Erro ao chamar o agente: {err}")
                st.stop()

            # 4. Salva no histórico
            st.session_state.agent_history.append({"role": "user",      "content": user_text})
            st.session_state.agent_history.append({"role": "assistant",  "content": reply})

            # 5. TTS na resposta
            if tts_response and speech_ok:
                with st.spinner("Sintetizando resposta..."):
                    audio_out = agent_tts(reply, agent_api_key, speech_region, selected_voice)
                if audio_out:
                    st.audio(audio_out, format="audio/wav", autoplay=True)

    # Exibe histórico
    if st.session_state.agent_history:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("**Histórico da conversa:**")
        for msg in st.session_state.agent_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                st.markdown(f'<div class="agent-msg-user">👤 <b>Você:</b> {content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="agent-msg-assistant">🤖 <b>Agente:</b> {content}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# ── STT ──────────────────────────────────────
# ══════════════════════════════════════════════
elif svc == "stt":
    st.markdown("#### 🎤 Reconhecimento de Fala (Speech to Text)")
    st.markdown("Converte áudio em texto usando Azure Cognitive Services Speech.")

    audio_bytes, _ = audio_input_selector("stt")

    text_hint = st.text_input("📝 Texto esperado (opcional, para comparação)", placeholder="Ex: Como funciona o reconhecimento de fala?")

    col1, _ = st.columns([1, 3])
    with col1:
        run = st.button("▶ Reconhecer", use_container_width=True, type="primary")

    if run:
        if not speech_ok:
            st.error("Preencha a Chave da API e a Região Speech na barra lateral.")
        elif not audio_bytes:
            st.warning("Grave ou envie um áudio antes de processar.")
        else:
            with st.spinner("Enviando para Azure Speech..."):
                text, err = stt_from_bytes(agent_api_key, speech_region, selected_language_code, audio_bytes)
            if err:
                st.error(f"Erro: {err}")
            elif text:
                st.markdown('<div class="result-label">Texto reconhecido</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-box">💬 {text}</div>', unsafe_allow_html=True)
                if text_hint:
                    match = text_hint.strip().lower() in text.lower()
                    st.markdown(f"**Correspondência:** {'✅ Sim' if match else '❌ Diferente'}")


# ══════════════════════════════════════════════
# ── TTS ──────────────────────────────────────
# ══════════════════════════════════════════════
elif svc == "tts":
    st.markdown("#### 🔊 Síntese de Fala (Text to Speech)")
    st.markdown("Converte texto em fala com as vozes neurais da Azure.")

    tts_text = st.text_area("Texto para sintetizar", placeholder="Digite aqui...", height=130)

    col1, _ = st.columns([1, 3])
    with col1:
        run = st.button("▶ Sintetizar", use_container_width=True, type="primary")

    if run:
        if not speech_ok:
            st.error("Preencha a Chave da API e a Região Speech na barra lateral.")
        elif not tts_text.strip():
            st.warning("Digite um texto para sintetizar.")
        else:
            with st.spinner(f"Gerando com a voz '{selected_voice}'..."):
                audio_data, err = tts_to_bytes(agent_api_key, speech_region, tts_text, selected_voice)
            if err:
                st.error(f"Erro: {err}")
            elif audio_data:
                st.success("✅ Áudio gerado!")
                st.audio(audio_data, format="audio/wav")
                st.download_button("⬇️ Baixar .wav", audio_data, "tts_output.wav", "audio/wav")


# ══════════════════════════════════════════════
# ── TRADUÇÃO ─────────────────────────────────
# ══════════════════════════════════════════════
elif svc == "translation":
    st.markdown("#### 🌐 Tradução de Fala")
    st.markdown("Reconhece fala e traduz para um ou mais idiomas simultaneamente.")

    target_names = st.multiselect("Idiomas de destino", list(TARGET_LANGUAGES_TRANS.keys()), default=["English"])
    target_codes = [TARGET_LANGUAGES_TRANS[n] for n in target_names]

    audio_bytes, _ = audio_input_selector("trans")

    col1, _ = st.columns([1, 3])
    with col1:
        run = st.button("▶ Traduzir", use_container_width=True, type="primary")

    if run:
        if not speech_ok:
            st.error("Preencha a Chave da API e a Região Speech na barra lateral.")
        elif not target_codes:
            st.warning("Selecione ao menos um idioma de destino.")
        elif not audio_bytes:
            st.warning("Grave ou envie um áudio antes de processar.")
        else:
            with st.spinner("Traduzindo..."):
                result, err = translate_from_bytes(agent_api_key, speech_region, selected_language_code, target_codes, audio_bytes)
            if err:
                st.error(f"Erro: {err}")
            elif result:
                st.markdown('<div class="result-label">Original reconhecido</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-box">🗣️ {result["original"]}</div>', unsafe_allow_html=True)
                st.markdown('<div class="result-label" style="margin-top:1rem;">Traduções</div>', unsafe_allow_html=True)
                for code, tr in result["translations"].items():
                    name = next((k for k, v in TARGET_LANGUAGES_TRANS.items() if v == code), code)
                    st.markdown(f'<div class="result-box"><b>{name}:</b> {tr}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# ── SSML ─────────────────────────────────────
# ══════════════════════════════════════════════
elif svc == "ssml":
    st.markdown("#### 🎭 Síntese com SSML")
    st.markdown("Controle entonação, pausas, velocidade e volume com marcação SSML.")

    ssml_default = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{selected_language_code}">
    <voice name="{selected_voice}">
        Olá! Bem-vindo ao laboratório de <emphasis level="strong">Azure Speech</emphasis>.
        <break time="500ms"/>
        <prosody rate="slow" pitch="+5%">
            Hoje vamos explorar o poder da síntese de voz.
        </prosody>
        <break time="300ms"/>
        Isso é <prosody volume="loud">incrivelmente poderoso!</prosody>
    </voice>
</speak>"""

    ssml_input = st.text_area("SSML personalizado", value=ssml_default, height=220)

    st.markdown("""
    <details>
    <summary style='cursor:pointer;color:#63b3ed;font-size:0.88rem;'>💡 Tags SSML úteis</summary>
    <div style='background:rgba(255,255,255,0.04);padding:1rem;border-radius:8px;font-size:0.83rem;margin-top:0.4rem;'>
    <ul>
    <li><code>&lt;break time="500ms"/&gt;</code> — pausa</li>
    <li><code>&lt;prosody rate="slow"&gt;</code> — velocidade: slow / medium / fast</li>
    <li><code>&lt;prosody pitch="+10%"&gt;</code> — tom de voz</li>
    <li><code>&lt;emphasis level="strong"&gt;</code> — ênfase</li>
    <li><code>&lt;prosody volume="loud"&gt;</code> — volume</li>
    </ul>
    </div>
    </details>
    """, unsafe_allow_html=True)

    col1, _ = st.columns([1, 3])
    with col1:
        run = st.button("▶ Gerar Fala", use_container_width=True, type="primary")

    if run:
        if not speech_ok:
            st.error("Preencha a Chave da API e a Região Speech na barra lateral.")
        elif not ssml_input.strip():
            st.warning("O campo SSML não pode estar vazio.")
        else:
            with st.spinner("Sintetizando com SSML..."):
                audio_data, err = ssml_to_bytes(agent_api_key, speech_region, ssml_input)
            if err:
                st.error(f"Erro: {err}")
            elif audio_data:
                st.success("✅ Áudio SSML gerado!")
                st.audio(audio_data, format="audio/wav")
                st.download_button("⬇️ Baixar .wav", audio_data, "ssml_output.wav", "audio/wav")


# ─────────────────────────────────────────────
# Rodapé
# ─────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;color:#4a5568;font-size:0.75rem;font-family:Space Mono,monospace;'>
Azure Speech Lab &nbsp;•&nbsp; mslearn-ai-fundamentals / 04a-speech &nbsp;•&nbsp; Streamlit + Azure AI Foundry
</div>
""", unsafe_allow_html=True)
