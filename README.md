# 🎙️ AI Windows Voice Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

> An intelligent, privacy-first voice-controlled Windows automation agent powered by local LLMs and offline speech recognition.

**No cloud. No data collection. Complete privacy.**

---

## 🌟 Features

- **🎤 Offline Speech Recognition** - Faster-Whisper for accurate, private transcription
- **🤖 Local LLM Planning** - Uses Ollama/llama.cpp for command understanding
- **⚡ Smart Execution** - Safely automates Windows tasks via natural language
- **🛡️ Safety First** - Risk assessment and confirmation for all commands
- **🎨 Modern UI** - Clean React frontend with real-time updates
- **📝 Audit Logging** - Complete history of all executed commands
- **🔧 Fully Customizable** - Configure apps, shortcuts, and behaviors

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Windows 10/11
- Microphone

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-windows-agent.git
cd ai-windows-agent

# Run automated setup (Windows)
setup_day1.bat

# Or manual setup:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Run the Agent

```bash
python main.py
```

Say **"Hey computer"** to activate, then speak your command!

---

## 📋 Current Status (Day 1 Complete ✅)

- [x] Audio capture with wake word detection
- [x] Noise reduction and preprocessing
- [x] Offline Speech-to-Text (Faster-Whisper)
- [x] Voice Activity Detection
- [x] End-to-end voice → text pipeline
- [ ] LLM integration (Day 2)
- [ ] Command execution (Day 3)
- [ ] Frontend UI (Day 4-5)
- [ ] Safety & confirmation layer (Day 6)
- [ ] Desktop app packaging (Day 7)

---

## 🎯 Example Commands (Coming Soon)

```
"Open Chrome and search for Python tutorials"
"Create a new folder on Desktop named Projects"
"Send an email to John about the meeting"
"Play Spotify and minimize the window"
"Show me today's weather"
"Take a screenshot and save it to Downloads"
```

---

## 🏗️ Architecture

```
Voice Input → STT → LLM Planner → Safety Check → Executor → Confirmation → Action
```

### Project Structure

```
ai-windows-agent/
├── audio/              # Audio capture & preprocessing
├── stt/                # Speech-to-Text engine
├── llm/                # Local LLM planning
├── executor/           # Command execution
├── permissions/        # Safety & confirmation
├── backend/            # FastAPI backend
├── frontend/           # React UI
└── main.py            # Entry point
```

---

## 🔧 Configuration

Edit `config.json` to customize:

```json
{
  "wake_words": ["hey computer", "computer"],
  "stt": {
    "model_size": "base",
    "device": "cpu"
  },
  "apps": {
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "vscode": "..."
  }
}
```

---

## 🧪 Testing

### Test Individual Components

```bash
# Test microphone
cd audio && python mic_input.py

# Test speech recognition
cd stt && python faster_whisper_stt.py

# Test full pipeline
python main.py
```

---

## 🛣️ Roadmap

### Phase 1: Core Functionality (Week 1)
- [x] Day 1: Audio capture + STT
- [ ] Day 2: LLM integration
- [ ] Day 3: Command executor + safety
- [ ] Day 4: Backend API
- [ ] Day 5: Frontend integration
- [ ] Day 6: Confirmation flow
- [ ] Day 7: Polish + packaging

### Phase 2: Enhanced Features (Week 2)
- [ ] Multi-language support
- [ ] Custom wake word training
- [ ] Voice feedback (TTS)
- [ ] Context awareness
- [ ] Learning from corrections

### Phase 3: Ecosystem (Week 3+)
- [ ] Plugin system
- [ ] Mobile companion app
- [ ] Cloud sync (optional)
- [ ] Third-party integrations

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📊 Performance

| Component | Metric | Target | Current |
|-----------|--------|--------|---------|
| STT Latency | Time to transcribe 5s audio | <3s | ~2.3s ✅ |
| Wake Word | Detection accuracy | >80% | ~85% ✅ |
| Command Parse | LLM response time | <2s | TBD |
| Execution | Command execution | <1s | TBD |

---

## 🔒 Privacy & Security

- **100% Offline** - No data sent to cloud services
- **Local Processing** - All AI runs on your machine
- **Audit Logs** - Complete transparency of all actions
- **Safety Checks** - Risk assessment before execution
- **User Confirmation** - Manual approval for sensitive operations

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - Efficient speech recognition
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI framework

---

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/midhat81/ai-windows-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/midhat81/ai-windows-agent/discussions)

---

## 📧 Contact

Your Name - [Muhammad Midhat/ mianmidhat@gmail.com]

Project Link: [https://github.com/midhat81/ai-windows-agent](https://github.com/midhat81/ai-windows-agent)

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=midhat81/ai-windows-agent&type=Date)](https://star-history.com/midhat81/ai-windows-agent&Date)

---

<p align="center">Muhammad Midhat AI Agent 🤖</p>
<p align="center">
  <a href="#top">⬆️ Back to Top</a>
</p>