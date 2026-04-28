import os
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import requests
from pydantic import BaseModel, Field
from typing import Optional
import speech_recognition as sr
import asyncio
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

async_client = AsyncOpenAI(
  api_key=os.getenv("OPENAI_API_KEY"),
  base_url="https://api.openai.com/v1/",
)

async def tts(speech: str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=speech,
        instructions="Speak in a cheerful and positive tone.",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)


def run_command(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout.strip()
        error  = result.stderr.strip()
        if result.returncode != 0:
            return f"Error (exit {result.returncode}): {error or output}"
        return output or "Command executed successfully with no output."
    except Exception as e:
        return f"Error running command: {e}"


def write_file(args: str) -> str:
    try:
        data = json.loads(args)
        path, content = data["path"], data["content"]
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File '{path}' written successfully ({len(content)} chars)."
    except json.JSONDecodeError:
        return "Error: input must be valid JSON with 'path' and 'content' keys."
    except Exception as e:
        return f"Error writing file: {e}"

def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def list_directory(path: str = ".") -> str:
    try:
        files = os.listdir(path)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing directory: {e}"

def get_weather_report(location: str) -> str:
    url = f"https://wttr.in/{location.lower()}?format=%C+%t+%m"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The current weather in {location} is: {response.text}"
    return "Oops! Unable to fetch weather data at the moment."


available_tools = {
    "_get_weather": get_weather_report,
    "_run_command": run_command,
    "_write_file":  write_file,
    "_read_file":   read_file,
    "_list_directory": list_directory,
}

SYSTEM_PROMPT = """
You are an expert AI assistant. You solve user queries step by step using the
START , PLAN , TOOL , OBSERVE , OUTPUT workflow.

CRITICAL RULES:
- Always respond with a single JSON object (never a list).
- Only run one step at a time and wait for the next instruction.
- NEVER use printf/cat/echo/type in _run_command to write file content.
- ALL tool inputs that take JSON must be a valid JSON string.

FILE MODIFICATION RULE (very important):
- To ADD code to an existing file: use _patch_file (if available) with a small 'old' anchor + 'new' replacement.
  NEVER rewrite the whole file with _write_file the model will truncate large files.
- To CREATE a new file: use _write_file.
- To READ a file: use _read_file (if available) FIRST, before any modification.

Output JSON format:
{
  "step": "START" | "PLAN" | "TOOL" | "OBSERVE" | "OUTPUT",
  "content": "string",
  "tool": "tool_name  (only for TOOL step)",
  "input": "tool input (only for TOOL step)"
}

Available tools:

_get_weather(location: str)
  Input: plain string â€” city name.

_run_command(command: str)
  Input: plain string â€” a shell command.
  Use for: mkdir, dir, running scripts, etc. NOT for writing file content.

_write_file(json_string)
  Input: {"path": "...", "content": "..."}
  Creates or OVERWRITES a file. Use ONLY for brand-new files.

_read_file(path: str)
  Input: plain string - path to file.

_list_directory(path: str)
  Input: plain string - path to directory.
"""


class AgentStep(BaseModel):
    step:    str           = Field(..., description="START | PLAN | TOOL | OBSERVE | OUTPUT")
    content: Optional[str] = Field(None)
    tool:    Optional[str] = Field(None)
    input:   Optional[str] = Field(None)

print()
messages = [{"role": "system", "content": SYSTEM_PROMPT}]

recognizer = sr.Recognizer()
with sr.Microphone() as source:
    print("Listening...")
    print("Say something!")
    audio = recognizer.listen(source)

    print("Processing Audio... ")
    stt = recognizer.recognize_google(audio)
    print("You said: ", stt)
    recognizer.adjust_for_ambient_noise(source)
    recognizer.pause_threshold = 2

    while True:

        messages.append({"role": "user", "content": stt})

        response = client.chat.completions.parse(
            model="gemini-robotics-er-1.6-preview",
            response_format=AgentStep,
            messages=messages,
        )

        raw = response.choices[0].message.content
        parsed: AgentStep = response.choices[0].message.parsed
        messages.append({"role": "assistant", "content": raw})

        step = parsed.step

        if step == "START":
            print(f"Start  : {parsed.content}")
            messages.append({"role": "user", "content": "Proceed."})

        elif step == "PLAN":
            print(f"Plan   : {parsed.content}")
            messages.append({"role": "user", "content": "Proceed."})

        elif step == "TOOL":
            tool_name  = parsed.tool
            tool_input = parsed.input or ""
            preview    = tool_input[:120] + ("..." if len(tool_input) > 120 else "")
            print(f"Tool   : {tool_name}({preview})")

            if tool_name in available_tools:
                tool_result = available_tools[tool_name](tool_input)
            else:
                tool_result = f"Error: tool '{tool_name}' not found."

            print(f"Result : {tool_result[:300]}{'...' if len(tool_result) > 300 else ''}")
            observe_msg = json.dumps({
                "step": "OBSERVE", "tool": tool_name,
                "input": tool_input, "output": tool_result
            })
            messages.append({"role": "user", "content": observe_msg})

        elif step == "OBSERVE":
            print(f"Observe: {parsed.content}")
            messages.append({"role": "user", "content": "Proceed."})

        elif step == "OUTPUT":
            print(f"\nAnswer : {parsed.content}")
            ai_response = response.choices[0].message.content
            print("AI Response: ", ai_response)

            asyncio.run(tts(speech=ai_response))
            break

        else:
            print(f"Unknown step '{step}', stopping.")
            break

print()