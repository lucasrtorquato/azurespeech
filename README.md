# 🎙️ Azure Speech Lab

Laboratório interativo para explorar os serviços de fala da **Azure AI Foundry**, baseado na atividade [mslearn-ai-fundamentals / 04a-speech](https://microsoftlearning.github.io/mslearn-ai-fundamentals/Instructions/Exercises/04a-speech.html).

## 🚀 Como rodar localmente

```bash
pip install -r requirements.txt
streamlit run azure_speech_lab.py
```

## 📦 Dependências

```
streamlit
azure-cognitiveservices-speech
streamlit-audiorecorder
requests
```

## 🔑 Configuração

Na barra lateral do app, preencha:

| Campo | Onde encontrar |
|---|---|
| **Endpoint do Agente** | Azure AI Foundry → Seu projeto → Endpoint |
| **Chave da API** | Azure AI Foundry → Seu projeto → Chaves e Endpoint |
| **Agent ID / Deployment Name** | Nome do deployment criado no Foundry |
| **Região Speech** | Ex: `eastus`, `brazilsouth` (para STT/TTS) |

## 🛠️ Serviços disponíveis

- 🤖 **Agente de Voz (Voice Live)** — conversa com o agente via texto ou microfone
- 🎤 **Speech to Text** — transcreve áudio em texto
- 🔊 **Text to Speech** — sintetiza texto em voz
- 🌐 **Tradução de Fala** — reconhece e traduz simultaneamente
- 🎭 **SSML** — síntese com controle de entonação e pausas
