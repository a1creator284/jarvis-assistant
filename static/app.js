// ========================
//   J.A.R.V.I.S WEB HUD
// ========================

document.addEventListener("DOMContentLoaded", () => {
    console.log("JARVIS app.js loaded");

    // ---- DOM refs ----
    const bootScreen    = document.getElementById("boot-screen");
    const hud           = document.getElementById("hud");
    const chatBox       = document.getElementById("chat-box");
    const hudTime       = document.getElementById("hud-time");
    const hudBattery    = document.getElementById("hud-battery");
    const redAlertAudio = document.getElementById("red-alert-sound");

    const textInput     = document.getElementById("text-command");
    const sendButton    = document.getElementById("send-command");

    const WAKE_WORD = "jarvis";

    // --------------------------
    //   BASIC CHAT UI HELPERS
    // --------------------------
    function addMessage(text, sender) {
        if (!chatBox || !text) return;
        const div = document.createElement("div");
        div.className = sender === "user" ? "msg-user" : "msg-jarvis";
        div.textContent = (sender === "user" ? "YOU: " : "JARVIS: ") + text;
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // --------------------------
    //   SPEECH: ONLY MAC SPEAKS
    // --------------------------
    function speak(text) {
        if (!text) return;

        // Always ask backend (Mac) to speak
        try {
            console.log("Sending to backend /speak:", text);
            fetch("/speak", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text })
            });
        } catch (e) {
            console.log("Speech request error:", e);
        }

        // Old browser speech logic is intentionally NOT executed
        // to avoid double-speaking on phone.
        // (Kept as comment so code size is not reduced.)
        /*
        if (!("speechSynthesis" in window) || !text) return;
        try {
            speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            utter.rate = 1.0;
            utter.pitch = 0.95;
            speechSynthesis.speak(utter);
        } catch (e) {
            console.log("Speech error:", e);
        }
        */
    }

    // --------------------------
    //   RED ALERT SOUND HELPERS
    // --------------------------
    function playRedAlertSound() {
        if (!redAlertAudio) return;
        try {
            redAlertAudio.currentTime = 0;
            redAlertAudio.loop = true;
            redAlertAudio.play();
        } catch (e) {
            console.log("Red alert sound error:", e);
        }
    }

    function stopRedAlertSound() {
        if (!redAlertAudio) return;
        try {
            redAlertAudio.pause();
            redAlertAudio.currentTime = 0;
        } catch (e) {
            console.log("Red alert sound stop error:", e);
        }
    }

    // --------------------------
    //   BACKEND COMMUNICATION
    // --------------------------
    async function sendToJarvis(text) {
        if (!text) return;
        addMessage(text, "user");

        try {
            const res = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();
            const reply = data.reply || "I did not get a reply from the server.";
            addMessage(reply, "jarvis");

            // Mac speaks reply (once)
            speak(reply);
        } catch (err) {
            console.error("Backend error:", err);
            addMessage("There was an error contacting the server.", "jarvis");
            speak("There was an error contacting the server, sir.");
        }
    }

    // --------------------------
    //   STATUS POLLING (HUD)
    // --------------------------
    async function pollStatus() {
        try {
            const res = await fetch("/status");
            const data = await res.json();
            if (hudTime && data.time) {
                hudTime.textContent = data.time;
            }
            if (hudBattery && data.battery != null) {
                hudBattery.textContent = data.battery + "%";
            }
        } catch (e) {
            // ignore errors
        }
    }

    setInterval(pollStatus, 5000);
    pollStatus();

    // --------------------------
    //   VOICE RECOGNITION
    // --------------------------
    let recognition = null;
    let listening = false;

    // Soft reset helper: stop current session so browser can restart fresh
    function resetRecognitionSoft() {
        if (!recognition) return;
        try {
            console.log("Soft resetting recognition session...");
            recognition.stop();
            // onend handler will flip listening=false and restart
        } catch (e) {
            console.log("Recognition stop error:", e);
        }
    }

    function startListening() {
        if (!recognition || listening) return;
        try {
            recognition.start();
            listening = true;
            console.log("Voice recognition started");
        } catch (e) {
            console.log("Recognition start error:", e);
        }
    }

    if ("webkitSpeechRecognition" in window) {
        recognition = new webkitSpeechRecognition();
        recognition.lang = "en-IN";
        recognition.continuous = true;
        recognition.interimResults = false;

        recognition.onresult = (event) => {
            const transcript = event.results[event.resultIndex][0].transcript
                .trim()
                .toLowerCase();
            console.log("Heard:", transcript);

            if (!transcript.includes(WAKE_WORD)) return;

            const cmd = transcript.split(WAKE_WORD).slice(1).join(" ").trim();

            // Only wake word detected
            if (!cmd) {
                const line = "Yes sir?";
                addMessage(line, "jarvis");
                speak(line);
                // Soft reset after answer so mic session stays fresh
                resetRecognitionSoft();
                return;
            }

            // RED ALERT MODE
            if (cmd.includes("red alert")) {
                document.body.classList.add("red-alert");
                playRedAlertSound();
                const line = "Red alert protocol activated, sir.";
                addMessage(line, "jarvis");
                speak(line);
                // Reset session after handling
                resetRecognitionSoft();
                return;
            }

            if (cmd.includes("normal mode") || cmd.includes("stand down")) {
                document.body.classList.remove("red-alert");
                stopRedAlertSound();
                const line = "Standing down from red alert, sir.";
                addMessage(line, "jarvis");
                speak(line);
                // Reset session after handling
                resetRecognitionSoft();
                return;
            }

            // Normal command → backend
            sendToJarvis(cmd);

            // 🔁 IMPORTANT:
            // After every full command, reset recognition so browser
            // does not get stuck after several commands.
            resetRecognitionSoft();
        };

        recognition.onend = () => {
            console.log("Recognition ended");
            listening = false;
            // auto-restart after a short pause
            setTimeout(startListening, 600);
        };

        recognition.onerror = (e) => {
            console.log("Recognition error:", e);
            listening = false;
            // give browser a moment, then try again
            setTimeout(startListening, 1200);
        };

        // Extra watchdog: if for any reason listening is false for too long, restart
        setInterval(() => {
            if (!recognition) return;
            if (!listening) {
                console.log("Watchdog: recognition not listening, trying restart...");
                startListening();
            }
        }, 10000);
    } else {
        const line = "Browser does not support speech recognition, sir.";
        addMessage(line, "jarvis");
        speak(line);
    }

    // --------------------------
    //   TYPED COMMANDS (PHONE / DESKTOP)
    // --------------------------
    function sendTypedCommand() {
        if (!textInput) return;
        const value = textInput.value.trim();
        if (!value) return;
        textInput.value = "";

        // Do NOT speak here to avoid double-speaking.
        console.log("Typed command sent, waiting for Jarvis reply...");

        // Send to backend
        sendToJarvis(value);
    }

    if (sendButton && textInput) {
        sendButton.addEventListener("click", () => {
            sendTypedCommand();
            textInput.focus();
        });

        textInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                sendTypedCommand();
            }
        });
    }

    // --------------------------
    //   BOOT SEQUENCE HANDLING
    // --------------------------
    function finishBoot() {
        if (bootScreen) {
            bootScreen.style.display = "none";
        }
        if (hud) {
            hud.classList.remove("hidden");
            hud.style.display = "block";
        }

        const bootLine = "JARVIS system online. Welcome back, sir. Say Jarvis, then your command.";

        addMessage("SYSTEM: Audio link engaged. I will speak all responses through your laptop speakers.", "jarvis");
        addMessage("SYSTEM: Voice channel active. Say 'Jarvis' then your command, or type below.", "jarvis");
        addMessage("SYSTEM: " + bootLine, "jarvis");
        speak(bootLine);

        startListening();
    }

    // Show HUD after 3.5 seconds
    setTimeout(finishBoot, 3500);
});
