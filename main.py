import speech_recognition as sr
import webbrowser
import pyttsx3
import time
import requests
import musicLibrary
import os
import platform
import datetime
import wikipedia
import asyncio
import json
import threading

# Try to import websockets
try:
    import websockets
    from websockets.server import serve
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    print("Warning: websockets module not available. Install with: pip install websockets")

# ─── Initialize Recognizer ───────────────────────────────────────────────────
recognizer = sr.Recognizer()

# ─── Initialize TTS Engine ───────────────────────────────────────────────────
if platform.system() == "Windows":
    engine = pyttsx3.init('sapi5')
else:
    engine = pyttsx3.init()

engine.setProperty('rate', 170)

# ─── API Key ─────────────────────────────────────────────────────────────────
newsapi = os.getenv("NEWS_API_KEY", "04eefa7fa262466895a090be6b27270e")

# ─── WebSocket Variables ─────────────────────────────────────────────────────
connected_clients = set()
websocket_loop = None

# ─── Speak Function ──────────────────────────────────────────────────────────
def speak(text):
    print(f"[Jarvis]: {text}")
    engine.stop()
    engine.say(text)
    engine.runAndWait()
    
    # Broadcast to WebSocket clients if available
    if WEBSOCKET_AVAILABLE and websocket_loop and connected_clients:
        # Create a new event loop in a thread if needed
        try:
            future = asyncio.run_coroutine_threadsafe(
                broadcast_response({"type": "speak", "message": text}),
                websocket_loop
            )
            # Don't wait for result to avoid blocking
        except Exception as e:
            print(f"WebSocket broadcast error: {e}")

async def broadcast_response(data):
    """Send response to all connected WebSocket clients"""
    if connected_clients:
        message = json.dumps(data)
        if connected_clients:
            await asyncio.gather(*[client.send(message) for client in connected_clients])

# ─── Tell Time ────────────────────────────────────────────────────────────────
def tell_time():
    now = datetime.datetime.now()
    hour = now.strftime("%I")
    minute = now.strftime("%M")
    am_pm = now.strftime("%p")
    response = f"The time is {hour} {minute} {am_pm}"
    speak(response)
    return response

# ─── Tell Date ────────────────────────────────────────────────────────────────
def tell_date():
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    response = f"Today is {date_str}"
    speak(response)
    return response

# ─── Wikipedia Search ─────────────────────────────────────────────────────────
def search_wikipedia(query):
    try:
        speak(f"Searching Wikipedia for {query}")
        result = wikipedia.summary(query, sentences=2)
        print(f"[Wikipedia]: {result}")
        speak(result)
        return result
    except wikipedia.exceptions.DisambiguationError:
        msg = "There are multiple results. Please be more specific."
        speak(msg)
        return msg
    except wikipedia.exceptions.PageError:
        msg = "Sorry, I couldn't find anything on Wikipedia for that."
        speak(msg)
        return msg
    except Exception as e:
        msg = "Something went wrong with the Wikipedia search."
        speak(msg)
        print(f"[Wikipedia Error]: {e}")
        return msg

# ─── Process Command ──────────────────────────────────────────────────────────
def ProcessCommand(c):
    c_lower = c.lower()
    response = ""

    # --- Websites ---
    if "open google" in c_lower:
        response = "Opening Google"
        speak(response)
        webbrowser.open("https://google.com")

    elif "open facebook" in c_lower:
        response = "Opening Facebook"
        speak(response)
        webbrowser.open("https://facebook.com")

    elif "open youtube" in c_lower:
        response = "Opening YouTube"
        speak(response)
        webbrowser.open("https://youtube.com")

    elif "open gmail" in c_lower:
        response = "Opening Gmail"
        speak(response)
        webbrowser.open("https://mail.google.com")

    # --- Music ---
    elif c_lower.startswith("play"):
        song = c_lower.replace("play", "").strip()
        if song in musicLibrary.music:
            link = musicLibrary.music[song]
            response = f"Playing {song}"
            speak(response)
            webbrowser.open(link)
        else:
            response = f"Sorry, I couldn't find {song} in your music library"
            speak(response)

    # --- News ---
    elif "news" in c_lower:
        speak("Here are the latest headlines")
        try:
            r = requests.get(
                f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}",
                timeout=5
            )
            if r.status_code == 200:
                data = r.json()
                articles = data.get("articles", [])
                for article in articles[:5]:
                    title = article.get("title")
                    if title:
                        print(f"[News]: {title}")
                        speak(title)
            else:
                speak("Sorry, I couldn't fetch the news right now.")
        except requests.exceptions.RequestException:
            speak("I'm having trouble connecting to the news service.")

    # --- Time ---
    elif "time" in c_lower:
        tell_time()

    # --- Date ---
    elif "date" in c_lower:
        tell_date()

    # --- Wikipedia ---
    elif c_lower.startswith("search") or c_lower.startswith("who is") or c_lower.startswith("what is"):
        query = ""
        for prefix in ["search for", "search", "who is", "what is"]:
            if c_lower.startswith(prefix):
                query = c_lower.replace(prefix, "").strip()
                break
        if query:
            search_wikipedia(query)
        else:
            speak("What would you like me to search for?")

    # --- Exit ---
    elif "stop" in c_lower or "exit" in c_lower or "bye" in c_lower:
        response = "Goodbye! Have a great day!"
        speak(response)
        return "exit"

    # --- Fallback ---
    else:
        response = "Sorry, I didn't understand that command. Please try again."
        speak(response)
    
    return response

# ─── WebSocket Handler ────────────────────────────────────────────────────────
async def handle_websocket(websocket, path):
    """Handle WebSocket connections from frontend"""
    connected_clients.add(websocket)
    print(f"✅ Client connected. Total clients: {len(connected_clients)}")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"📩 Received from frontend: {data}")
            
            if data.get("type") == "command":
                command = data.get("command", "")
                print(f"⚡ Processing command: {command}")
                result = ProcessCommand(command)
                
                await websocket.send(json.dumps({
                    "type": "result",
                    "command": command,
                    "result": result if result else "Command processed"
                }))
                
                if result == "exit":
                    break
                    
            elif data.get("type") == "ping":
                await websocket.send(json.dumps({"type": "pong"}))
                
    except websockets.exceptions.ConnectionClosed:
        print("🔌 Client disconnected")
    finally:
        connected_clients.remove(websocket)
        print(f"📊 Client removed. Total clients: {len(connected_clients)}")

# ─── Voice Recognition Thread ────────────────────────────────────────────────
def voice_recognition_loop():
    """Run voice recognition in a separate thread"""
    while True:
        try:
            with sr.Microphone() as source:
                print("\n🎤 [Listening for wake word...]")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=4)

            print("🔍 [Recognizing...]")
            word = recognizer.recognize_google(audio)
            print(f"📝 [Heard]: {word}")

            if "jarvis" in word.lower():
                speak("Yes, how can I help?")
                time.sleep(0.5)

                with sr.Microphone() as source:
                    print("🎙️ [Jarvis active - waiting for command...]")
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)

                command = recognizer.recognize_google(audio)
                print(f"💬 [Command]: {command}")
                
                # Broadcast to WebSocket clients
                if WEBSOCKET_AVAILABLE and websocket_loop and connected_clients:
                    try:
                        asyncio.run_coroutine_threadsafe(
                            broadcast_response({"type": "user_command", "command": command}),
                            websocket_loop
                        )
                    except Exception as e:
                        print(f"Broadcast error: {e}")
                
                ProcessCommand(command)

        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"[Speech Recognition Error]: {e}")
        except Exception as e:
            print(f"[Error]: {e}")

# ─── Main Function ────────────────────────────────────────────────────────────
async def start_websocket_server():
    """Start the WebSocket server"""
    global websocket_loop
    websocket_loop = asyncio.get_running_loop()
    
    # Use the new recommended way for websockets 16.0
    async with serve(handle_websocket, "localhost", 8765):
        print("🌐 WebSocket server started on ws://localhost:8765")
        print("🤖 JARVIS is ready and listening!")
        print("=" * 50)
        await asyncio.Future()  # Run forever

def main():
    """Main function to run JARVIS"""
    speak("Initializing Jarvis")
    
    # Start voice recognition in a separate thread
    voice_thread = threading.Thread(target=voice_recognition_loop, daemon=True)
    voice_thread.start()
    print("🎤 Voice recognition thread started")
    
    if WEBSOCKET_AVAILABLE:
        try:
            # Run WebSocket server
            asyncio.run(start_websocket_server())
        except KeyboardInterrupt:
            print("\n👋 Shutting down Jarvis...")
        except Exception as e:
            print(f"Error starting WebSocket server: {e}")
            print("Running in voice-only mode...")
            # Keep the voice thread running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Shutting down Jarvis...")
    else:
        print("⚠️ WebSocket not available. Running in voice-only mode.")
        print("To enable WebSocket, run: pip install websockets")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down Jarvis...")

if __name__ == "__main__":
    main()