import os
import struct

import pvporcupine
import pyaudio
import requests
import speech_recognition as sr

# ================== CONFIG ==================

# 👉 PASTE YOUR PICOVOICE ACCESS KEY HERE:
ACCESS_KEY = "pv_z5GeuLBli3kyYr64C9xmqb6ohCSFg/fR3BcjmSfM9agHbIjyZ+OtOQ=="

# Flask server URL (your existing JARVIS backend)
SERVER_URL = "http://127.0.0.1:5001/ask"

# Keyword file path (jarvis.ppn in your project folder)
KEYWORD_PATH = "jarvis.ppn"


# ================== HELPERS ==================

def send_to_server(cmd: str):
    """Send recognized command text to your Flask /ask route."""
    try:
        res = requests.post(SERVER_URL, json={"message": cmd})
        data = res.json()
        reply = data.get("reply", "")
        print(f"Jarvis reply: {reply}")
    except Exception as e:
        print("Error talking to server:", e)


def listen_command() -> str:
    """After wake word, listen for one spoken command."""
    print("Listening for command...")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=6)
        except Exception as e:
            print("Listen error (command):", e)
            return ""

    try:
        text = recognizer.recognize_google(audio, language="en-IN")
        text = text.lower().strip()
        print("Heard command:", text)
        return text
    except Exception as e:
        print("Speech recognition error:", e)
        return ""


# ================== MAIN WAKE WORD LOOP ==================

def main():
    if not ACCESS_KEY or not ACCESS_KEY.startswith("pv_"):
        print("ERROR: You must set ACCESS_KEY in wakeword_listener.py (your Picovoice key).")
        return

    if not os.path.exists(KEYWORD_PATH):
        print(f"ERROR: Could not find keyword file: {KEYWORD_PATH}")
        print("Make sure jarvis.ppn is in the same folder as this script.")
        return

    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[KEYWORD_PATH],
    )

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    print("Wake Word Listener Active... say 'Jarvis' 🔊")

    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected: JARVIS")
                command = listen_command()
                if command:
                    send_to_server(command)
                else:
                    print("No valid command heard.")
    except KeyboardInterrupt:
        print("Stopping wake word listener...")
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()


if __name__ == "__main__":
    main()
