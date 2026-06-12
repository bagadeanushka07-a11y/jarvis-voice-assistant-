from flask import Flask, request, jsonify
from flask_cors import CORS
import webbrowser
import pyttsx3
import platform
import datetime
import musicLibrary
import threading
import time
import sys

app = Flask(__name__)
CORS(app)

# Global engine
engine = None

def init_tts():
    """Initialize the TTS engine"""
    global engine
    try:
        if platform.system() == "Windows":
            engine = pyttsx3.init('sapi5')
        else:
            engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 1.0)
        print("✅ TTS Engine initialized successfully")
        return True
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return False

# Initialize TTS
init_tts()

def speak(text):
    """Speak the text using TTS"""
    print(f"[Jarvis]: {text}")
    
    def _speak():
        global engine
        try:
            if engine:
                # Stop any ongoing speech
                engine.stop()
                # Say the new text
                engine.say(text)
                engine.runAndWait()
            else:
                print("TTS not available - reinstantiating")
                init_tts()
                if engine:
                    engine.say(text)
                    engine.runAndWait()
        except Exception as e:
            print(f"TTS speaking error: {e}")
    
    # Run in thread so it doesn't block
    thread = threading.Thread(target=_speak, daemon=True)
    thread.start()
    # Small delay to ensure thread starts
    time.sleep(0.05)

def tell_time():
    now = datetime.datetime.now()
    hour = now.strftime("%I")
    minute = now.strftime("%M")
    am_pm = now.strftime("%p")
    response = f"The time is {hour} {minute} {am_pm}"
    speak(response)
    return response

def tell_date():
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    response = f"Today is {date_str}"
    speak(response)
    return response

@app.route('/api/command', methods=['POST'])
def handle_command():
    try:
        data = request.json
        command = data.get('command', '')
        print(f"\n📝 Received: {command}")
        cmd_lower = command.lower().strip()
        
        # Open websites
        if "open youtube" in cmd_lower:
            speak("Opening YouTube")
            webbrowser.open("https://youtube.com")
            result = "Opening YouTube"
        
        elif "open google" in cmd_lower:
            speak("Opening Google")
            webbrowser.open("https://google.com")
            result = "Opening Google"
        
        elif "open facebook" in cmd_lower:
            speak("Opening Facebook")
            webbrowser.open("https://facebook.com")
            result = "Opening Facebook"
        
        # Play music
        elif cmd_lower.startswith("play "):
            song = cmd_lower.replace("play ", "").strip()
            if song in musicLibrary.music:
                speak(f"Playing {song}")
                webbrowser.open(musicLibrary.music[song])
                result = f"Playing {song}"
            else:
                speak(f"Sorry, I couldn't find {song} in your music library")
                result = f"Sorry, couldn't find {song}"
        
        # Time and date
        elif "time" in cmd_lower:
            result = tell_time()
        
        elif "date" in cmd_lower:
            result = tell_date()
        
        # List songs
        elif "songs" in cmd_lower or "music" in cmd_lower:
            songs_list = ", ".join(musicLibrary.music.keys())
            result = f"Available songs: {songs_list}"
            speak(result)
        
        # News
        elif "news" in cmd_lower:
            speak("Opening Google News")
            webbrowser.open("https://news.google.com")
            result = "Opening Google News"
        
        # Help
        elif "help" in cmd_lower:
            help_text = """Available commands:
• time - Get current time
• date - Get current date
• open youtube - Open YouTube
• open google - Open Google
• play [song] - Play a song
• songs - List all songs
• news - Open news
• stop - Exit JARVIS"""
            result = help_text
            speak("Here are the available commands")
        
        # Exit
        elif "stop" in cmd_lower or "exit" in cmd_lower or "bye" in cmd_lower:
            speak("Goodbye! Have a great day!")
            result = "exit"
        
        # Unknown command
        else:
            result = f"Sorry, I didn't understand '{command}'. Try saying 'help' for options."
            speak(result)
        
        return jsonify({'success': True, 'command': command, 'response': result})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok', 
        'message': 'JARVIS is running!',
        'songs': list(musicLibrary.music.keys())
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 J.A.R.V.I.S - Voice Assistant")
    print("="*60)
    print("📍 Server: http://localhost:5000")
    print("\n📋 Available Songs:")
    for song in musicLibrary.music.keys():
        print(f"   🎵 {song}")
    print("\n💡 Try these commands:")
    print("   • time - JARVIS will speak the time")
    print("   • open youtube - Opens YouTube")
    print("   • play shape of you - Plays music")
    print("="*60 + "\n")
    
    # Test TTS on startup
    speak("JARVIS is ready")
    
    app.run(host='localhost', port=5000, debug=False, threaded=True, use_reloader=False)