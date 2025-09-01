#!/bin/bash

# Whisper-Input 一键启动脚本
# 适用于 macOS 系统

echo "🎤 Whisper-Input 一键启动脚本"
echo "================================"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查是否在项目目录中
if [ ! -f "$SCRIPT_DIR/main.py" ]; then
    echo "❌ 错误：无法找到项目文件，请检查脚本位置"
    exit 1
fi

# 切换到项目目录
cd "$SCRIPT_DIR"
echo "📁 切换到项目目录: $SCRIPT_DIR"

# 检查 Python 版本
echo "🔍 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3，请先安装 Python 3.10 或更高版本"
    echo "推荐使用 Homebrew 安装：brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python 版本：$PYTHON_VERSION"

# 检查 Python 版本是否满足要求
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "✅ Python 版本满足要求（3.10+）"
else
    echo "❌ 错误：Python 版本过低，需要 3.10 或更高版本"
    exit 1
fi

# 检查虚拟环境
echo "🔍 检查虚拟环境..."
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 创建虚拟环境失败"
        exit 1
    fi
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ 激活虚拟环境失败"
    exit 1
fi
echo "✅ 虚拟环境已激活"

# 检查 .env 文件
echo "🔍 检查配置文件..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 复制配置文件模板..."
        cp .env.example .env
        echo "✅ 配置文件已创建，请编辑 .env 文件配置 API KEY"
        echo "💡 提示："
        echo "   - 对于 SiliconFlow：设置 SERVICE_PLATFORM=siliconflow 和 SILICONFLOW_API_KEY"
        echo "   - 对于 Groq：设置 SERVICE_PLATFORM=groq 和 GROQ_API_KEY"
        echo ""
        echo "请配置完成后重新运行此脚本"
        exit 0
    else
        echo "❌ 错误：未找到 .env 或 .env.example 文件"
        exit 1
    fi
fi

# 检查依赖是否已安装
echo "🔍 检查依赖..."
if ! python3 -c "import sounddevice, pynput, openai, requests" &> /dev/null; then
    echo "📦 安装依赖包..."
    
    # 优先使用现有的 requirements.txt
    if [ -f "requirements.txt" ]; then
        echo "使用 requirements.txt 安装依赖..."
        pip install -r requirements.txt
    elif [ -f "requirements.in" ]; then
        echo "使用 requirements.in 编译并安装依赖..."
        pip install pip-tools
        pip-compile requirements.in
        pip install -r requirements.txt
    else
        echo "❌ 错误：未找到依赖文件 requirements.txt 或 requirements.in"
        exit 1
    fi
    
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi

# 检查权限
echo "🔍 检查系统权限..."
echo "⚠️  注意：此应用需要以下权限："
echo "   1. 麦克风权限 - 用于录音"
echo "   2. 辅助功能权限 - 用于键盘监听和文本输入"
echo ""

# 启动程序
echo "🚀 启动 Whisper-Input..."
echo "================================"
echo "💡 使用说明："
echo "   - 按住 Option 键开始录音（语音转文字）"
echo "   - 按住 Shift + Option 开始录音（中文翻译为英文）"
echo "   - 松开按键结束录音并处理"
echo ""
echo "按 Ctrl+C 退出程序"
echo "================================"

# 运行主程序
python3 main.py
