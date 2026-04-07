
# 🤖 Jarvis — Python Voice Assistant

A voice-activated personal assistant built with Python, inspired by J.A.R.V.I.S from Iron Man. Just say **"Jarvis"** and give a command — it listens, understands, and responds.

---

## 📸 Demo

> Say **"Jarvis"** → It wakes up → You give a command → It responds!

---

## ✨ Features

| Feature | Voice Command Example |
|---|---|
| 🌐 Open websites | *"Jarvis, open Google"* |
| 🎵 Play music | *"Jarvis, play perfect"* |
| 📰 Latest news | *"Jarvis, tell me the news"* |
| 🕐 Current time | *"Jarvis, what's the time"* |
| 📅 Today's date | *"Jarvis, what's the date"* |
| 🔍 Wikipedia search | *"Jarvis, who is Elon Musk"* |
| ❌ Exit assistant | *"Jarvis, stop"* |

---

## 🗂️ Project Structure

```
jarvis-voice-assistant/
│
├── main.py              # Core assistant logic
├── musicLibrary.py      # Song name → YouTube URL mapping
├── requirements.txt     # Python dependencies
└── README.md            # You're reading this!
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/jarvis-voice-assistant.git
cd jarvis-voice-assistant
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your News API key

Get a free API key from [https://newsapi.org](https://newsapi.org) and set it as an environment variable:

```bash
# Windows
set NEWS_API_KEY=your_api_key_here

# Mac/Linux
export NEWS_API_KEY=your_api_key_here
```

---

## ▶️ Running the Assistant

```bash
python main.py
```

Once started, Jarvis will say **"Initializing Jarvis"** and begin listening. Say **"Jarvis"** to wake it up, then speak your command.

---

## 🎵 Adding Songs

Open `musicLibrary.py` and add songs in this format:

```python
music = {
    "song name": "https://youtube.com/your-link",
    "shape of you": "https://www.youtube.com/watch?v=JGwWNGJdvx8",
    # add more here...
}
```

Then just say: *"Jarvis, play shape of you"*

---

## 📦 Requirements

```
speechrecognition
pyttsx3
requests
wikipedia
pyaudio
```

> **Note:** `pyaudio` can be tricky to install on Windows. If it fails, download the `.whl` file from [https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install manually.

---

## 🔧 Troubleshooting

**Microphone not detected**
- Make sure your mic is connected and set as the default input device.
- Try running `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"` to list available mics.

**`pyttsx3` not speaking on Mac/Linux**
- Install `espeak`: `sudo apt install espeak` (Linux) or `brew install espeak` (Mac)

**`pyaudio` install error on Windows**
- Use: `pip install pipwin` then `pipwin install pyaudio`

**News not loading**
- Double-check your `NEWS_API_KEY` environment variable is set correctly.

---

## 🚀 Future Ideas

- [ ] Weather updates using OpenWeatherMap API
- [ ] Set reminders and alarms
- [ ] Spotify integration
- [ ] Volume control
- [ ] WhatsApp message sending
- [ ] ChatGPT integration for general Q&A

---

## 🛠️ Built With

- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) — voice input
- [pyttsx3](https://pypi.org/project/pyttsx3/) — text-to-speech
- [Wikipedia](https://pypi.org/project/wikipedia/) — knowledge search
- [NewsAPI](https://newsapi.org/) — live news headlines
- [webbrowser](https://docs.python.org/3/library/webbrowser.html) — browser control

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙋‍♂️ Author

Made with ❤️ by [Your Name](https://github.com/your-username)

> *"Sometimes you gotta run before you can walk."* — Tony Stark
