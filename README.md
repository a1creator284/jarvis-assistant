# Jarvis – AI Voice Assistant

**Developer:** Raj Aryan  
**Platform:** macOS (Python + Web HUD)

Jarvis is an advanced desktop AI assistant with a futuristic HUD inspired by Iron Man.  
It combines **voice**, **vision**, **reminders**, **study planner**, **security mode**,  
and **system control** into one personal AI control center.

---

## 🔥 UI Preview

> Save your JARVIS HUD screenshot into the repo, for example at:  
> `screenshots/jarvis_ui.png`  
> Then add this line (update the filename if needed):

```markdown
![Jarvis HUD](screenshots/jarvis_ui.png)
✨ Key Features (Overview)
🎤 Hands-free voice assistant with wake word “Jarvis”

🔊 Mac system voice output (say command, Daniel voice)

🧠 GPT-powered brain via OpenAI

🧩 Personal memory (name, favourites, notes)

🕒 Smart reminders with natural language times

📚 Study planner with daily reminders & progress tracking

🔐 Security mode with face verification & intruder alerts

👁️ Vision utilities – face register/recognize, hand gesture, person detection

💻 System intelligence – CPU/RAM/battery/temperature, cache cleanup, restart/shutdown flow

🌐 Internet skills – YouTube, web search, Wikipedia, weather, news, live cricket

🏠 Virtual smart home device states (lights, fan, AC, temperature)

🛰️ Futuristic web HUD with status, log feed, red alert mode & chat box

😄 Fun personality – motivation & roasting on request

📁 Project Structure (Simplified)
text
Copy code
JARVIS project/
├── main.py                 # CLI version of Jarvis (voice-only)
├── server.py               # Flask server (HUD + API endpoints)
├── client.py               # Simple OpenAI test client (optional)
├── jarvis_logic.py         # Extra logic/utility code
├── vision.py               # Face / hand gesture / person detection
├── knowledge.py            # RAG over notes/PDFs
├── knowledge_docs/         # Your PDFs / notes
├── knowledge_index.json    # Vector index for knowledge base
├── news.py / news_test.py  # News helper scripts
├── musicLibrary.py         # Music helpers (optional)
├── run_jarvis.command      # Mac helper script to start Jarvis
├── static/
│   ├── app.js              # Frontend HUD logic (voice, chat, red alert, polling)
│   ├── style.css           # Futuristic JARVIS UI theme
│   └── red-alert.mp3       # Red alert alarm sound
├── templates/
│   └── index.html          # JARVIS HUD page
├── faces/                  # Stored face images (your face) – PRIVATE
├── memory.json             # Jarvis memory (notes, favourites, reminders, etc.) – PRIVATE
├── .env                    # API keys and config – PRIVATE
├── .gitignore              # Files/folders not tracked by git
└── README.md               # This file
🧠 Detailed Features
1. Voice & Wake Word
Files: main.py, static/app.js

Browser uses webkitSpeechRecognition for continuous listening.

Wake word is “jarvis” – Jarvis only reacts after hearing it.

Example commands:

“Jarvis play lo-fi beats on YouTube”

“Jarvis what’s the weather in Delhi”

Replies are spoken using macOS say with a configurable voice:

python
Copy code
VOICE = "Daniel"
subprocess.run(["/usr/bin/say", "-v", VOICE, text])
Browser does not speak; it calls backend /speak so only your Mac voice is used.

2. Futuristic Web HUD
Files: templates/index.html, static/style.css, static/app.js

Boot screen → after ~3.5 seconds, HUD appears with welcome lines:

“JARVIS system online. Welcome back, sir. Say Jarvis, then your command.”

Chat panel:

Shows YOU: and JARVIS: messages.

Typed commands:

Type into input → press Send or Enter → sends to /ask.

Status polling:

Calls /status every 5 seconds to update time and battery percentage.

Red Alert Mode:

“Jarvis red alert” → red-alert CSS + looping red-alert.mp3.

“Jarvis normal mode” or “Jarvis stand down” → stops alert and resets UI.

3. Personal Memory & Profile
Storage: memory.json (local, private)

Jarvis can learn and recall information about you:

Learns name:

“My name is Raj”

Learns favourites:

“My favourite game is GTA V”

“My favourite subject is DSA”

Free-form notes:

“Remember that I have a test on Monday”

“Remember that my laptop charger is in the drawer”

Queries Jarvis can answer:

“What is my name?”

“What is my favourite game?”

“What do you know about me?”

“What do you remember?”

All data is stored locally in memory.json and never uploaded.

4. Knowledge Base Over Notes / PDFs (RAG)
Files: knowledge.py, knowledge_docs/, knowledge_index.json

Jarvis can answer questions from your own notes and PDFs.

Commands:

“Reload knowledge”

“Reload my notes”

“Search my notes for binary search”

“Ask my notes about trees”

“What does my PDF say about linked lists?”

Internals:

knowledge.rebuild_knowledge_base(client) rebuilds the vector index from knowledge_docs/.

knowledge.answer_from_knowledge(question, client) answers using that index + GPT.

5. Smart Reminders (with Background Thread)
Functions: set_reminder, list_reminders, clear_reminders, reminder_watcher

Supported examples:

“Remind me in 10 minutes to drink water”

“Remind me in 2 hours to study”

“Remind me at 8 pm to sleep”

“Remind me tomorrow at 9 am to go college”

“Remind me on Monday at 7 am to go gym”

“Remind me every day at 8 pm to study DSA”

Other commands:

“What are my reminders?”

“List my reminders”

“Clear reminders”

“Delete all reminders”

Jarvis:

Stores reminders in memory["reminders"] (text, time, repeat).

Runs reminder_watcher thread every 30 seconds.

Speaks when reminder time is reached:

“Reminder, sir: <your text>”

Daily reminders are automatically rescheduled for next day.

6. Study Planner
Functions: create_study_plan, list_study_plans, show_study_plan_for, update_study_progress

Commands:

“Help me learn data structures”

“Create a study plan for operating systems”

“Make a learning plan for machine learning”

“Show my study plans”

“Show my plan for data structures”

“Update my progress for data structures to 40 percent”

Features:

Uses GPT (gpt-4.1-mini) to generate a 7-day study plan (with fallback template if no API).

Stores plan + progress in memory["plans"].

Automatically sets a daily reminder at 8 PM for that topic.

Tracks progress percentage per topic.

7. Security Mode & Intruder Detection
Functions: enable_security_mode, disable_security_mode, security_status, security_check, intruder_watcher
Module: vision.py

Security mode protects sensitive actions like cleanup, restart, shutdown.

Commands:

“Enable security mode” / “Turn on security mode”

“Disable security mode”

“Security status”

“Verify my identity”

Behaviour:

memory["security"] stores:

enabled

last_auth_time

auth_timeout_sec (default ~60 seconds)

When security is ON and a sensitive command is used (e.g. clean system, restart, shutdown):

security_check() calls vision.recognize_face("raj").

If face matches stored reference → action allowed.

If not → Jarvis denies the command.

Intruder watcher:

Background intruder_watcher thread runs every few seconds.

Only active when security mode is enabled.

If vision.see_any_person() is true and face ≠ “raj”:

Jarvis says:

“Intruder detected, sir. Triggering red alert protocol.”

Extra vision commands:

“Register my face” / “Remember my face”

“Do you see me?” / “Who is in front of you?”

“Check my hand” / “See my hand” (detects open palm etc.)

“Do you see anyone?” / “What do you see?”

8. System Intelligence & Maintenance
Functions: system_report, get_cpu_temperature, clean_system

Commands:

“System diagnostics” / “System status” / “Status report”

“CPU usage”

“Temperature” / “Overheating” / “Too hot”

“Clean my system” / “Clear cache” / “Clear junk”

“Restart system” / “Confirm restart”

“Shutdown system” / “Confirm shutdown”

Features:

Uses psutil to read:

CPU usage

RAM usage

Battery percentage

Uses osx-cpu-temp (Homebrew) to read CPU temperature.

system_report() returns a friendly summary:

“System diagnostics: CPU at X percent, RAM usage Y percent, battery Z%. CPU temperature 45.0°C…”

clean_system() deletes files in ~/Library/Caches (safe cache cleanup).

Restart / shutdown require user confirmation and pass security_check() when security is ON.

9. Mac App / Website Launcher
Function: launch_any_app

Commands:

“Open Chrome”

“Open VS Code”

“Open Spotify”

“Open Canva”

“Open Terminal”

“Open YouTube”

“Open Facebook”

“Open LinkedIn”

“Open instagram dot com”

Behaviour:

Maps spoken names (e.g. “vs code”, “chrome”) to real macOS app names.

Tries open -a "<AppName>".

If the app doesn’t exist:

Treats the phrase as a website (‘facebook dot com’ → facebook.com).

Opens https://<site> in default browser.

10. Display, Volume & Screenshot
Functions: change_brightness_relative, set_volume, take_screenshot

Commands:

“Increase brightness” / “Brightness up”

“Decrease brightness” / “Brightness down”

“Increase volume”

“Decrease volume”

“Volume 50” (or any number between 0 and 100)

“Screenshot” / “Take a screenshot”

Actions:

Uses AppleScript key codes via osascript to adjust brightness.

Sets system volume to exact percentage.

Takes screenshot with screencapture and saves as
~/Desktop/jarvis_screenshot_<timestamp>.png.

11. Time & Battery
Functions: tell_time, get_status

Commands:

“What’s the time?”

“What is the time and date?”

“Battery status”

“Battery percentage”

Uses Python datetime and psutil.sensors_battery() to answer.

/status endpoint (used by HUD) returns:

json
Copy code
{ "time": "HH:MM:SS", "battery": 52 }
12. Internet Skills
YouTube
Function: play_youtube

“Play lo-fi hip hop”

“Play Alan Walker Faded”

Jarvis:

Searches YouTube via HTML.

Extracts first video ID.

Opens video in browser.

Speaks: “Playing <query> on YouTube.”

Weather
Function: get_weather

“What’s the weather?”

“What’s the weather in Delhi?”

Uses OpenWeather API and WEATHER_API_KEY.

News
Function: get_news

“What’s the news?”

“Latest news headlines”

Uses NewsAPI (NEWS_API_KEY) to fetch top headlines based on NEWS_COUNTRY.

Wikipedia
Function: wiki

“Who is Elon Musk?”

“What is binary search?”

“Tell me about operating systems”

Uses wikipedia.summary(topic, sentences=2).

Web Search (DuckDuckGo)
Function: web_search_ddg

“Search Python decorators”

“Jarvis can you search Tesla Model 3 review”

Jarvis:

Calls DuckDuckGo HTML endpoint.

Scrapes top result titles.

Opens results page in browser.

Speaks a short summary of top results.

Live Cricket
Function: get_live_cricket_score

“Cricket score”

“Live score of today’s match”

“What is India’s match score?”

Uses CricketData API (CRICKET_API_KEY):

Fetches current matches.

Prioritises India’s match if you mention India.

Speaks formatted score + status.

13. Virtual Smart Home
Function: control_smart_home

Commands:

“Turn on the room lights”

“Turn off the bedroom fan”

“Set AC to 24”

“Set temperature to 22”

Behaviour:

Parses action (on / off), device (light, fan, AC, lamp, etc.) and room (bedroom, hall, kitchen, room).

Stores state in memory["smarthome"]:

bedroom_light = "on"

room_fan = "off"

ac_temperature = 24

Currently a virtual smart home; later you can connect it to real APIs.

14. Sleep Mode
Commands:

“Go to sleep” / “Sleep mode”

Sets jarvis_sleep = True and responds:

“Entering sleep mode. Say Jarvis wake up.”

“Wake up”

Sets jarvis_sleep = False and responds:

“I am awake sir.”

When sleeping, any other command returns:

“I am currently in sleep mode. Say Jarvis wake up.”

15. Fun Personality
“Roast me” → light roast.

“Motivate me” / “Motivation” → motivational lines like:

“You are literally building your own JARVIS. Most people only dream about it, sir.”

⚙️ Tech Stack
Technology	Purpose
Python	Core logic & backend
Flask	HTTP API for /ask, /speak, /status
OpenAI API	GPT-based reasoning and study plans
SpeechRecognition	Microphone input (CLI mode)
macOS say	System text-to-speech for Jarvis voice
psutil	CPU/RAM/battery monitoring
wikipedia	Quick text summaries
requests	HTTP calls (weather, news, cricket, web)
DuckDuckGo HTML	Web search
python-dotenv	.env config management
JavaScript (app.js)	HUD logic & browser speech recognition
webkitSpeechRecognition	Browser speech engine
HTML + CSS	JARVIS interface layout & styling
Custom vision module	Face / gesture / person detection

🔐 Environment Variables (.env)
Create a file called .env in the project root:

env
Copy code
OPENAI_API_KEY=your_openai_key_here
WEATHER_API_KEY=your_openweather_key_here
NEWS_API_KEY=your_newsapi_key_here
NEWS_COUNTRY=in
WEATHER_CITY=Delhi
CRICKET_API_KEY=your_cricketdata_key_here
.env is in .gitignore, so it will not be uploaded to GitHub.

🚀 Installation & Running
1. Clone the Repository
bash
Copy code
git clone https://github.com/a1creator284/jarvis-assistant.git
cd jarvis-assistant
2. Create and Activate Virtual Environment
bash
Copy code
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows (if you ever port it)
3. Install Dependencies
Create a requirements.txt similar to:

text
Copy code
flask
openai
python-dotenv
requests
wikipedia
psutil
SpeechRecognition
pyaudio
opencv-python
numpy
Then:

bash
Copy code
pip install -r requirements.txt
4. Configure .env
Fill in all the keys and values described in the Environment Variables section.

5. Run the Backend
Web HUD
bash
Copy code
python server.py
Open in your browser (port may vary depending on server.py):

text
Copy code
http://localhost:5000
CLI-Only Jarvis
bash
Copy code
python main.py
Jarvis will speak a boot message and start listening through the microphone.

🧹 Git & Privacy
Typical .gitignore (already in this project):

gitignore
Copy code
# Secrets / env
.env
*.env

# Virtual environments
.venv/
.jarvis_env/
env/
venv/

# Python cache
__pycache__/
*.py[cod]

# Personal / generated data
memory.json
faces/
screenshot_*.png
.DS_Store
.vscode/
# (Optionally) ignore knowledge docs if private
# knowledge_docs/
# knowledge_index.json
This prevents API keys, personal faces, and local data from being pushed.

📝 Roadmap / Future Ideas
Multi-user profiles with separate memories

More advanced red-alert protocol (logging, email, notifications)

Richer gesture controls (pause/resume music, mute, etc.)

Native macOS app packaging

Email / WhatsApp integration

Real smart home device integration (Tuya, Home Assistant, etc.)

Cross-platform support (Windows / Linux)

⭐ Support
If you like this project:

⭐ Star the repo on GitHub

🧑‍💻 Share it with friends and on social media

🎥 Record and share a demo video of your JARVIS in action
