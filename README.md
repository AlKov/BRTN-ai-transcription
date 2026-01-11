# BRTN (Baritone) - AI Transcriber

<p align="center">
  <img src="app_icon.png" alt="BRTN Logo" width="128" height="128">
</p>

<p align="center">
  <strong>Privacy-First Speech-to-Text for macOS</strong>
</p>

<p align="center">
  A free, open-source transcription app that lets you talk your thoughts and paste the text whenever you want—all while keeping your data completely private.
</p>

---

## 🎯 What is BRTN?

BRTN (Baritone) is a macOS menu bar application that provides real-time speech-to-text transcription using OpenAI's Whisper Large V3 Turbo model. Unlike cloud-based solutions, BRTN processes everything locally on your Mac, ensuring your voice data never leaves your device.

Perfect for:
- 📝 Taking quick notes by voice
- ✍️ Drafting emails and documents
- 💭 Capturing thoughts on the fly
- 🎙️ Transcribing meetings and interviews
- 🚀 Boosting productivity without compromising privacy

---

## ✨ Key Features

### 🔒 **100% Private**
- All processing happens locally on your Mac
- No cloud uploads or external API calls
- No data collection or tracking
- Your voice data never leaves your device

### 🚀 **Powered by Whisper Large V3 Turbo**
- State-of-the-art AI speech recognition
- High accuracy across multiple languages
- Optimized for speed and performance
- Based on open-source technology

### 🎯 **Simple & Convenient**
- Lives in your menu bar for instant access
- Quick keyboard shortcuts for recording
- Copy transcribed text to clipboard automatically
- No sign-up or account required

### 💰 **Completely Free**
- No premium tier or in-app purchases
- No subscriptions or hidden costs
- Free forever

### 🌐 **Works Offline**
- No internet connection required
- Perfect for sensitive environments
- Reliable transcription anywhere

---

## 📋 Requirements

- **Operating System**: macOS 12.0 (Monterey) or later
- **Python**: Python 3.8 or later
- **RAM**: Minimum 8GB recommended (16GB for optimal performance)
- **Storage**: ~3GB for the Whisper model
- **Microphone**: Any working microphone input

---

## 🚀 Installation

### Prerequisites

1. **Install Homebrew** (if not already installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install Python** (if not already installed):
```bash
brew install python@3.11
```

3. **Install ffmpeg** (required by Whisper):
```bash
brew install ffmpeg
```

### Quick Install

1. **Clone the repository**:
```bash
git clone https://github.com/AlKov/BRTN-ai-transcription.git
cd BRTN-ai-transcription
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install Whisper**:
```bash
pip install openai-whisper
```

4. **Run the setup script**:
```bash
chmod +x brtn.sh
./brtn.sh
```

5. **Grant microphone permissions**:
   - When prompted, allow BRTN to access your microphone in System Settings
   - Go to: System Settings → Privacy & Security → Microphone

---

## 📖 Usage

### Starting BRTN

Launch BRTN from the command line:
```bash
python brtn_launcher.py
```

Or use the shell script:
```bash
./brtn.sh
```

### Menu Bar Controls

Once running, BRTN appears as an icon in your menu bar:

- **Click the icon** to open the menu
- **Start Recording** to begin transcription
- **Stop Recording** to end transcription and copy text to clipboard
- **Settings** to configure options
- **Quit** to exit the application

### Keyboard Shortcuts

Configure custom keyboard shortcuts in Settings for:
- Start/Stop recording
- Quick paste transcription
- Open settings

### Configuration

Access settings through the menu bar icon to configure:
- **Model Selection**: Choose from different Whisper models (turbo, large, medium, small)
- **Language**: Set preferred language or enable auto-detection
- **Audio Settings**: Adjust microphone input and sensitivity
- **Keyboard Shortcuts**: Customize hotkeys
- **Output Format**: Configure how transcribed text is formatted

---

## 🛠️ Technical Details

### Architecture

BRTN consists of several key components:

- **`brtn_launcher.py`**: Main application launcher and menu bar interface
- **`brtn_transcriber.py`**: Core transcription engine using Whisper
- **`brtn_settings_ui.py`**: Settings configuration interface
- **`brtn_config.py`**: Configuration management
- **`run_transcriber.sh`**: Helper script for running the transcriber

### Whisper Model

BRTN uses [Whisper Large V3 Turbo](https://huggingface.co/openai/whisper-large-v3-turbo), which offers:
- Near state-of-the-art accuracy
- Faster inference than previous versions
- Multilingual support (99+ languages)
- Robust performance with various accents and audio conditions

### Audio Processing

- **Sample Rate**: 16kHz (Whisper's native rate)
- **Format**: 16-bit PCM
- **Processing**: Real-time with minimal latency
- **Voice Activity Detection**: Automatic silence detection

---

## 🔐 Privacy & Security

BRTN is built with privacy as the foundation:

- ✅ **No cloud services**: All processing is local
- ✅ **No data collection**: We don't collect any user data
- ✅ **No analytics**: No tracking or usage statistics
- ✅ **No network requests**: App works completely offline
- ✅ **Open source**: Code is fully auditable

For detailed privacy information, see our [Privacy Policy](docs/PRIVACY_POLICY.md).

---

## 🐛 Troubleshooting

### Microphone Not Working

1. Check System Settings → Privacy & Security → Microphone
2. Ensure BRTN/Python has microphone permission
3. Restart BRTN after granting permissions

### Poor Transcription Quality

1. **Check microphone quality**: Use a better microphone if possible
2. **Reduce background noise**: Find a quieter environment
3. **Try a larger model**: Switch to `large-v3` in settings (slower but more accurate)
4. **Speak clearly**: Moderate pace and clear enunciation help

### High CPU/Memory Usage

1. **Use turbo model**: Switch to `large-v3-turbo` for better performance
2. **Close other applications**: Free up system resources
3. **Consider hardware upgrade**: Whisper benefits from more RAM and CPU

### Installation Issues

**Python version errors**:
```bash
python3 --version  # Should be 3.8 or later
```

**Missing dependencies**:
```bash
pip install --upgrade -r requirements.txt
```

**ffmpeg not found**:
```bash
brew reinstall ffmpeg
```

---

## 🗺️ Roadmap

Future enhancements we're considering:

- [ ] Support for custom Whisper models
- [ ] Real-time transcription display
- [ ] Export transcriptions to various formats
- [ ] Speaker diarization (identify different speakers)
- [ ] Punctuation and formatting improvements
- [ ] Integration with popular note-taking apps
- [ ] Windows and Linux support
- [ ] Custom vocabulary and terminology support

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/BRTN-ai-transcription.git
cd BRTN-ai-transcription

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python brtn_launcher.py
```

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Update documentation for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

- **Whisper**: MIT License ([OpenAI Whisper](https://github.com/openai/whisper))
- **PyAudio**: MIT License
- Other dependencies: See individual package licenses

---

## 🙏 Acknowledgments

- **OpenAI** for the incredible [Whisper](https://github.com/openai/whisper) model
- All contributors who help improve BRTN
- The open-source community for making projects like this possible

---

## 📧 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/AlKov/BRTN-ai-transcription/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AlKov/BRTN-ai-transcription/discussions)
- **Email**: [Your Contact Email]

---

## ⭐ Star History

If you find BRTN useful, please consider giving it a star on GitHub! It helps others discover the project.

---

## 📸 Screenshots

*Coming soon - Screenshots of BRTN in action will be added here*

---

<p align="center">
  Made with ❤️ for privacy-conscious Mac users
</p>

<p align="center">
  <a href="https://github.com/AlKov/BRTN-ai-transcription/stargazers">⭐ Star</a> •
  <a href="https://github.com/AlKov/BRTN-ai-transcription/issues">🐛 Report Bug</a> •
  <a href="https://github.com/AlKov/BRTN-ai-transcription/issues">✨ Request Feature</a>
</p>
