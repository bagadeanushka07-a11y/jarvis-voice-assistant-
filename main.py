import speech_recognition as sr
import webbrowser
import pyttsx3
import time
import requests
import musicLibrary
import os
import platform
import datetime
import wikipedia  # pip install wikipedia


# ─── Initialize Recognizer ───────────────────────────────────────────────────
recognizer = sr.Recognizer()

# ─── Initialize TTS Engine (cross-platform fix) ──────────────────────────────
if platform.system() == "Windows":
    engine = pyttsx3.init('sapi5')
else:
    engine = pyttsx3.init()

engine.setProperty('rate', 170)

# ─── API Key from environment variable (security fix) ────────────────────────
newsapi = os.getenv("NEWS_API_KEY", "04eefa7fa262466895a090be6b27270e")  # set env var in production


# ─── Speak Function ───────────────────────────────────────────────────────────
def speak(text):
    print(f"[Jarvis]: {text}")
    engine.stop()
    engine.say(text)
    engine.runAndWait()


# ─── Tell Time ────────────────────────────────────────────────────────────────
def tell_time():
    now = datetime.datetime.now()
    hour = now.strftime("%I")        # 12-hour format
    minute = now.strftime("%M")
    am_pm = now.strftime("%p")
    speak(f"The time is {hour} {minute} {am_pm}")


# ─── Tell Date ────────────────────────────────────────────────────────────────
def tell_date():
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    speak(f"Today is {date_str}")


# ─── Wikipedia Search ─────────────────────────────────────────────────────────
def search_wikipedia(query):
    try:
        speak(f"Searching Wikipedia for {query}")
        result = wikipedia.summary(query, sentences=2)
        print(f"[Wikipedia]: {result}")
        speak(result)
    except wikipedia.exceptions.DisambiguationError:
        speak("There are multiple results. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("Sorry, I couldn't find anything on Wikipedia for that.")
    except Exception as e:
        speak("Something went wrong with the Wikipedia search.")
        print(f"[Wikipedia Error]: {e}")


# ─── Process Command ──────────────────────────────────────────────────────────
def ProcessCommand(c):
    c_lower = c.lower()

    # --- Websites ---
    if "open google" in c_lower:
        speak("Opening Google")
        webbrowser.open("https://google.com")

    elif "open facebook" in c_lower:
        speak("Opening Facebook")
        webbrowser.open("https://facebook.com")

    elif "open youtube" in c_lower:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")

    elif "open gmail" in c_lower:
        speak("Opening Gmail")
        webbrowser.open("https://mail.google.com")

    # --- Music ---
    elif c_lower.startswith("play"):
        song = c_lower.replace("play", "").strip()
        if song in musicLibrary.music:
            link = musicLibrary.music[song]
            speak(f"Playing {song}")
            webbrowser.open(link)
        else:
            speak(f"Sorry, I couldn't find {song} in your music library")

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
        # Extract search query
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
        speak("Goodbye! Have a great day!")
        exit()

    # --- Fallback (unrecognized command fix) ---
    else:
        speak("Sorry, I didn't understand that command. Please try again.")


# ─── Main Loop ────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    speak("Initializing Jarvis")

    while True:
        try:
            with sr.Microphone() as source:
                print("\n[Listening for wake word...]")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=4)

            print("[Recognizing...]")
            word = recognizer.recognize_google(audio)
            print(f"[Heard]: {word}")

            if "jarvis" in word.lower():
                speak("Yes, how can I help?")
                time.sleep(0.5)

                # Listen for command (timeout fix added)
                with sr.Microphone() as source:
                    print("[Jarvis active - waiting for command...]")
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)  # FIX: was no timeout

                command = recognizer.recognize_google(audio)
                print(f"[Command]: {command}")
                ProcessCommand(command)

        except sr.WaitTimeoutError:
            pass  # No speech detected, keep looping silently

        except sr.UnknownValueError:
            pass  # Couldn't understand audio, keep looping silently

        except sr.RequestError as e:
            print(f"[Speech Recognition Error]: {e}")

        except Exception as e:
            print(f"[Error]: {e}")
