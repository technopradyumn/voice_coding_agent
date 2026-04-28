<div align="center">

# 🎙️ Voice Coding Agent

**A production-grade AI voice assistant that listens, thinks, acts, and speaks — powered by Google Gemini + OpenAI TTS.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-API-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![OpenAI](https://img.shields.io/badge/OpenAI-TTS-412991?style=for-the-badge&logo=openai&logoColor=white)](https://platform.openai.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-f97316?style=for-the-badge)](https://github.com/technopradyumn/voice_coding_agent/pulls)

<br/>

> _"Speak to your computer. It listens, plans, acts, and talks back."_

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [How It Works — The Agentic Loop](#-how-it-works--the-agentic-loop)
- [Project Structure](#-project-structure)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Environment Variables](#-environment-variables)
- [Usage](#-usage)
- [Deep Code Walkthrough](#-deep-code-walkthrough)
- [Available Tools](#-available-tools)
- [Rate Limits & Model Selection Guide](#-rate-limits--model-selection-guide)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🧠 Overview

**Voice Coding Agent** is an end-to-end voice-driven AI system that allows you to interact with your computer and file system using **natural spoken language**. You speak — it transcribes your speech, reasons through a structured multi-step plan, executes real tools (file reads, writes, shell commands, weather), and speaks the result back to you using a high-quality AI voice.

It comes in **two modes**:

| Script | Mode | Description |
|--------|------|-------------|
| `codex.py` | **Agentic (Smart)** | Uses a structured START→PLAN→TOOL→OBSERVE→OUTPUT loop. Best for complex tasks like modifying files, running code, querying APIs. |
| `main.py` | **Conversational (Simple)** | Simple voice chat loop. No tool use. Great for Q&A and conversation. |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    VOICE CODING AGENT                    │
│                                                          │
│   🎤 Microphone Input                                    │
│         │                                                │
│         ▼                                                │
│   [ SpeechRecognition ]  ──▶  Google STT (Free)         │
│         │                                                │
│         ▼                                                │
│   [ Gemini LLM ]         ──▶  Agentic ReAct Loop        │
│    (via OpenAI API                                       │
│     compatibility layer)  START → PLAN → TOOL            │
│         │                         │                      │
│         │              ┌──────────┘                      │
│         │              ▼                                 │
│         │      [ Tool Executor ]                         │
│         │       • _get_weather                           │
│         │       • _run_command                           │
│         │       • _write_file                            │
│         │       • _read_file                             │
│         │       • _list_directory                        │
│         │              │                                 │
│         │              ▼                                 │
│         │       OBSERVE → OUTPUT                         │
│         │                                                │
│         ▼                                                │
│   [ OpenAI TTS ]         ──▶  gpt-4o-mini-tts           │
│         │                     Voice: Coral (cheerful)    │
│         ▼                                                │
│   🔊 Speaker Output (PCM Streaming)                     │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 How It Works — The Agentic Loop

The core intelligence of `codex.py` is a **ReAct-style agentic loop** — a proven pattern used in production AI systems. The agent reasons through problems **one step at a time**, never rushing to an answer.

```
User speaks: "Add a dark mode button to my todo app"
         │
         ▼
┌─────────────────┐
│     START       │  Agent acknowledges the task
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     PLAN        │  "I'll read the current HTML, then modify it"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     TOOL        │  Calls _read_file("todo-app/index.html")
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    OBSERVE      │  Receives file content, analyses it
└────────┬────────┘
         │
    (loops back to PLAN if more steps needed)
         │
         ▼
┌─────────────────┐
│     OUTPUT      │  Delivers the final answer / confirmation
└─────────────────┘
         │
         ▼
   🔊 TTS speaks the answer aloud
```

Each step is a **structured JSON object** validated by Pydantic, ensuring the LLM never goes off-format:

```python
class AgentStep(BaseModel):
    step:    str           # "START" | "PLAN" | "TOOL" | "OBSERVE" | "OUTPUT"
    content: Optional[str] # Human-readable description of this step
    tool:    Optional[str] # Tool name (only for TOOL step)
    input:   Optional[str] # Tool input (only for TOOL step)
```

---

## 📂 Project Structure

```
voice_coding_agent/
│
├── codex.py              # 🤖 Main agentic voice agent (START→PLAN→TOOL→OUTPUT loop)
├── main.py               # 💬 Simple conversational voice agent (no tools)
├── requirements.txt      # 📦 All Python dependencies (pinned versions)
├── .env                  # 🔑 API keys (NEVER committed to git)
├── .gitignore            # 🛡️ Protects secrets & cache from version control
└── README.md             # 📖 This file
```

---

## ✨ Features

- 🎤 **Real-time voice input** via microphone using `SpeechRecognition`
- 🧠 **Google Gemini LLM** for intelligent multi-step reasoning
- 🔁 **Agentic ReAct loop** — plan, act, observe, repeat until done
- 🛠️ **Tool use** — read/write files, run shell commands, fetch live weather
- 🔊 **AI Voice output** — streams audio response via OpenAI's `gpt-4o-mini-tts`
- 📐 **Structured outputs** via Pydantic — guarantees valid JSON from LLM every time
- 🔒 **Secrets-safe** — `.env` excluded from git, keys loaded at runtime
- 🌐 **Gemini via OpenAI SDK** — uses Google's OpenAI-compatible endpoint

---

## 🧰 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Speech-to-Text** | Google Speech Recognition (free) | Converts microphone input to text |
| **LLM / Brain** | Google Gemini (`gemini-2.0-flash`) | Reasoning, planning, tool orchestration |
| **API Compatibility** | OpenAI Python SDK + Gemini base URL | Call Gemini using the familiar OpenAI interface |
| **Structured Output** | Pydantic `BaseModel` + `.parse()` | Forces LLM to return valid, typed JSON |
| **Text-to-Speech** | OpenAI `gpt-4o-mini-tts` (streaming) | Converts AI response to spoken audio |
| **Audio Playback** | `LocalAudioPlayer` (PCM streaming) | Plays audio in real-time as it streams |
| **Environment** | `python-dotenv` | Loads API keys from `.env` file |
| **HTTP** | `requests` | Fetches live weather data |

---

## ✅ Prerequisites

Before you begin, ensure you have the following:

- **Python 3.10 or higher** — [Download here](https://python.org/downloads)
- **pip** (comes with Python)
- **A working microphone**
- **Google Gemini API key** — [Get it free at ai.google.dev](https://ai.google.dev)
- **OpenAI API key** (for TTS only) — [Get it at platform.openai.com](https://platform.openai.com)
- **PyAudio** — required by `SpeechRecognition` for microphone access

> ⚠️ **Windows users**: PyAudio requires a special install step. See the setup below.

---

## 🚀 Installation & Setup

### Step 1 — Clone the Repository

```bash
git clone https://github.com/technopradyumn/voice_coding_agent.git
cd voice_coding_agent
```

### Step 2 — Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3 — Install PyAudio (Windows — Do This First)

PyAudio requires native audio bindings. On Windows, install via `pipwin`:

```bash
pip install pipwin
pipwin install pyaudio
```

> **macOS**: `brew install portaudio && pip install pyaudio`
> **Linux**: `sudo apt-get install portaudio19-dev && pip install pyaudio`

### Step 4 — Install All Dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Windows
copy NUL .env

# macOS/Linux
touch .env
```

Then open `.env` and add your API keys (see next section).

---

## 🔑 Environment Variables

Your `.env` file must contain the following:

```env
# ─────────────────────────────────────────────
# Google Gemini API Key
# Get yours free at: https://ai.google.dev
# ─────────────────────────────────────────────
GEMINI_API_KEY=your_gemini_api_key_here

# ─────────────────────────────────────────────
# OpenAI API Key (used ONLY for TTS voice output)
# Get yours at: https://platform.openai.com
# ─────────────────────────────────────────────
OPENAI_API_KEY=your_openai_api_key_here
```

> 🔒 **Security**: The `.env` file is listed in `.gitignore` and will **never** be committed to GitHub. Your keys are safe.

---

## ▶️ Usage

### Run the Agentic Agent (Recommended)

```bash
python codex.py
```

This starts the full agentic loop:
1. 🎤 Microphone activates — **say your command**
2. 🧠 Gemini reasons through the task step by step
3. 🛠️ Tools are called automatically as needed
4. 🔊 The final answer is spoken back to you

**Example voice commands:**
```
"What is the weather in Mumbai?"
"List the files in the current directory"
"Read the index.html file"
"Create a file called notes.txt with my shopping list"
"Run the script main.py"
```

### Run the Simple Conversational Agent

```bash
python main.py
```

Starts a continuous voice chat loop — speak, get a response, speak again. No tool use, pure conversation.

---

## 🔬 Deep Code Walkthrough

### `codex.py` — The Agentic Agent

#### 1. Client Initialization (Lines 18–26)

```python
# Gemini client using OpenAI-compatible endpoint
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# OpenAI async client for streaming TTS
async_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1/",
)
```

> **Why OpenAI SDK for Gemini?** Google provides an OpenAI-compatible REST endpoint, meaning you can use the battle-tested OpenAI Python SDK — including structured output parsing (`.parse()`) — with zero code changes.

#### 2. Streaming TTS (Lines 28–36)

```python
async def tts(speech: str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=speech,
        instructions="Speak in a cheerful and positive tone.",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)
```

> **Key design:** The response is streamed as raw **PCM audio** — this means playback begins almost instantly, before the full audio is generated. This eliminates the delay you'd get if you waited for the full file to download.

#### 3. Tool Implementations (Lines 39–84)

Each tool is a plain Python function with a consistent signature:

```python
def run_command(command: str) -> str:     # Execute shell commands
def write_file(args: str) -> str:         # Create/overwrite files (JSON input)
def read_file(path: str) -> str:          # Read file content
def list_directory(path: str) -> str:     # List files in a folder
def get_weather_report(location: str) -> str:  # Fetch live weather
```

Tools are registered in a dispatch dict for clean, safe lookup:

```python
available_tools = {
    "_get_weather":    get_weather_report,
    "_run_command":    run_command,
    "_write_file":     write_file,
    "_read_file":      read_file,
    "_list_directory": list_directory,
}
```

#### 4. Structured Output with Pydantic (Lines 139–143)

```python
class AgentStep(BaseModel):
    step:    str           = Field(..., description="START | PLAN | TOOL | OBSERVE | OUTPUT")
    content: Optional[str] = Field(None)
    tool:    Optional[str] = Field(None)
    input:   Optional[str] = Field(None)
```

When calling `client.chat.completions.parse(response_format=AgentStep, ...)`, the OpenAI SDK + Gemini automatically enforce this schema. If the model tries to return malformed JSON, it's automatically repaired or retried. You always get a valid `AgentStep` object.

#### 5. The Agentic Loop (Lines 162–218)

```python
while True:
    messages.append({"role": "user", "content": stt})

    response = client.chat.completions.parse(
        model="gemini-2.0-flash",
        response_format=AgentStep,
        messages=messages,
    )

    parsed: AgentStep = response.choices[0].message.parsed

    if parsed.step == "TOOL":
        tool_result = available_tools[parsed.tool](parsed.input)
        # Inject tool result back into conversation
        messages.append({"role": "user", "content": observe_msg})

    elif parsed.step == "OUTPUT":
        asyncio.run(tts(speech=ai_response))
        break  # Exit loop — task complete
```

> **Conversation memory**: All messages (user, assistant, tool results) accumulate in the `messages` list. This gives the LLM full context of everything that happened, allowing it to chain multi-step reasoning correctly.

---

## 🛠️ Available Tools

| Tool | Input | What It Does |
|------|-------|-------------|
| `_get_weather` | `"Mumbai"` | Fetches real-time weather via [wttr.in](https://wttr.in) |
| `_run_command` | `"dir"` or `"python script.py"` | Executes any shell command, returns stdout/stderr |
| `_write_file` | `{"path": "file.txt", "content": "..."}` | Creates or overwrites a file |
| `_read_file` | `"path/to/file.txt"` | Returns full file content as string |
| `_list_directory` | `"."` or `"./src"` | Returns list of files in the specified directory |

---

## ⚡ Rate Limits & Model Selection Guide

The Gemini free tier has per-model rate limits. Since the agentic loop makes **multiple API calls per query**, choose a model with sufficient RPM:

| Model | Free RPM | Recommended For |
|-------|----------|----------------|
| `gemini-2.0-flash` | 15 | ✅ **Best overall** — fast, smart, ample quota |
| `gemini-1.5-flash` | 15 | ✅ Stable alternative |
| `gemini-1.5-flash-8b` | 15 | ✅ Fastest/lightest |
| `gemini-2.5-flash-preview-04-17` | 10 | ✅ Most capable on free tier |
| `gemini-robotics-er-1.6-preview` | 5 | ❌ Too low for agentic use |

Change the model in `codex.py` line 167:
```python
model="gemini-2.0-flash",   # Recommended
```

---

## 🐞 Troubleshooting

### `RateLimitError 429` — Quota Exceeded
- Switch to `gemini-2.0-flash` (15 RPM free) instead of preview models
- Wait 60 seconds between runs for quota reset
- Or upgrade to a paid Gemini API plan at [ai.dev](https://ai.dev/rate-limit)

### `OSError: [Errno -9999] Unanticipated host error` — Microphone Not Found
- Check that your microphone is plugged in and set as the default recording device
- On Windows: Settings → Sound → Input → choose your microphone

### `ModuleNotFoundError: No module named 'pyaudio'`
```bash
pip install pipwin
pipwin install pyaudio
```

### `UnknownValueError` — Speech Not Recognized
- Speak clearly and closer to the microphone
- Reduce background noise
- The `adjust_for_ambient_noise()` call calibrates for your environment at startup

### `insufficient_quota` — OpenAI TTS Error
- Your OpenAI account has no credits for TTS
- Add billing at [platform.openai.com/account/billing](https://platform.openai.com/account/billing)
- Alternatively, comment out `asyncio.run(tts(...))` to disable voice output

---

## 🗺️ Roadmap

- [ ] 🔁 Continuous listen loop (always-on mode)
- [ ] 🌐 Web browser tool (open URLs, search Google)
- [ ] 📋 Clipboard read/write tool
- [ ] 🖥️ Screenshot + Vision tool (see your screen)
- [ ] 📁 Multi-file patch tool (diff-based file editing)
- [ ] 💾 Conversation memory persistence (across sessions)
- [ ] 🐍 Python REPL execution tool
- [ ] 🎛️ GUI launcher with mute/settings controls
- [ ] 🌍 Multi-language voice support

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feat/my-new-tool`
3. **Commit** your changes: `git commit -m 'feat: add web search tool'`
4. **Push** to the branch: `git push origin feat/my-new-tool`
5. **Open a Pull Request**

Please follow these guidelines:
- Keep tool functions pure and side-effect-free where possible
- Add your tool to `available_tools` dict and `SYSTEM_PROMPT` documentation
- Test with at least 3 different voice commands before submitting

---

## 📄 License

This project is licensed under the **MIT License** — you are free to use, modify, and distribute it.

---

<div align="center">

**Built with ❤️ by [Pradyumn](https://github.com/technopradyumn)**

⭐ **Star this repo if it helped you!** ⭐

</div>
