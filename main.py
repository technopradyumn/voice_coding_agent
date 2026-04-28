import speech_recognition as sr
import os
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import requests
from pydantic import BaseModel, Field
from typing import Optional
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

def main():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        recognizer.pause_threshold = 2
    
        SYSTEM_PROMPT = """
        You are a expert voice agent. You are given the transcript of whats user has said using voice.
        You need to output as if you are voice agent and whatsever you speak will be converted to audio using AI and played back to user.
        """
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        while True:
            print("Say something!")
            audio = recognizer.listen(source)

            print("Processing Audio... ")
            stt = recognizer.recognize_google(audio)
            print("Your said: ", stt)

            messages.append({"role": "user", "content": stt})

            response = client.chat.completions.create(
                model="gemini-1.5-flash",
                messages=messages
            )
            ai_response = response.choices[0].message.content
            print("AI Response: ", ai_response)

            asyncio.run(tts(speech=ai_response))

            
main()

