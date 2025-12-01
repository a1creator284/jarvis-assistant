# jarvis_logic.py
"""
Tiny wrapper so the website can use the same Jarvis brain
you already wrote in main.py (the handle() function).
"""

import main  # this imports your existing main.py


def handle_command(text: str) -> str:
    """
    Take plain text from the website and return Jarvis reply as text.
    We pass an empty history because the site doesn't need chat memory yet.
    """
    try:
        reply = main.handle(text, [])
        return reply
    except Exception as e:
        print("jarvis_logic error:", e)
        return "Sorry, something went wrong in my brain."
