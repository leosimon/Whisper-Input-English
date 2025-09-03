# Quick Deployment Guide

## Prerequisites
Install Python 3.1x for Mac first
python3 --version

## Installation Steps

### Step 1: Download Source Code

```bash
git clone https://github.com/leosimon/Whisper-Input-English.git
cd Whisper-Input-English
```

### Step 2: Register API Service

* Visit [Groq Console](https://console.groq.com/login)
* Get your API Key

### Step 3: Create and Edit Configuration File

```bash
chmod +x start.sh
./start.sh  # Script will automatically create .env file
```

Edit two key configurations in the `.env` file:

```bash
SERVICE_PLATFORM=groq
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### Step 4: Configure System Permissions ⭐ **Critical Step**

**Configure permissions before editing the .env file!**

1. **Microphone Permission**
   * System Preferences → Privacy & Security → Microphone
   * Add Terminal and check it

2. **Accessibility Permission**
   * System Preferences → Privacy & Security → Accessibility
   * Add Terminal and check it

### Step 5: One-Click Startup

```bash
./start.sh
```

### Step 6: Create Desktop Shortcut (Optional)

1. **Use Automator to Create Application**
   * Open Automator
   * Select "Application"
   * Add "Run Shell Script" action
   * Configure script content (see below)

2. **Automator Script Content**

   #!/bin/bash
   
   cd "/Users/leo/Whisper-Input-English"
   
   osascript -e 'tell application "Terminal"
       activate
       do script "cd \"/Users/leo/Whisper-Input-English\" && ./start.sh"
   end tell'

## 🎮 Usage Instructions

After successful startup, you can use:

* **Option Key**: Start speech-to-text recording
* **Release Key**: Stop recording and process
* **Shift + Option**: Start Chinese to English translation recording

## 🔧 Troubleshooting

### Common Errors and Solutions

1. **"Input event monitoring will not be possible"**
   * Solution: Grant accessibility permission in System Preferences

2. **"Unable to access audio device"**
   * Solution: Grant microphone permission in System Preferences

3. **"API request timeout"**
   * Solution: Set `API_TIMEOUT_SECONDS` value to 120 or higher in .env file

4. **"Dependency installation failed"**
   * Solution: Use `clean_and_setup.sh` script to reconfigure environment

## 📚 Additional Resources

* [Original Project](https://github.com/ErlichLiu/Whisper-Input)
* [Issues & Support](https://github.com/leosimon/Whisper-Input-English/issues)
* [Contributing](https://github.com/leosimon/Whisper-Input-English/blob/main/CONTRIBUTING.md)
