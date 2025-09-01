#!/bin/bash

# Whisper-Input One-Click Startup Script
# For macOS systems

echo "🎤 Whisper-Input One-Click Startup Script"
echo "================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if in project directory
if [ ! -f "$SCRIPT_DIR/main.py" ]; then
    echo "❌ Error: Cannot find project files, please check script location"
    exit 1
fi

# Switch to project directory
cd "$SCRIPT_DIR"
echo "📁 Switched to project directory: $SCRIPT_DIR"

# Check Python version
echo "🔍 Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 not found, please install Python 3.10 or higher"
    echo "Recommended installation via Homebrew: brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python version: $PYTHON_VERSION"

# Check if Python version meets requirements
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "✅ Python version meets requirements (3.10+)"
else
    echo "❌ Error: Python version too low, requires 3.10 or higher"
    exit 1
fi

# Check virtual environment
echo "🔍 Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created successfully"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo "✅ Virtual environment activated"

# Check .env file
echo "🔍 Checking configuration file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Copying configuration file template..."
        cp .env.example .env
        echo "✅ Configuration file created, please edit .env file to configure API KEY"
        echo "💡 Tips:"
        echo "   - For SiliconFlow: set SERVICE_PLATFORM=siliconflow and SILICONFLOW_API_KEY"
        echo "   - For Groq: set SERVICE_PLATFORM=groq and GROQ_API_KEY"
        echo ""
        echo "Please configure and rerun this script"
        exit 0
    else
        echo "❌ Error: .env or .env.example file not found"
        exit 1
    fi
fi

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
if ! python3 -c "import sounddevice, pynput, openai, requests" &> /dev/null; then
    echo "📦 Installing dependency packages..."
    
    # Prioritize existing requirements.txt
    if [ -f "requirements.txt" ]; then
        echo "Installing dependencies using requirements.txt..."
        pip install -r requirements.txt
    elif [ -f "requirements.in" ]; then
        echo "Compiling and installing dependencies using requirements.in..."
        pip install pip-tools
        pip-compile requirements.in
        pip install -r requirements.txt
    else
        echo "❌ Error: Dependency file requirements.txt or requirements.in not found"
        exit 1
    fi
    
    if [ $? -ne 0 ]; then
        echo "❌ Dependency installation failed"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ Dependencies already installed"
fi

# Check permissions
echo "🔍 Checking system permissions..."
echo "⚠️  Note: This application requires the following permissions:"
echo "   1. Microphone permission - for audio recording"
echo "   2. Accessibility permission - for keyboard monitoring and text input"
echo ""

# Start program
echo "🚀 Starting Whisper-Input..."
echo "================================"
echo "💡 Usage instructions:"
echo "   - Hold Option key to start recording (speech-to-text)"
echo "   - Hold Shift + Option to start recording (Chinese to English translation)"
echo "   - Release key to stop recording and process"
echo ""
echo "Press Ctrl+C to exit program"
echo "================================"

# Run main program
python3 main.py
